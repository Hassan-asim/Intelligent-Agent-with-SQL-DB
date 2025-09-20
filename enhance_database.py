#!/usr/bin/env python3
"""
Enhanced Database Population Script
Adds 10x more realistic fake data to the school management database.
This script creates a comprehensive dataset with realistic names, dates, and relationships.
"""

import sqlite3
import random
import pathlib
from datetime import datetime, timedelta
import json

# Get the database path
SCRIPT_DIR = pathlib.Path(__file__).parent
DB_PATH = SCRIPT_DIR / "school_management.db"

# Realistic data pools
FIRST_NAMES = [
    # Male names
    'James', 'Robert', 'John', 'Michael', 'David', 'William', 'Richard', 'Joseph', 'Thomas', 'Christopher',
    'Charles', 'Daniel', 'Matthew', 'Anthony', 'Mark', 'Donald', 'Steven', 'Paul', 'Andrew', 'Joshua',
    'Kenneth', 'Kevin', 'Brian', 'George', 'Timothy', 'Ronald', 'Jason', 'Edward', 'Jeffrey', 'Ryan',
    'Jacob', 'Gary', 'Nicholas', 'Eric', 'Jonathan', 'Stephen', 'Larry', 'Justin', 'Scott', 'Brandon',
    'Benjamin', 'Samuel', 'Gregory', 'Alexander', 'Patrick', 'Jack', 'Dennis', 'Jerry', 'Tyler', 'Aaron',
    'Jose', 'Henry', 'Adam', 'Douglas', 'Nathan', 'Peter', 'Zachary', 'Kyle', 'Noah', 'Alan',
    'Ethan', 'Jeremy', 'Mason', 'Christian', 'Sean', 'Austin', 'Logan', 'Lucas', 'Hunter', 'Caleb',
    'Connor', 'Aiden', 'Jackson', 'Luke', 'Brayden', 'Carter', 'Owen', 'Wyatt', 'Sebastian', 'Carson',
    'Landon', 'Eli', 'Mason', 'Isaac', 'Levi', 'Gabriel', 'Julian', 'Mateo', 'Anthony', 'Jaxon',
    'Lincoln', 'Josiah', 'Asher', 'Christopher', 'John', 'David', 'Matthew', 'Andrew', 'Daniel', 'Joshua',
    
    # Female names
    'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen',
    'Nancy', 'Lisa', 'Betty', 'Helen', 'Sandra', 'Donna', 'Carol', 'Ruth', 'Sharon', 'Michelle',
    'Laura', 'Sarah', 'Kimberly', 'Deborah', 'Dorothy', 'Lisa', 'Nancy', 'Karen', 'Betty', 'Helen',
    'Sandra', 'Donna', 'Carol', 'Ruth', 'Sharon', 'Michelle', 'Laura', 'Sarah', 'Kimberly', 'Deborah',
    'Dorothy', 'Amy', 'Angela', 'Ashley', 'Brenda', 'Emma', 'Olivia', 'Cynthia', 'Marie', 'Janet',
    'Catherine', 'Frances', 'Christine', 'Samantha', 'Debra', 'Rachel', 'Carolyn', 'Janet', 'Virginia',
    'Maria', 'Heather', 'Diane', 'Julie', 'Joyce', 'Victoria', 'Kelly', 'Christina', 'Joan', 'Evelyn',
    'Judith', 'Megan', 'Cheryl', 'Andrea', 'Hannah', 'Jacqueline', 'Martha', 'Gloria', 'Teresa', 'Sara',
    'Janice', 'Julia', 'Marie', 'Madison', 'Grace', 'Judy', 'Theresa', 'Beverly', 'Denise', 'Marilyn',
    'Amber', 'Danielle', 'Brittany', 'Diana', 'Abigail', 'Jane', 'Lori', 'Megan', 'Stephanie', 'Donna',
    'Katherine', 'Rachel', 'Carolyn', 'Janet', 'Virginia', 'Maria', 'Heather', 'Diane', 'Julie', 'Joyce'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
    'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
    'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
    'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
    'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts',
    'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker', 'Cruz', 'Edwards', 'Collins', 'Reyes',
    'Stewart', 'Morris', 'Morales', 'Murphy', 'Cook', 'Rogers', 'Gutierrez', 'Ortiz', 'Morgan', 'Cooper',
    'Peterson', 'Bailey', 'Reed', 'Kelly', 'Howard', 'Ramos', 'Kim', 'Cox', 'Ward', 'Richardson',
    'Watson', 'Brooks', 'Chavez', 'Wood', 'James', 'Bennett', 'Gray', 'Mendoza', 'Ruiz', 'Hughes',
    'Price', 'Alvarez', 'Castillo', 'Sanders', 'Patel', 'Myers', 'Long', 'Ross', 'Foster', 'Jimenez',
    'Powell', 'Jenkins', 'Perry', 'Russell', 'Sullivan', 'Bell', 'Coleman', 'Butler', 'Henderson', 'Barnes',
    'Gonzales', 'Fisher', 'Vasquez', 'Simmons', 'Romero', 'Jordan', 'Patterson', 'Alexander', 'Hamilton', 'Graham',
    'Reynolds', 'Griffin', 'Wallace', 'Moreno', 'West', 'Cole', 'Hayes', 'Bryant', 'Herrera', 'Gibson',
    'Ellis', 'Tran', 'Medina', 'Aguilar', 'Stevens', 'Murray', 'Ford', 'Castro', 'Marshall', 'Owens'
]

