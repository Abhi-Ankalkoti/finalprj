#!/usr/bin/env python3
"""
Script to populate user_profiles table with data from existing users and session_data
"""

from database import DatabaseManager
import re

def extract_skills_from_resume(resume_text):
    """Extract skills from resume text"""
    if not resume_text:
        return ""
    
    # Common technical skills to look for
    technical_skills = [
        'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
        'HTML', 'CSS', 'React', 'Vue', 'Angular', 'Node.js', 'Express', 'Django',
        'Flask', 'Spring', 'Laravel', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis',
        'AWS', 'Azure', 'Docker', 'Kubernetes', 'Git', 'Jenkins', 'CI/CD',
        'Machine Learning', 'AI', 'Data Science', 'Analytics', 'TensorFlow',
        'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn'
    ]
    
    found_skills = []
    resume_lower = resume_text.lower()
    
    for skill in technical_skills:
        if skill.lower() in resume_lower:
            found_skills.append(skill)
    
    return ', '.join(found_skills[:10])  # Limit to 10 skills

def determine_experience_level(resume_text):
    """Determine experience level based on resume content"""
    if not resume_text:
        return 'Entry'
    
    resume_lower = resume_text.lower()
    
    # Look for experience indicators
    senior_indicators = ['senior', 'lead', 'principal', 'architect', 'manager', 'director', '5+ years', '10+ years']
    mid_indicators = ['mid-level', 'intermediate', '3+ years', '4+ years', '5 years']
    entry_indicators = ['junior', 'entry', 'graduate', 'intern', '0-2 years', '1-2 years']
    
    if any(indicator in resume_lower for indicator in senior_indicators):
        return 'Senior'
    elif any(indicator in resume_lower for indicator in mid_indicators):
        return 'Mid'
    elif any(indicator in resume_lower for indicator in entry_indicators):
        return 'Entry'
    else:
        # Default to Entry if no clear indicators
        return 'Entry'

def extract_contact_info(resume_text):
    """Extract contact information from resume"""
    if not resume_text:
        return None, None, None
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, resume_text)
    email = emails[0] if emails else None
    
    # Extract phone number
    phone_pattern = r'(\+?1[-.\s]?)?(\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})'
    phones = re.findall(phone_pattern, resume_text)
    phone = ''.join(phones[0]) if phones else None
    
    # Extract name (simple approach - first two words that are capitalized)
    name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
    names = re.findall(name_pattern, resume_text)
    full_name = names[0] if names else None
    
    return full_name, email, phone

def populate_user_profiles():
    """Populate user_profiles table with data from existing users and session data"""
    db = DatabaseManager()
    
    print("=== POPULATING USER_PROFILES TABLE ===")
    
    # Get all users
    cursor = db.connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    profiles_created = 0
    profiles_updated = 0
    
    for user in users:
        user_id = user['id']
        username = user['username']
        
        print(f"\nProcessing user: {username} (ID: {user_id})")
        
        # Check if profile already exists
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = %s", (user_id,))
        existing_profile = cursor.fetchone()
        
        # Get latest session data for this user
        cursor.execute("""
            SELECT resume_text, job_role, interview_score, ats_score, created_at
            FROM session_data 
            WHERE user_id = %s 
            ORDER BY updated_at DESC 
            LIMIT 1
        """, (user_id,))
        
        latest_session = cursor.fetchone()
        
        if latest_session:
            resume_text = latest_session.get('resume_text', '')
            job_role = latest_session.get('job_role', 'Software Engineer')
            
            # Extract information from resume
            full_name, email, phone = extract_contact_info(resume_text)
            skills = extract_skills_from_resume(resume_text)
            experience_level = determine_experience_level(resume_text)
            
            if existing_profile:
                # Update existing profile
                cursor.execute("""
                    UPDATE user_profiles 
                    SET full_name = %s, email = %s, phone = %s, 
                        preferred_job_role = %s, experience_level = %s, 
                        skills = %s, resume_text = %s
                    WHERE user_id = %s
                """, (full_name, email, phone, job_role, experience_level, 
                     skills, resume_text, user_id))
                profiles_updated += 1
                print(f"  Updated profile for {username}")
            else:
                # Create new profile
                cursor.execute("""
                    INSERT INTO user_profiles 
                    (user_id, full_name, email, phone, preferred_job_role, 
                     experience_level, skills, resume_text)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, full_name, email, phone, job_role, 
                     experience_level, skills, resume_text))
                profiles_created += 1
                print(f"  Created profile for {username}")
                
                if full_name:
                    print(f"    Name: {full_name}")
                if email:
                    print(f"    Email: {email}")
                if job_role:
                    print(f"    Job Role: {job_role}")
                if skills:
                    print(f"    Skills: {skills[:100]}...")
        else:
            # Create basic profile even without session data
            if not existing_profile:
                cursor.execute("""
                    INSERT INTO user_profiles 
                    (user_id, preferred_job_role, experience_level)
                    VALUES (%s, %s, %s)
                """, (user_id, 'Software Engineer', 'Entry'))
                profiles_created += 1
                print(f"  Created basic profile for {username}")
    
    db.connection.commit()
    cursor.close()
    
    print(f"\n=== POPULATION COMPLETE ===")
    print(f"Profiles created: {profiles_created}")
    print(f"Profiles updated: {profiles_updated}")
    print(f"Total users processed: {len(users)}")
    
    # Verify the results
    print(f"\n=== VERIFICATION ===")
    cursor = db.connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM user_profiles")
    total_profiles = cursor.fetchone()[0]
    print(f"Total profiles in database: {total_profiles}")
    cursor.close()

if __name__ == "__main__":
    populate_user_profiles()
