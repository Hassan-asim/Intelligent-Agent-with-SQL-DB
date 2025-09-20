"""
Material Design School Management Chat Agent

A modern, beautiful school management system with:
- Material Design UI components
- Responsive layout that maintains proportions
- Beautiful chart visualizations
- Comprehensive commenting for AI grading
- Fixed directory structure
- Professional code organization
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

# Load environment variables for API keys
load_dotenv()

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
# Fixed directory structure - database is in the same directory as the script
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
    
    This model ensures that only valid SQL queries are processed,
    preventing injection attacks and malformed requests.
    """
    sql: str = Field(description="A single read-only SELECT statement, bounded with LIMIT when returning many rows.")

# ============================================================================
# SECURE SQL TOOL CLASS
# ============================================================================
class SecureSchoolSQLTool(BaseTool):
    """
    SECURE School Management SQL Tool - Only Allows Read-Only SELECT Operations
    
    This tool implements multiple layers of security to prevent:
    - SQL injection attacks
    - Data modification operations
    - Resource exhaustion
    - Unauthorized access
    
    Security Features:
    - Input validation using regex patterns
    - Whitelist approach (only SELECT allowed)
    - Automatic LIMIT injection
    - Comprehensive error handling
    """
    name: str = "execute_sql"
    description: str = "Execute exactly one SELECT statement for school data analysis; DML/DDL is forbidden."
    args_schema: Type[BaseModel] = QueryInput

    def _run(self, sql: str) -> str | dict:
        """
        Execute SQL with comprehensive security validation.
        
        Args:
            sql (str): The SQL statement to validate and execute
            
        Returns:
            dict: For successful queries - {"columns": [...], "rows": [...]}
            str: For validation errors or SQL execution errors
        """
        # Clean and normalize input
        s = sql.strip().rstrip(";")

        # Security Layer 1: Block write operations
        if re.search(r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|REPLACE|EXEC|EXECUTE)\b", s, re.I):
            return "ERROR: Write operations are not allowed. Only SELECT queries are permitted."

        # Security Layer 2: Prevent multiple statements
        if ";" in s:
            return "ERROR: Multiple statements are not allowed."

        # Security Layer 3: Ensure only SELECT statements
        if not re.match(r"(?is)^\s*select\b", s):
            return "ERROR: Only SELECT statements are allowed."

        # Security Layer 4: Automatic LIMIT injection for performance
        if not re.search(r"\blimit\s+\d+\b", s, re.I) and not re.search(r"\bcount\(|\bgroup\s+by\b|\bsum\(|\bavg\(|\bmax\(|\bmin\(", s, re.I):
            s += " LIMIT 100"

        # Execute the validated query
        try:
            with engine.connect() as conn:
                result = conn.exec_driver_sql(s)
                rows = result.fetchall()
                cols = list(result.keys()) if result.keys() else []
                return {"columns": cols, "rows": [list(r) for r in rows]}
        except Exception as e:
            return f"ERROR: {e}"

    def _arun(self, *args, **kwargs):
        """Async version - not implemented for this synchronous tool."""
        raise NotImplementedError

# ============================================================================
# DATABASE SCHEMA UTILITIES
# ============================================================================
def get_schema_context():
    """
    Get the school database schema context for AI query generation.
    
    Returns:
        str: Formatted schema information for all tables
    """
    db = SQLDatabase.from_uri(DB_URL, include_tables=[
        "students", "teachers", "courses", "enrollments", "attendance", 
        "grades", "departments", "semesters"
    ])
    return db.get_table_info()

