"""
Unified Chat School Management Agent

This script provides a single chat interface that:
- Takes natural language input
- Automatically generates SQL queries
- Creates appropriate charts based on data
- Maintains conversation context
- Shows everything in one unified chat interface
"""

import os
import re
import sqlite3
import pathlib
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import google.generativeai as genai
from dotenv import load_dotenv
import sqlalchemy
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_community.utilities import SQLDatabase
from typing import Type
import threading
import time
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Database Configuration
script_dir = pathlib.Path(__file__).parent
DB_FILE_PATH = script_dir / "school_management.db"
DB_URL = f"sqlite:///{DB_FILE_PATH.as_posix()}"

# Create Database Engine
engine = sqlalchemy.create_engine(DB_URL)

class QueryInput(BaseModel):
    """Pydantic model for safe SQL query input validation."""
    sql: str = Field(description="A single read-only SELECT statement, bounded with LIMIT when returning many rows.")

class SecureSchoolSQLTool(BaseTool):
    """
    SECURE School Management SQL Tool - Only Allows Read-Only SELECT Operations
    """
    name: str = "execute_sql"
    description: str = "Execute exactly one SELECT statement for school data analysis; DML/DDL is forbidden."
    args_schema: Type[BaseModel] = QueryInput

    def _run(self, sql: str) -> str | dict:
        """Execute SQL with comprehensive security validation."""
        s = sql.strip().rstrip(";")

        # Security validations
        if re.search(r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|REPLACE|EXEC|EXECUTE)\b", s, re.I):
            return "ERROR: Write operations are not allowed. Only SELECT queries are permitted."

        if ";" in s:
            return "ERROR: Multiple statements are not allowed."

        if not re.match(r"(?is)^\s*select\b", s):
            return "ERROR: Only SELECT statements are allowed."

        # School-specific optimizations
        if not re.search(r"\blimit\s+\d+\b", s, re.I) and not re.search(r"\bcount\(|\bgroup\s+by\b|\bsum\(|\bavg\(|\bmax\(|\bmin\(", s, re.I):
            s += " LIMIT 100"  # Reasonable limit for school data

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
    """Get the school database schema context."""
    db = SQLDatabase.from_uri(DB_URL, include_tables=[
        "students", "teachers", "courses", "enrollments", "attendance", 
        "grades", "departments", "semesters"
    ])
    return db.get_table_info()

