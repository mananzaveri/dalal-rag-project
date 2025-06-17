import streamlit as st

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

# Chat input
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(f"Type your message in {input_lang}...", label_visibility="collapsed")
    submit_button = st.form_submit_button("Send")

if submit_button and user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "text": user_input})

    # Placeholder response — would normally include translation and LLM logic
    response = f"(Responding in {output_lang}) Sure, I'd be happy to help!"
    st.session_state.messages.append({"role": "bot", "text": response})
