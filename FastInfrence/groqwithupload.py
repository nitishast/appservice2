import os
import config
import google.generativeai as genai
import streamlit as st
import tempfile

from PyPDF2 import PdfReader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyPDFDirectoryLoader, PyPDFLoader
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
import config
import time

groq_api_key = config.GROQ_API_KEY
pdf_directory = "./pdf_files"

prompt = ChatPromptTemplate.from_template(
    "You are a helpful AI assistant. Answer questions based solely on the provided context. If the answer is not in the context, say 'The answer is not in the provided context.' Do not add any additional commentary or information beyond what is given.:\n\n{context}\n\nQuestion: {input}\nAnswer:"
)

def vector_embeddings(pdf_path, is_directory=True):
    start_time = time.time()
    st.session_state.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    if is_directory:
        loader = PyPDFDirectoryLoader(pdf_path)
    else:
        loader = PyPDFLoader(pdf_path)
    
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    final_documents = text_splitter.split_documents(documents)
    vector_store = FAISS.from_documents(final_documents, st.session_state.embeddings)
    
    end_time = time.time()
    creation_time = end_time - start_time
    
    return vector_store, creation_time

groqmodels = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "llama3-groq-70b-8192-tool-use-preview", "gemma-7b-it"]

def run():
    st.header("High-Performance Document Interaction: Leveraging GROQ API for Rapid Inference")

    col1, col2 = st.columns(2)
    with col1:
        use_own_doc = st.button("Use Own Document",type="primary")
    with col2:
        use_existing_doc = st.button("Use Existing Document",type="primary")

    if use_own_doc:
        st.session_state.show_upload = True
    elif use_existing_doc:
        st.session_state.show_upload = False

    if 'show_upload' not in st.session_state:
        st.session_state.show_upload = False
    st.text("Here are some sample questions:")
    st.text("What is the document about?")
    st.text("Tell me about this topic in the document?")
    if st.session_state.show_upload:
        with st.expander("Upload Your Document", expanded=True):
            uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")
            if st.button("Submit & Process",type="primary"):
                if uploaded_file is not None:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                        temp_file.write(uploaded_file.read())
                        temp_file_path = temp_file.name

                    st.session_state.vector_store, st.session_state.vector_store_creation_time = vector_embeddings(temp_file_path, is_directory=False)
                    os.unlink(temp_file_path)  # Delete the temporary file
                    st.write("Vector Store Created from Uploaded Document")
                    st.write(f"Time Taken to create the vector store: {st.session_state.vector_store_creation_time:.2f} seconds")
                else:
                    st.warning("Please upload a PDF file first.")
    elif use_existing_doc:
        st.session_state.vector_store, st.session_state.vector_store_creation_time = vector_embeddings(pdf_directory)
        st.write("Vector Store Created from Existing Document")
        st.write(f"Time Taken to create the vector store: {st.session_state.vector_store_creation_time:.2f} seconds")

    # Model selection
    selected_model = st.selectbox("Select a model for inference:", groqmodels)

    prompt1 = st.text_input("Enter your question?")

    if prompt1 and 'vector_store' in st.session_state:
        llm = ChatGroq(groq_api_key=groq_api_key, model_name=selected_model)
        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = st.session_state.vector_store.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        start = time.time()
        response = retrieval_chain.invoke({"input": prompt1})
        end = time.time()
        response_time = end - start
        
        st.write(f"Model: {selected_model}")
        st.write(f"Response: {response['answer']}")
        st.write(f"Time taken: {response_time:.2f} seconds")

# if __name__ == "__main__":
#     run()