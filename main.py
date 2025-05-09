import streamlit as st
import pandas as pd
from app.services.chat import chat_service

st.title("Cheese Products AI - Assistant")

# Initialize session state. session state is used to store the messages between the user and the assistant
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are helpful assistant to assist user providing information about cheese products."},
        {"role": "assistant", "content": "How can I help you?"}
    ]

# Display the messages between the user and the assistant
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Get the user's input an
if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    
    # Process the user's input and get the response from the assistant
    result = chat_service.process_message(prompt, st.session_state.messages)
    
    # Append the response to the session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": result["response"]})
    st.chat_message("assistant").write(result["response"])