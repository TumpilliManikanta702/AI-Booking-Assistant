import streamlit as st
import pandas as pd
from database import get_all_bookings

def admin_page():
    st.header("Admin Dashboard - Bookings Overview")
    
    # Refresh button
    if st.button("Refresh Data"):
        st.rerun()

    df = get_all_bookings()
    
    if df.empty:
        st.info("No bookings found.")
        return

    # Filters
    st.subheader("Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        name_filter = st.text_input("Filter by Name")
    with col2:
        email_filter = st.text_input("Filter by Email")
    with col3:
        date_filter = st.text_input("Filter by Date (YYYY-MM-DD)")

    # Apply filters
    if name_filter:
        df = df[df['name'].str.contains(name_filter, case=False, na=False)]
    if email_filter:
        df = df[df['email'].str.contains(email_filter, case=False, na=False)]
    if date_filter:
        df = df[df['booking_date'].str.contains(date_filter, case=False, na=False)]

    # Display table
    st.dataframe(df, use_container_width=True)

    # Export to CSV (Bonus)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Bookings as CSV",
        data=csv,
        file_name='bookings.csv',
        mime='text/csv',
    )
