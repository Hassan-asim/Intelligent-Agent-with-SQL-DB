"""
Gemini SQL Agent with GUI

This script demonstrates a secure SQL agent that uses the Gemini API to interact
with a database in natural language. It also includes a simple GUI to display
the results and a graphical representation of the data.

Security Features Implemented:
✅ Input validation using regex patterns
✅ Whitelist approach - only SELECT statements allowed
✅ Automatic LIMIT injection to prevent large result sets
✅ SQL injection protection through pattern matching
✅ Multiple statement prevention
✅ Error handling for SQL execution failures
✅ Read-only operations only - no data modification possible
"""

import os
import re
import sqlite3
from setup_database import setup_database

DB_FILE_PATH = "C:/Users/user/OneDrive/Desktop/SQL agent by Hassan/task by hassan/week_10/SQLAgent/sql_agent_class.db"

# Check if the database file exists at the specified absolute path.
if not os.path.exists(DB_FILE_PATH):
    setup_database() # If the database does not exist, call the setup_database function to create and populate it.
import sqlalchemy
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_community.utilities import SQLDatabase
from langchain.schema import SystemMessage
from typing import Type
from dotenv import load_dotenv
import tkinter as tk
from tkinter import scrolledtext, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Database Configuration
DB_URL = f"sqlite:///{DB_FILE_PATH}"

# Create Database Engine
engine = sqlalchemy.create_engine(DB_URL)

class QueryInput(BaseModel):
    """
    Pydantic model for safe SQL query input validation.
    """
    sql: str = Field(description="A single read-only SELECT statement, bounded with LIMIT when returning many rows.")

class SafeSQLTool(BaseTool):
    """
    SECURE SQL Tool - Only Allows Read-Only SELECT Operations
    """
    name: str = "execute_sql"
    description: str = "Execute exactly one SELECT statement; DML/DDL is forbidden."
    args_schema: Type[BaseModel] = QueryInput

    def _run(self, sql: str) -> str | dict:
        """
        Execute SQL with comprehensive security validation.
        """
        s = sql.strip().rstrip(";")

        if re.search(r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|REPLACE)\b", s, re.I):
            return "ERROR: write operations are not allowed."

        if ";" in s:
            return "ERROR: multiple statements are not allowed."

        if not re.match(r"(?is)^\s*select\b", s):
            return "ERROR: only SELECT statements are allowed."

        if not re.search(r"\blimit\s+\d+\b", s, re.I) and not re.search(r"\bcount\(|group\s+by\b|\bsum\(|\bavg\(|\bmax\(|\bmin\(", s, re.I):
            s += " LIMIT 200"

        try:
            with engine.connect() as conn:
                result = conn.exec_driver_sql(s)
                rows = result.fetchall()
                cols = list(result.keys()) if result.keys() else []
                return {"columns": cols, "rows": [list(r) for r in rows]}
        except Exception as e:
            return f"ERROR: {e}"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError

def get_schema_context():
    """
    Get the database schema context.
    """
    db = SQLDatabase.from_uri(DB_URL, include_tables=["instructors", "courses", "students", "classes"])
    return db.get_table_info()

def execute_query(query: str):
    """
    Execute a natural language query using the Gemini API and the SafeSQLTool.
    """
    print(f"User query: {query}")
    # Configure the Gemini API
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    model = genai.GenerativeModel('models/gemini-1.5-flash')

    # Get the database schema
    schema = get_schema_context()

    # Create the prompt
    prompt = f"""You are a careful analytics engineer for SQLite. Use only these tables.

{schema}

Given the following user query, generate a SQL query to answer it.

User Query: {query}

SQL Query:
"""

    # Generate the SQL query
    response = model.generate_content(prompt)
    sql_query = response.text.strip()
    print(f"Generated SQL query: {sql_query}")

    # Execute the SQL query using the SafeSQLTool
    safe_tool = SafeSQLTool()
    result = safe_tool._run(sql_query)
    print(f"Query result: {result}")

    return result, sql_query

def create_chart(data, chart_type='bar'):
    """
    Create a chart from the query result.
    """
    fig, ax = plt.subplots()

    if not data or not data['rows']:
        ax.text(0.5, 0.5, "No data to display", horizontalalignment='center', verticalalignment='center')
        return fig

    df = pd.DataFrame(data['rows'], columns=data['columns'])

    if chart_type == 'bar':
        df.plot(kind='bar', ax=ax)
    elif chart_type == 'line':
        df.plot(kind='line', ax=ax)
    elif chart_type == 'pie':
        df.plot(kind='pie', y=df.columns[1], labels=df.columns[0], ax=ax)

    return fig

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini SQL Agent")
        self.root.configure(bg="#f0f0f0")

        style = ttk.Style()
        style.configure("TLabel", background="#f0f0f0", foreground="#333", font=("Arial", 10))
        style.configure("TButton", background="#4CAF50", foreground="white", font=("Arial", 10, "bold"))
        style.configure("TFrame", background="#f0f0f0")

        self.query_label = ttk.Label(root, text="Enter your query:")
        self.query_label.pack(pady=5)

        self.query_input = ttk.Entry(root, width=100, font=("Arial", 10))
        self.query_input.pack(pady=5)

        self.submit_button = ttk.Button(root, text="Submit", command=self.submit_query, style="TButton")
        self.submit_button.pack(pady=5)

        self.result_label = ttk.Label(root, text="Result:")
        self.result_label.pack(pady=5)

        self.result_text = scrolledtext.ScrolledText(root, width=100, height=10, font=("Arial", 10))
        self.result_text.pack(pady=5)

        self.chart_label = ttk.Label(root, text="Chart:")
        self.chart_label.pack(pady=5)

        self.chart_frame = ttk.Frame(root)
        self.chart_frame.pack(pady=5)

    def submit_query(self):
        query = self.query_input.get()
        if not query:
            return

        result, sql_query = execute_query(query)

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"SQL Query: {sql_query}\n\n")
        self.result_text.insert(tk.END, str(result))

        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig = create_chart(result)
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