DEPARTMENTS = [
    ('Computer Science', 'Department of Computer Science and Information Technology'),
    ('Mathematics', 'Department of Mathematics and Statistics'),
    ('Physics', 'Department of Physics and Astronomy'),
    ('Chemistry', 'Department of Chemistry and Biochemistry'),
    ('Biology', 'Department of Biology and Life Sciences'),
    ('English', 'Department of English Literature and Language'),
    ('History', 'Department of History and Political Science'),
    ('Psychology', 'Department of Psychology and Behavioral Sciences'),
    ('Business', 'School of Business Administration'),
    ('Engineering', 'School of Engineering and Technology'),
    ('Art', 'Department of Fine Arts and Design'),
    ('Music', 'Department of Music and Performing Arts'),
    ('Education', 'School of Education and Teaching'),
    ('Nursing', 'School of Nursing and Health Sciences'),
    ('Economics', 'Department of Economics and Finance'),
    ('Sociology', 'Department of Sociology and Anthropology'),
    ('Philosophy', 'Department of Philosophy and Ethics'),
    ('Languages', 'Department of Foreign Languages and Linguistics'),
    ('Communications', 'Department of Communications and Media'),
    ('Environmental Science', 'Department of Environmental Science and Sustainability')
]

COURSE_PREFIXES = {
    'Computer Science': ['CS', 'IT', 'CIS', 'SE'],
    'Mathematics': ['MATH', 'STAT', 'CALC'],
    'Physics': ['PHYS', 'ASTR'],
    'Chemistry': ['CHEM', 'BIOC'],
    'Biology': ['BIO', 'BIOL', 'MICRO'],
    'English': ['ENG', 'LIT', 'WRIT'],
    'History': ['HIST', 'POLI', 'GOVT'],
    'Psychology': ['PSYC', 'BEHAV'],
    'Business': ['BUS', 'MGT', 'MKT', 'FIN', 'ACCT'],
    'Engineering': ['ENG', 'MECH', 'CIVIL', 'ELEC'],
    'Art': ['ART', 'DESIGN', 'DRAW'],
    'Music': ['MUS', 'PERF'],
    'Education': ['EDU', 'TEACH'],
    'Nursing': ['NURS', 'HEALTH'],
    'Economics': ['ECON', 'FIN'],
    'Sociology': ['SOC', 'ANTH'],
    'Philosophy': ['PHIL', 'ETHICS'],
    'Languages': ['SPAN', 'FREN', 'GERM', 'LANG'],
    'Communications': ['COMM', 'MEDIA', 'JOURN'],
    'Environmental Science': ['ENV', 'SUST', 'ECOL']
}

