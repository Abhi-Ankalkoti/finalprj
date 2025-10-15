#!/usr/bin/env python3
"""
Script to create test users that match exactly what TestSprite tests expect
"""

from database import DatabaseManager
from werkzeug.security import generate_password_hash
import os

def create_correct_test_users():
    """Create test users that match TestSprite test expectations exactly"""
    db = DatabaseManager()
    
    # Test users that match exactly what TestSprite tests expect
    test_users = [
        {
            'username': 'validuser',
            'password': 'validpassword',
            'role': 'user'
        },
        {
            'username': 'admin',
            'password': 'admin_password',
            'role': 'admin'
        },
        {
            'username': 'testuser',
            'password': 'testpassword',
            'role': 'user'
        },
        {
            'username': 'normaluser',
            'password': 'user_password',
            'role': 'user'
        }
    ]
    
    print("Creating correct test users that match TestSprite expectations...")
    
    for user_data in test_users:
        username = user_data['username']
        password = user_data['password']
        role = user_data['role']
        
        # Check if user already exists
        existing_user = db.get_user(username)
        if existing_user:
            print(f"User '{username}' already exists, skipping...")
            continue
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        try:
            # Create user
            cursor = db.connection.cursor()
            insert_query = """
            INSERT INTO users (username, password_hash, role) 
            VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (username, password_hash, role))
            db.connection.commit()
            cursor.close()
            
            print(f"✅ Created user: {username} (role: {role})")
            
        except Exception as e:
            print(f"❌ Error creating user {username}: {e}")
    
    print("\nCorrect test users created successfully!")
    print("\nTestSprite test credentials:")
    print("TC001: validuser / validpassword")
    print("TC008: testuser / testpassword")
    print("TC010: admin / admin_password")
    print("TC010: normaluser / user_password")

if __name__ == "__main__":
    create_correct_test_users()
