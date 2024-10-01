import streamlit as st

def landingpage():
    st.title("Welcome to Multi-App Platform")
    
    st.write("""
    This is the landing page for our versatile application suite. Here's what you can do:
    
    - **Invoice Reader**: Read and extract information from Invoice
    - **Lets Chat!**: Ask questions and get answers from our AI
    - **Talk To Your PDF**: Interact with PDF documents
    - **PDF Chat with GroQ(Faster Inference)**: Experience high-performance document interaction
    - **Query a DB**: Query a Database in Natural Language
    
    Select an app from the navigation menu on the left to get started!
    """)
    
    # st.image("public/homepage.png", caption="Our Multi-App Platform", use_column_width=True)
    
    st.markdown("---")
    st.write("© 2024 IP of Nitish Asthana ; All rights reserved.")
    import base64

    def get_base64_of_bin_file(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()

    def set_png_as_page_bg(png_file):
        bin_str = get_base64_of_bin_file(png_file)
        page_bg_img = '''
        <style>
        .stApp {
            background-image: url("data:image/png;base64,%s");
            background-size: cover;
            background-attachment: fixed;
        }
        </style>
        ''' % bin_str
        st.markdown(page_bg_img, unsafe_allow_html=True)



