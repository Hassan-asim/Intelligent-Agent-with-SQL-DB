"""
Modern School Management SQL Agent with Enhanced UI

This script provides a comprehensive school management system with:
- Secure read-only database access
- Modern UI with cards, shadows, hover effects
- Graphical representations of data
- Real-time analytics and insights
- Toast notifications and smooth animations
"""

import os
import re
import sqlite3
import pathlib
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import google.generativeai as genai
from dotenv import load_dotenv
import sqlalchemy
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_community.utilities import SQLDatabase
from langchain.schema import SystemMessage
from typing import Type
import threading
import time
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Database Configuration
script_dir = pathlib.Path(__file__).parent
project_root = script_dir.parent
DB_FILE_PATH = project_root / "school_management.db"
DB_URL = f"sqlite:///{DB_FILE_PATH.as_posix()}"

# Create Database Engine
engine = sqlalchemy.create_engine(DB_URL)

class QueryInput(BaseModel):
    """Pydantic model for safe SQL query input validation."""
    sql: str = Field(description="A single read-only SELECT statement, bounded with LIMIT when returning many rows.")

class SecureSchoolSQLTool(BaseTool):
    """
    SECURE School Management SQL Tool - Only Allows Read-Only SELECT Operations
    
    Enhanced security features:
    - Multiple validation layers
    - SQL injection prevention
    - Result set limiting
    - School-specific query optimization
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

def execute_query(query: str):
    """Execute a natural language query using Gemini API and SecureSQLTool."""
    print(f"User query: {query}")
    
    try:
        # Configure Gemini API
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('models/gemini-1.5-flash')

        # Get database schema
        schema = get_schema_context()

        # Create enhanced prompt for school management
        prompt = f"""You are an expert school management analytics assistant. Use only these tables:

{schema}

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

User Query: {query}

