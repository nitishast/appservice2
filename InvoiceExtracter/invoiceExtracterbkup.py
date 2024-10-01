import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import config

api_key = config.GOOGLE_API_KEY
chat_model = config.CHAT_MODEL
chunk_size = config.CHUNK_SIZE
chunk_overlap = config.CHUNK_OVERLAP
embeddings_model = config.EMBEDDINGS_MODEL

# Configure the Gemini API
genai.configure(api_key=api_key)

# Set up the model
model = genai.GenerativeModel(chat_model)

def get_gemini_reponse(input, image, prompt):
    response = model.generate_content([prompt, image, input])
    return response.text

def get_image_in_byte(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded.")

def run():
    # st.set_page_config(page_title="Multilanguage Invoice Extracter App")
    st.header("Upload an Invoice(Ex: GST Invoice from the web) and start asking field information")
    st.text("Example: What is the address of the entity in the invoice?")

    input = st.text_input("Enter the field or information you would like to know:", key='input')
    uploaded_file = st.file_uploader("Choose an image of an invoice:", 
                                     type=['jpg', 'jpeg', 'png'])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image",  use_column_width=False, width=400)

    submit = st.button("Tell me about the invoice.")
    input_prompt = """
    You are an expert in understanding invoices. I will upload an invoice and you will have to answer the question
    based on the information in the invoice. Only answer the asked question with specific information without additional commentary.
    """

    if submit:
        image_data = Image.open(uploaded_file)
        response = get_gemini_reponse(input_prompt, image_data, input)
        st.subheader("The response is")
        st.write(response)
