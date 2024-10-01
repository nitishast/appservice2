import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import config
import os

api_key = config.GOOGLE_API_KEY
chat_model = config.CHAT_MODEL
chunk_size = config.CHUNK_SIZE
chunk_overlap = config.CHUNK_OVERLAP
embeddings_model = config.EMBEDDINGS_MODEL


genai.configure(api_key=api_key)

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
    st.header("Upload an Invoice (Ex: GST Invoice from the web) and start asking field information")
    st.text("Example: What is the address of the entity in the invoice?")

    
    sample_invoice_path = "InvoiceExtracter/gst image.jpg"  # Update this path
    if os.path.exists(sample_invoice_path):
        with open(sample_invoice_path, "rb") as file:
            st.download_button(
                label="Download Sample Invoice",
                data=file,
                file_name="sample_invoice.jpg",
                mime="image/jpeg"
            )
    else:
        st.warning("Sample invoice file not found.")

    input = st.text_input("Enter the field or information you would like to know:", key='input')
    uploaded_file = st.file_uploader("Choose an image of an invoice:", 
                                     type=['jpg', 'jpeg', 'png'])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        # Create two columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image, caption="Uploaded Invoice", use_column_width=True)
        
        with col2:
            # Display file details
            file_details = {
                "Filename": uploaded_file.name,
                "File Type": uploaded_file.type,
                "File Size": f"{uploaded_file.size / 1024:.2f} KB"
            }
            st.write("File Details:")
            for key, value in file_details.items():
                st.write(f"- {key}: {value}")

    submit = st.button("Tell me about the invoice.",type="primary")
    input_prompt = """
    You are an expert in understanding invoices. I will upload an invoice and you will have to answer the question
    based on the information in the invoice. Only answer the asked question with specific information without additional commentary.
    """

    if submit:
        if uploaded_file is None:
            st.error("Please upload an invoice image before submitting.")
        else:
            image_data = Image.open(uploaded_file)
            response = get_gemini_reponse(input_prompt, image_data, input)
            st.subheader("The response is")
            st.write(response)