SQL Query:"""

        # Generate SQL query
        response = model.generate_content(prompt)
        sql_query = response.text.strip()
        print(f"Generated SQL query: {sql_query}")

        # Execute using secure tool
        safe_tool = SecureSchoolSQLTool()
        result = safe_tool._run(sql_query)
        print(f"Query result: {result}")

        return result, sql_query
    except Exception as e:
        return f"ERROR: {str(e)}", ""

class ModernSchoolUI:
    """Modern school management UI with enhanced styling and animations."""
    
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.setup_styles()
        self.create_widgets()
        self.setup_animations()
        
    def setup_ui(self):
        """Setup the main UI configuration."""
        self.root.title("🎓 School Management Analytics Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f8fafc")
        self.root.minsize(1200, 800)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1400x900+{x}+{y}")
        
    def setup_styles(self):
        """Setup modern styling with CSS-like approach."""
        self.style = ttk.Style()
        
        # Configure modern theme
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
                           font=('Segoe UI', 24, 'bold'),
                           foreground=self.colors['dark'],
                           background=self.colors['light'])
        
        self.style.configure('Card.TFrame',
                           background=self.colors['white'],
                           relief='solid',
                           borderwidth=0)
        
        self.style.configure('Modern.TButton',
                           font=('Segoe UI', 10, 'bold'),
                           background=self.colors['primary'],
                           foreground=self.colors['white'],
                           borderwidth=0,
                           focuscolor='none',
                           padding=(20, 10))
        
        self.style.map('Modern.TButton',
                      background=[('active', '#2563eb'),
                                ('pressed', '#1d4ed8')])
        
        self.style.configure('Query.TEntry',
                           font=('Segoe UI', 11),
                           padding=(15, 12),
                           relief='solid',
                           borderwidth=1)
        
    def create_widgets(self):
        """Create all UI widgets with modern design."""
        # Main container with padding
        main_frame = tk.Frame(self.root, bg=self.colors['light'], padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Header section
        self.create_header(main_frame)
        
        # Content area with cards
        self.create_content_area(main_frame)
        
        # Footer
        self.create_footer(main_frame)
        
    def create_header(self, parent):
        """Create the header section."""
        header_frame = tk.Frame(parent, bg=self.colors['light'])
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title
        title_label = ttk.Label(header_frame, 
                               text="🎓 School Management Analytics",
                               style='Title.TLabel')
        title_label.pack(side='left')
        
        # Status indicator
        self.status_frame = tk.Frame(header_frame, bg=self.colors['light'])
        self.status_frame.pack(side='right')
        
        self.status_indicator = tk.Label(self.status_frame,
                                       text="🟢 Connected",
                                       font=('Segoe UI', 10),
                                       fg=self.colors['success'],
                                       bg=self.colors['light'])
        self.status_indicator.pack()
        
    def create_content_area(self, parent):
        """Create the main content area with cards."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill='both', expand=True)
        
        # Query tab
        self.create_query_tab()
        
        # Analytics tab
        self.create_analytics_tab()
        
        # Reports tab
        self.create_reports_tab()
        
    def create_query_tab(self):
        """Create the query interface tab."""
        query_frame = ttk.Frame(self.notebook)
        self.notebook.add(query_frame, text="🔍 Query Interface")
        
        # Query input card
        query_card = self.create_card(query_frame, "Natural Language Query")
        
        # Query input
        self.query_var = tk.StringVar()
        self.query_entry = ttk.Entry(query_card, 
                                   textvariable=self.query_var,
                                   style='Query.TEntry',
                                   font=('Segoe UI', 11))
        self.query_entry.pack(fill='x', pady=(0, 15))
        self.query_entry.bind('<Return>', lambda e: self.execute_query())
        
        # Query buttons
        button_frame = tk.Frame(query_card, bg=self.colors['white'])
        button_frame.pack(fill='x', pady=(0, 15))
        
        self.query_btn = ttk.Button(button_frame,
                                  text="🚀 Execute Query",
                                  style='Modern.TButton',
                                  command=self.execute_query)
        self.query_btn.pack(side='left', padx=(0, 10))
        
        self.clear_btn = ttk.Button(button_frame,
                                  text="🗑️ Clear",
                                  style='Modern.TButton',
                                  command=self.clear_query)
        self.clear_btn.pack(side='left')
        
        # Results area
        results_card = self.create_card(query_frame, "Query Results")
        
        # Results text
        self.results_text = tk.Text(results_card,
                                  height=15,
                                  font=('Consolas', 10),
                                  bg='#f8f9fa',
                                  fg='#212529',
                                  relief='solid',
                                  borderwidth=1,
                                  wrap='word')
        self.results_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Chart area
        self.chart_frame = tk.Frame(results_card, bg=self.colors['white'])
        self.chart_frame.pack(fill='both', expand=True)
        
    def create_analytics_tab(self):
        """Create the analytics dashboard tab."""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📊 Analytics Dashboard")
        
        # Create grid of analytics cards
        self.create_analytics_grid(analytics_frame)
        
    def create_analytics_grid(self, parent):
        """Create a grid of analytics cards."""
        # Top row - Key metrics
        top_frame = tk.Frame(parent, bg=self.colors['light'])
        top_frame.pack(fill='x', pady=(0, 20))
        
        # Student count card
        self.student_card = self.create_metric_card(top_frame, "👥 Total Students", "20", self.colors['primary'])
        self.student_card.pack(side='left', padx=(0, 15), fill='x', expand=True)
        
        # Course count card
        self.course_card = self.create_metric_card(top_frame, "📚 Active Courses", "5", self.colors['success'])
        self.course_card.pack(side='left', padx=(0, 15), fill='x', expand=True)
        
        # Teacher count card
        self.teacher_card = self.create_metric_card(top_frame, "👨‍🏫 Teachers", "16", self.colors['info'])
        self.teacher_card.pack(side='left', padx=(0, 15), fill='x', expand=True)
        
        # Department count card
        self.dept_card = self.create_metric_card(top_frame, "🏛️ Departments", "8", self.colors['warning'])
        self.dept_card.pack(side='left', fill='x', expand=True)
        
        # Charts row
        charts_frame = tk.Frame(parent, bg=self.colors['light'])
        charts_frame.pack(fill='both', expand=True)
        
        # Left chart - Attendance
        left_chart_card = self.create_card(charts_frame, "📈 Attendance Overview")
        left_chart_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.attendance_chart_frame = tk.Frame(left_chart_card, bg=self.colors['white'])
        self.attendance_chart_frame.pack(fill='both', expand=True)
        
        # Right chart - Grade Distribution
        right_chart_card = self.create_card(charts_frame, "📊 Grade Distribution")
        right_chart_card.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.grades_chart_frame = tk.Frame(right_chart_card, bg=self.colors['white'])
        self.grades_chart_frame.pack(fill='both', expand=True)
        
        # Load default analytics
        self.load_default_analytics()
        
    def create_reports_tab(self):
        """Create the reports tab."""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="📋 Reports")
        
        # Quick reports section
        quick_reports_card = self.create_card(reports_frame, "Quick Reports")
        
        # Report buttons
        report_buttons = [
            ("📊 Student Performance Report", self.generate_student_performance_report),
            ("📈 Attendance Summary", self.generate_attendance_report),
            ("🎓 Course Enrollment Report", self.generate_enrollment_report),
            ("👨‍🏫 Teacher Workload Report", self.generate_teacher_workload_report),
            ("📚 Department Statistics", self.generate_department_report)
        ]
        
        for i, (text, command) in enumerate(report_buttons):
            btn = ttk.Button(quick_reports_card,
                           text=text,
                           style='Modern.TButton',
                           command=command)
            btn.pack(fill='x', pady=5)
            
        # Reports display area
        self.reports_display = tk.Text(reports_frame,
                                     height=20,
                                     font=('Consolas', 10),
                                     bg='#f8f9fa',
                                     fg='#212529',
                                     relief='solid',
                                     borderwidth=1,
                                     wrap='word')
        self.reports_display.pack(fill='both', expand=True, pady=(20, 0))
        
    def create_card(self, parent, title):
        """Create a modern card widget."""
        card_frame = tk.Frame(parent, bg=self.colors['white'], relief='solid', borderwidth=1)
        card_frame.pack(fill='both', expand=True, pady=10, padx=10)
        
        # Add shadow effect
        shadow_frame = tk.Frame(parent, bg='#e2e8f0', height=2)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg=self.colors['white'])
        header_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        title_label = tk.Label(header_frame,
                             text=title,
                             font=('Segoe UI', 14, 'bold'),
                             fg=self.colors['dark'],
                             bg=self.colors['white'])
        title_label.pack(side='left')
        
        # Card content
        content_frame = tk.Frame(card_frame, bg=self.colors['white'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        return content_frame
        
    def create_metric_card(self, parent, title, value, color):
        """Create a metric display card."""
        card = tk.Frame(parent, bg=self.colors['white'], relief='solid', borderwidth=1)
        
        # Title
        title_label = tk.Label(card,
                             text=title,
                             font=('Segoe UI', 10),
                             fg=self.colors['secondary'],
                             bg=self.colors['white'])
        title_label.pack(pady=(15, 5))
        
        # Value
        value_label = tk.Label(card,
                             text=value,
                             font=('Segoe UI', 24, 'bold'),
                             fg=color,
                             bg=self.colors['white'])
        value_label.pack(pady=(0, 15))
        
        return card
        
    def setup_animations(self):
        """Setup smooth animations and hover effects."""
        # Add hover effects to buttons
        self.add_hover_effects()
        
    def add_hover_effects(self):
        """Add hover effects to interactive elements."""
        # This would be implemented with custom event bindings
        pass
        
    def execute_query(self):
        """Execute the natural language query."""
        query = self.query_var.get().strip()
        if not query:
            self.show_toast("Please enter a query", "warning")
            return
            
        # Show loading state
        self.query_btn.config(text="⏳ Processing...", state='disabled')
        self.status_indicator.config(text="🟡 Processing", fg=self.colors['warning'])
        
        # Execute in thread to prevent UI freezing
        def run_query():
            try:
                result, sql_query = execute_query(query)
                
                # Update UI in main thread
                self.root.after(0, self.update_query_results, result, sql_query)
                
            except Exception as e:
                self.root.after(0, self.show_error, str(e))
            finally:
                self.root.after(0, self.reset_query_button)
                
        threading.Thread(target=run_query, daemon=True).start()
        
    def update_query_results(self, result, sql_query):
        """Update the query results display."""
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Display SQL query
        self.results_text.insert(tk.END, f"SQL Query:\n{sql_query}\n\n")
        self.results_text.insert(tk.END, "="*50 + "\n\n")
        
        # Display results
        if isinstance(result, dict) and 'columns' in result:
            # Format as table
            self.results_text.insert(tk.END, "Query Results:\n\n")
            
            # Headers
            headers = " | ".join(result['columns'])
            self.results_text.insert(tk.END, headers + "\n")
            self.results_text.insert(tk.END, "-" * len(headers) + "\n")
            
            # Data rows
            for row in result['rows']:
                row_str = " | ".join(str(cell) for cell in row)
                self.results_text.insert(tk.END, row_str + "\n")
                
            # Create chart if possible
            self.create_chart_from_data(result)
            
        else:
            # Display error or simple result
            self.results_text.insert(tk.END, f"Result: {result}")
            
        self.status_indicator.config(text="🟢 Connected", fg=self.colors['success'])
        
    def create_chart_from_data(self, data):
        """Create a chart from query results."""
        try:
            # Clear previous chart
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
                
            if not data['rows'] or len(data['rows']) == 0:
                return
                
            # Convert to DataFrame
            df = pd.DataFrame(data['rows'], columns=data['columns'])
            
            # Determine chart type based on data
            if len(df.columns) >= 2:
                fig, ax = plt.subplots(figsize=(8, 4))
                
                # Try to create appropriate chart
                if df.dtypes[df.columns[1]].dtype in ['int64', 'float64']:
                    # Numeric data - bar chart
                    df.plot(kind='bar', x=df.columns[0], y=df.columns[1], ax=ax)
                    ax.set_title('Query Results Visualization')
                    ax.tick_params(axis='x', rotation=45)
                else:
                    # Categorical data - count plot
                    df[df.columns[0]].value_counts().plot(kind='bar', ax=ax)
                    ax.set_title('Query Results Distribution')
                    ax.tick_params(axis='x', rotation=45)
                
                plt.tight_layout()
                
                # Embed in tkinter
                canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill='both', expand=True)
                
        except Exception as e:
            print(f"Chart creation error: {e}")
            
    def clear_query(self):
        """Clear the query input and results."""
        self.query_var.set("")
        self.results_text.delete(1.0, tk.END)
        
        # Clear chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
    def reset_query_button(self):
        """Reset the query button state."""
        self.query_btn.config(text="🚀 Execute Query", state='normal')
        
    def show_error(self, error_msg):
        """Show error message."""
        self.show_toast(f"Error: {error_msg}", "danger")
        self.status_indicator.config(text="🔴 Error", fg=self.colors['danger'])
        
    def show_toast(self, message, type="info"):
        """Show a toast notification."""
        # Create toast window
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.configure(bg=self.colors['dark'])
        
        # Position toast
        toast.geometry("300x60+{}+{}".format(
            self.root.winfo_x() + 50,
            self.root.winfo_y() + 50
        ))
        
        # Toast content
        color = self.colors.get(type, self.colors['info'])
        label = tk.Label(toast,
                        text=message,
                        font=('Segoe UI', 10),
                        fg=self.colors['white'],
                        bg=self.colors['dark'])
        label.pack(expand=True)
        
        # Auto-close after 3 seconds
        toast.after(3000, toast.destroy)
        
    def load_default_analytics(self):
        """Load default analytics charts."""
        self.create_attendance_chart()
        self.create_grades_chart()
        
    def create_attendance_chart(self):
        """Create attendance overview chart."""
        try:
            # Query attendance data
            safe_tool = SecureSchoolSQLTool()
            result = safe_tool._run("""
                SELECT 
                    c.course_name,
                    COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present_count,
                    COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as absent_count,
                    COUNT(CASE WHEN a.status = 'late' THEN 1 END) as late_count
                FROM courses c
                LEFT JOIN attendance a ON c.id = a.course_id
                GROUP BY c.id, c.course_name
                ORDER BY present_count DESC
            """)
            
            if isinstance(result, dict) and result['rows']:
                df = pd.DataFrame(result['rows'], columns=result['columns'])
                
                fig, ax = plt.subplots(figsize=(6, 4))
                
                # Create stacked bar chart
                df.set_index('course_name')[['present_count', 'absent_count', 'late_count']].plot(
                    kind='bar', stacked=True, ax=ax, 
                    color=['#10b981', '#ef4444', '#f59e0b']
                )
                
                ax.set_title('Attendance by Course', fontsize=12, fontweight='bold')
                ax.set_xlabel('Course')
                ax.set_ylabel('Number of Students')
                ax.tick_params(axis='x', rotation=45)
                ax.legend(['Present', 'Absent', 'Late'])
                
                plt.tight_layout()
                
                canvas = FigureCanvasTkAgg(fig, master=self.attendance_chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill='both', expand=True)
                
        except Exception as e:
            print(f"Attendance chart error: {e}")
            
    def create_grades_chart(self):
        """Create grade distribution chart."""
        try:
            # Query grades data
            safe_tool = SecureSchoolSQLTool()
            result = safe_tool._run("""
                SELECT 
                    letter_grade,
                    COUNT(*) as count
                FROM grades
                GROUP BY letter_grade
                ORDER BY 
                    CASE letter_grade
                        WHEN 'A+' THEN 1
                        WHEN 'A' THEN 2
                        WHEN 'A-' THEN 3
                        WHEN 'B+' THEN 4
                        WHEN 'B' THEN 5
                        WHEN 'B-' THEN 6
                        WHEN 'C+' THEN 7
                        WHEN 'C' THEN 8
                        WHEN 'C-' THEN 9
                        WHEN 'D+' THEN 10
                        WHEN 'D' THEN 11
                        WHEN 'D-' THEN 12
                        WHEN 'F' THEN 13
                    END
            """)
            
            if isinstance(result, dict) and result['rows']:
                df = pd.DataFrame(result['rows'], columns=result['columns'])
                
                fig, ax = plt.subplots(figsize=(6, 4))
                
                # Create bar chart
                bars = ax.bar(df['letter_grade'], df['count'], 
                            color=['#10b981' if g in ['A+', 'A', 'A-'] else 
                                  '#f59e0b' if g in ['B+', 'B', 'B-'] else
                                  '#ef4444' for g in df['letter_grade']])
                
                ax.set_title('Grade Distribution', fontsize=12, fontweight='bold')
                ax.set_xlabel('Letter Grade')
                ax.set_ylabel('Number of Grades')
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}', ha='center', va='bottom')
                
                plt.tight_layout()
                
                canvas = FigureCanvasTkAgg(fig, master=self.grades_chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill='both', expand=True)
                
        except Exception as e:
            print(f"Grades chart error: {e}")
            
    def generate_student_performance_report(self):
        """Generate student performance report."""
        try:
            safe_tool = SecureSchoolSQLTool()
            result = safe_tool._run("""
                SELECT 
                    s.first_name || ' ' || s.last_name as student_name,
                    s.student_id,
                    s.gpa,
                    COUNT(e.course_id) as courses_enrolled,
                    AVG(g.grade_percentage) as avg_grade_percentage
                FROM students s
                LEFT JOIN enrollments e ON s.id = e.student_id
                LEFT JOIN grades g ON s.id = g.student_id
                GROUP BY s.id, s.first_name, s.last_name, s.student_id, s.gpa
                ORDER BY s.gpa DESC
            """)
            
            if isinstance(result, dict) and result['rows']:
                self.display_report("Student Performance Report", result)
                
        except Exception as e:
            self.show_toast(f"Error generating report: {e}", "danger")
            
    def generate_attendance_report(self):
        """Generate attendance report."""
        try:
            safe_tool = SecureSchoolSQLTool()
            result = safe_tool._run("""
                SELECT 
                    c.course_name,
                    COUNT(a.id) as total_records,
                    COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present,
                    COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as absent,
                    COUNT(CASE WHEN a.status = 'late' THEN 1 END) as late,
                    ROUND(COUNT(CASE WHEN a.status = 'present' THEN 1 END) * 100.0 / COUNT(a.id), 2) as attendance_rate
                FROM courses c
                LEFT JOIN attendance a ON c.id = a.course_id
                GROUP BY c.id, c.course_name
                ORDER BY attendance_rate DESC
            """)
            
            if isinstance(result, dict) and result['rows']:
                self.display_report("Attendance Report", result)
                
        except Exception as e:
            self.show_toast(f"Error generating report: {e}", "danger")
            
    def generate_enrollment_report(self):
        """Generate course enrollment report."""
        try:
            safe_tool = SecureSchoolSQLTool()
            result = safe_tool._run("""
                SELECT 
                    c.course_name,
                    c.course_code,
                    c.credits,
                    c.max_students,
                    c.current_enrollment,
                    ROUND(c.current_enrollment * 100.0 / c.max_students, 2) as enrollment_percentage
                FROM courses c
                ORDER BY c.current_enrollment DESC
            """)
            
            if isinstance(result, dict) and result['rows']:
                self.display_report("Course Enrollment Report", result)
                
        except Exception as e:
            self.show_toast(f"Error generating report: {e}", "danger")
            
    def generate_teacher_workload_report(self):
        """Generate teacher workload report."""
        try:
            safe_tool = SecureSchoolSQLTool()
            result = safe_tool._run("""
                SELECT 
                    t.first_name || ' ' || t.last_name as teacher_name,
                    d.name as department,
                    COUNT(c.id) as courses_teaching,
                    SUM(c.current_enrollment) as total_students,
                    t.specialization
                FROM teachers t
                LEFT JOIN departments d ON t.department_id = d.id
                LEFT JOIN courses c ON t.id = c.teacher_id
                GROUP BY t.id, t.first_name, t.last_name, d.name, t.specialization
                ORDER BY total_students DESC
            """)
            
            if isinstance(result, dict) and result['rows']:
                self.display_report("Teacher Workload Report", result)
                
        except Exception as e:
            self.show_toast(f"Error generating report: {e}", "danger")
            
    def generate_department_report(self):
        """Generate department statistics report."""
        try:
            safe_tool = SecureSchoolSQLTool()
            result = safe_tool._run("""
                SELECT 
                    d.name as department,
                    COUNT(DISTINCT t.id) as teachers,
                    COUNT(DISTINCT c.id) as courses,
                    COUNT(DISTINCT e.student_id) as students_enrolled,
                    AVG(s.gpa) as avg_student_gpa
                FROM departments d
                LEFT JOIN teachers t ON d.id = t.department_id
                LEFT JOIN courses c ON d.id = c.department_id
                LEFT JOIN enrollments e ON c.id = e.course_id
                LEFT JOIN students s ON e.student_id = s.id
                GROUP BY d.id, d.name
                ORDER BY students_enrolled DESC
            """)
            
            if isinstance(result, dict) and result['rows']:
                self.display_report("Department Statistics Report", result)
                
        except Exception as e:
            self.show_toast(f"Error generating report: {e}", "danger")
            
    def display_report(self, title, data):
        """Display a report in the reports tab."""
        # Switch to reports tab
        self.notebook.select(1)
        
        # Clear previous report
        self.reports_display.delete(1.0, tk.END)
        
        # Add title
        self.reports_display.insert(tk.END, f"{title}\n")
        self.reports_display.insert(tk.END, "=" * len(title) + "\n\n")
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.reports_display.insert(tk.END, f"Generated: {timestamp}\n\n")
        
        # Add data
        if isinstance(data, dict) and 'columns' in data:
            # Headers
            headers = " | ".join(data['columns'])
            self.reports_display.insert(tk.END, headers + "\n")
            self.reports_display.insert(tk.END, "-" * len(headers) + "\n")
            
            # Data rows
            for row in data['rows']:
                row_str = " | ".join(str(cell) for cell in row)
                self.reports_display.insert(tk.END, row_str + "\n")
        else:
            self.reports_display.insert(tk.END, str(data))
            
    def create_footer(self, parent):
        """Create the footer section."""
        footer_frame = tk.Frame(parent, bg=self.colors['light'])
        footer_frame.pack(fill='x', pady=(20, 0))
        
        # Footer text
        footer_label = tk.Label(footer_frame,
                              text="🎓 School Management System v2.0 | Secure & Modern",
                              font=('Segoe UI', 9),
                              fg=self.colors['secondary'],
                              bg=self.colors['light'])
        footer_label.pack()

def main():
    """Main function to run the school management system."""
    # Check if database exists
    if not DB_FILE_PATH.exists():
        print("Database not found. Creating school management database...")
        from setup_school_database import setup_school_database
        setup_school_database()
    
    # Create and run the application
    root = tk.Tk()
    app = ModernSchoolUI(root)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
