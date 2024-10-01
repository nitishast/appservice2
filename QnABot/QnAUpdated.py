import streamlit as st
import google.generativeai as genai
import config

api_key = config.GOOGLE_API_KEY
chat_model = config.CHAT_MODEL

genai.configure(api_key=api_key)

model = genai.GenerativeModel(chat_model)
chat = model.start_chat(history=[])

def generate_response(question):
    response = chat.send_message(question, stream=True)
    return response

def clear_chat_history():
    st.session_state['chat_history'] = []
    global chat
    chat = model.start_chat(history=[])

def run():
    st.markdown("""
    <style>
    .chat-container {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        max-height: 400px;
        overflow-y: auto;
    }
    .user-message {
        background-color: #e6f3ff;
        padding: 5px 10px;
        border-radius: 15px;
        margin: 5px 0;
        text-align: right;
    }
    .bot-message {
        background-color: #f0f0f0;
        padding: 5px 10px;
        border-radius: 15px;
        margin: 5px 0;
        text-align: left;
    }
    .stTextInput>div>div>input {
        border-radius: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Let's Chat!")

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    chat_container = st.container()

    col1, col2 = st.columns([4, 1])
    with col1:
        with st.form(key="user_input_form", clear_on_submit=True):
            user_input = st.text_input("Ask a question:", placeholder="Type your question here")
            submit_button = st.form_submit_button(label="Send")
    with col2:
        clear_button = st.button("Clear Chat")

    if clear_button:
        clear_chat_history()

    with chat_container:
        for role, text in st.session_state['chat_history']:
            if role == "You":
                st.markdown(f'<div class="user-message">{text}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message">{text}</div>', unsafe_allow_html=True)

        if submit_button and user_input:
            st.session_state['chat_history'].append(("You", user_input))
            st.markdown(f'<div class="user-message">{user_input}</div>', unsafe_allow_html=True)
            
            response = generate_response(user_input)
            full_response = ""
            message_placeholder = st.empty()

            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(f'<div class="bot-message">{full_response}</div>', unsafe_allow_html=True)
            
            st.session_state['chat_history'].append(("Bot", full_response))

if __name__ == "__main__":
    run()