COURSE_NAMES = {
    'Computer Science': [
        'Introduction to Programming', 'Data Structures', 'Algorithms', 'Database Systems',
        'Software Engineering', 'Web Development', 'Mobile App Development', 'Machine Learning',
        'Artificial Intelligence', 'Computer Networks', 'Operating Systems', 'Cybersecurity',
        'Data Science', 'Cloud Computing', 'Game Development', 'Computer Graphics',
        'Human-Computer Interaction', 'Information Systems', 'System Analysis', 'Project Management'
    ],
    'Mathematics': [
        'Calculus I', 'Calculus II', 'Linear Algebra', 'Discrete Mathematics',
        'Statistics', 'Probability', 'Differential Equations', 'Number Theory',
        'Abstract Algebra', 'Real Analysis', 'Complex Analysis', 'Topology',
        'Mathematical Modeling', 'Numerical Analysis', 'Geometry', 'Trigonometry',
        'Finite Mathematics', 'Applied Mathematics', 'Mathematical Logic', 'Optimization'
    ],
    'Physics': [
        'General Physics I', 'General Physics II', 'Modern Physics', 'Thermodynamics',
        'Quantum Mechanics', 'Electromagnetism', 'Optics', 'Mechanics',
        'Waves and Oscillations', 'Nuclear Physics', 'Astrophysics', 'Solid State Physics',
        'Fluid Mechanics', 'Statistical Mechanics', 'Relativity', 'Particle Physics',
        'Plasma Physics', 'Biophysics', 'Geophysics', 'Acoustics'
    ],
    'Chemistry': [
        'General Chemistry I', 'General Chemistry II', 'Organic Chemistry I', 'Organic Chemistry II',
        'Physical Chemistry', 'Biochemistry', 'Analytical Chemistry', 'Inorganic Chemistry',
        'Environmental Chemistry', 'Medicinal Chemistry', 'Polymer Chemistry', 'Electrochemistry',
        'Spectroscopy', 'Chromatography', 'Chemical Kinetics', 'Thermodynamics',
        'Quantum Chemistry', 'Materials Chemistry', 'Food Chemistry', 'Forensic Chemistry'
    ],
    'Biology': [
        'General Biology I', 'General Biology II', 'Cell Biology', 'Genetics',
        'Ecology', 'Evolution', 'Microbiology', 'Anatomy and Physiology',
        'Molecular Biology', 'Biotechnology', 'Marine Biology', 'Plant Biology',
        'Animal Behavior', 'Immunology', 'Neuroscience', 'Developmental Biology',
        'Conservation Biology', 'Bioinformatics', 'Pharmacology', 'Pathology'
    ],
    'English': [
        'Composition I', 'Composition II', 'British Literature', 'American Literature',
        'World Literature', 'Creative Writing', 'Technical Writing', 'Poetry',
        'Fiction Writing', 'Drama', 'Literary Criticism', 'Shakespeare',
        'Modern Literature', 'Contemporary Literature', 'Children\'s Literature',
        'Science Fiction', 'Mystery and Detective Fiction', 'Romance Literature',
        'Literary Theory', 'Rhetoric and Public Speaking'
    ],
    'History': [
        'World History I', 'World History II', 'American History I', 'American History II',
        'European History', 'Asian History', 'African History', 'Latin American History',
        'Ancient History', 'Medieval History', 'Renaissance History', 'Modern History',
        'Military History', 'Political History', 'Social History', 'Cultural History',
        'Economic History', 'Women\'s History', 'African American History', 'Historiography'
    ],
    'Psychology': [
        'General Psychology', 'Developmental Psychology', 'Social Psychology', 'Cognitive Psychology',
        'Abnormal Psychology', 'Personality Psychology', 'Educational Psychology', 'Clinical Psychology',
        'Behavioral Psychology', 'Experimental Psychology', 'Neuropsychology', 'Counseling Psychology',
        'Industrial Psychology', 'Health Psychology', 'Sports Psychology', 'Forensic Psychology',
        'Child Psychology', 'Adolescent Psychology', 'Adult Psychology', 'Psychology of Learning'
    ],
    'Business': [
        'Principles of Management', 'Marketing Principles', 'Financial Accounting', 'Managerial Accounting',
        'Business Law', 'Economics for Business', 'Operations Management', 'Human Resource Management',
        'Strategic Management', 'International Business', 'Entrepreneurship', 'Business Ethics',
        'Organizational Behavior', 'Project Management', 'Supply Chain Management', 'Business Statistics',
        'Corporate Finance', 'Investment Analysis', 'Business Communication', 'Leadership'
    ],
    'Engineering': [
        'Engineering Fundamentals', 'Statics', 'Dynamics', 'Thermodynamics',
        'Fluid Mechanics', 'Materials Science', 'Electrical Circuits', 'Digital Systems',
        'Engineering Design', 'Project Management', 'Engineering Ethics', 'Computer-Aided Design',
        'Control Systems', 'Signal Processing', 'Structural Analysis', 'Heat Transfer',
        'Manufacturing Processes', 'Quality Control', 'Engineering Economics', 'Professional Practice'
    ]
}

