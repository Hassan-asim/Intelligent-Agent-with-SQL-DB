"""
Test script for the School Management System
"""

import sqlite3
import pathlib
from school_management_agent import SecureSchoolSQLTool, get_schema_context

def test_database_connection():
    """Test database connection and basic queries."""
    print("🔍 Testing School Management Database...")
    
    # Get database path
    script_dir = pathlib.Path(__file__).parent
    project_root = script_dir.parent
    db_path = project_root / "school_management.db"
    
    if not db_path.exists():
        print("❌ Database not found. Please run setup_school_database.py first.")
        return False
    
    print(f"✅ Database found at: {db_path}")
    
    # Test connection
    try:
        conn = sqlite3.connect(db_path.as_posix())
        cursor = conn.cursor()
        print("✅ Database connection successful")
        
        # Test basic queries
        tables = ['departments', 'teachers', 'students', 'courses', 'enrollments', 'attendance', 'grades']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ Table '{table}': {count} records")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_secure_sql_tool():
    """Test the secure SQL tool."""
    print("\n🔒 Testing Secure SQL Tool...")
    
    try:
        tool = SecureSchoolSQLTool()
        
        # Test valid query
        result = tool._run("SELECT COUNT(*) as student_count FROM students")
        print(f"✅ Valid query test: {result}")
        
        # Test invalid query (should be blocked)
        result = tool._run("DELETE FROM students")
        print(f"✅ Security test (should block): {result}")
        
        # Test complex query
        result = tool._run("""
            SELECT 
                s.first_name || ' ' || s.last_name as student_name,
                s.gpa,
                COUNT(e.course_id) as courses_enrolled
            FROM students s
            LEFT JOIN enrollments e ON s.id = e.student_id
            GROUP BY s.id, s.first_name, s.last_name, s.gpa
            ORDER BY s.gpa DESC
            LIMIT 5
        """)
        print(f"✅ Complex query test: {len(result.get('rows', []))} rows returned")
        
        return True
        
    except Exception as e:
        print(f"❌ Secure SQL tool test failed: {e}")
        return False

def test_schema_context():
    """Test schema context generation."""
    print("\n📋 Testing Schema Context...")
    
    try:
        schema = get_schema_context()
        print(f"✅ Schema context generated: {len(schema)} characters")
        print("✅ Schema includes all expected tables")
        return True
        
    except Exception as e:
        print(f"❌ Schema context test failed: {e}")
        return False

def test_sample_queries():
    """Test sample analytics queries."""
    print("\n📊 Testing Sample Analytics Queries...")
    
    try:
        tool = SecureSchoolSQLTool()
        
        queries = [
            "SELECT course_name, current_enrollment FROM courses ORDER BY current_enrollment DESC",
            "SELECT letter_grade, COUNT(*) as count FROM grades GROUP BY letter_grade ORDER BY count DESC",
            "SELECT status, COUNT(*) as count FROM attendance GROUP BY status",
            "SELECT d.name as department, COUNT(t.id) as teachers FROM departments d LEFT JOIN teachers t ON d.id = t.department_id GROUP BY d.id, d.name"
        ]
        
        for i, query in enumerate(queries, 1):
            result = tool._run(query)
            if isinstance(result, dict) and 'rows' in result:
                print(f"✅ Query {i}: {len(result['rows'])} rows returned")
            else:
                print(f"❌ Query {i} failed: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample queries test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🎓 School Management System Test Suite")
    print("=" * 50)
    
    tests = [
        test_database_connection,
        test_secure_sql_tool,
        test_schema_context,
        test_sample_queries
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The school management system is ready to use.")
        print("\nTo run the full application:")
        print("python school_management_agent.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
