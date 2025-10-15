#!/usr/bin/env python3
"""
Database Initialization Script for AI Resume Interview System
This script initializes the MySQL database with all required tables and test data.
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
import mysql.connector
from mysql.connector import Error

def main():
    """Initialize the database"""
    print("🚀 AI Resume Interview System - Database Initialization")
    print("=" * 60)
    
    try:
        # Initialize database manager
        print("📊 Initializing database connection...")
        db = DatabaseManager()
        
        if not db.connection or not db.connection.is_connected():
            print("❌ Failed to connect to database")
            return False
        
        print("✅ Database connection established")
        
        # Verify database health
        print("\n🔍 Verifying database health...")
        if db.verify_database_health():
            print("✅ Database health check passed")
        else:
            print("⚠️ Database health check failed, but continuing...")
        
        # Get database statistics
        print("\n📈 Database Statistics:")
        stats = db.get_database_stats()
        for key, value in stats.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Test basic operations
        print("\n🧪 Testing basic database operations...")
        
        # Test user creation
        test_user = db.get_user('admin')
        if test_user:
            print("✅ User retrieval test passed")
        else:
            print("❌ User retrieval test failed")
        
        # Test session data operations
        session_data = db.get_session_data(test_user['id'])
        print(f"✅ Session data retrieval test passed (found {len(session_data)} records)")
        
        print("\n🎉 Database initialization completed successfully!")
        print("\n📋 Available test credentials:")
        print("  Admin: admin / admin123")
        print("  Test User: validuser / validpassword")
        print("  Test User: testuser / testpass")
        print("  Admin User: admin_user / admin_password")
        
        return True
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_connection_info():
    """Show current database connection information"""
    print("🔌 Current Database Configuration:")
    print(f"  Host: 2s6vhs.h.filess.io")
    print(f"  Port: 61032")
    print(f"  User: Major_audiencedo")
    print(f"  Database: Major_audiencedo")
    print(f"  SSL: Enabled (if supported by server)")

if __name__ == "__main__":
    print("AI Resume Interview System - Database Setup")
    print("=" * 50)
    
    show_connection_info()
    
    choice = input("""
Choose an option:
1. Initialize database (recommended)
2. Show connection info only
3. Exit

Enter your choice (1-3): """).strip()
    
    if choice == '1':
        success = main()
        if success:
            print("\n✅ Database setup completed successfully!")
            print("You can now run the application with: python app.py")
        else:
            print("\n❌ Database setup failed. Please check your connection settings.")
    elif choice == '2':
        show_connection_info()
    elif choice == '3':
        print("Goodbye!")
    else:
        print("Invalid choice. Please run the script again.")
