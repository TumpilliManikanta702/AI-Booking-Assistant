import sys
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../db"))
if DB_PATH not in sys.path:
    sys.path.append(DB_PATH)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import get_email_config
from database import add_customer, create_booking
from langchain_core.tools import tool
import streamlit as st



@tool
def rag_query_tool(query: str):
    """
    Queries the Knowledge Base (RAG) to answer general questions.
    Returns the answer based on uploaded PDFs.
    """
    if "rag_pipeline" in st.session_state:
        return st.session_state["rag_pipeline"].query(query)
    return "RAG Pipeline not initialized."

@tool
def send_email_tool(to_email: str, subject: str, body: str):
    """
    Sends an email to the specified recipient.
    Useful for sending booking confirmations.
    """
    email_config = get_email_config()
    sender_email = email_config["sender_email"]
    sender_password = email_config["sender_password"]
    smtp_server = email_config["smtp_server"]
    smtp_port = email_config["smtp_port"]

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {str(e)}"

@tool
def save_booking_tool(name: str, email: str, phone: str, booking_type: str, date: str, time: str):
    """
    Saves a booking to the database.
    Requires customer name, email, phone, booking type, date (YYYY-MM-DD), and time (HH:MM).
    Returns the Booking ID.
    """
    try:
        customer_id = add_customer(name, email, phone)
        if not customer_id:
            return "Failed to save customer details."
        
        booking_id = create_booking(customer_id, booking_type, date, time)
        if booking_id:
            return f"Booking saved successfully. Booking ID: {booking_id}"
        else:
            return "Failed to save booking."
    except Exception as e:
        return f"Error saving booking: {str(e)}"