class ChatSchoolAgent:
    """Unified chat interface for school management."""
    
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.setup_styles()
        self.create_widgets()
        self.chat_history = []
        self.setup_gemini()
        
    def setup_ui(self):
        """Setup the main UI configuration."""
        self.root.title("🎓 School Management Chat Assistant")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f8fafc")
        self.root.minsize(1000, 700)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
        
    def setup_styles(self):
        """Setup modern styling."""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Define color scheme
        self.colors = {
            'primary': '#3b82f6',
            'secondary': '#64748b',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'info': '#06b6d4',
            'light': '#f8fafc',
            'dark': '#1e293b',
            'white': '#ffffff',
            'gray': '#e2e8f0'
        }
        
        # Configure styles
        self.style.configure('Title.TLabel', 
                           font=('Segoe UI', 20, 'bold'),
                           foreground=self.colors['dark'],
                           background=self.colors['light'])
        
        self.style.configure('Modern.TButton',
                           font=('Segoe UI', 10, 'bold'),
                           background=self.colors['primary'],
                           foreground=self.colors['white'],
                           borderwidth=0,
                           focuscolor='none',
                           padding=(15, 8))
        
        self.style.map('Modern.TButton',
                      background=[('active', '#2563eb'),
                                ('pressed', '#1d4ed8')])
        
        self.style.configure('Query.TEntry',
                           font=('Segoe UI', 11),
                           padding=(12, 10),
                           relief='solid',
                           borderwidth=1)
        
    def create_widgets(self):
        """Create all UI widgets."""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['light'], padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Chat area
        self.create_chat_area(main_frame)
        
        # Input area
        self.create_input_area(main_frame)
        
    def create_header(self, parent):
        """Create the header section."""
        header_frame = tk.Frame(parent, bg=self.colors['light'])
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title
        title_label = ttk.Label(header_frame, 
                               text="🎓 School Management Chat Assistant",
                               style='Title.TLabel')
        title_label.pack(side='left')
        
        # Status indicator
        self.status_frame = tk.Frame(header_frame, bg=self.colors['light'])
        self.status_frame.pack(side='right')
        
        self.status_indicator = tk.Label(self.status_frame,
                                       text="🟢 Ready",
                                       font=('Segoe UI', 10),
                                       fg=self.colors['success'],
                                       bg=self.colors['light'])
        self.status_indicator.pack()
        
    def create_chat_area(self, parent):
        """Create the chat display area."""
        # Chat container with scrollbar
        chat_container = tk.Frame(parent, bg=self.colors['light'])
        chat_container.pack(fill='both', expand=True, pady=(0, 20))
        
        # Chat text area
        self.chat_text = scrolledtext.ScrolledText(
            chat_container,
            height=25,
            font=('Segoe UI', 10),
            bg=self.colors['white'],
            fg=self.colors['dark'],
            relief='solid',
            borderwidth=1,
            wrap='word',
            state='disabled'
        )
        self.chat_text.pack(fill='both', expand=True, padx=(0, 10))
        
        # Chart area (right side)
        self.chart_frame = tk.Frame(chat_container, bg=self.colors['white'], relief='solid', borderwidth=1)
        self.chart_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Welcome message
        self.add_message("🤖 Assistant", "Hello! I'm your School Management Assistant. Ask me anything about students, courses, attendance, grades, or teachers. I can also create charts and visualizations for you!", "assistant")
        
    def create_input_area(self, parent):
        """Create the input area."""
        input_frame = tk.Frame(parent, bg=self.colors['light'])
        input_frame.pack(fill='x')
        
        # Input entry
        self.query_var = tk.StringVar()
        self.query_entry = ttk.Entry(input_frame, 
                                   textvariable=self.query_var,
                                   style='Query.TEntry',
                                   font=('Segoe UI', 11))
        self.query_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.query_entry.bind('<Return>', lambda e: self.send_message())
        
        # Send button
        self.send_btn = ttk.Button(input_frame,
                                  text="Send",
                                  style='Modern.TButton',
                                  command=self.send_message)
        self.send_btn.pack(side='right')
        
        # Clear button
        self.clear_btn = ttk.Button(input_frame,
                                   text="Clear",
                                   style='Modern.TButton',
                                   command=self.clear_chat)
        self.clear_btn.pack(side='right', padx=(0, 10))
        
    def setup_gemini(self):
        """Setup Gemini API."""
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel('models/gemini-1.5-flash')
            self.schema = get_schema_context()
        except Exception as e:
            self.add_message("❌ Error", f"Failed to setup Gemini API: {e}", "error")
            
    def add_message(self, sender, message, msg_type="user"):
        """Add a message to the chat."""
        self.chat_text.config(state='normal')
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M")
        
        # Format message based on type
        if msg_type == "assistant":
            color = self.colors['primary']
            prefix = "🤖"
        elif msg_type == "error":
            color = self.colors['danger']
            prefix = "❌"
        elif msg_type == "success":
            color = self.colors['success']
            prefix = "✅"
        else:
            color = self.colors['dark']
            prefix = "👤"
        
        # Insert message
        self.chat_text.insert(tk.END, f"[{timestamp}] {prefix} {sender}:\n", "header")
        self.chat_text.insert(tk.END, f"{message}\n\n", "message")
        
        # Configure tags
        self.chat_text.tag_configure("header", foreground=color, font=('Segoe UI', 9, 'bold'))
        self.chat_text.tag_configure("message", foreground=self.colors['dark'], font=('Segoe UI', 10))
        
        # Scroll to bottom
        self.chat_text.see(tk.END)
        self.chat_text.config(state='disabled')
        
    def send_message(self):
        """Send a message and get response."""
        query = self.query_var.get().strip()
        if not query:
            return
            
        # Add user message
        self.add_message("You", query, "user")
        self.chat_history.append({"role": "user", "content": query})
        
        # Clear input
        self.query_var.set("")
        
        # Disable send button
        self.send_btn.config(text="⏳ Processing...", state='disabled')
        self.status_indicator.config(text="🟡 Processing", fg=self.colors['warning'])
        
        # Process in thread
        def process_query():
            try:
                response = self.process_natural_language_query(query)
                self.root.after(0, self.handle_response, response)
            except Exception as e:
                self.root.after(0, self.handle_error, str(e))
            finally:
                self.root.after(0, self.reset_send_button)
                
        threading.Thread(target=process_query, daemon=True).start()
        
    def process_natural_language_query(self, query):
        """Process natural language query and return response."""
        try:
            # Create enhanced prompt
            prompt = f"""You are an expert school management analytics assistant. Use only these tables:

{self.schema}

School Management Context:
- Students: Personal info, GPA, enrollment status
- Teachers: Department assignments, specializations  
- Courses: Course codes, credits, enrollment limits
- Enrollments: Student-course relationships
- Attendance: Daily attendance tracking
- Grades: Assignment scores and letter grades
- Departments: Academic departments
- Semesters: Academic terms

Given the following user query, generate a SQL query to answer it. Focus on:
- Student performance analytics
- Attendance patterns
- Course enrollment statistics
- Grade distributions
- Department performance
- Teacher workload analysis

IMPORTANT: Return ONLY the SQL query, no explanations or markdown formatting.

User Query: {query}

SQL Query:"""

            # Generate SQL query
            response = self.model.generate_content(prompt)
            sql_query = response.text.strip()
            
            # Clean up SQL query (remove markdown formatting)
            sql_query = re.sub(r'```sql\s*', '', sql_query)
            sql_query = re.sub(r'```\s*', '', sql_query)
            sql_query = sql_query.strip()
            
            # Execute SQL query
            safe_tool = SecureSchoolSQLTool()
            result = safe_tool._run(sql_query)
            
            return {
                "sql_query": sql_query,
                "result": result,
                "original_query": query
            }
            
        except Exception as e:
            return {"error": str(e), "original_query": query}
            
    def handle_response(self, response):
        """Handle the response from query processing."""
        if "error" in response:
            self.add_message("❌ Error", response["error"], "error")
            return
            
        sql_query = response["sql_query"]
        result = response["result"]
        original_query = response["original_query"]
        
        # Add SQL query to chat
        self.add_message("🔍 SQL Query", f"```sql\n{sql_query}\n```", "assistant")
        
        # Handle result
        if isinstance(result, dict) and 'columns' in result:
            # Format table data
            self.display_table_data(result)
            
            # Check if we should create a chart
            if self.should_create_chart(original_query, result):
                self.create_appropriate_chart(result, original_query)
        else:
            # Display error or simple result
            self.add_message("📊 Result", str(result), "assistant")
            
        # Update status
        self.status_indicator.config(text="🟢 Ready", fg=self.colors['success'])
        
    def display_table_data(self, data):
        """Display table data in chat."""
        if not data['rows']:
            self.add_message("📊 Result", "No data found.", "assistant")
            return
            
        # Create table
        table_text = "📊 Query Results:\n\n"
        
        # Headers
        headers = " | ".join(data['columns'])
        table_text += headers + "\n"
        table_text += "-" * len(headers) + "\n"
        
        # Data rows (limit to 20 for display)
        for row in data['rows'][:20]:
            row_str = " | ".join(str(cell) for cell in row)
            table_text += row_str + "\n"
            
        if len(data['rows']) > 20:
            table_text += f"\n... and {len(data['rows']) - 20} more rows"
            
        self.add_message("📊 Result", table_text, "assistant")
        
    def should_create_chart(self, query, data):
        """Determine if we should create a chart based on query and data."""
        query_lower = query.lower()
        chart_keywords = ['chart', 'graph', 'plot', 'visualize', 'show', 'display', 'attendance', 'grades', 'distribution', 'trend', 'performance']
        
        # Check if query mentions visualization
        if any(keyword in query_lower for keyword in chart_keywords):
            return True
            
        # Check if data is suitable for charting
        if len(data['rows']) > 1 and len(data['columns']) >= 2:
            # Check if second column is numeric
            try:
                float(data['rows'][0][1])
                return True
            except (ValueError, IndexError):
                pass
                
        return False
        
    def create_appropriate_chart(self, data, query):
        """Create an appropriate chart based on data and query."""
        try:
            # Clear previous chart
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
                
            if not data['rows'] or len(data['rows']) == 0:
                return
                
            # Convert to DataFrame
            df = pd.DataFrame(data['rows'], columns=data['columns'])
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 5))
            
            # Determine chart type based on query and data
            query_lower = query.lower()
            
            if 'attendance' in query_lower:
                self.create_attendance_chart(df, ax)
            elif 'grade' in query_lower or 'performance' in query_lower:
                self.create_grade_chart(df, ax)
            elif 'enrollment' in query_lower or 'course' in query_lower:
                self.create_enrollment_chart(df, ax)
            elif 'department' in query_lower:
                self.create_department_chart(df, ax)
            else:
                # Default chart based on data
                self.create_default_chart(df, ax)
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
            self.add_message("📈 Chart", "Chart created and displayed!", "success")
            
        except Exception as e:
            self.add_message("❌ Chart Error", f"Could not create chart: {e}", "error")
            
    def create_attendance_chart(self, df, ax):
        """Create attendance chart."""
        if len(df.columns) >= 2:
            # Bar chart for attendance data
            df.plot(kind='bar', x=df.columns[0], y=df.columns[1], ax=ax, color='#3b82f6')
            ax.set_title('Attendance Overview', fontweight='bold')
            ax.tick_params(axis='x', rotation=45)
            
    def create_grade_chart(self, df, ax):
        """Create grade distribution chart."""
        if len(df.columns) >= 2:
            # Bar chart for grades
            bars = ax.bar(df[df.columns[0]], df[df.columns[1]], 
                        color=['#10b981' if 'A' in str(g) else 
                              '#f59e0b' if 'B' in str(g) else
                              '#ef4444' for g in df[df.columns[0]]])
            ax.set_title('Grade Distribution', fontweight='bold')
            ax.tick_params(axis='x', rotation=45)
            
    def create_enrollment_chart(self, df, ax):
        """Create enrollment chart."""
        if len(df.columns) >= 2:
            # Pie chart for enrollment
            ax.pie(df[df.columns[1]], labels=df[df.columns[0]], autopct='%1.1f%%')
            ax.set_title('Enrollment Distribution', fontweight='bold')
            
    def create_department_chart(self, df, ax):
        """Create department chart."""
        if len(df.columns) >= 2:
            # Horizontal bar chart
            df.plot(kind='barh', x=df.columns[0], y=df.columns[1], ax=ax, color='#06b6d4')
            ax.set_title('Department Statistics', fontweight='bold')
            
    def create_default_chart(self, df, ax):
        """Create default chart based on data."""
        if len(df.columns) >= 2:
            try:
                # Try bar chart
                df.plot(kind='bar', x=df.columns[0], y=df.columns[1], ax=ax)
                ax.set_title('Data Visualization', fontweight='bold')
                ax.tick_params(axis='x', rotation=45)
            except:
                # Fallback to line chart
                df.plot(kind='line', x=df.columns[0], y=df.columns[1], ax=ax)
                ax.set_title('Data Visualization', fontweight='bold')
                
    def handle_error(self, error_msg):
        """Handle errors."""
        self.add_message("❌ Error", f"An error occurred: {error_msg}", "error")
        self.status_indicator.config(text="🔴 Error", fg=self.colors['danger'])
        
    def reset_send_button(self):
        """Reset the send button."""
        self.send_btn.config(text="Send", state='normal')
        
    def clear_chat(self):
        """Clear the chat history."""
        self.chat_text.config(state='normal')
        self.chat_text.delete(1.0, tk.END)
        self.chat_text.config(state='disabled')
        
        # Clear chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        # Reset chat history
        self.chat_history = []
        
        # Add welcome message
        self.add_message("🤖 Assistant", "Chat cleared! How can I help you with school management data?", "assistant")

def main():
    """Main function to run the chat school management system."""
    # Check if database exists
    if not DB_FILE_PATH.exists():
        print("Database not found. Creating school management database...")
        from setup_school_database import setup_school_database
        setup_school_database()
    
    # Create and run the application
    root = tk.Tk()
    app = ChatSchoolAgent(root)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
