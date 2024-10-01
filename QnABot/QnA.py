import streamlit as st
import google.generativeai as genai
import config

api_key = config.GOOGLE_API_KEY
chat_model = config.CHAT_MODEL

genai.configure(api_key=api_key)

model = genai.GenerativeModel(chat_model)
chat = model.start_chat(history=[])

# def generate_response(question):
#     response = chat.send_message(question, stream=True)
#     return response

def generate_response(question):
    response = chat.send_message(question, stream=True)
    # Prompt the model to generate a concise summary of the response
    concise_response = model.generate_text(prompt="Summarize the following text concisely:", text=response.text)
    return concise_response.text

def run():
    # st.set_page_config(page_title="Conversational Gemini Bot")

    st.header("QnA Demo App")

    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    input = st.text_input("Input:", key='input')
    submit = st.button("Ask the question")

    if submit and input:
        response = generate_response(input)
        # Use session chat history to store question and response
        st.session_state['chat_history'].append(("You", input))
        st.subheader("The response is")
        for chunk in response:
            st.write(chunk.text)
            st.session_state['chat_history'].append(("Bot", chunk.text))

    st.subheader("The chat history is")
    for role, text in st.session_state['chat_history']:
        st.write(f"{role}:{text}")
