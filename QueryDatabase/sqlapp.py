import os
import streamlit as st
import google.generativeai as genai
from sqlalchemy import create_engine, text
import config
import sqlite3
import tempfile

google_api_key = config.GOOGLE_API_KEY
chat_model = config.CHAT_MODEL

genai.configure(api_key=google_api_key)
model = genai.GenerativeModel(model_name=chat_model)

class TextToSQL:
    def __init__(self):
        self.db_path = None

    def create_database_from_sql(self, sql_content):
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.db', delete=False) as temp_file:
            temp_file.write("") # Ensure the file exists
            self.db_path = temp_file.name

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(sql_content)
            return self.db_path
        except Exception as e:
            raise Exception(f"Error creating SQLite database: {e}")

    def get_schema(self):
        try:
            engine = create_engine(f"sqlite:///{self.db_path}", echo=True)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT sql FROM sqlite_master WHERE type='table';"))
                schema = result.fetchall()
            return schema
        except Exception as e:
            raise Exception(f"Error getting schema: {e}")

    def get_model_response(self, question, schema):
        prompt = f"""
        You are an expert SQL developer. Given the input question {question} and the schema {schema},
        create a correct SQL query to run which will fetch the exact result as desired by the question.
        Important: You should only give output a SQL query only and nothing else. The query should be
        directly executable on the db so respond in the same manner. Do not apply any quote or extra.
        Do not apply ``` at the beginning or end.
        """
        response = model.generate_content([prompt])
        return response.text.strip()

    def query_database(self, sql_query):
        try:
            engine = create_engine(f"sqlite:///{self.db_path}", echo=True)
            with engine.connect() as conn:
                result = conn.execute(text(sql_query))
                return result.fetchall()
        except Exception as e:
            raise Exception(f"Error querying database: {e}")

class SQLApp:
    def __init__(self):
        self.text_to_sql = TextToSQL()

    def run(self):
        st.header("Query Database")
        uploaded_file = st.file_uploader("Upload a .sql file", type="sql")
        input_question = st.text_input("Enter your question about the database", key="input")
        
        st.text("Here are some sample questions:")
        st.text("What are the names of the tables in the database?")
        st.text("What are the names of the artists?")
        
        if st.button("Submit", type="primary"):
            if uploaded_file and input_question:
                try:
                    sql_content = uploaded_file.getvalue().decode("utf-8")
                    db_path = self.text_to_sql.create_database_from_sql(sql_content)
                    
                    if db_path:
                        st.success("Connected to SQLite database")
                        schema = self.text_to_sql.get_schema()
                        if schema:
                            sql_query = self.text_to_sql.get_model_response(input_question, schema)
                            st.text_area("Generated SQL Query", sql_query, height=200)
                            results = self.text_to_sql.query_database(sql_query)
                            if results:
                                st.write("Query Results:")
                                for row in results:
                                    st.write(row)
                            else:
                                st.warning("No results returned from the query.")
                        else:
                            st.error("Failed to retrieve schema from the database.")
                    else:
                        st.error("Failed to create the database from the SQL file.")
                except Exception as e:
                    st.error(str(e))
            else:
                st.warning("Please upload an SQL file and enter a question.")

# if __name__ == "__main__":
#     app = SQLApp()
#     app.run()