ASSIGNMENT_TYPES = ['homework', 'quiz', 'exam', 'project', 'participation']
GRADE_LETTERS = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F']
ATTENDANCE_STATUS = ['present', 'absent', 'late', 'excused']

def generate_realistic_date(start_year=2020, end_year=2024):
    """Generate a realistic date between start_year and end_year."""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

def generate_phone():
    """Generate a realistic phone number."""
    return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"

def generate_email(first_name, last_name, used_emails=None):
    """Generate a realistic email address."""
    if used_emails is None:
        used_emails = set()
    
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'university.edu']
    base_email = f"{first_name.lower()}.{last_name.lower()}"
    
    # Try base email first
    email = f"{base_email}@{random.choice(domains)}"
    counter = 1
    
    # If email exists, add numbers until unique
    while email in used_emails:
        email = f"{base_email}{counter}@{random.choice(domains)}"
        counter += 1
    
    used_emails.add(email)
    return email

def generate_student_id(used_ids=None):
    """Generate a realistic student ID."""
    if used_ids is None:
        used_ids = set()
    
    while True:
        student_id = f"STU{random.randint(100000, 999999)}"
        if student_id not in used_ids:
            used_ids.add(student_id)
            return student_id

def calculate_gpa(letter_grade):
    """Calculate GPA from letter grade."""
    gpa_map = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0, 'F': 0.0
    }
    return gpa_map.get(letter_grade, 0.0)

