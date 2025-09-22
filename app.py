
import os
import re
import sqlite3
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import json
import hashlib
import sqlalchemy
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_community.utilities import SQLDatabase
from typing import Type
import threading
import time
from datetime import datetime
import json
import streamlit as st

# Load environment variables for API keys
load_dotenv()

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
# Fixed directory structure - database is in the project root
SCRIPT_DIR = pathlib.Path(__file__).parent
DB_FILE_PATH = SCRIPT_DIR / "school_management.db"
DB_URL = f"sqlite:///{DB_FILE_PATH.as_posix()}"

# Create database engine for SQL operations
engine = sqlalchemy.create_engine(DB_URL)

# ============================================================================
# PYDANTIC MODELS FOR DATA VALIDATION
# ============================================================================
class QueryInput(BaseModel):
    """
    Pydantic model for safe SQL query input validation.
    """
    sql: str = Field(description="A single read-only SELECT statement, bounded with LIMIT when returning many rows.")

# ============================================================================
# SECURITY MANAGEMENT
# ============================================================================
class SecurityManager:
    """Handles authentication and security for database write operations."""
    
    def __init__(self):
        # Load credentials from environment variables
        self.admin_email = "hassanasim337@gmail.com"
        admin_password = "12345678"
        self.admin_password_hash = self._hash_password(admin_password)
        if 'is_authenticated' not in st.session_state:
            st.session_state.is_authenticated = False
    
    def _hash_password(self, password):
        """Hash password using SHA-256 for security."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, email, password):
        """Verify credentials."""
        if email == self.admin_email and self._hash_password(password) == self.admin_password_hash:
            st.session_state.is_authenticated = True
            return True
        else:
            st.session_state.is_authenticated = False
            return False
    
    def logout(self):
        """Logout and reset authentication status."""
        st.session_state.is_authenticated = False

# ============================================================================
# SECURE SQL TOOL CLASS
# ============================================================================
class SecureSchoolSQLTool(BaseTool):
    """
    SECURE School Management SQL Tool - Supports Read Operations and Write Operations with Authentication
    """
    name: str = "execute_sql"
    description: str = "Execute SQL statements for school data analysis. Write operations require authentication."
    args_schema: Type[BaseModel] = QueryInput
    
    _security_manager = None
    
    @classmethod
    def set_security_manager(cls, security_manager):
        """Set the security manager for the class."""
        cls._security_manager = security_manager

    def _run(self, sql: str) -> str | dict:
        """
        Execute SQL with comprehensive security validation.
        """
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        results = []

        for s in statements:
            write_operations = re.search(r"\b(INSERT|UPDATE|DELETE|CREATE|ALTER|REPLACE)\b", s, re.I)
            dangerous_operations = re.search(r"\b(DROP|TRUNCATE|EXEC|EXECUTE)\b", s, re.I)
            
            if dangerous_operations:
                return "ERROR: Dangerous operations (DROP, TRUNCATE, EXEC) are not allowed for security reasons."
            
            if write_operations:
                if not self._security_manager or not st.session_state.is_authenticated:
                    return "ERROR: Write operations require authentication. Please authenticate first."

            if not re.match(r"(?is)^\s*(select|update|insert|delete)\b", s):
                return "ERROR: Only SELECT, UPDATE, INSERT, DELETE statements are allowed."

            if (re.match(r"(?is)^\s*select\b", s) and 
                not re.search(r"\blimit\s+\d+\b", s, re.I) and 
                not re.search(r"\bcount\(|\bgroup\s+by\b|\bsum\(|\bavg\(|\bmax\(|\bmin\(", s, re.I)):
                s += " LIMIT 100"

            try:
                with engine.connect() as conn:
                    result = conn.exec_driver_sql(s)
                    
                    if re.match(r"(?is)^\s*select\b", s):
                        rows = result.fetchall()
                        cols = list(result.keys()) if result.keys() else []
                        results.append({"columns": cols, "rows": [list(r) for r in rows]})
                    else:
                        conn.commit()
                        operation = s.split()[0].upper()
                        results.append(f"{operation} operation completed successfully")
                        
            except Exception as e:
                return f"ERROR: {e}"
        
        return results[0] if len(results) == 1 else results

    def _arun(self, *args, **kwargs):
        raise NotImplementedError

# ============================================================================
# DATABASE SCHEMA UTILITIES
# ============================================================================
def get_schema_context():
    """
    Get the school database schema context for AI query generation.
    """
    db = SQLDatabase.from_uri(DB_URL, include_tables=[
        "students", "teachers", "courses", "enrollments", "attendance", 
        "grades", "departments", "semesters"
    ])
    return db.get_table_info()

# ============================================================================
# CONVERSATIONAL HANDLER
# ============================================================================
def handle_conversational_query(query):
    """Handle conversational questions that don't require SQL queries."""
    query_lower = query.lower().strip()
    
    greetings = ["hello", "hi", "hey", "how are you", "what's up"]
    if query_lower in greetings:
        return "Hello! I am your school management assistant. How can I help you today?"

    return None

def handle_chart_of_that_request(query):
    """Handle requests to create a chart of the previous data."""
    query_lower = query.lower().strip()
    chart_of_that_phrases = ["make a chart of that", "chart of that", "plot that", "graph that"]

    if any(phrase in query_lower for phrase in chart_of_that_phrases):
        if st.session_state.get("last_data_result"):
            return st.session_state.last_data_result
    
    return None

# ============================================================================
# STREAMLIT UI
# ============================================================================