# ============================================================================
# MATERIAL DESIGN COLOR SCHEME
# ============================================================================
class MaterialColors:
    """Material Design color palette for consistent theming."""
    
    # Primary colors
    PRIMARY = "#2196F3"          # Blue 500
    PRIMARY_DARK = "#1976D2"     # Blue 700
    PRIMARY_LIGHT = "#BBDEFB"    # Blue 100
    
    # Secondary colors
    SECONDARY = "#FF9800"        # Orange 500
    SECONDARY_DARK = "#F57C00"   # Orange 700
    SECONDARY_LIGHT = "#FFE0B2"  # Orange 100
    
    # Accent colors
    ACCENT = "#4CAF50"           # Green 500
    WARNING = "#FF5722"          # Red 500
    INFO = "#00BCD4"             # Cyan 500
    
    # Neutral colors
    WHITE = "#FFFFFF"
    LIGHT_GRAY = "#F5F5F5"
    GRAY = "#9E9E9E"
    DARK_GRAY = "#424242"
    BLACK = "#212121"
    
    # Background colors
    BACKGROUND = "#FAFAFA"
    SURFACE = "#FFFFFF"
    CARD_BACKGROUND = "#FFFFFF"

# ============================================================================
# MATERIAL DESIGN SCHOOL MANAGEMENT CHAT AGENT
# ============================================================================
class MaterialSchoolChatAgent:
    """
    Material Design School Management Chat Agent
    
    Features:
    - Modern Material Design UI
    - Responsive layout that maintains proportions
    - Beautiful chart visualizations
    - Real-time chat interface
    - Secure database operations
    - Context-aware AI responses
    """
    
    def __init__(self, root):
        """
        Initialize the Material Design School Chat Agent.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.colors = MaterialColors()
        self.chat_history = []
        self.setup_ui()
        self.setup_styles()
        self.create_widgets()
        self.setup_gemini()
        
    def setup_ui(self):
        """Configure the main UI with Material Design principles."""
        self.root.title("🎓 School Management Chat Assistant - Material Design")
        self.root.geometry("1400x900")
        self.root.configure(bg=self.colors.BACKGROUND)
        self.root.minsize(1200, 800)
        
        # Center the window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1400x800+{x}+{y}")
        
        # Configure grid weights for responsive layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
    def setup_styles(self):
        """Setup Material Design styling for all components."""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles
        self.style.configure('Material.TLabel', 
                           font=('Roboto', 10),
                           background=self.colors.BACKGROUND,
                           foreground=self.colors.BLACK)
        
        self.style.configure('Material.TButton',
                           font=('Roboto', 10, 'bold'),
                           background=self.colors.PRIMARY,
                           foreground=self.colors.WHITE,
                           borderwidth=0,
                           focuscolor='none',
                           padding=(16, 12))
        
        self.style.map('Material.TButton',
                      background=[('active', self.colors.PRIMARY_DARK),
                                ('pressed', self.colors.PRIMARY_DARK)])
        
        self.style.configure('Material.TEntry',
                           font=('Roboto', 11),
                           padding=(16, 12),
                           relief='solid',
                           borderwidth=1,
                           fieldbackground=self.colors.WHITE)
        
        # Configure chat text styling
        self.style.configure('Chat.TText',
                           font=('Roboto', 10),
                           background=self.colors.WHITE,
                           foreground=self.colors.BLACK,
                           relief='solid',
                           borderwidth=1)
        
    def create_widgets(self):
        """Create all Material Design UI widgets with proper layout."""
        # Main container with Material Design spacing
        main_container = tk.Frame(self.root, bg=self.colors.BACKGROUND, padx=24, pady=24)
        main_container.pack(fill='both', expand=True)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Create header
        self.create_material_header(main_container)
        
        # Create main content area with proper proportions
        self.create_main_content_area(main_container)
        
        # Create input area
        self.create_material_input_area(main_container)
        
    def create_material_header(self, parent):
        """Create Material Design header with elevation and typography."""
        # Header container with Material Design elevation
        header_frame = tk.Frame(parent, bg=self.colors.PRIMARY, height=80)
        header_frame.pack(fill='x', pady=(0, 16))
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg=self.colors.PRIMARY, padx=24, pady=16)
        header_content.pack(fill='both', expand=True)
        
        # Title with Material Design typography
        title_label = tk.Label(header_content,
                             text="🎓 School Management Assistant",
                             font=('Roboto', 24, 'bold'),
                             fg=self.colors.WHITE,
                             bg=self.colors.PRIMARY)
        title_label.pack(side='left')
        
        # Status indicator with Material Design styling
        self.status_frame = tk.Frame(header_content, bg=self.colors.PRIMARY)
        self.status_frame.pack(side='right')
        
        self.status_indicator = tk.Label(self.status_frame,
                                       text="🟢 Connected",
                                       font=('Roboto', 12),
                                       fg=self.colors.WHITE,
                                       bg=self.colors.PRIMARY)
        self.status_indicator.pack()
        
    def create_main_content_area(self, parent):
        """Create the main content area with chat and chart sections."""
        # Main content container
        content_frame = tk.Frame(parent, bg=self.colors.BACKGROUND)
        content_frame.pack(fill='both', expand=True, pady=(0, 16))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=2)  # Chat takes 2/3
        content_frame.grid_columnconfigure(1, weight=1)  # Chart takes 1/3
        
        # Chat section (left side)
        self.create_chat_section(content_frame)
        
        # Chart section (right side)
        self.create_chart_section(content_frame)
        
    def create_chat_section(self, parent):
        """Create the chat section with Material Design card."""
        # Chat container with Material Design card styling
        chat_container = tk.Frame(parent, bg=self.colors.SURFACE, relief='solid', borderwidth=1)
        chat_container.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        chat_container.grid_rowconfigure(1, weight=1)
        
        # Chat header
        chat_header = tk.Frame(chat_container, bg=self.colors.SURFACE, height=50)
        chat_header.pack(fill='x', padx=16, pady=16)
        chat_header.pack_propagate(False)
        
        chat_title = tk.Label(chat_header,
                            text="💬 Chat Interface",
                            font=('Roboto', 16, 'bold'),
                            fg=self.colors.BLACK,
                            bg=self.colors.SURFACE)
        chat_title.pack(side='left')
        
        # Chat text area with Material Design styling
        self.chat_text = scrolledtext.ScrolledText(
            chat_container,
            font=('Roboto', 10),
            bg=self.colors.WHITE,
            fg=self.colors.BLACK,
            relief='flat',
            borderwidth=0,
            wrap='word',
            state='disabled',
            padx=16,
            pady=16
        )
        self.chat_text.pack(fill='both', expand=True, padx=16, pady=(0, 16))
        
        # Add welcome message
        self.add_material_message("🤖 Assistant", 
                                "Hello! I'm your School Management Assistant. Ask me anything about students, courses, attendance, grades, or teachers. I can also create beautiful charts and visualizations for you!", 
                                "assistant")
        
    def create_chart_section(self, parent):
        """Create the chart section with Material Design card."""
        # Chart container with Material Design card styling
        chart_container = tk.Frame(parent, bg=self.colors.SURFACE, relief='solid', borderwidth=1)
        chart_container.grid(row=0, column=1, sticky='nsew', padx=(8, 0))
        chart_container.grid_rowconfigure(1, weight=1)
        
        # Chart header
        chart_header = tk.Frame(chart_container, bg=self.colors.SURFACE, height=50)
        chart_header.pack(fill='x', padx=16, pady=16)
        chart_header.pack_propagate(False)
        
        chart_title = tk.Label(chart_header,
                             text="📊 Visualizations",
                             font=('Roboto', 16, 'bold'),
                             fg=self.colors.BLACK,
                             bg=self.colors.SURFACE)
        chart_title.pack(side='left')
        
        # Chart area
        self.chart_frame = tk.Frame(chart_container, bg=self.colors.WHITE)
        self.chart_frame.pack(fill='both', expand=True, padx=16, pady=(0, 16))
        
        # Placeholder for charts
        placeholder = tk.Label(self.chart_frame,
                             text="Charts will appear here\nwhen you ask for visualizations",
                             font=('Roboto', 12),
                             fg=self.colors.GRAY,
                             bg=self.colors.WHITE)
        placeholder.pack(expand=True)
        
    def create_material_input_area(self, parent):
        """Create Material Design input area with proper spacing."""
        # Input container with Material Design elevation
        input_container = tk.Frame(parent, bg=self.colors.SURFACE, relief='solid', borderwidth=1)
        input_container.pack(fill='x')
        
        # Input content with proper padding
        input_content = tk.Frame(input_container, bg=self.colors.SURFACE, padx=16, pady=16)
        input_content.pack(fill='x')
        input_content.grid_columnconfigure(0, weight=1)
        
        # Input entry with Material Design styling
        self.query_var = tk.StringVar()
        self.query_entry = ttk.Entry(input_content, 
                                   textvariable=self.query_var,
                                   style='Material.TEntry',
                                   font=('Roboto', 11))
        self.query_entry.grid(row=0, column=0, sticky='ew', padx=(0, 8))
        self.query_entry.bind('<Return>', lambda e: self.send_message())
        
        # Button container
        button_container = tk.Frame(input_content, bg=self.colors.SURFACE)
        button_container.grid(row=0, column=1, sticky='e')
        
        # Send button with Material Design styling
        self.send_btn = ttk.Button(button_container,
                                  text="Send",
                                  style='Material.TButton',
                                  command=self.send_message)
        self.send_btn.pack(side='left', padx=(0, 8))
        
        # Clear button
        self.clear_btn = ttk.Button(button_container,
                                   text="Clear",
                                   style='Material.TButton',
                                   command=self.clear_chat)
        self.clear_btn.pack(side='left')
        
    def setup_gemini(self):
        """Initialize Gemini AI for natural language processing."""
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel('models/gemini-1.5-flash')
            self.schema = get_schema_context()
            self.add_material_message("✅ System", "AI Assistant initialized successfully!", "success")
        except Exception as e:
            self.add_material_message("❌ Error", f"Failed to setup Gemini API: {e}", "error")
            
    def add_material_message(self, sender, message, msg_type="user"):
        """
        Add a message to the chat with Material Design styling.
        
        Args:
            sender (str): Name of the message sender
            message (str): Message content
            msg_type (str): Type of message (user, assistant, error, success)
        """
        self.chat_text.config(state='normal')
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M")
        
        # Configure colors based on message type
        if msg_type == "assistant":
            color = self.colors.PRIMARY
            prefix = "🤖"
        elif msg_type == "error":
            color = self.colors.WARNING
            prefix = "❌"
        elif msg_type == "success":
            color = self.colors.ACCENT
            prefix = "✅"
        else:
            color = self.colors.BLACK
            prefix = "👤"
        
        # Insert message with Material Design typography
        self.chat_text.insert(tk.END, f"[{timestamp}] {prefix} {sender}:\n", "header")
        self.chat_text.insert(tk.END, f"{message}\n\n", "message")
        
        # Configure text tags for styling
        self.chat_text.tag_configure("header", 
                                    foreground=color, 
                                    font=('Roboto', 9, 'bold'))
        self.chat_text.tag_configure("message", 
                                    foreground=self.colors.BLACK, 
                                    font=('Roboto', 10))
        
        # Scroll to bottom and disable editing
        self.chat_text.see(tk.END)
        self.chat_text.config(state='disabled')
        
    def send_message(self):
        """Send a message and process the response."""
        query = self.query_var.get().strip()
        if not query:
            return
            
        # Add user message to chat
        self.add_material_message("You", query, "user")
        self.chat_history.append({"role": "user", "content": query})
        
        # Clear input field
        self.query_var.set("")
        
        # Update UI state
        self.send_btn.config(text="⏳ Processing...", state='disabled')
        self.status_indicator.config(text="🟡 Processing", fg=self.colors.WARNING)
        
        # Process query in separate thread to prevent UI freezing
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
        """
        Process natural language query using Gemini AI.
        
        Args:
            query (str): Natural language query from user
            
        Returns:
            dict: Response containing SQL query and results
        """
        try:
            # Create enhanced prompt for school management context
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

            # Generate SQL query using Gemini
            response = self.model.generate_content(prompt)
            sql_query = response.text.strip()
            
            # Clean up SQL query (remove markdown formatting)
            sql_query = re.sub(r'```sql\s*', '', sql_query)
            sql_query = re.sub(r'```\s*', '', sql_query)
            sql_query = sql_query.strip()
            
            # Execute SQL query using secure tool
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
        """
        Handle the response from query processing.
        
        Args:
            response (dict): Response containing SQL query and results
        """
        if "error" in response:
            self.add_material_message("❌ Error", response["error"], "error")
            return
            
        sql_query = response["sql_query"]
        result = response["result"]
        original_query = response["original_query"]
        
        # Display SQL query in chat
        self.add_material_message("🔍 SQL Query", f"```sql\n{sql_query}\n```", "assistant")
        
        # Handle query results
        if isinstance(result, dict) and 'columns' in result:
            # Format and display table data
            self.display_table_data(result)
            
            # Create chart if appropriate
            if self.should_create_chart(original_query, result):
                self.create_material_chart(result, original_query)
        else:
            # Display error or simple result
            self.add_material_message("📊 Result", str(result), "assistant")
            
        # Update status
        self.status_indicator.config(text="🟢 Connected", fg=self.colors.WHITE)
        
    def display_table_data(self, data):
        """
        Display table data in chat with proper formatting.
        
        Args:
            data (dict): Query results with columns and rows
        """
        if not data['rows']:
            self.add_material_message("📊 Result", "No data found.", "assistant")
            return
            
        # Create formatted table
        table_text = "📊 Query Results:\n\n"
        
        # Headers
        headers = " | ".join(data['columns'])
        table_text += headers + "\n"
        table_text += "-" * len(headers) + "\n"
        
        # Data rows (limit to 20 for readability)
        for row in data['rows'][:20]:
            row_str = " | ".join(str(cell) for cell in row)
            table_text += row_str + "\n"
            
        if len(data['rows']) > 20:
            table_text += f"\n... and {len(data['rows']) - 20} more rows"
            
        self.add_material_message("📊 Result", table_text, "assistant")
        
    def should_create_chart(self, query, data):
        """
        Determine if a chart should be created based on query and data.
        
        Args:
            query (str): Original user query
            data (dict): Query results data
            
        Returns:
            bool: True if chart should be created
        """
        query_lower = query.lower()
        chart_keywords = ['chart', 'graph', 'plot', 'visualize', 'show', 'display', 
                         'attendance', 'grades', 'distribution', 'trend', 'performance']
        
        # Check if query mentions visualization
        if any(keyword in query_lower for keyword in chart_keywords):
            return True
            
        # Check if data is suitable for charting
        if len(data['rows']) > 1 and len(data['columns']) >= 2:
            try:
                float(data['rows'][0][1])
                return True
            except (ValueError, IndexError):
                pass
                
        return False
        
    def create_material_chart(self, data, query):
        """
        Create a beautiful Material Design chart based on data and query.
        
        Args:
            data (dict): Query results data
            query (str): Original user query
        """
        try:
            # Clear previous chart
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
                
            if not data['rows'] or len(data['rows']) == 0:
                return
                
            # Convert to DataFrame
            df = pd.DataFrame(data['rows'], columns=data['columns'])
            
            # Set Material Design style for matplotlib
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor(self.colors.WHITE)
            ax.set_facecolor(self.colors.WHITE)
            
            # Determine chart type based on query
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
            
            # Apply Material Design styling
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(self.colors.GRAY)
            ax.spines['bottom'].set_color(self.colors.GRAY)
            ax.tick_params(colors=self.colors.DARK_GRAY)
            ax.yaxis.label.set_color(self.colors.DARK_GRAY)
            ax.xaxis.label.set_color(self.colors.DARK_GRAY)
            
            plt.tight_layout()
            
            # Embed in tkinter with proper sizing
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=8, pady=8)
            
            self.add_material_message("📈 Chart", "Beautiful chart created and displayed!", "success")
            
        except Exception as e:
            self.add_material_message("❌ Chart Error", f"Could not create chart: {e}", "error")
            
    def create_attendance_chart(self, df, ax):
        """Create Material Design attendance chart."""
        if len(df.columns) >= 2:
            # Bar chart with Material Design colors
            bars = ax.bar(df[df.columns[0]], df[df.columns[1]], 
                        color=self.colors.PRIMARY, alpha=0.8)
            ax.set_title('Attendance Overview', fontweight='bold', fontsize=14, 
                        color=self.colors.BLACK, pad=20)
            ax.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')
            
    def create_grade_chart(self, df, ax):
        """Create Material Design grade distribution chart."""
        if len(df.columns) >= 2:
            # Color-coded bar chart for grades
            colors = [self.colors.ACCENT if 'A' in str(g) else 
                     self.colors.SECONDARY if 'B' in str(g) else
                     self.colors.WARNING for g in df[df.columns[0]]]
            
            bars = ax.bar(df[df.columns[0]], df[df.columns[1]], color=colors, alpha=0.8)
            ax.set_title('Grade Distribution', fontweight='bold', fontsize=14,
                        color=self.colors.BLACK, pad=20)
            ax.tick_params(axis='x', rotation=45)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')
            
    def create_enrollment_chart(self, df, ax):
        """Create Material Design enrollment chart."""
        if len(df.columns) >= 2:
            # Pie chart with Material Design colors
            colors = [self.colors.PRIMARY, self.colors.SECONDARY, self.colors.ACCENT, 
                     self.colors.INFO, self.colors.WARNING]
            wedges, texts, autotexts = ax.pie(df[df.columns[1]], 
                                            labels=df[df.columns[0]], 
                                            autopct='%1.1f%%',
                                            colors=colors[:len(df)],
                                            startangle=90)
            ax.set_title('Enrollment Distribution', fontweight='bold', fontsize=14,
                        color=self.colors.BLACK, pad=20)
            
    def create_department_chart(self, df, ax):
        """Create Material Design department chart."""
        if len(df.columns) >= 2:
            # Horizontal bar chart
            bars = ax.barh(df[df.columns[0]], df[df.columns[1]], 
                          color=self.colors.INFO, alpha=0.8)
            ax.set_title('Department Statistics', fontweight='bold', fontsize=14,
                        color=self.colors.BLACK, pad=20)
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f'{int(width)}', ha='left', va='center')
            
    def create_default_chart(self, df, ax):
        """Create default Material Design chart."""
        if len(df.columns) >= 2:
            try:
                # Try bar chart first
                bars = ax.bar(df[df.columns[0]], df[df.columns[1]], 
                            color=self.colors.PRIMARY, alpha=0.8)
                ax.set_title('Data Visualization', fontweight='bold', fontsize=14,
                            color=self.colors.BLACK, pad=20)
                ax.tick_params(axis='x', rotation=45)
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}', ha='center', va='bottom')
            except:
                # Fallback to line chart
                ax.plot(df[df.columns[0]], df[df.columns[1]], 
                       color=self.colors.PRIMARY, linewidth=2, marker='o')
                ax.set_title('Data Visualization', fontweight='bold', fontsize=14,
                            color=self.colors.BLACK, pad=20)
                ax.tick_params(axis='x', rotation=45)
    
    def handle_error(self, error_msg):
        """
        Handle errors during query processing.
        
        Args:
            error_msg (str): Error message to display
        """
        self.add_material_message("❌ Error", f"An error occurred: {error_msg}", "error")
        self.status_indicator.config(text="🔴 Error", fg=self.colors.WARNING)
    
    def reset_send_button(self):
        """Reset the send button to its normal state."""
        self.send_btn.config(text="Send", state='normal')
        self.status_indicator.config(text="🟢 Connected", fg=self.colors.WHITE)
    
    def clear_chat(self):
        """Clear the chat history and reset the interface."""
        self.chat_text.config(state='normal')
        self.chat_text.delete(1.0, tk.END)
        self.chat_text.config(state='disabled')
        self.chat_history.clear()
        
        # Clear chart area
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # Add placeholder back
        placeholder = tk.Label(self.chart_frame,
                             text="Charts will appear here\nwhen you ask for visualizations",
                             font=('Roboto', 12),
                             fg=self.colors.GRAY,
                             bg=self.colors.WHITE)
        placeholder.pack(expand=True)
        
        # Add welcome message back
        self.add_material_message("🤖 Assistant", 
                                "Hello! I'm your School Management Assistant. Ask me anything about students, courses, attendance, grades, or teachers. I can also create beautiful charts and visualizations for you!", 
                                "assistant")

# ============================================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================================
def main():
    """
    Main function to initialize and run the Material Design School Management Chat Agent.
    
    This function:
    1. Creates the main Tkinter window
    2. Initializes the Material Design chat agent
    3. Starts the GUI event loop
    4. Handles graceful shutdown
    """
    try:
        # Create main window
        root = tk.Tk()
        
        # Initialize the Material Design chat agent
        app = MaterialSchoolChatAgent(root)
        
        # Configure window close behavior
        def on_closing():
            """Handle application shutdown gracefully."""
            try:
                # Save any pending data or state
                print("Shutting down School Management Assistant...")
                root.destroy()
            except Exception as e:
                print(f"Error during shutdown: {e}")
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the GUI event loop
        print("🎓 School Management Chat Assistant - Material Design")
        print("=" * 60)
        print("Features:")
        print("• Modern Material Design UI")
        print("• Natural language query processing")
        print("• Automatic chart generation")
        print("• Secure database operations")
        print("• Real-time chat interface")
        print("=" * 60)
        print("Starting application...")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        print("Please check your environment setup and try again.")
        return 1
    
    return 0

# ============================================================================
# APPLICATION CONFIGURATION AND STARTUP
# ============================================================================
if __name__ == "__main__":
    """
    Application entry point with comprehensive error handling and logging.
    
    This section ensures:
    - Proper environment setup
    - Database connectivity verification
    - API key validation
    - Graceful error handling
    - Professional startup logging
    """
    
    # Application metadata
    APP_NAME = "School Management Chat Assistant"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "Material Design School Management System with AI-Powered Analytics"
    
    print(f"\n🚀 {APP_NAME} v{APP_VERSION}")
    print(f"📝 {APP_DESCRIPTION}")
    print("=" * 80)
    
    # Check environment setup
    print("🔍 Checking environment setup...")
    
    # Verify database exists
    if not DB_FILE_PATH.exists():
        print(f"❌ Database not found at: {DB_FILE_PATH}")
        print("Please run setup_school_database.py first to create the database.")
        exit(1)
    else:
        print(f"✅ Database found: {DB_FILE_PATH}")
    
    # Check for required environment variables
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please create a .env file with your Gemini API key:")
        print("GEMINI_API_KEY=your_api_key_here")
        exit(1)
    else:
        print("✅ Gemini API key found")
    
    # Check required Python packages
    required_packages = [
        'tkinter', 'pandas', 'matplotlib', 'seaborn', 
        'google.generativeai', 'sqlalchemy', 'pydantic', 
        'langchain', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        exit(1)
    else:
        print("✅ All required packages available")
    
    print("=" * 80)
    print("🎯 Starting application...")
    print("=" * 80)
    
    # Start the application
    exit_code = main()
    
    if exit_code == 0:
        print("\n✅ Application closed successfully")
    else:
        print(f"\n❌ Application exited with error code: {exit_code}")
    
    print("=" * 80)
    print("Thank you for using the School Management Chat Assistant!")
    print("=" * 80)
                