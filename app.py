import streamlit as st
import sqlite3
import hashlib
import re
import pandas as pd
from collections import Counter
from langdetect import detect
from googletrans import Translator  

st.set_page_config(page_title="Text Analysis & Translator", page_icon="🌍")

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
if "page" not in st.session_state:
    st.session_state.page = "login"

# Page Navigation Function
def set_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# Login & Signup Page
if st.session_state.page == "login":
    st.title("🔐 Welcome to Text Analysis & Translator")
    st.subheader("Login & Signup")  
    auth_option = st.radio("Choose an option:", ["Login", "Signup"])

    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Password", type="password")

    if auth_option == "Signup":
        if st.button("Signup"):
            if signup(email, password):
                st.success("✅ Account created successfully! Please login.")
            else:
                st.error("❌ Email already exists!")

    elif auth_option == "Login":
        if st.button("Login"):
            if login(email, password):
                st.session_state.authenticated = True
                set_page("analysis")
            else:
                st.error("❌ Invalid Email or Password")

# App Content After Login
if st.session_state.authenticated and st.session_state.page == "analysis":
    st.title("🌍 Text Analysis & Translator")
    
    tab1, tab2 = st.tabs(["📊 Text Analysis", "🌍 Translation"])
    
    with tab1:
        st.subheader("📊 Text Analysis Tool")
        
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

        text_input = st.text_area("Enter your text here:", value=st.session_state.text_input)
        
        cols = st.columns([2, 2, 2])
        
        with cols[0]:
            if st.button("Clear"):
                st.session_state.text_input = ""
                st.session_state.submitted = False
                st.rerun()

        with cols[1]:
            if st.button("Submit"):
                if not text_input.strip():
                    st.warning("⚠️ Please enter some text before submitting.")
                else:
                    st.session_state.text_input = text_input
                    st.session_state.submitted = True
                    st.rerun()

        if st.session_state.submitted and st.session_state.text_input.strip():
            df_results = analyze_text(st.session_state.text_input)
            st.subheader("📌 Analysis Results")
            st.dataframe(df_results, use_container_width=True)
            if st.button("Proceed to Translation"):
                set_page("translation")

    with tab2:
        st.subheader("🌍 AI-Powered Text Translator")
        
        input_text = st.text_area("Enter text to translate (min 50 words)", height=150)
        
        def detect_language(text):
            try:
                lang_code = detect(text)
                lang_map = {"en": "English", "ta": "Tamil", "hi": "Hindi", "te": "Telugu", "fr": "French"}
                return lang_map.get(lang_code, "Unknown")
            except:
                return "Could not detect"

        if input_text:
            detected_lang = detect_language(input_text)
            st.info(f"Detected Language: **{detected_lang}**")

        languages = {"Tamil": "ta", "English": "en", "Hindi": "hi", "Telugu": "te", "French": "fr"}
        target_language = st.selectbox("Select the language to translate to:", list(languages.keys()))

        def translate_text(text, target_lang):
            translator = Translator()
            target_code = languages.get(target_lang, "en")
            translated = translator.translate(text, dest=target_code)
            return translated.text

        if st.button("Translate"):
            if len(input_text.split()) < 50:
                st.warning("⚠️ Please enter at least 50 words for translation.")
            else:
                translated_text = translate_text(input_text, target_language)
                st.success("✅ Translation Completed!")
                st.markdown(f"**📜 Translated Text:**\n\n{translated_text}")
                if st.button("Thank You, Go to Home Page"):
                    set_page("analysis")
