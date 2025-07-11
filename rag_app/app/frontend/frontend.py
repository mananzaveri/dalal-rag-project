import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.backend.core.retriever import RAGRetriever
from app.backend.translator.translator import translate

# Language mapping for Google Translate
lang_map = {
    "English": "english",
    "Spanish": "spanish",
    "Hindi": "hindi",
    "French": "french",
    "Chinese": "chinese",
    "Gujarati": "gujarati",
    "Thai": "thai"
}

retriever = RAGRetriever()

# Page setup
st.set_page_config(page_title="AI Tutor", page_icon="💬", layout="centered")

# Sidebar for language settings
with st.sidebar:
    st.markdown("## Home")
    st.markdown("### Language Settings")
    input_lang = st.selectbox("Input Language", list(lang_map.keys()), index=0)
    output_lang = st.selectbox("Output Language", list(lang_map.keys()), index=0)

src_lang = lang_map.get(input_lang, "english")
tgt_lang = lang_map.get(output_lang, "english")

# Header
st.markdown("<h1 style='margin-bottom: 1rem;'>AI Tutor</h1>", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "text": "Hello! How can I assist you today?"}
    ]

# Chat input
user_input = st.chat_input(f"Type your message in {input_lang}...")

if user_input and len(user_input.strip()) >= 2:
    # Append user message immediately
    st.session_state.messages.append({"role": "user", "text": user_input})

    # Translate user input to English for RAG
    translated_input = translate(user_input, src_lang=src_lang, tgt_lang="english")

    st.session_state.pending_input = translated_input
    st.session_state.pending_output_lang = output_lang
    st.rerun()    
    
# Display message history
for msg in st.session_state.messages:
    align = "flex-start" if msg["role"] == "bot" else "flex-end"
    bubble_color = "#2146db" if msg["role"] == "bot" else "#569aec"
    st.markdown(
        f"""
        <div style='display: flex; justify-content: {align}; margin-bottom: 10px;'>
            <div style='background-color: {bubble_color}; padding: 10px 15px; border-radius: 10px; max-width: 70%; color: white;'>
                {msg["text"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

if "pending_input" in st.session_state:
    with st.spinner("Thinking..."):
        try:
            result = retriever.get_response(st.session_state.pending_input)
            english_answer = result.get("answer", "").strip()

            # Handle empty or fallback answers
            if not english_answer:
                english_answer = "Sorry, I couldn't generate an answer."

            # Translate answer back to selected output language
            translated_answer = translate(english_answer, src_lang="english", tgt_lang=tgt_lang)
            full_response = f"(Responding in {st.session_state.pending_output_lang}) {translated_answer}"
        except Exception as e:
            full_response = f"There was an error: {e}"

        st.session_state.messages.append({"role": "bot", "text": full_response})
        del st.session_state["pending_input"]
        del st.session_state["pending_output_lang"]
        st.rerun()

# Smooth scroll to bottom (nice UX)
st.markdown("""
    <script>
        var chatContainer = window.parent.document.querySelector('.main');
        if (chatContainer) {
            chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
        }
    </script>
""", unsafe_allow_html=True)
