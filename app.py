import streamlit as st
import sqlite3
import hashlib
import re
import pandas as pd
from collections import Counter

st.set_page_config(page_title="Text Analysis App", page_icon="🔐")

# Database connection
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# Create users table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT)''')
conn.commit()

# Password Hashing Function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Authentication Functions
def signup(email, password):
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    if cursor.fetchone():
        return False  # Email already exists
    cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hash_password(password)))
    conn.commit()
    return True

def login(email, password):
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hash_password(password)))
    return cursor.fetchone() is not None

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "text_input" not in st.session_state:
    st.session_state.text_input = ""

st.title("🔐 Login & Signup Page")

# Authentication System
if not st.session_state.authenticated:
    auth_option = st.radio("Choose an option:", ["Login", "Signup"])

    if auth_option == "Signup":
        email = st.text_input("📧 Email")
        password = st.text_input("🔑 Password", type="password")
        if st.button("Signup"):
            if signup(email, password):
                st.success("✅ Account created successfully! Please login.")
            else:
                st.error("❌ Email already exists!")

    elif auth_option == "Login":
        email = st.text_input("📧 Email")
        password = st.text_input("🔑 Password", type="password")
        
        if st.button("Login"):
            if login(email, password):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Invalid Email or Password")

# Show the next screen after login
if st.session_state.authenticated:
    st.success("✅ Login Successful! Redirecting to Text Analysis Tool...")

    # TEXT ANALYSIS TOOL
    def analyze_text(text):
        char_count = len(text)
        words = [word.lower() for word in text.split()]
        word_count = len(words)
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)

        word_freq = Counter(words)
        single_word_repeated = sum(1 for count in word_freq.values() if count == 2)
        double_word_repeated = sum(1 for count in word_freq.values() if count == 3)
        triple_word_repeated = sum(1 for count in word_freq.values() if count == 4)

        return {
            "Total Characters": char_count,
            "Total Words": word_count,
            "Total Sentences": sentence_count,
            "Single Word Repeated Count": single_word_repeated,
            "Double Word Repeated Count": double_word_repeated,
            "Triple Word Repeated Count": triple_word_repeated
        }

    st.title("📊 Text Analysis Tool")

    if not st.session_state.submitted:
        # Input section
        text_input = st.text_area("Enter your text here:", value=st.session_state.text_input)

        # Buttons in a single row
        cols = st.columns([2, 2, 2])
        with cols[0]:
            if st.button("Submit"):
                st.session_state.text_input = text_input
                st.session_state.submitted = True
                st.snow()
                st.rerun()

        with cols[1]:
            if st.button("Clear"):
                st.session_state.text_input = ""
                st.session_state.submitted = False
                st.rerun()

    # Display results in a table
    if st.session_state.submitted:
        if st.session_state.text_input.strip():
            results = analyze_text(st.session_state.text_input)
            df = pd.DataFrame(results.items(), columns=["Metric", "Value"])
            
            st.subheader("📌 Analysis Results")
            st.dataframe(df, use_container_width=True)  # Display results in a table

            # New button to restart analysis
            if st.button("Add New Text"):
                st.session_state.text_input = ""
                st.session_state.submitted = False
                st.rerun()
