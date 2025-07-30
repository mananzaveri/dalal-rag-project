import streamlit as st
import sys
import os
import pyperclip

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.backend.core.retriever import RAGRetriever
from app.backend.translator.translator import translate

retriever = RAGRetriever()

st.set_page_config(page_title="AI Tutor", page_icon="💬", layout="centered")

# Sidebar
with st.sidebar:
    st.markdown("## Home")
    st.markdown("### Language Settings")
    input_lang = st.selectbox(
        "Input Language",
        ["English", "Spanish", "French", "Russian", "Hindi", "Gujarati", "Chinese (Simplified)", "Thai"],
        index=0
    )
    output_lang = st.selectbox(
        "Output Language",
        ["English", "Spanish", "French", "Russian", "Hindi", "Gujarati", "Chinese (Simplified)", "Thai"],
        index=0
    )

st.markdown("<h1 style='margin-bottom: 1rem;'>AI Tutor</h1>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "bot", "text": "Hello! How can I assist you today?"}]

user_input = st.chat_input(f"Type your message in {input_lang}...")

# Handle user message
if user_input and len(user_input.strip()) >= 2:
    st.session_state.messages.append({"role": "user", "text": user_input})

    # Translate input to English for processing
    translated_input = translate(user_input, src_lang=input_lang, tgt_lang="English")

    st.session_state.pending_input = translated_input
    st.session_state.pending_output_lang = output_lang
    st.rerun()

# Display chat history with copy buttons
# Display chat history with proper alignment and simple copy
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "bot":
        # Clean text for copying (remove language prefix)
        clean_text = msg["text"]
        if clean_text.startswith("(") and ")" in clean_text:
            clean_text = clean_text.split(")", 1)[1].strip()
        
        # Bot message aligned left with copy button
        col1, col2, col3 = st.columns([8, 1, 3])  # Message, button, spacer
        
        with col1:
            st.markdown(
                f"""
                <div style='background-color:#2146db; padding:15px; border-radius:10px; color:white; margin-bottom:10px;'>
                    {msg["text"]}
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            copy_key = f"copy_{i}_{hash(msg['text']) % 10000}"
            if st.button("📋", key=copy_key, help="Copy to clipboard"):
                try:
                    pyperclip.copy(clean_text)
                    st.success("✅")
                except Exception as e:
                    st.error("❌ Copy failed")
                    
    else:
        # User message aligned right
        col1, col2 = st.columns([3, 8])  # Spacer, message
        
        with col2:
            st.markdown(
                f"""
                <div style='display:flex; justify-content:flex-end; margin-bottom:10px;'>
                    <div style='background-color:#569aec; padding:10px 15px; border-radius:10px; max-width:100%; color:white;'>
                        {msg["text"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# Process response
if "pending_input" in st.session_state:
    with st.spinner("Thinking..."):
        try:
            result = retriever.get_response(st.session_state.pending_input)
            english_answer = result.get("answer", "").strip() or "Sorry, I couldn't generate an answer."

            # Only translate if target language is not English
            if st.session_state.pending_output_lang == "English":
                full_response = english_answer
            else:
                # Translate answer to output language
                translated_answer = translate(english_answer, src_lang="English", tgt_lang=st.session_state.pending_output_lang)
                
                # Check if translation actually worked by comparing with original
                if translated_answer != english_answer and not translated_answer.startswith("[Translation error"):
                    full_response = f"(Responding in {st.session_state.pending_output_lang}) {translated_answer}"
                else:
                    full_response = f"(Translation to {st.session_state.pending_output_lang} failed, responding in English) {english_answer}"

        except Exception as e:
            full_response = f"There was an error: {e}"

        st.session_state.messages.append({"role": "bot", "text": full_response})
        del st.session_state["pending_input"]
        del st.session_state["pending_output_lang"]
        st.rerun()


# Smooth autoscroll to bottom of chat
st.markdown("""
<script>
    var chatContainer = window.parent.document.querySelector('.main');
    if (chatContainer) {
        chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
    }
</script>
""", unsafe_allow_html=True)