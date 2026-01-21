import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

try:
    print("Checking imports...")
    from app.main import init_db
    from app.rag_pipeline import RAGPipeline
    from app.chat_logic import detect_intent
    from app.booking_flow import handle_booking_conversation
    from db.database import get_connection
    print("Imports successful.")

    print("Checking Database...")
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables found: {tables}")
    conn.close()
    
    if not any('customers' in t for t in tables) or not any('bookings' in t for t in tables):
        print("Error: Tables not created.")
    else:
        print("Database initialized successfully.")

except Exception as e:
    print(f"Test failed: {e}")
