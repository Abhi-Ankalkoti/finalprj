#!/usr/bin/env python3
"""
Script to create test users for TestSprite testing
"""

from database import DatabaseManager
from werkzeug.security import generate_password_hash
import os

def create_test_users():
    """Create test users for automated testing"""
    db = DatabaseManager()
    
    # Test users that match what TestSprite expects
    test_users = [
        {
            'username': 'valid_user',
            'password': 'valid_password',
            'role': 'user'
        },
        {
            'username': 'admin_user',
            'password': 'admin_password',
            'role': 'admin'
        },
        {
            'username': 'testuser',
            'password': 'testpass',
            'role': 'user'
        }
    ]
    
    print("Creating test users...")
    
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
    
    print("\nTest users created successfully!")
    print("\nAvailable test credentials:")
    print("Regular user: valid_user / valid_password")
    print("Admin user: admin_user / admin_password")
    print("Test user: testuser / testpass")

if __name__ == "__main__":
    create_test_users()
