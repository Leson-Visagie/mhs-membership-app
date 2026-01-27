#!/usr/bin/env python3
"""
System Verification Script
Run this to check if everything is set up correctly
"""

import os
import sys

def check_file(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✅ {description}: {filepath} ({size:,} bytes)")
        return True
    else:
        print(f"❌ MISSING: {description}: {filepath}")
        return False

def main():
    print("\n" + "="*60)
    print("🎓 Middies Klub System Verification")
    print("="*60 + "\n")
    
    all_good = True
    
    # Check Python version
    print("Python Version:")
    version = sys.version.split()[0]
    print(f"  Current: {version}")
    major, minor = sys.version_info[:2]
    if major >= 3 and minor >= 7:
        print("  ✅ Python 3.7+ (Good!)")
    else:
        print("  ❌ Need Python 3.7 or higher")
        all_good = False
    print()
    
    # Check required files
    print("Required Files:")
    files_to_check = [
        ("server.py", "Backend server"),
        ("static/index.html", "Frontend interface"),
        ("add_admin.py", "Admin setup script"),
        ("requirements.txt", "Dependencies"),
        ("README.md", "Documentation"),
        ("START_HERE.txt", "Quick start guide")
    ]
    
    for filepath, description in files_to_check:
        if not check_file(filepath, description):
            all_good = False
    
    print()
    
    # Check if dependencies are installed
    print("Dependencies:")
    try:
        import flask
        print(f"  ✅ Flask installed (version {flask.__version__})")
    except ImportError:
        print("  ❌ Flask not installed")
        print("     Run: pip install -r requirements.txt")
        all_good = False
    
    try:
        import flask_cors
        print("  ✅ flask-cors installed")
    except ImportError:
        print("  ❌ flask-cors not installed")
        print("     Run: pip install -r requirements.txt")
        all_good = False
    
    print()
    
    # Check database
    if os.path.exists('membership.db'):
        size = os.path.getsize('membership.db')
        print(f"Database:")
        print(f"  ✅ Database exists: membership.db ({size:,} bytes)")
        
        # Try to check if it has tables
        try:
            import sqlite3
            conn = sqlite3.connect('membership.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            if tables:
                print(f"  ✅ Tables found: {', '.join([t[0] for t in tables])}")
            else:
                print("  ⚠️  Database exists but has no tables")
                print("     Run: python server.py (to initialize)")
        except Exception as e:
            print(f"  ⚠️  Could not check database: {e}")
    else:
        print("Database:")
        print("  ℹ️  Database not created yet")
        print("     This is normal for first-time setup")
        print("     Run: python server.py (to create)")
    
    print()
    
    # Final verdict
    print("="*60)
    if all_good:
        print("✅ VERIFICATION PASSED!")
        print("="*60)
        print("\nNext steps:")
        print("1. Run: python server.py")
        print("2. Open new terminal and run: python add_admin.py")
        print("3. Open browser: http://localhost:5000")
        print("4. Login and import Excel file")
    else:
        print("❌ VERIFICATION FAILED!")
        print("="*60)
        print("\nPlease fix the issues above before continuing.")
        print("See README.md or START_HERE.txt for help.")
    
    print("\n")

if __name__ == '__main__':
    main()
