# AI Booking Assistant

## Project Overview
This is a production-grade GenAI Booking Assistant built with Python, Streamlit, and LangChain. It allows users to query information from uploaded PDFs (RAG) and book appointments through a conversational interface.

## Features
- **Chat Interface**: Interactive chat with intent detection.
- **RAG Pipeline**: Upload PDFs to answer general questions.
- **Booking System**: Collects user details (Name, Email, Phone, Date, Time) and saves to SQLite.
- **Email Confirmation**: Sends booking details via SMTP.
- **Admin Dashboard**: View and manage bookings.
- **Tool Calling**: Modular tools for RAG, Database, and Email operations.

## Tech Stack
- **Frontend**: Streamlit
- **Backend**: Python, LangChain
- **LLM**: Groq (Llama/Mixtral) or OpenAI (configurable)
- **Database**: SQLite
- **Vector Store**: FAISS
- **Email**: SMTP (Gmail)

## Setup Instructions

1. **Clone the repository**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Secrets**
   - Update `.streamlit/secrets.toml` with your API keys and Email credentials.
   - For Gmail, generate an App Password.

4. **Run the Application**
   ```bash
   streamlit run app/main.py
   ```

## Architecture Diagram
```mermaid
graph TD
    User[User] -->|Chat Interface| StreamlitUI[Streamlit UI]
    StreamlitUI -->|Intent Detection| Router{Intent Router}
    
    Router -->|Booking Intent| BookingEngine[Booking Flow Engine]
    Router -->|General Query| RAGTool[RAG Tool]
    
    BookingEngine -->|Store State| SessionState[Session State]
    BookingEngine -->|Save Booking| DBTool[Database Tool]
    BookingEngine -->|Send Confirmation| EmailTool[Email Tool]
    
    RAGTool -->|Retrieve Context| VectorDB[(FAISS Vector Store)]
    RAGTool -->|Generate Answer| LLM[LLM (Groq/OpenAI)]
    
    DBTool --> SQLite[(SQLite DB)]
    EmailTool --> SMTP[SMTP Server]
    
    Admin[Admin] -->|View Data| AdminDashboard[Admin Dashboard]
    AdminDashboard --> SQLite
```

## Deployment
This app is ready for Streamlit Cloud. Ensure you add the secrets from `.streamlit/secrets.toml` to the Streamlit Cloud "Secrets" management section.

## Project Structure
```
project_root/
│
├── app/
│   ├── main.py                # Streamlit entry point
│   ├── chat_logic.py          # Intent detection + memory handling
│   ├── booking_flow.py        # Slot filling + confirmation logic
│   ├── rag_pipeline.py        # PDF ingestion, chunking, embeddings, retrieval
│   ├── tools.py               # RAG tool, DB tool, Email tool
│   ├── admin_dashboard.py     # Admin UI
│   └── config.py              # Configuration
│
├── db/
│   ├── database.py            # Database connection & queries
│   └── models.py              # Schema definitions
│
├── docs/                      # Documentation & Sample PDFs
│
├── requirements.txt           # Dependencies
└── .streamlit/secrets.toml    # Secrets (ignored in git)
```
