PRAGMA foreign_keys = ON;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS semesters;

-- Create tables
CREATE TABLE departments (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  head_teacher_id INTEGER,
  created_at TEXT NOT NULL
);

CREATE TABLE teachers (
  id INTEGER PRIMARY KEY,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  phone TEXT,
  department_id INTEGER NOT NULL,
  hire_date TEXT NOT NULL,
  salary INTEGER,
  specialization TEXT,
  FOREIGN KEY(department_id) REFERENCES departments(id)
);

CREATE TABLE students (
  id INTEGER PRIMARY KEY,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  phone TEXT,
  date_of_birth TEXT NOT NULL,
  enrollment_date TEXT NOT NULL,
  student_id TEXT UNIQUE NOT NULL,
  gpa REAL DEFAULT 0.0,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'graduated', 'suspended'))
);

CREATE TABLE semesters (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  start_date TEXT NOT NULL,
  end_date TEXT NOT NULL,
  is_current BOOLEAN DEFAULT 0
);

CREATE TABLE courses (
  id INTEGER PRIMARY KEY,
  course_code TEXT UNIQUE NOT NULL,
  course_name TEXT NOT NULL,
  description TEXT,
  credits INTEGER NOT NULL,
  department_id INTEGER NOT NULL,
  teacher_id INTEGER NOT NULL,
  semester_id INTEGER NOT NULL,
  max_students INTEGER DEFAULT 30,
  current_enrollment INTEGER DEFAULT 0,
  FOREIGN KEY(department_id) REFERENCES departments(id),
  FOREIGN KEY(teacher_id) REFERENCES teachers(id),
  FOREIGN KEY(semester_id) REFERENCES semesters(id)
);

CREATE TABLE enrollments (
  id INTEGER PRIMARY KEY,
  student_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL,
  enrollment_date TEXT NOT NULL,
  status TEXT DEFAULT 'enrolled' CHECK (status IN ('enrolled', 'dropped', 'completed', 'failed')),
  FOREIGN KEY(student_id) REFERENCES students(id),
  FOREIGN KEY(course_id) REFERENCES courses(id),
  UNIQUE(student_id, course_id)
);

CREATE TABLE attendance (
  id INTEGER PRIMARY KEY,
  student_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL,
  date TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('present', 'absent', 'late', 'excused')),
  notes TEXT,
  FOREIGN KEY(student_id) REFERENCES students(id),
  FOREIGN KEY(course_id) REFERENCES courses(id)
);

CREATE TABLE grades (
  id INTEGER PRIMARY KEY,
  student_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL,
  assignment_name TEXT NOT NULL,
  points_earned INTEGER NOT NULL,
  points_possible INTEGER NOT NULL,
  grade_percentage REAL NOT NULL,
  letter_grade TEXT NOT NULL,
  assignment_type TEXT NOT NULL CHECK (assignment_type IN ('homework', 'quiz', 'exam', 'project', 'participation')),
  date_graded TEXT NOT NULL,
  FOREIGN KEY(student_id) REFERENCES students(id),
  FOREIGN KEY(course_id) REFERENCES courses(id)
);
