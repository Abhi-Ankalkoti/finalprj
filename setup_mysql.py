#!/usr/bin/env python3
"""
MySQL Setup Script for AI Resume Interview System
This script helps you set up the MySQL database and configure the connection.
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

def setup_mysql():
    """Setup MySQL database and tables"""
    print("🚀 Setting up MySQL for AI Resume Interview System")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get database configuration
    host = input("Enter MySQL host (default: localhost): ").strip() or 'localhost'
    user = input("Enter MySQL username (default: root): ").strip() or 'root'
    password = input("Enter MySQL password (press Enter if none): ").strip()
    database = input("Enter database name (default: ai_interview_system): ").strip() or 'ai_interview_system'
    port = input("Enter MySQL port (default: 3306): ").strip() or '3306'
    
    try:
        # Test connection to MySQL server
        print(f"\n🔌 Testing connection to MySQL server at {host}:{port}...")
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=int(port)
        )
        
        if connection.is_connected():
            print("✅ Successfully connected to MySQL server")
            
            # Create database
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            print(f"✅ Database '{database}' created/verified")
            
            # Use the database
            cursor.execute(f"USE {database}")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role ENUM('admin', 'user') DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Users table created")
            
            # Create session_data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    resume_filename VARCHAR(255),
                    interview_score INT DEFAULT 0,
                    ats_score INT,
                    ats_feedback TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            print("✅ Session data table created")
            
            # Insert default admin user
            from werkzeug.security import generate_password_hash
            admin_password_hash = generate_password_hash('admin123')
            cursor.execute("""
                INSERT IGNORE INTO users (username, password_hash, role) 
                VALUES ('admin', %s, 'admin')
            """, (admin_password_hash,))
            print("✅ Default admin user created (username: admin, password: admin123)")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            # Update .env file
            update_env_file(host, user, password, database, port)
            
            print("\n🎉 MySQL setup completed successfully!")
            print("You can now run your application with: python app.py")
            
        else:
            print("❌ Failed to connect to MySQL server")
            
    except Error as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure MySQL server is running")
        print("2. Check your MySQL credentials")
        print("3. Ensure MySQL is installed and accessible")
        print("4. Try connecting with a MySQL client first")

def update_env_file(host, user, password, database, port):
    """Update .env file with MySQL configuration"""
    env_content = f"""COHERE_API_KEY=YLfFHkiQPgtObzCBfQEzYMAmw0eRVVxneIqsfZbU

# MySQL Database Configuration
DB_HOST={host}
DB_USER={user}
DB_PASSWORD={password}
DB_NAME={database}
DB_PORT={port}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file updated with MySQL configuration")

def test_connection():
    """Test the database connection"""
    print("\n🧪 Testing database connection...")
    
    try:
        from database import db
        if db.connection and db.connection.is_connected():
            print("✅ Database connection test successful!")
            return True
        else:
            print("❌ Database connection test failed!")
            return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

if __name__ == "__main__":
    print("AI Resume Interview System - MySQL Setup")
    print("=" * 40)
    
    choice = input("""
Choose an option:
1. Setup MySQL database (recommended for first time)
2. Test existing connection
3. Exit

Enter your choice (1-3): """).strip()
    
    if choice == '1':
        setup_mysql()
    elif choice == '2':
        test_connection()
    elif choice == '3':
        print("Goodbye!")
    else:
        print("Invalid choice. Please run the script again.")

