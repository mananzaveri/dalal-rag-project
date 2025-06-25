import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


from app.backend.core.retriever import RAGRetriever


retriever = RAGRetriever()
# Page setup
st.set_page_config(page_title="AI Tutor", page_icon="💬", layout="centered")

# Sidebar with language selectors
with st.sidebar:
    st.markdown("## Home")
    st.markdown("### Language Settings")
    input_lang = st.selectbox("Input Language", ["English", "Spanish", "Hindi", "French", "Chinese"], index=0)
    output_lang = st.selectbox("Output Language", ["English", "Spanish", "Hindi", "French", "Chinese"], index=0)

# Header
st.markdown("<h1 style='margin-bottom: 1rem;'>AI Tutor</h1>", unsafe_allow_html=True)

# Store messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "text": "Hello! How can I assist you today?"}
    ]

# Chat input
user_input = st.chat_input(f"Type your message in {input_lang}...")

# Check to make sure user input is valid, also displays input immediately in chat
if user_input and len(user_input.strip()) >= 2:
    st.session_state.messages.append({"role": "user", "text": user_input})
    st.rerun()

# Display chat history
for msg in st.session_state.messages:
    align = "flex-start" if msg["role"] == "bot" else "flex-end"
    bubble_color = "#2146db" if msg["role"] == "bot" else "#569aec"
    st.markdown(
        f"""
        <div style='display: flex; justify-content: {align}; margin-bottom: 10px;'>
            <div style='background-color: {bubble_color}; padding: 10px 15px; border-radius: 10px; max-width: 70%;'>
                {msg["text"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("""
    <script>
        var chatContainer = window.parent.document.querySelector('.main');
        if (chatContainer) {
            chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
        }
    </script>
""", unsafe_allow_html=True)

# Process user input, calls retriever to generate response
if len(st.session_state.messages) >= 2 and st.session_state.messages[-1]["role"] == "user":
    user_input = st.session_state.messages[-1]["text"]
    
    with st.spinner("Thinking..."):
        try:
            result = retriever.get_response(user_input)
            answer = result.get("answer", "Sorry, I couldn't generate an answer.")
            full_response = f"(Responding in {output_lang}) {answer}"
        except Exception as e:
            full_response = f"There was an error: {e}"

    st.session_state.messages.append({"role": "bot", "text": full_response})
    st.rerun()