def main():
    st.set_page_config(page_title="School Management Chat Assistant", page_icon="🎓", layout="wide")

    st.title("🎓 School Management Chat Assistant")

    # Initialize security manager
    security_manager = SecurityManager()

    # Sidebar
    with st.sidebar:
        st.header("🔐 Database Access")
        if st.session_state.get("is_authenticated"):
            st.success(f"Authenticated as {security_manager.admin_email}")
            if st.button("Logout"):
                security_manager.logout()
                st.rerun()
        else:
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if security_manager.authenticate(email, password):
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        st.header("Actions")
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.last_data_result = None
            st.rerun()

        if st.session_state.get("messages"):
            chat_history = ""
            for message in st.session_state.messages:
                chat_history += f'{message["role"]}: {message["content"]}\n'
            st.download_button(
                label="Download Chat",
                data=chat_history,
                file_name="chat_history.txt",
                mime="text/plain",
            )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask me anything about students, courses, attendance, grades, or teachers."):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Process the query
        with st.spinner("Processing..."):
            conversational_response = handle_conversational_query(prompt)
            if conversational_response:
                st.chat_message("assistant").markdown(conversational_response)
                st.session_state.messages.append({"role": "assistant", "content": conversational_response})
            else:
                chart_data = handle_chart_of_that_request(prompt)
                if chart_data:
                    with st.chat_message("assistant"):
                        st.markdown("Here is the chart you requested:")
                        fig = create_chart(pd.DataFrame(chart_data['rows'], columns=chart_data['columns']), prompt)
                        st.pyplot(fig)
                        st.session_state.messages.append({"role": "assistant", "content": "Generated a chart from the previous data."})
                else:
                    response = process_natural_language_query(prompt, security_manager)
                    if response:
                        handle_response(response)

def process_natural_language_query(query, security_manager, is_write_operation=False):
    """
    Process natural language query using Gemini AI.
    """
    try:
        schema = get_schema_context()
        
        conversation_history = ""
        for message in st.session_state.get("messages", [])[-5:]:
            conversation_history += f'{message["role"]}: {message["content"]}\n'

        prompt = f'''You are an expert school management analytics assistant. Use only these tables:

{schema}

Conversation History:
{conversation_history}

Given the following user query, generate an appropriate SQL query.
Return ONLY the SQL query, no explanations or markdown formatting.

User Query: {query}

SQL Query:'''

        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")

        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(prompt)
        sql_query = response.text.strip().replace("`", "").replace("sql", "")
        
        safe_tool = SecureSchoolSQLTool()
        SecureSchoolSQLTool.set_security_manager(security_manager)
        result = safe_tool._run(sql_query)
        
        return {
            "sql_query": sql_query,
            "result": result,
            "original_query": query
        }
        
    except Exception as e:
        return {"error": str(e), "original_query": query}

def handle_response(response):
    """
    Handle the response from query processing.
    """
    if "error" in response:
        st.error(response["error"])
        st.session_state.messages.append({"role": "assistant", "content": response["error"]})
        return
        
    sql_query = response["sql_query"]
    result = response["result"]
    original_query = response["original_query"]
    
    with st.chat_message("assistant"):
        response_content = f"""**SQL Query:**
```sql
{sql_query}
```"""
        st.markdown(response_content)
        
        if isinstance(result, list):
            for res in result:
                if isinstance(res, dict) and 'columns' in res:
                    st.session_state.last_data_result = res
                    df = pd.DataFrame(res['rows'], columns=res['columns'])
                    st.dataframe(df)
                    response_content += f"\n\n{df.to_markdown()}"
                else:
                    st.success(res)
                    response_content += f"\n\n{res}"
        elif isinstance(result, dict) and 'columns' in result:
            st.session_state.last_data_result = result
            df = pd.DataFrame(result['rows'], columns=result['columns'])
            st.dataframe(df)
            response_content += f"\n\n{df.to_markdown()}"
            
            if should_create_chart(original_query, result):
                fig = create_chart(df, original_query)
                st.pyplot(fig)

        elif isinstance(result, str):
            st.success(result)
            response_content += f"\n\n{result}"
        else:
            st.info("I couldn't find any data matching your request.")
            response_content += "\n\nI couldn't find any data matching your request."

    st.session_state.messages.append({"role": "assistant", "content": response_content})


def should_create_chart(query, data):
    """
    Determine if a chart should be created based on query and data.
    """
    query_lower = query.lower()
    chart_keywords = ['chart', 'graph', 'plot', 'visualize', 'pie', 'bar', 'line']
    
    if any(keyword in query_lower for keyword in chart_keywords):
        return True
        
    if len(data['rows']) > 1 and len(data['columns']) >= 2:
        try:
            float(data['rows'][0][1])
            return True
        except (ValueError, IndexError):
            pass
            
    return False

def create_chart(df, query):
    """
    Create a chart based on the query and data.
    """
    fig, ax = plt.subplots()
    query_lower = query.lower()

    if 'pie' in query_lower:
        df.set_index(df.columns[0])[df.columns[1]].plot(kind='pie', ax=ax, autopct='%1.1f%%')
    elif 'bar' in query_lower:
        df.plot(kind='bar', x=df.columns[0], y=df.columns[1], ax=ax)
    elif 'line' in query_lower:
        df.plot(kind='line', x=df.columns[0], y=df.columns[1], ax=ax)
    else:
        # Auto-detect chart type
        if pd.api.types.is_numeric_dtype(df[df.columns[1]]):
            df.plot(kind='bar', x=df.columns[0], y=df.columns[1], ax=ax)
        else:
            df.set_index(df.columns[0])[df.columns[1]].plot(kind='pie', ax=ax, autopct='%1.1f%%')

    plt.tight_layout()
    return fig

if __name__ == "__main__":
    main()
