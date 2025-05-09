import streamlit as st
import pandas as pd
from app.services.chat import chat_service
from datetime import datetime
import sqlite3

# Initialize database connection
def init_db():
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            user_id TEXT,
            description TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp DATETIME,
            FOREIGN KEY(session_id) REFERENCES chat_sessions(id)
        )
    ''')
    conn.commit()
    return conn

# Load chat history
def load_chat_history(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            cs.id, 
            cs.timestamp, 
            cs.user_id, 
            (SELECT m.content FROM messages m WHERE m.session_id = cs.id ORDER BY m.timestamp ASC LIMIT 1) as first_message,
            (SELECT m.content FROM messages m WHERE m.session_id = cs.id ORDER BY m.timestamp DESC LIMIT 1) as last_message
        FROM chat_sessions cs
        ORDER BY cs.timestamp DESC
        LIMIT 5
    ''')
    return cursor.fetchall()

# Load specific chat session
def load_chat_session(conn, session_id):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, content, timestamp 
        FROM messages 
        WHERE session_id = ?
        ORDER BY timestamp ASC
    ''', (session_id,))
    return cursor.fetchall()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

# Initialize database connection
conn = init_db()

# Add new chat button
if st.sidebar.button("New Chat"):
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

# Add chat history section with buttons
st.sidebar.title("Chat History")
chat_history = load_chat_history(conn)

# Create a container for chat history buttons
with st.sidebar.expander("Previous Chats"):
    if chat_history:
        # Create a grid layout for buttons
        cols = st.columns(2)  # 2 columns for the grid
        for i, row in enumerate(chat_history):
            session_id = row[0]
            timestamp = row[1]
            user_id = row[2]
            first_message = row[3]
            last_message = row[4]
            
            # Determine which column to place the button in
            col = cols[i % 2]
            with col:
                if st.button(f"Session {i+1} - {timestamp}"):
                    loaded_messages = load_chat_session(conn, session_id)
                    st.session_state["messages"] = [{"role": msg[0], "content": msg[1]} for msg in loaded_messages]
    else:
        st.write("No chat history available.")

st.title("Cheese Products AI - Assistant")

# Display messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Get user input
if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    
    # Process message
    result = chat_service.process_message(prompt, st.session_state.messages)
    
    # Store message in session state and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": result["response"]})
    st.chat_message("assistant").write(result["response"])

    # Store messages in database
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_sessions 
        (timestamp, user_id, description) 
        VALUES (?, ?, ?)
    ''', (datetime.now(), st.session_state.get("user_id", "anonymous"), prompt))
    session_id = cursor.lastrowid
    for msg in st.session_state.messages[-2:]:
        cursor.execute('''
            INSERT INTO messages 
            (session_id, role, content, timestamp) 
            VALUES (?, ?, ?, ?)
        ''', (session_id, msg["role"], msg["content"], datetime.now()))
    conn.commit()

# Close database connection
conn.close()