import streamlit as st
import os

# Load configuration from Streamlit secrets
def get_config():
    return st.secrets

def get_llm_config():
    config = get_config()
    provider = config["general"]["llm_provider"]
    if provider == "groq":
        return {
            "provider": "groq",
            "api_key": config["groq"]["api_key"],
            "model_name": config["groq"]["model_name"]
        }
    elif provider == "openai":
        return {
            "provider": "openai",
            "api_key": config["openai"]["api_key"],
            "model_name": config["openai"]["model_name"]
        }
    else:
        raise ValueError("Invalid LLM provider specified in secrets.")

def get_email_config():
    config = get_config()
    return config["email"]
