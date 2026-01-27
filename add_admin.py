#!/usr/bin/env python3
"""
Add First Admin Script
Run this BEFORE importing Excel if you need an admin account to login
"""

import sqlite3
import hashlib
import sys

def add_admin():
    print("\n" + "="*60)
    print("🎓 Add First Admin to Membership System")
    print("="*60 + "\n")
    
    # Get admin details
    print("Enter admin details:")
    email = input("Email address: ").strip().lower()
    
    if not email or '@' not in email:
        print("❌ Invalid email address")
        return
    
    first_name = input("First name: ").strip()
    surname = input("Surname: ").strip()
    member_number = input("Member number (e.g., M0001): ").strip() or "M0001"
    
    # Password is email by default
    password = email
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Connect to database
    try:
        conn = sqlite3.connect('membership.db')
        cursor = conn.cursor()
        
        # Check if member already exists
        cursor.execute('SELECT email FROM members WHERE email = ?', (email,))
        if cursor.fetchone():
            print(f"\n⚠️  Member with email {email} already exists!")
            update = input("Update to admin? (yes/no): ").lower()
            if update == 'yes':
                cursor.execute('UPDATE members SET is_admin = 1 WHERE email = ?', (email,))
                conn.commit()
                print(f"✅ Updated {email} to admin")
            conn.close()
            return
        
        # Insert new admin
        cursor.execute('''
            INSERT INTO members 
            (member_number, first_name, surname, email, phone, password_hash, 
             membership_type, expiry_date, status, photo_url, is_admin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (
            member_number,
            first_name,
            surname,
            email,
            '',
            password_hash,
            'Solo',
            '2027-12-31',
            'active',
            f'https://ui-avatars.com/api/?name={first_name}+{surname}&background=059669&color=fff'
        ))
        
        conn.commit()
        conn.close()
        
        print("\n✅ Admin created successfully!")
        print("\n" + "="*60)
        print("Login Credentials:")
        print("="*60)
        print(f"Email:    {email}")
        print(f"Password: {email}")
        print("="*60)
        print("\nYou can now:")
        print("1. Start the server: python server.py")
        print("2. Open http://localhost:5000")
        print("3. Login with the credentials above")
        print("4. Import your Excel file")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. You're in the correct directory")
        print("2. The server has been run at least once (to create database)")
        print("3. The server is NOT currently running")

if __name__ == '__main__':
    add_admin()
