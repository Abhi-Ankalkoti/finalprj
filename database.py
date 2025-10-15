import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host='2s6vhs.h.filess.io',
                user='Major_audiencedo',
                password='b2ff8916bde72e33589ca325f0b8b32e5acbb7ce',
                database='Major_audiencedo',
                port=61032
            )
            print("✅ Successfully connected to MySQL database")
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            # Create database if it doesn't exist
            self.create_database()
    
    def create_database(self):
        """Create database if it doesn't exist"""
        try:
            connection = mysql.connector.connect(
                host='2s6vhs.h.filess.io',
                user='Major_audiencedo',
                password='b2ff8916bde72e33589ca325f0b8b32e5acbb7ce',
                port=61032
            )
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS Major_audiencedo")
            print("✅ Database 'Major_audiencedo' created successfully")
            cursor.close()
            connection.close()
            self.connect()
        except Error as e:
            print(f"❌ Error creating database: {e}")
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role ENUM('admin', 'user') DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    full_name VARCHAR(100),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    preferred_job_role VARCHAR(100),
                    experience_level ENUM('Entry', 'Mid', 'Senior', 'Lead') DEFAULT 'Entry',
                    skills TEXT,
                    resume_text LONGTEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Session data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    resume_filename VARCHAR(255),
                    resume_text LONGTEXT,
                    job_role VARCHAR(100),
                    interview_score INT DEFAULT 0,
                    ats_score INT,
                    ats_feedback TEXT,
                    skill_gaps TEXT,
                    recommendations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_data_user_id ON session_data(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_data_resume_filename ON session_data(resume_filename)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id)")
            print("✅ Database indexes created")
            
            # Insert default admin user if not exists
            from werkzeug.security import generate_password_hash
            admin_password_hash = generate_password_hash('admin123')
            cursor.execute("""
                INSERT IGNORE INTO users (username, password_hash, role) 
                VALUES ('admin', %s, 'admin')
            """, (admin_password_hash,))
            
            # Insert test users for TestSprite testing
            test_users = [
                ('validuser', 'validpassword', 'user'),
                ('valid_user', 'valid_password', 'user'),
                ('admin_user', 'admin_password', 'admin'),
                ('testuser', 'testpass', 'user'),
                ('testuser_atss', 'testpass123', 'user')
            ]
            
            for username, password, role in test_users:
                password_hash = generate_password_hash(password)
                cursor.execute("""
                    INSERT IGNORE INTO users (username, password_hash, role) 
                    VALUES (%s, %s, %s)
                """, (username, password_hash, role))
            
            print("✅ Test users created for testing")
            
            self.connection.commit()
            cursor.close()
            print("✅ Database tables created successfully")
            
            # Run database migrations
            self.run_migrations()
            
        except Error as e:
            print(f"❌ Error creating tables: {e}")
    
    def run_migrations(self):
        """Run database migrations to update schema if needed"""
        try:
            cursor = self.connection.cursor()
            
            # Migration 1: Add any missing columns to session_data table
            try:
                cursor.execute("ALTER TABLE session_data ADD COLUMN resume_text LONGTEXT")
                print("✅ Added resume_text column to session_data")
            except:
                pass  # Column already exists
            
            try:
                cursor.execute("ALTER TABLE session_data ADD COLUMN job_role VARCHAR(100)")
                print("✅ Added job_role column to session_data")
            except:
                pass  # Column already exists
            
            try:
                cursor.execute("ALTER TABLE session_data ADD COLUMN skill_gaps TEXT")
                print("✅ Added skill_gaps column to session_data")
            except:
                pass  # Column already exists
            
            try:
                cursor.execute("ALTER TABLE session_data ADD COLUMN recommendations TEXT")
                print("✅ Added recommendations column to session_data")
            except:
                pass  # Column already exists
            
            # Migration 2: Update interview_score default and constraints
            try:
                cursor.execute("ALTER TABLE session_data MODIFY COLUMN interview_score INT DEFAULT 0")
                print("✅ Updated interview_score default value")
            except:
                pass
            
            # Migration 3: Add additional indexes if needed
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_data_ats_score ON session_data(ats_score)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_data_interview_score ON session_data(interview_score)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_data_created_at ON session_data(created_at)")
                print("✅ Added additional performance indexes")
            except:
                pass
            
            self.connection.commit()
            cursor.close()
            print("✅ Database migrations completed successfully")
            
        except Error as e:
            print(f"❌ Error running migrations: {e}")
    
    def get_user(self, username):
        """Get user by username"""
        try:
            # Check if connection is still valid, reconnect if needed
            if not self.is_connection_valid():
                self.reconnect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Error getting user: {e}")
            return None
    
    def create_user(self, username, password_hash, role='user'):
        """Create a new user"""
        try:
            # Check if connection is still valid, reconnect if needed
            if not self.is_connection_valid():
                self.reconnect()
            
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, password_hash, role)
            )
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error creating user: {e}")
            return False
    
    def get_session_data(self, user_id):
        """Get session data for a user"""
        try:
            # Check if connection is still valid, reconnect if needed
            if not self.is_connection_valid():
                self.reconnect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM session_data 
                WHERE user_id = %s 
                ORDER BY updated_at DESC
            """, (user_id,))
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Error getting session data: {e}")
            return []
    
    def update_or_create_session_data(self, user_id, resume_filename, interview_score=None, ats_score=None, ats_feedback=None):
        """Update or create session data for a user"""
        try:
            # Check if connection is still valid, reconnect if needed
            if not self.is_connection_valid():
                self.reconnect()
            
            cursor = self.connection.cursor()
            
            # Check if record exists
            cursor.execute("""
                SELECT id FROM session_data 
                WHERE user_id = %s AND resume_filename = %s
            """, (user_id, resume_filename))
            
            existing_record = cursor.fetchone()
            
            if existing_record:
                # Update existing record
                update_fields = []
                values = []
                
                if interview_score is not None:
                    update_fields.append("interview_score = %s")
                    values.append(interview_score)
                
                if ats_score is not None:
                    update_fields.append("ats_score = %s")
                    values.append(ats_score)
                
                if ats_feedback is not None:
                    update_fields.append("ats_feedback = %s")
                    values.append(ats_feedback)
                
                if update_fields:
                    values.extend([user_id, resume_filename])
                    cursor.execute(f"""
                        UPDATE session_data 
                        SET {', '.join(update_fields)}
                        WHERE user_id = %s AND resume_filename = %s
                    """, values)
            else:
                # Create new record
                cursor.execute("""
                    INSERT INTO session_data (user_id, resume_filename, interview_score, ats_score, ats_feedback)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, resume_filename, interview_score or 0, ats_score, ats_feedback))
            
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error updating session data: {e}")
            return False
    
    def get_all_session_data(self):
        """Get all session data for admin dashboard"""
        try:
            # Check if connection is still valid, reconnect if needed
            if not self.is_connection_valid():
                self.reconnect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.username, sd.resume_filename, sd.job_role, sd.interview_score, 
                       sd.ats_score, sd.ats_feedback, sd.skill_gaps, sd.recommendations
                FROM session_data sd
                JOIN users u ON sd.user_id = u.id
                ORDER BY sd.ats_score DESC, sd.updated_at DESC
            """)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Error getting all session data: {e}")
            return []
    
    def get_all_session_data_with_profiles(self):
        """Get all session data with user profile information for admin dashboard"""
        try:
            # Check if connection is still valid, reconnect if needed
            if not self.is_connection_valid():
                self.reconnect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.username, 
                       sd.resume_filename, sd.job_role, sd.interview_score, 
                       sd.ats_score, sd.ats_feedback, sd.skill_gaps, sd.recommendations,
                       up.full_name, up.email, up.phone, up.preferred_job_role,
                       up.experience_level, up.skills, up.resume_text
                FROM session_data sd
                JOIN users u ON sd.user_id = u.id
                LEFT JOIN user_profiles up ON u.id = up.user_id
                ORDER BY sd.ats_score DESC, sd.updated_at DESC
            """)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Error getting all session data with profiles: {e}")
            return []
    
    def create_or_update_user_profile(self, user_id, full_name=None, email=None, phone=None, 
                                    preferred_job_role=None, experience_level=None, skills=None, resume_text=None):
        """Create or update user profile"""
        try:
            if not self.is_connection_valid():
                self.reconnect()
            
            cursor = self.connection.cursor()
            
            # Check if profile exists
            cursor.execute("SELECT id FROM user_profiles WHERE user_id = %s", (user_id,))
            existing_profile = cursor.fetchone()
            
            if existing_profile:
                # Update existing profile
                update_fields = []
                values = []
                
                if full_name is not None:
                    update_fields.append("full_name = %s")
                    values.append(full_name)
                if email is not None:
                    update_fields.append("email = %s")
                    values.append(email)
                if phone is not None:
                    update_fields.append("phone = %s")
                    values.append(phone)
                if preferred_job_role is not None:
                    update_fields.append("preferred_job_role = %s")
                    values.append(preferred_job_role)
                if experience_level is not None:
                    update_fields.append("experience_level = %s")
                    values.append(experience_level)
                if skills is not None:
                    update_fields.append("skills = %s")
                    values.append(skills)
                if resume_text is not None:
                    update_fields.append("resume_text = %s")
                    values.append(resume_text)
                
                if update_fields:
                    values.append(user_id)
                    cursor.execute(f"""
                        UPDATE user_profiles 
                        SET {', '.join(update_fields)}
                        WHERE user_id = %s
                    """, values)
            else:
                # Create new profile
                cursor.execute("""
                    INSERT INTO user_profiles (user_id, full_name, email, phone, preferred_job_role, 
                                             experience_level, skills, resume_text)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, full_name, email, phone, preferred_job_role, experience_level, skills, resume_text))
            
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error creating/updating user profile: {e}")
            return False
    
    def get_user_profile(self, user_id):
        """Get user profile by user_id"""
        try:
            if not self.is_connection_valid():
                self.reconnect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Error getting user profile: {e}")
            return None
    
    def update_session_data_with_analysis(self, user_id, resume_filename, resume_text, job_role, 
                                        interview_score=None, ats_score=None, ats_feedback=None,
                                        skill_gaps=None, recommendations=None):
        """Update session data with comprehensive analysis"""
        try:
            if not self.is_connection_valid():
                self.reconnect()
            
            cursor = self.connection.cursor()
            
            # Check if record exists
            cursor.execute("""
                SELECT id FROM session_data 
                WHERE user_id = %s AND resume_filename = %s
            """, (user_id, resume_filename))
            
            existing_record = cursor.fetchone()
            
            if existing_record:
                # Update existing record
                update_fields = []
                values = []
                
                if resume_text is not None:
                    update_fields.append("resume_text = %s")
                    values.append(resume_text)
                if job_role is not None:
                    update_fields.append("job_role = %s")
                    values.append(job_role)
                if interview_score is not None:
                    update_fields.append("interview_score = %s")
                    values.append(interview_score)
                if ats_score is not None:
                    update_fields.append("ats_score = %s")
                    values.append(ats_score)
                if ats_feedback is not None:
                    update_fields.append("ats_feedback = %s")
                    values.append(ats_feedback)
                if skill_gaps is not None:
                    update_fields.append("skill_gaps = %s")
                    values.append(skill_gaps)
                if recommendations is not None:
                    update_fields.append("recommendations = %s")
                    values.append(recommendations)
                
                if update_fields:
                    values.extend([user_id, resume_filename])
                    cursor.execute(f"""
                        UPDATE session_data 
                        SET {', '.join(update_fields)}
                        WHERE user_id = %s AND resume_filename = %s
                    """, values)
            else:
                # Create new record
                cursor.execute("""
                    INSERT INTO session_data (user_id, resume_filename, resume_text, job_role, 
                                            interview_score, ats_score, ats_feedback, skill_gaps, recommendations)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, resume_filename, resume_text, job_role, 
                     interview_score or 0, ats_score, ats_feedback, skill_gaps, recommendations))
            
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error updating session data with analysis: {e}")
            return False
    
    def is_connection_valid(self):
        """Check if the database connection is still valid"""
        try:
            if self.connection is None:
                return False
            if not self.connection.is_connected():
                return False
            # Test the connection with a simple query
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except:
            return False
    
    def reconnect(self):
        """Reconnect to the database"""
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
            self.connect()
            print("✅ Database reconnected successfully")
        except Error as e:
            print(f"❌ Error reconnecting to database: {e}")
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Database connection closed")
    
    def verify_database_health(self):
        """Verify database health and return status"""
        try:
            cursor = self.connection.cursor()
            
            # Check if all required tables exist
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            required_tables = ['users', 'user_profiles', 'session_data']
            
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"⚠️ Missing tables: {missing_tables}")
                return False
            
            # Check table structures
            for table in required_tables:
                cursor.execute(f"DESCRIBE {table}")
                columns = [row[0] for row in cursor.fetchall()]
                print(f"✅ Table '{table}' has {len(columns)} columns")
            
            # Check if test users exist
            cursor.execute("SELECT COUNT(*) FROM users WHERE username IN ('validuser', 'admin', 'testuser')")
            test_user_count = cursor.fetchone()[0]
            print(f"✅ Found {test_user_count} test users")
            
            cursor.close()
            print("✅ Database health check passed")
            return True
            
        except Error as e:
            print(f"❌ Database health check failed: {e}")
            return False
    
    def get_database_stats(self):
        """Get database statistics"""
        try:
            cursor = self.connection.cursor()
            
            stats = {}
            
            # Count users
            cursor.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = cursor.fetchone()[0]
            
            # Count user profiles
            cursor.execute("SELECT COUNT(*) FROM user_profiles")
            stats['total_profiles'] = cursor.fetchone()[0]
            
            # Count session data
            cursor.execute("SELECT COUNT(*) FROM session_data")
            stats['total_sessions'] = cursor.fetchone()[0]
            
            # Count admin users
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            stats['admin_users'] = cursor.fetchone()[0]
            
            # Average ATS scores
            cursor.execute("SELECT AVG(ats_score) FROM session_data WHERE ats_score IS NOT NULL")
            avg_ats = cursor.fetchone()[0]
            stats['avg_ats_score'] = round(avg_ats, 2) if avg_ats else 0
            
            # Average interview scores
            cursor.execute("SELECT AVG(interview_score) FROM session_data WHERE interview_score > 0")
            avg_interview = cursor.fetchone()[0]
            stats['avg_interview_score'] = round(avg_interview, 2) if avg_interview else 0
            
            cursor.close()
            return stats
            
        except Error as e:
            print(f"❌ Error getting database stats: {e}")
            return {}

# Global database instance
db = DatabaseManager()
