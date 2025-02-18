import streamlit as st
import sqlite3
import hashlib
import re
import pandas as pd
from collections import Counter

st.set_page_config(page_title="Welcome to TextAnalysis", page_icon="🔐")

# Database connection
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
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

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "text_input" not in st.session_state:
    st.session_state.text_input = ""

# Login & Signup Page
if not st.session_state.authenticated:
    st.title("🔐 Welcome to TextAnalysis")
    st.subheader("Login & Signup")  # New heading below title
    
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
                st.rerun()  # Immediate refresh
            else:
                st.error("❌ Invalid Email or Password")

# Text Analysis Page (Shown after successful login)
if st.session_state.authenticated:
    st.title("📊 Text Analysis Tool")

    # Function to analyze text
    def analyze_text(text):
        char_count = len(text)
        words = [word.lower() for word in text.split()]
        word_count = len(words)
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)

        word_freq = Counter(words)
        repeated_words = {word: count for word, count in word_freq.items() if count > 1}

        single_word_repeated = sum(1 for count in word_freq.values() if count == 2)
        double_word_repeated = sum(1 for count in word_freq.values() if count == 3)
        triple_word_repeated = sum(1 for count in word_freq.values() if count == 4)

        return pd.DataFrame({
            "Metric": ["Total Characters", "Total Words", "Total Sentences", "Single Word Repeated", "Double Word Repeated", "Triple Word Repeated"],
            "Value": [char_count, word_count, sentence_count, single_word_repeated, double_word_repeated, triple_word_repeated]
        })

    # Input Section
    if not st.session_state.submitted:
        text_input = st.text_area("Enter your text here:", value=st.session_state.text_input)

        cols = st.columns([2, 2, 2])  # Closer button alignment

        # Clear button
        with cols[0]:
            if st.button("Clear"):
                st.session_state.text_input = ""
                st.session_state.submitted = False
                st.rerun()  # Ensures immediate refresh

        # Submit button
        with cols[1]:
            if st.button("Submit"):
                st.session_state.text_input = text_input
                st.session_state.submitted = True
                st.rerun()  # Refresh the app to show results

    # Results Display
    if st.session_state.submitted:
        if st.session_state.text_input.strip():
            df_results = analyze_text(st.session_state.text_input)

            st.subheader("📌 Analysis Results")
            st.dataframe(df_results, use_container_width=True)  # Non-clickable table

            # Add New Text Button
            if st.button("Add New Text"):
                st.session_state.text_input = ""
                st.session_state.submitted = False
                st.rerun()
