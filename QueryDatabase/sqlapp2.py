import sqlite3
import tempfile
import google.generativeai as genai
import streamlit as st
from sqlalchemy import create_engine, text
import os

# Configure Google AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-exp-0801")

def create_database_from_sql(sql_content):
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.db', delete=False) as temp_db:
        conn = sqlite3.connect(temp_db.name)
        conn.executescript(sql_content)
        conn.close()
        return temp_db.name

def execute_query(db_path, query):
    engine = create_engine(f'sqlite:///{db_path}')
    with engine.connect() as connection:
        result = connection.execute(text(query))
        return result.fetchall()

def generate_sql_query(question, schema):
    prompt = f"""
    Given the following SQLite database schema:
    {schema}
    
    Generate a SQLite-compatible SQL query to answer the following question:
    {question}
    
    Important: Use SQLite syntax. For example, to list all tables, use:
    SELECT name FROM sqlite_master WHERE type='table';
    
    Return only the SQL query, without any explanations and do not put ``` at the beggining or end.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def get_schema(db_path):
    engine = create_engine(f'sqlite:///{db_path}')
    with engine.connect() as connection:
        tables = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        schema = []
        for table in tables:
            columns = connection.execute(text(f"PRAGMA table_info('{table[0]}')"))
            schema.append(f"Table: {table[0]}")
            schema.extend([f"  - {col[1]} ({col[2]})" for col in columns])
    return "\n".join(schema)

st.set_page_config(page_title="SQL Database Query App")
st.title("SQL Database Query App")

uploaded_file = st.file_uploader("Upload your .sql file", type="sql")

if uploaded_file:
    sql_content = uploaded_file.getvalue().decode("utf-8")
    db_path = create_database_from_sql(sql_content)
    st.success("Database created successfully!")
    
    schema = get_schema(db_path)
    st.text_area("Database Schema", schema, height=200)
    
    question = st.text_input("Enter your question about the database")
    
    if st.button("Generate and Execute Query"):
        if question:
            generated_query = generate_sql_query(question, schema)
            # st.code(generated_query, language="sql")
            
            try:
                results = execute_query(db_path, generated_query)
                st.write("Query Results:")
                st.table(results)
            except Exception as e:
                st.error(f"Error executing query: {str(e)}")
        else:
            st.warning("Please enter a question.")
else:
    st.info("Please upload a .sql file to begin.")