import streamlit as st
from chat_logic import detect_intent, get_llm
from booking_flow import handle_booking_conversation
from rag_pipeline import RAGPipeline
from admin_dashboard import admin_page
from tools import rag_query_tool
from database import init_db
from langchain_core.messages import SystemMessage, HumanMessage
from chat_logic import detect_intent, get_llm
from booking_flow import handle_booking_conversation
from rag_pipeline import RAGPipeline
from admin_dashboard import admin_page


# Page Config
st.set_page_config(page_title="AI Booking Assistant", layout="wide")

# Initialize DB
init_db()

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "booking_state" not in st.session_state:
    st.session_state["booking_state"] = None
if "rag_pipeline" not in st.session_state:
    st.session_state["rag_pipeline"] = RAGPipeline()

# Sidebar
with st.sidebar:
    st.title("Settings")
    
    # Navigation
    page = st.radio("Go to", ["Chat", "Admin Dashboard"])
    
    st.divider()
    
    # PDF Upload
    st.subheader("Knowledge Base")
    uploaded_files = st.file_uploader("Upload PDFs", accept_multiple_files=True, type=["pdf"])
    if uploaded_files:
        if st.button("Process PDFs"):
            with st.spinner("Processing..."):
                result = st.session_state["rag_pipeline"].process_pdfs(uploaded_files)
                st.success(result)
                st.session_state["rag_auto_processed"] = [f.name for f in uploaded_files]
        else:
            # Auto-process newly uploaded PDFs once
            uploaded_names = [f.name for f in uploaded_files]
            if st.session_state.get("rag_auto_processed") != uploaded_names:
                with st.spinner("Processing..."):
                    result = st.session_state["rag_pipeline"].process_pdfs(uploaded_files)
                    st.success(result)
                    st.session_state["rag_auto_processed"] = uploaded_names

# Main Content
if page == "Admin Dashboard":
    admin_page()
else:
    st.title("AI Booking Assistant 🤖")
    
    # Display Chat History
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if user_input := st.chat_input("How can I help you today?"):
        # Display User Message
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state["messages"].append({"role": "user", "content": user_input})
        
        # Maintain history limit (25 messages)
        if len(st.session_state["messages"]) > 25:
            st.session_state["messages"] = st.session_state["messages"][-25:]

        # Generate Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_text = ""
                
                # Check if we are already in a booking flow
                if st.session_state.get("booking_state"):
                    response_text = handle_booking_conversation(user_input, st.session_state)
                else:
                    # Detect Intent
                    intent = detect_intent(user_input, st.session_state["messages"])
                    
                    if intent == "booking":
                        response_text = handle_booking_conversation(user_input, st.session_state)
                    else:
                        # RAG Flow via Tool
                        context = rag_query_tool.invoke(user_input)
                        
                        llm = get_llm()
                        if llm:
                            messages = [
                                SystemMessage(content="You are a helpful booking assistant. Use the following context to answer the user's question. If the answer is not in the context, politely say you don't know but can help with bookings. \n\n"
                                                      f"Context: {context}"),
                                HumanMessage(content=user_input)
                            ]
                            try:
                                res = llm.invoke(messages)
                                response_text = res.content
                            except Exception as e:
                                # Fallback to direct context if LLM fails
                                if context and not context.startswith("Knowledge base is empty"):
                                    response_text = f"Based on the uploaded documents:\n\n{context}"
                                else:
                                    response_text = f"Error communicating with LLM: {e}"
                        else:
                            response_text = "LLM configuration missing. Please check secrets."

            st.markdown(response_text)
            st.session_state["messages"].append({"role": "assistant", "content": response_text})