def enhance_database():
    """Enhance the database with 10x more realistic data."""
    print("🚀 Starting database enhancement...")
    print("📊 Adding 10x more realistic data...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Clear existing data
        print("🗑️ Clearing existing data...")
        cursor.execute("DELETE FROM grades")
        cursor.execute("DELETE FROM attendance")
        cursor.execute("DELETE FROM enrollments")
        cursor.execute("DELETE FROM courses")
        cursor.execute("DELETE FROM students")
        cursor.execute("DELETE FROM teachers")
        cursor.execute("DELETE FROM departments")
        cursor.execute("DELETE FROM semesters")
        
        # Reset auto-increment counters (if table exists)
        try:
            cursor.execute("DELETE FROM sqlite_sequence")
        except sqlite3.OperationalError:
            pass  # Table doesn't exist, which is fine
        
        # 1. Create Departments (20 departments)
        print("🏫 Creating departments...")
        for i, (name, description) in enumerate(DEPARTMENTS, 1):
            cursor.execute("""
                INSERT INTO departments (id, name, description, head_teacher_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (i, name, description, None, generate_realistic_date(2020, 2021)))
        
        # 2. Create Semesters (8 semesters)
        print("📅 Creating semesters...")
        semesters = [
            ('Fall 2020', '2020-08-15', '2020-12-15', 0),
            ('Spring 2021', '2021-01-15', '2021-05-15', 0),
            ('Fall 2021', '2021-08-15', '2021-12-15', 0),
            ('Spring 2022', '2022-01-15', '2022-05-15', 0),
            ('Fall 2022', '2022-08-15', '2022-12-15', 0),
            ('Spring 2023', '2023-01-15', '2023-05-15', 0),
            ('Fall 2023', '2023-08-15', '2023-12-15', 0),
            ('Spring 2024', '2024-01-15', '2024-05-15', 1)  # Current semester
        ]
        
        for i, (name, start_date, end_date, is_current) in enumerate(semesters, 1):
            cursor.execute("""
                INSERT INTO semesters (id, name, start_date, end_date, is_current)
                VALUES (?, ?, ?, ?, ?)
            """, (i, name, start_date, end_date, is_current))
        
        # 3. Create Teachers (200 teachers - 10 per department)
        print("👨‍🏫 Creating teachers...")
        teacher_id = 1
        used_emails = set()
        for dept_id in range(1, 21):  # 20 departments
            for _ in range(10):  # 10 teachers per department
                first_name = random.choice(FIRST_NAMES)
                last_name = random.choice(LAST_NAMES)
                email = generate_email(first_name, last_name, used_emails)
                phone = generate_phone()
                hire_date = generate_realistic_date(2015, 2023)
                salary = random.randint(45000, 120000)
                
                # Get department name for specialization
                dept_name = DEPARTMENTS[dept_id - 1][0]
                specializations = {
                    'Computer Science': ['Software Engineering', 'Data Science', 'Cybersecurity', 'AI/ML'],
                    'Mathematics': ['Statistics', 'Applied Math', 'Pure Math', 'Actuarial Science'],
                    'Physics': ['Theoretical Physics', 'Experimental Physics', 'Astrophysics', 'Quantum Physics'],
                    'Chemistry': ['Organic Chemistry', 'Inorganic Chemistry', 'Physical Chemistry', 'Biochemistry'],
                    'Biology': ['Molecular Biology', 'Ecology', 'Genetics', 'Marine Biology'],
                    'English': ['Creative Writing', 'Literature', 'Linguistics', 'Rhetoric'],
                    'History': ['American History', 'European History', 'World History', 'Political History'],
                    'Psychology': ['Clinical Psychology', 'Cognitive Psychology', 'Social Psychology', 'Developmental Psychology'],
                    'Business': ['Finance', 'Marketing', 'Management', 'Accounting'],
                    'Engineering': ['Mechanical', 'Electrical', 'Civil', 'Computer Engineering']
                }
                
                specialization = random.choice(specializations.get(dept_name, ['General']))
                
                cursor.execute("""
                    INSERT INTO teachers (id, first_name, last_name, email, phone, department_id, 
                                       hire_date, salary, specialization)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (teacher_id, first_name, last_name, email, phone, dept_id, 
                      hire_date, salary, specialization))
                teacher_id += 1
        
        # 4. Create Students (2000 students)
        print("👨‍🎓 Creating students...")
        student_id = 1
        used_student_ids = set()
        for _ in range(2000):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            email = generate_email(first_name, last_name, used_emails)
            phone = generate_phone()
            dob = generate_realistic_date(1995, 2006)  # Ages 18-29
            enrollment_date = generate_realistic_date(2020, 2024)
            student_id_str = generate_student_id(used_student_ids)
            
            # Generate realistic GPA
            gpa = round(random.uniform(2.0, 4.0), 2)
            
            # Student status
            statuses = ['active'] * 80 + ['graduated'] * 15 + ['inactive'] * 4 + ['suspended'] * 1
            status = random.choice(statuses)
            
            cursor.execute("""
                INSERT INTO students (id, first_name, last_name, email, phone, date_of_birth,
                                   enrollment_date, student_id, gpa, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (student_id, first_name, last_name, email, phone, dob, 
                  enrollment_date, student_id_str, gpa, status))
            student_id += 1
        
        # 5. Create Courses (400 courses - 20 per department)
        print("📚 Creating courses...")
        course_id = 1
        used_course_codes = set()
        for dept_id in range(1, 21):  # 20 departments
            dept_name = DEPARTMENTS[dept_id - 1][0]
            course_names = COURSE_NAMES.get(dept_name, ['General Course'])
            prefixes = COURSE_PREFIXES.get(dept_name, ['GEN'])
            
            for i in range(20):  # 20 courses per department
                # Generate unique course code
                while True:
                    course_code = f"{random.choice(prefixes)}{random.randint(100, 999)}"
                    if course_code not in used_course_codes:
                        used_course_codes.add(course_code)
                        break
                
                course_name = random.choice(course_names)
                description = f"Comprehensive study of {course_name.lower()}"
                credits = random.choice([3, 4])
                
                # Get a random teacher from this department
                cursor.execute("SELECT id FROM teachers WHERE department_id = ? ORDER BY RANDOM() LIMIT 1", (dept_id,))
                teacher_id = cursor.fetchone()[0]
                
                # Random semester
                semester_id = random.randint(1, 8)
                
                max_students = random.randint(15, 50)
                current_enrollment = random.randint(5, max_students)
                
                cursor.execute("""
                    INSERT INTO courses (id, course_code, course_name, description, credits,
                                       department_id, teacher_id, semester_id, max_students, current_enrollment)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (course_id, course_code, course_name, description, credits,
                      dept_id, teacher_id, semester_id, max_students, current_enrollment))
                course_id += 1
        
        # 6. Create Enrollments (8000 enrollments)
        print("📝 Creating enrollments...")
        enrollment_id = 1
        for _ in range(8000):
            student_id = random.randint(1, 2000)
            course_id = random.randint(1, 400)
            enrollment_date = generate_realistic_date(2020, 2024)
            
            # Enrollment status
            statuses = ['enrolled'] * 85 + ['completed'] * 10 + ['dropped'] * 4 + ['failed'] * 1
            status = random.choice(statuses)
            
            try:
                cursor.execute("""
                    INSERT INTO enrollments (id, student_id, course_id, enrollment_date, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (enrollment_id, student_id, course_id, enrollment_date, status))
                enrollment_id += 1
            except sqlite3.IntegrityError:
                # Skip duplicate enrollments
                continue
        
        # 7. Create Attendance Records (50000 records)
        print("📊 Creating attendance records...")
        attendance_id = 1
        for _ in range(50000):
            student_id = random.randint(1, 2000)
            course_id = random.randint(1, 400)
            date = generate_realistic_date(2020, 2024)
            
            # Attendance status with realistic distribution
            statuses = ['present'] * 85 + ['absent'] * 10 + ['late'] * 4 + ['excused'] * 1
            status = random.choice(statuses)
            
            notes = None
            if status == 'excused':
                notes = random.choice(['Medical appointment', 'Family emergency', 'Religious observance', 'School activity'])
            elif status == 'late':
                notes = f"Arrived {random.randint(5, 30)} minutes late"
            
            cursor.execute("""
                INSERT INTO attendance (id, student_id, course_id, date, status, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (attendance_id, student_id, course_id, date, status, notes))
            attendance_id += 1
        
        # 8. Create Grades (100000 records)
        print("📈 Creating grade records...")
        grade_id = 1
        assignment_names = [
            'Homework 1', 'Homework 2', 'Homework 3', 'Quiz 1', 'Quiz 2', 'Midterm Exam',
            'Final Exam', 'Project 1', 'Project 2', 'Lab Report 1', 'Lab Report 2',
            'Research Paper', 'Presentation', 'Participation', 'Extra Credit'
        ]
        
        for _ in range(100000):
            student_id = random.randint(1, 2000)
            course_id = random.randint(1, 400)
            assignment_name = random.choice(assignment_names)
            
            # Realistic grade distribution
            points_possible = random.choice([10, 20, 25, 50, 100])
            
            # Grade distribution: more A's and B's, fewer F's
            grade_weights = [0.15, 0.20, 0.25, 0.20, 0.20]  # A, B, C, D, F
            grade_ranges = [(90, 100), (80, 89), (70, 79), (60, 69), (0, 59)]
            
            grade_choice = random.choices(range(5), weights=grade_weights)[0]
            if grade_choice < 4:
                min_grade, max_grade = grade_ranges[grade_choice]
                grade_percentage = random.randint(min_grade, max_grade)
            else:
                grade_percentage = random.randint(0, 59)
            
            points_earned = int((grade_percentage / 100) * points_possible)
            
            # Convert percentage to letter grade
            if grade_percentage >= 97:
                letter_grade = 'A+'
            elif grade_percentage >= 93:
                letter_grade = 'A'
            elif grade_percentage >= 90:
                letter_grade = 'A-'
            elif grade_percentage >= 87:
                letter_grade = 'B+'
            elif grade_percentage >= 83:
                letter_grade = 'B'
            elif grade_percentage >= 80:
                letter_grade = 'B-'
            elif grade_percentage >= 77:
                letter_grade = 'C+'
            elif grade_percentage >= 73:
                letter_grade = 'C'
            elif grade_percentage >= 70:
                letter_grade = 'C-'
            elif grade_percentage >= 67:
                letter_grade = 'D+'
            elif grade_percentage >= 60:
                letter_grade = 'D'
            else:
                letter_grade = 'F'
            
            assignment_type = random.choice(ASSIGNMENT_TYPES)
            date_graded = generate_realistic_date(2020, 2024)
            
            cursor.execute("""
                INSERT INTO grades (id, student_id, course_id, assignment_name, points_earned,
                                  points_possible, grade_percentage, letter_grade, assignment_type, date_graded)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (grade_id, student_id, course_id, assignment_name, points_earned,
                  points_possible, grade_percentage, letter_grade, assignment_type, date_graded))
            grade_id += 1
        
        # Update department head teachers
        print("👑 Assigning department heads...")
        for dept_id in range(1, 21):
            cursor.execute("""
                SELECT id FROM teachers WHERE department_id = ? ORDER BY hire_date ASC LIMIT 1
            """, (dept_id,))
            head_teacher = cursor.fetchone()
            if head_teacher:
                cursor.execute("""
                    UPDATE departments SET head_teacher_id = ? WHERE id = ?
                """, (head_teacher[0], dept_id))
        
        conn.commit()
        
        # Print statistics
        print("\n📊 Database Enhancement Complete!")
        print("=" * 50)
        
        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        print(f"🏫 Departments: {dept_count}")
        
        cursor.execute("SELECT COUNT(*) FROM teachers")
        teacher_count = cursor.fetchone()[0]
        print(f"👨‍🏫 Teachers: {teacher_count}")
        
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        print(f"👨‍🎓 Students: {student_count}")
        
        cursor.execute("SELECT COUNT(*) FROM courses")
        course_count = cursor.fetchone()[0]
        print(f"📚 Courses: {course_count}")
        
        cursor.execute("SELECT COUNT(*) FROM enrollments")
        enrollment_count = cursor.fetchone()[0]
        print(f"📝 Enrollments: {enrollment_count}")
        
        cursor.execute("SELECT COUNT(*) FROM attendance")
        attendance_count = cursor.fetchone()[0]
        print(f"📊 Attendance Records: {attendance_count}")
        
        cursor.execute("SELECT COUNT(*) FROM grades")
        grade_count = cursor.fetchone()[0]
        print(f"📈 Grade Records: {grade_count}")
        
        print("=" * 50)
        print("✅ Database successfully enhanced with 10x more realistic data!")
        
    except Exception as e:
        print(f"❌ Error enhancing database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    enhance_database()
