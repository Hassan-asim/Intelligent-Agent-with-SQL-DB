#!/usr/bin/env python3
"""
Test script for Material Design School Management Chat Agent

This script tests the core functionality of the Material Design agent
without requiring the full GUI interface.
"""

import os
import sys
import pathlib
import sqlite3
from dotenv import load_dotenv

# Add current directory to path
SCRIPT_DIR = pathlib.Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

def test_database_connection():
    """Test database connectivity and data availability."""
    print("🔍 Testing database connection...")
    
    db_path = SCRIPT_DIR / "school_management.db"
    if not db_path.exists():
        print("❌ Database not found. Please run setup_school_database.py first.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test basic connectivity
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✅ Database connected. Found {len(tables)} tables: {[t[0] for t in tables]}")
        
        # Test data availability
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        print(f"✅ Students table has {student_count} records")
        
        cursor.execute("SELECT COUNT(*) FROM courses")
        course_count = cursor.fetchone()[0]
        print(f"✅ Courses table has {course_count} records")
        
        cursor.execute("SELECT COUNT(*) FROM attendance")
        attendance_count = cursor.fetchone()[0]
        print(f"✅ Attendance table has {attendance_count} records")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_environment_setup():
    """Test environment variables and dependencies."""
    print("\n🔍 Testing environment setup...")
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please create a .env file with your Gemini API key")
        return False
    else:
        print("✅ Gemini API key found")
    
    # Check required packages
    required_packages = [
        'tkinter', 'pandas', 'matplotlib', 'seaborn', 
        'google.generativeai', 'sqlalchemy', 'pydantic', 
        'langchain', 'dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        return False
    else:
        print("✅ All required packages available")
    
    return True

def test_sql_tool():
    """Test the secure SQL tool functionality."""
    print("\n🔍 Testing SQL tool...")
    
    try:
        from material_school_agent import SecureSchoolSQLTool
        
        tool = SecureSchoolSQLTool()
        
        # Test valid query
        result = tool._run("SELECT COUNT(*) as student_count FROM students")
        if isinstance(result, dict) and 'columns' in result:
            print("✅ Valid SQL query executed successfully")
            print(f"   Result: {result['rows'][0][0]} students")
        else:
            print(f"❌ SQL query failed: {result}")
            return False
        
        # Test invalid query (should be blocked)
        result = tool._run("DELETE FROM students")
        if "ERROR" in str(result):
            print("✅ Invalid query properly blocked")
        else:
            print("❌ Security validation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ SQL tool error: {e}")
        return False

def test_chart_generation():
    """Test chart generation functionality."""
    print("\n🔍 Testing chart generation...")
    
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        
        # Create sample data
        data = {
            'Course': ['Math', 'Science', 'English', 'History'],
            'Students': [25, 30, 28, 22]
        }
        df = pd.DataFrame(data)
        
        # Test basic chart creation
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(df['Course'], df['Students'])
        ax.set_title('Test Chart')
        
        print("✅ Chart generation test passed")
        plt.close(fig)
        return True
        
    except Exception as e:
        print(f"❌ Chart generation error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Material Design School Management Agent - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Environment Setup", test_environment_setup),
        ("SQL Tool", test_sql_tool),
        ("Chart Generation", test_chart_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test passed")
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\n🚀 To start the application, run:")
        print("   python material_school_agent.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues before running the application.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
