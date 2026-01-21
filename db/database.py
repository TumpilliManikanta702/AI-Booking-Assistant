import sqlite3
import pandas as pd
from db.models import CREATE_CUSTOMERS_TABLE, CREATE_BOOKINGS_TABLE
import os

DB_NAME = "booking_assistant.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    """Initialize the database with tables."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(CREATE_CUSTOMERS_TABLE)
    cursor.execute(CREATE_BOOKINGS_TABLE)
    conn.commit()
    conn.close()

def add_customer(name, email, phone):
    """Add a new customer or update existing one."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if customer exists
        cursor.execute("SELECT customer_id FROM customers WHERE email = ?", (email,))
        result = cursor.fetchone()
        
        if result:
            customer_id = result[0]
            # Update details if needed
            cursor.execute("UPDATE customers SET name = ?, phone = ? WHERE customer_id = ?", (name, phone, customer_id))
        else:
            cursor.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
            customer_id = cursor.lastrowid
            
        conn.commit()
        return customer_id
    except Exception as e:
        print(f"Error adding customer: {e}")
        return None
    finally:
        conn.close()

def create_booking(customer_id, booking_type, date, time):
    """Create a new booking."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO bookings (customer_id, booking_type, booking_date, booking_time) VALUES (?, ?, ?, ?)",
            (customer_id, booking_type, date, time)
        )
        booking_id = cursor.lastrowid
        conn.commit()
        return booking_id
    except Exception as e:
        print(f"Error creating booking: {e}")
        return None
    finally:
        conn.close()

def get_all_bookings():
    """Fetch all bookings for admin dashboard."""
    conn = get_connection()
    query = """
    SELECT 
        b.id, c.name, c.email, c.phone, b.booking_type, b.booking_date, b.booking_time, b.status, b.created_at
    FROM bookings b
    JOIN customers c ON b.customer_id = c.customer_id
    ORDER BY b.created_at DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
