import streamlit as st
import pandas as pd
from app.services.chat import chat_service
from datetime import datetime
import sqlite3
import uuid
import hashlib

# Initialize database connection
def init_db():
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            created_at DATETIME,
            last_seen DATETIME,
            display_name TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            user_id TEXT,
            description TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
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

# Generate or get user ID from session_state
def get_user_id():
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = str(uuid.uuid4())
    return st.session_state['user_id']

# Load chat history for specific user
def load_chat_history(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            cs.id, 
            cs.timestamp, 
            cs.user_id, 
            (SELECT m.content FROM messages m WHERE m.session_id = cs.id ORDER BY m.timestamp ASC LIMIT 1) as first_message,
            (SELECT m.content FROM messages m WHERE m.session_id = cs.id ORDER BY m.timestamp DESC LIMIT 1) as last_message
        FROM chat_sessions cs
        WHERE cs.user_id = ?
        ORDER BY cs.timestamp DESC
        LIMIT 5
    ''', (user_id,))
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

# Clear all chat history
def clear_chat_history(conn):
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM chat_sessions
    ''')
    cursor.execute('''
        DELETE FROM messages
    ''')
    conn.commit()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

# Initialize database connection
conn = init_db()

# Get or create user ID
user_id = get_user_id()

# Add user profile section in sidebar
with st.sidebar.expander("User Profile"):
    cursor = conn.cursor()
    cursor.execute('SELECT display_name FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    current_name = result[0] if result else None
    
    new_name = st.text_input("Your Name", value=current_name or "")
    if new_name and new_name != current_name:
        cursor.execute('''
            INSERT OR REPLACE INTO users (id, created_at, last_seen, display_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, datetime.now(), datetime.now(), new_name))
        conn.commit()
        st.success("Name updated!")

# Add new chat and clear history buttons side by side
col_new, col_clear = st.sidebar.columns(2)
with col_new:
    if st.button("New Chat"):
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How can I help you?"}
        ]
with col_clear:
    if st.button("Clear History"):
        # Show confirmation dialog
        with st.expander("Confirm Clear History"):
            st.warning("Are you sure you want to clear all chat history? This action cannot be undone.")
            if st.button("Yes, Clear History"):
                cursor = conn.cursor()
                cursor.execute('DELETE FROM chat_sessions WHERE user_id = ?', (user_id,))
                conn.commit()
                st.session_state["messages"] = [
                    {"role": "assistant", "content": "How can I help you?"}
                ]
                st.success("Chat history has been cleared.")

# Add chat history section with buttons
st.sidebar.title("Chat History")
chat_history = load_chat_history(conn, user_id)

# Create a container for chat history buttons
with st.sidebar.expander("Previous Chats"):
    if chat_history:
        # Create a single column layout for buttons
        cols = st.columns(1)  # 1 column for the grid
        for i, row in enumerate(chat_history):
            session_id = row[0]
            timestamp = row[1]
            user_id = row[2]
            first_message = row[3]
            last_message = row[4]
            
            # Place the button in the single column
            with cols[0]:
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

    # Notification state management
    st.session_state["show_context_notification"] = True
    st.session_state["show_context_detail"] = False
    st.session_state["last_context"] = result.get("context", result["response"])  # fallback to response if no context

    # Store messages in database
    cursor = conn.cursor()
    # Update user's last seen timestamp
    cursor.execute('''
        INSERT OR REPLACE INTO users (id, created_at, last_seen)
        VALUES (?, COALESCE((SELECT created_at FROM users WHERE id = ?), ?), ?)
    ''', (user_id, user_id, datetime.now(), datetime.now()))
    
    cursor.execute('''
        INSERT INTO chat_sessions 
        (timestamp, user_id, description) 
        VALUES (?, ?, ?)
    ''', (datetime.now(), user_id, prompt))
    session_id = cursor.lastrowid
    for msg in st.session_state.messages[-2:]:
        cursor.execute('''
            INSERT INTO messages 
            (session_id, role, content, timestamp) 
            VALUES (?, ?, ?, ?)
        ''', (session_id, msg["role"], msg["content"], datetime.now()))
    conn.commit()

# Example: get a short version (first sentence or 50 chars)
def get_short_context(context):
    if not context:
        return ""
    # Try to get first sentence, else first 50 chars
    if '.' in context:
        return context.split('.')[0] + '.'
    return context[:50] + ('...' if len(context) > 50 else '')

# Notification UI (always show at the end of the script)
if st.session_state.get("show_context_notification"):
    with st.container():
        # Get context versions
        full_context = st.session_state.get("last_context", "No context available.")
        short_context = get_short_context(full_context)
        show_full = st.session_state.get("show_context_detail", False)

        # Display context (short or full)
        st.info(full_context if show_full else short_context)

        # Small icon-only buttons
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if not show_full:
                if st.button("", key="show_detail_btn", help="Show more", icon="👁️"):
                    st.session_state["show_context_detail"] = True
            else:
                if st.button("", key="less_context_btn", help="Show less", icon="➖"):
                    st.session_state["show_context_detail"] = False
        with col2:
            if st.button("", key="cancel_context_btn", help="Cancel notification", icon="❌"):
                st.session_state["show_context_notification"] = False
                st.session_state["show_context_detail"] = False

# Close database connection
conn.close()