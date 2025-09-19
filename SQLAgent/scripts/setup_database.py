"""
Database Setup Script

This script creates the database and populates it with demo data for classes,
courses, students, and instructors.
"""

import sqlite3

def setup_database():
    """
    Create the database and populate it with demo data.
    """
    conn = sqlite3.connect('C:/Users/user/OneDrive/Desktop/SQL agent by Hassan/task by hassan/week_10/SQLAgent/sql_agent_class.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS instructors (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        instructor_id INTEGER,
        FOREIGN KEY (instructor_id) REFERENCES instructors (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY,
        course_id INTEGER,
        student_id INTEGER,
        FOREIGN KEY (course_id) REFERENCES courses (id),
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
    """)

    # Insert demo data
    cursor.execute("INSERT INTO instructors (name, email) VALUES (?, ?)", ('John Doe', 'john.doe@example.com'))
    cursor.execute("INSERT INTO instructors (name, email) VALUES (?, ?)", ('Jane Smith', 'jane.smith@example.com'))

    cursor.execute("INSERT INTO courses (name, description, instructor_id) VALUES (?, ?, ?)", ('Introduction to Python', 'A beginner-friendly course on Python programming.', 1))
    cursor.execute("INSERT INTO courses (name, description, instructor_id) VALUES (?, ?, ?)", ('Advanced SQL', 'A deep dive into advanced SQL concepts.', 2))
    cursor.execute("INSERT INTO courses (name, description, instructor_id) VALUES (?, ?, ?)", ('Machine Learning', 'An introduction to machine learning concepts and algorithms.', 1))

    cursor.execute("INSERT INTO students (name, email) VALUES (?, ?)", ('Alice', 'alice@example.com'))
    cursor.execute("INSERT INTO students (name, email) VALUES (?, ?)", ('Bob', 'bob@example.com'))
    cursor.execute("INSERT INTO students (name, email) VALUES (?, ?)", ('Charlie', 'charlie@example.com'))

    cursor.execute("INSERT INTO classes (course_id, student_id) VALUES (?, ?)", (1, 1))
    cursor.execute("INSERT INTO classes (course_id, student_id) VALUES (?, ?)", (1, 2))
    cursor.execute("INSERT INTO classes (course_id, student_id) VALUES (?, ?)", (2, 2))
    cursor.execute("INSERT INTO classes (course_id, student_id) VALUES (?, ?)", (2, 3))
    cursor.execute("INSERT INTO classes (course_id, student_id) VALUES (?, ?)", (3, 1))
    cursor.execute("INSERT INTO classes (course_id, student_id) VALUES (?, ?)", (3, 3))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()
