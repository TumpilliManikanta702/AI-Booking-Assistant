import re
from email_validator import validate_email, EmailNotValidError
from tools import save_booking_tool, send_email_tool

REQUIRED_FIELDS = ["name", "email", "phone", "booking_type", "date", "time"]

def validate_input(field, value):
    if field == "email":
        try:
            validate_email(value, check_deliverability=False)
            return True
        except EmailNotValidError:
            return False
    if field == "date":
        # Simple regex for YYYY-MM-DD
        return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", value))
    if field == "time":
        # Simple regex for HH:MM
        return bool(re.match(r"^\d{2}:\d{2}$", value))
    return True

def handle_booking_conversation(user_input, session_state):
    """
    Manages the booking conversation flow.
    """
    booking_state = session_state.get("booking_state", {})
    
    # Initialize state if new
    if not booking_state:
        booking_state = {field: None for field in REQUIRED_FIELDS}
        booking_state["step"] = "collect_info"
        session_state["booking_state"] = booking_state

    # If we are in confirmation step
    if booking_state.get("step") == "confirm":
        if "yes" in user_input.lower():
            # Save booking
            result = save_booking_tool.invoke({
                "name": booking_state["name"],
                "email": booking_state["email"],
                "phone": booking_state["phone"],
                "booking_type": booking_state["booking_type"],
                "date": booking_state["date"],
                "time": booking_state["time"]
            })
            
            # Send email
            email_body = (
                f"Dear {booking_state['name']},\n\n"
                f"Your booking for {booking_state['booking_type']} is confirmed.\n"
                f"Date: {booking_state['date']}\n"
                f"Time: {booking_state['time']}\n\n"
                "Thank you!"
            )
            email_status = send_email_tool.invoke({
                "to_email": booking_state["email"],
                "subject": "Booking Confirmation",
                "body": email_body
            })
            
            # Reset state
            session_state["booking_state"] = None
            return f"{result} {email_status}"
        
        elif "no" in user_input.lower():
            session_state["booking_state"] = None
            return "Booking cancelled. You can start over if you wish."
        else:
            return "Please answer 'Yes' to confirm or 'No' to cancel."

    # Logic to fill fields
    # We check which field is currently missing (in order) and if the PREVIOUS turn asked for it, we assume the current input is the answer.
    # However, for a more robust flow, we need to track WHICH field we are currently asking for.
    
    current_field = booking_state.get("current_asking_field")
    
    if current_field:
        # Validate and save the input for the field we just asked about
        if validate_input(current_field, user_input):
            booking_state[current_field] = user_input
            booking_state["current_asking_field"] = None # Reset so we find the next missing one
        else:
            if current_field == "email":
                return "Invalid email format. Please enter a valid email address (e.g., user@example.com)."
            elif current_field == "date":
                return "Invalid date format. Please use YYYY-MM-DD (e.g., 2024-12-31)."
            elif current_field == "time":
                return "Invalid time format. Please use HH:MM (24-hour format, e.g., 14:30)."
            else:
                return f"Invalid format for {current_field}. Please try again."

    # Find next missing field
    for field in REQUIRED_FIELDS:
        if not booking_state[field]:
            booking_state["current_asking_field"] = field
            prompt_map = {
                "name": "May I have your full name?",
                "email": "What is your email address?",
                "phone": "What is your phone number?",
                "booking_type": "What service would you like to book?",
                "date": "What date would you prefer? (YYYY-MM-DD)",
                "time": "What time works best for you? (HH:MM)"
            }
            return prompt_map[field]

    # If all fields are filled, move to confirmation
    booking_state["step"] = "confirm"
    summary = (
        "Here are your booking details:\n"
        f"Name: {booking_state['name']}\n"
        f"Email: {booking_state['email']}\n"
        f"Phone: {booking_state['phone']}\n"
        f"Service: {booking_state['booking_type']}\n"
        f"Date: {booking_state['date']}\n"
        f"Time: {booking_state['time']}\n\n"
        "Do you confirm this booking? (Yes/No)"
    )
    return summary
