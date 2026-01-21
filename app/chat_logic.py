from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from config import get_llm_config
from langchain_core.messages import SystemMessage, HumanMessage

def get_llm():
    """Initialize the LLM based on config."""
    config = get_llm_config()
    
    if config["provider"] == "groq":
        return ChatGroq(
            api_key=config["api_key"],
            model_name=config["model_name"],
            temperature=0
        )
    elif config["provider"] == "openai":
        return ChatOpenAI(
            api_key=config["api_key"],
            model_name=config["model_name"],
            temperature=0
        )
    return None

def detect_intent(user_input, conversation_history):
    """
    Detect if the user wants to make a booking or is asking a general question.
    Returns: 'booking' or 'general'
    """
    llm = get_llm()
    
    # Simple prompt for intent classification
    messages = [
        SystemMessage(content="You are an intent classifier. Determine if the user's input indicates an intent to make a booking/appointment or if it is a general question/greeting. \n"
                              "Output ONLY 'booking' if they want to book something, schedule, or reserve. \n"
                              "Output 'general' for everything else (informational questions, greetings, etc.)."),
        HumanMessage(content=f"User Input: {user_input}")
    ]
    
    try:
        response = llm.invoke(messages)
        intent = response.content.strip().lower()
        if "booking" in intent:
            return "booking"
        return "general"
    except Exception as e:
        print(f"Error in intent detection: {e}")
        # Fallback keyword detection
        keywords = ["book", "appointment", "schedule", "reserve", "slot"]
        if any(k in user_input.lower() for k in keywords):
            return "booking"
        return "general"
