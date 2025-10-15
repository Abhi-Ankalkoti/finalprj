from flask import Flask, render_template, request, redirect, session, jsonify, send_file
import cohere
import PyPDF2
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io
from dotenv import load_dotenv
from database import db

# Software job roles
SOFTWARE_JOB_ROLES = [
    "Software Engineer", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "Data Scientist", "Machine Learning Engineer",
    "AI Engineer", "DevOps Engineer", "Database Administrator",
    "Cloud Engineer", "UI/UX Designer", "Cybersecurity Analyst",
    "Mobile App Developer", "Product Manager", "QA Engineer",
    "Embedded Systems Engineer", "Game Developer"
]

# Skill requirements for each job role
JOB_SKILL_REQUIREMENTS = {
    "Software Engineer": ["Programming Languages", "Data Structures", "Algorithms", "Software Design", "Testing"],
    "Backend Developer": ["Programming Languages", "Databases", "APIs", "Server Management", "Cloud Platforms"],
    "Frontend Developer": ["HTML/CSS", "JavaScript", "React/Vue/Angular", "Responsive Design", "UI/UX"],
    "Full Stack Developer": ["Frontend Technologies", "Backend Technologies", "Databases", "APIs", "DevOps"],
    "Data Scientist": ["Python/R", "Machine Learning", "Statistics", "Data Analysis", "SQL"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning", "Data Processing", "Model Deployment"],
    "AI Engineer": ["Python", "Machine Learning", "Deep Learning", "NLP", "Computer Vision"],
    "DevOps Engineer": ["Cloud Platforms", "CI/CD", "Containerization", "Monitoring", "Infrastructure"],
    "Database Administrator": ["SQL", "Database Design", "Performance Tuning", "Backup/Recovery", "Security"],
    "Cloud Engineer": ["Cloud Platforms", "Infrastructure", "Automation", "Security", "Networking"],
    "UI/UX Designer": ["Design Tools", "User Research", "Prototyping", "Visual Design", "Interaction Design"],
    "Cybersecurity Analyst": ["Security Tools", "Risk Assessment", "Incident Response", "Compliance", "Networking"],
    "Mobile App Developer": ["Mobile Frameworks", "Platform Knowledge", "APIs", "Testing", "Performance"],
    "Product Manager": ["Product Strategy", "Market Research", "Agile/Scrum", "Data Analysis", "Communication"],
    "QA Engineer": ["Testing Frameworks", "Automation", "Manual Testing", "Bug Tracking", "Quality Assurance"],
    "Embedded Systems Engineer": ["C/C++", "Microcontrollers", "Hardware", "Real-time Systems", "Debugging"],
    "Game Developer": ["Game Engines", "Programming", "3D Graphics", "Physics", "Game Design"]
}

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'ai_interview_system_secret_key_2024_secure'

# Get Cohere API key from environment variable
cohere_api_key = os.getenv('COHERE_API_KEY', '')
co = cohere.Client(cohere_api_key)

# Database is initialized in database.py

@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')
    return render_template('index.html')

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'static']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error="Username and password are required"), 400
        
        user = db.get_user(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user'] = username
            session['user_id'] = user['id']
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect('/admin_dashboard')
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid credentials"), 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = db.get_user(username)
        if existing_user:
            return render_template('register.html', error="Username already exists")
        
        hashed_password = generate_password_hash(password)
        if db.create_user(username, hashed_password, 'user'):
            return redirect('/login')
        else:
            return render_template('register.html', error="Error creating account. Please try again.")
    return render_template('register.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if session.get('role') != 'user':
        return jsonify({'error': 'Authentication required'}), 401
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Invalid file format. Only PDF files are allowed.'}), 400
    if file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()

        session['resume_text'] = text
        session['resume_filename'] = file.filename
        
        # Get form parameters
        question_count = int(request.form.get('question_count'))
        include_hr_questions = request.form.get('include_hr_questions') == 'on'
        job_role = request.form.get('job_role', 'Software Engineer')
        
        print(f"DEBUG: question_count={question_count}, include_hr_questions={include_hr_questions}, job_role={job_role}")
        
        # Store resume text and job role in database
        db.update_session_data_with_analysis(
            session.get('user_id'),
            file.filename,
            text,
            job_role
        )
        
        # Update user profile with extracted information
        import re
        
        # Extract contact information from resume
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        email = emails[0] if emails else None
        
        phone_pattern = r'(\+?1[-.\s]?)?(\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})'
        phones = re.findall(phone_pattern, text)
        phone = ''.join(phones[0]) if phones else None
        
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        names = re.findall(name_pattern, text)
        full_name = names[0] if names else None
        
        # Extract skills
        technical_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
            'HTML', 'CSS', 'React', 'Vue', 'Angular', 'Node.js', 'Express', 'Django',
            'Flask', 'Spring', 'Laravel', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis',
            'AWS', 'Azure', 'Docker', 'Kubernetes', 'Git', 'Jenkins', 'CI/CD',
            'Machine Learning', 'AI', 'Data Science', 'Analytics', 'TensorFlow',
            'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn'
        ]
        
        found_skills = []
        text_lower = text.lower()
        for skill in technical_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        skills = ', '.join(found_skills[:10])  # Limit to 10 skills
        
        # Determine experience level
        experience_level = 'Entry'
        if any(indicator in text_lower for indicator in ['senior', 'lead', 'principal', 'architect', 'manager', 'director', '5+ years', '10+ years']):
            experience_level = 'Senior'
        elif any(indicator in text_lower for indicator in ['mid-level', 'intermediate', '3+ years', '4+ years', '5 years']):
            experience_level = 'Mid'
        
        # Update user profile
        db.create_or_update_user_profile(
            session.get('user_id'),
            full_name=full_name,
            email=email,
            phone=phone,
            preferred_job_role=job_role,
            experience_level=experience_level,
            skills=skills,
            resume_text=text
        )

        # Check if Cohere API key is configured
        if not cohere_api_key:
            # Get form parameters for sample questions too
            question_count = int(request.form.get('question_count', 5))
            include_hr_questions = request.form.get('include_hr_questions') == 'on'
            
            # Build sample questions based on user preferences
            sample_questions = []
            
            if include_hr_questions:
                sample_questions.extend([
                    "Tell me about yourself and walk me through your background.",
                    "Why are you interested in this position and our company?",
                    "What are your greatest strengths and how do they apply to this role?"
                ])
            
            # Add technical/role-specific questions
            technical_questions = [
                "Tell me about your experience with the technologies mentioned in your resume.",
                "Describe a challenging project you worked on and how you overcame obstacles.",
                "Where do you see yourself in 5 years professionally?",
                "What interests you most about this role and our company?",
                "How do you stay updated with the latest trends in your field?",
                "Describe a time when you had to learn a new technology quickly.",
                "How do you prioritize tasks when working on multiple projects?",
                "Tell me about a time you had to work with a difficult team member."
            ]
            
            # Fill remaining slots with technical questions
            remaining_count = question_count - len(sample_questions)
            if remaining_count > 0:
                sample_questions.extend(technical_questions[:remaining_count])
            
            session['questions'] = sample_questions
            return render_template('questions.html', questions=enumerate(sample_questions, 1))

        try:
            # Get form parameters
            question_count = int(request.form.get('question_count', 5))
            include_hr_questions = request.form.get('include_hr_questions') == 'on'
            
            # Build the prompt based on user preferences
            hr_intro_text = ""
            if include_hr_questions:
                hr_intro_text = """
IMPORTANT: Include these common HR introduction questions in your response:
1. "Tell me about yourself" or "Can you walk me through your background?"
2. "Why are you interested in this position/company?"
3. "What are your greatest strengths?"

Then generate additional technical/role-specific questions based on the resume.
"""
            
            # Get required skills for the job role
            required_skills = JOB_SKILL_REQUIREMENTS.get(job_role, [])
            skills_text = ", ".join(required_skills) if required_skills else "general software development"
            
            prompt = f"""Generate {question_count} interview questions for a {job_role} position based on the following resume:

TARGET ROLE: {job_role}
KEY SKILLS TO FOCUS ON: {skills_text}

{hr_intro_text}

Resume content:
{text}

Please generate questions that:
1. Assess technical skills relevant to {job_role}
2. Evaluate experience with {skills_text}
3. Test problem-solving abilities in {job_role} context
4. Include behavioral questions relevant to the role

Format your response as:
1. **Question Category**  
   *"Your question here?"*

2. **Question Category**  
   *"Your question here?"*

[Continue for all {question_count} questions]

Questions:"""
            response = co.chat(
                model="command-nightly",
                message=prompt,
                max_tokens=1000,
                temperature=0.7
            )
            # Save response text into a text file
            with open("response_output.txt", "w", encoding="utf-8") as file:
                  file.write(response.text)

            print(response.text)
            # Split by newlines and clean up
            questions = []
            questions_text = response.text.strip()
            
            import re
            
            # Handle the specific format: "1. **Title** *\"Question\"*"
            # Look for patterns like: "1. **Title**\n   *\"Question\"*"
            question_pattern = r'\d+\.\s*\*\*(.*?)\*\*\s*\n\s*\*"(.*?)"\*'
            matches = re.findall(question_pattern, questions_text, re.DOTALL)
            
            if matches:
                for title, question in matches:
                    # Clean up the question text
                    question = question.strip()
                    if question and len(question) > 10:
                        questions.append(question)
            
            # If no matches found with the specific pattern, try simpler numbered patterns
            if not questions:
                # Split by numbered lines (1., 2., 3., etc.)
                lines = questions_text.split('\n')
                current_question = ""
                
                for line in lines:
                    line = line.strip()
                    if re.match(r'^\d+\.', line):
                        # This is a numbered line, save previous question if exists
                        if current_question and len(current_question) > 10:
                            questions.append(current_question)
                        # Start new question - remove numbering and markdown
                        cleaned = re.sub(r'^\d+\.\s*\*\*(.*?)\*\*\s*', '', line)
                        cleaned = cleaned.strip('*').strip()
                        current_question = cleaned
                    elif line and current_question and not line.startswith('These questions'):
                        # This is a continuation of the current question
                        cleaned = line.strip('*').strip()
                        if cleaned:
                            current_question += " " + cleaned
                
                # Don't forget the last question
                if current_question and len(current_question) > 10:
                    questions.append(current_question)
            
            # If still no questions, try splitting by numbered patterns on same line
            if not questions:
                numbered_parts = re.split(r'\s*\d+\.\s*', questions_text)
                for part in numbered_parts:
                    part = part.strip()
                    # Remove markdown formatting
                    part = re.sub(r'\*\*(.*?)\*\*', r'\1', part)  # Remove bold
                    part = re.sub(r'\*(.*?)\*', r'\1', part)      # Remove italic
                    part = part.strip('*').strip()
                    if part and len(part) > 10 and not part.startswith('Here are') and not part.startswith('These questions'):
                        questions.append(part)
            
            # Final fallback - just clean the original text
            if not questions:
                cleaned = questions_text.lstrip('0123456789.-) ').strip()
                cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)
                cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)
                if cleaned:
                    questions.append(cleaned)
            session['questions'] = questions
            return render_template('questions.html', questions=enumerate(questions, 1))
        except Exception as e:
            # Return sample questions if API call fails
            # Get form parameters for fallback questions too
            question_count = int(request.form.get('question_count', 5))
            include_hr_questions = request.form.get('include_hr_questions') == 'on'
            
            # Build fallback questions based on user preferences
            fallback_questions = []
            
            if include_hr_questions:
                fallback_questions.extend([
                    "Tell me about yourself and walk me through your background.",
                    "Why are you interested in this position and our company?",
                    "What are your greatest strengths and how do they apply to this role?"
                ])
            
            # Add technical/role-specific questions
            technical_questions = [
                "Tell me about your experience with the technologies mentioned in your resume.",
                "Describe a challenging project you worked on and how you overcame obstacles.",
                "Where do you see yourself in 5 years professionally?",
                "What interests you most about this role and our company?",
                "How do you stay updated with the latest trends in your field?",
                "Describe a time when you had to learn a new technology quickly.",
                "How do you prioritize tasks when working on multiple projects?",
                "Tell me about a time you had to work with a difficult team member."
            ]
            
            # Fill remaining slots with technical questions
            remaining_count = question_count - len(fallback_questions)
            if remaining_count > 0:
                fallback_questions.extend(technical_questions[:remaining_count])
            
            session['questions'] = fallback_questions
            return render_template('questions.html', questions=enumerate(fallback_questions, 1))
    
    # If no file was processed, return error
    return jsonify({'error': 'File upload failed'}), 500

def analyze_skill_gaps(resume_text, job_role, ats_score):
    """Analyze skill gaps and provide recommendations"""
    try:
        required_skills = JOB_SKILL_REQUIREMENTS.get(job_role, [])
        
        if ats_score >= 92:
            return {
                'skill_gaps': "Your resume shows strong alignment with the role requirements.",
                'recommendations': "Consider focusing on advanced topics and leadership skills to further enhance your profile."
            }
        
        # Generate skill gap analysis using AI
        if cohere_api_key:
            gap_prompt = f"""Analyze the following resume for a {job_role} position and identify skill gaps:

REQUIRED SKILLS: {', '.join(required_skills)}

RESUME:
{resume_text}

Provide:
1. Missing skills or areas for improvement
2. Specific recommendations for courses, certifications, or learning paths
3. YouTube playlist suggestions for skill development

Format as:
SKILL GAPS: [list missing skills]
RECOMMENDATIONS: [specific courses/certifications]
YOUTUBE PLAYLISTS: [relevant playlist topics]
"""
            
            response = co.chat(
                model="command-nightly",
                message=gap_prompt,
                max_tokens=300,
                temperature=0.5
            )
            
            return {
                'skill_gaps': response.text.split('RECOMMENDATIONS:')[0].replace('SKILL GAPS:', '').strip(),
                'recommendations': response.text.split('YOUTUBE PLAYLISTS:')[0].split('RECOMMENDATIONS:')[1].strip() if 'RECOMMENDATIONS:' in response.text else "Focus on the identified skill gaps",
                'youtube_suggestions': response.text.split('YOUTUBE PLAYLISTS:')[1].strip() if 'YOUTUBE PLAYLISTS:' in response.text else "Search for tutorials related to missing skills"
            }
        else:
            # Fallback recommendations
            missing_skills = []
            for skill in required_skills:
                if skill.lower() not in resume_text.lower():
                    missing_skills.append(skill)
            
            return {
                'skill_gaps': f"Consider strengthening: {', '.join(missing_skills[:3])}" if missing_skills else "Skills appear well-aligned",
                'recommendations': f"For {job_role}: Focus on {', '.join(required_skills[:3])}. Consider online courses and certifications.",
                'youtube_suggestions': f"Search for '{job_role} tutorial', '{job_role} skills', and '{job_role} interview preparation' playlists"
            }
    except Exception as e:
        return {
            'skill_gaps': "Unable to analyze skill gaps at this time.",
            'recommendations': "Consider reviewing job requirements and updating your resume accordingly.",
            'youtube_suggestions': "Search for tutorials related to your target role"
        }

@app.route('/evaluate_answer', methods=['POST'])
def evaluate_answer():
    # Check if user is authenticated
    if 'user' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    answer = data.get('answer')
    if not answer:
        return jsonify({'error': 'No answer provided'}), 400
    
    question_index = data.get('question_index', 0)
    
    # Get the question from session
    questions = session.get('questions', [])
    if question_index < len(questions):
        question = questions[question_index]
    else:
        question = "General interview question"

    # Check if Cohere API key is configured
    if not cohere_api_key:
        # Return sample evaluation if API key is not available
        sample_score = 7
        sample_feedback = "Good answer with room for improvement. Consider providing more specific examples."
        
        # Update session data in database
        db.update_session_data_with_analysis(
            session.get('user_id'),
            session.get('resume_filename', 'N/A'),
            session.get('resume_text', ''),
            session.get('job_role', 'Software Engineer'),
            interview_score=sample_score
        )
        return jsonify({'evaluation': f"{sample_score}/10 - {sample_feedback}"})

    try:
        eval_prompt = f"""Evaluate the following interview answer based on the specific question asked.

QUESTION: {question}

ANSWER: {answer}

Evaluation Criteria:
1. Relevance to the question asked
2. Completeness of the answer
3. Technical accuracy (if applicable)
4. Use of specific examples
5. Clarity and structure
6. Professional communication

Provide a score out of 10 and detailed feedback focusing on:
- How well the answer addresses the specific question
- Strengths in the response
- Areas for improvement
- Suggestions for better answers

Format:
Score: X/10
Feedback: [detailed feedback]

Score:"""
        response = co.chat(
            model="command-nightly",
            message=eval_prompt,
            max_tokens=1000,
            temperature=0.7
        )

        output = response.text.strip()
        lines = output.strip().splitlines()
        score = None
        feedback = ""

        # Parse the new format with improved pattern matching
        for i, line in enumerate(lines):
            # Look for patterns like "Score: 8/10", "**Score:** 8/10", "8/10", etc.
            match = re.search(r'(?:Score:?\s*)?(?:\*\*)?(\d{1,2})\s*/\s*10(?:\*\*)?', line, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                # Collect feedback from next lines, skip empty lines but continue
                feedback_lines = []
                for feedback_line in lines[i+1:]:
                    # Remove markdown formatting from feedback lines
                    clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', feedback_line.strip())
                    if clean_line:  # Only add non-empty lines
                        feedback_lines.append(clean_line)
                feedback = ' '.join(feedback_lines).strip()
                # Remove "Feedback:" prefix if present
                if feedback.lower().startswith('feedback:'):
                    feedback = feedback[9:].strip()
                break
        
        # If no match found with the above pattern, try a more flexible approach
        if score is None:
            # Look for any line containing a number followed by /10
            for i, line in enumerate(lines):
                match = re.search(r'(\d{1,2})\s*/\s*10', line)
                if match:
                    score = int(match.group(1))
                    # Collect feedback from remaining lines, skip empty lines but continue
                    feedback_lines = []
                    for feedback_line in lines[i+1:]:
                        # Remove markdown formatting from feedback lines
                        clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', feedback_line.strip())
                        if clean_line:  # Only add non-empty lines
                            feedback_lines.append(clean_line)
                    feedback = ' '.join(feedback_lines).strip()
                    # Remove "Feedback:" prefix if present
                    if feedback.lower().startswith('feedback:'):
                        feedback = feedback[9:].strip()
                    break

        if score is None or not feedback:
            print(f"Error parsing evaluation response. Score: {score}, Feedback: '{feedback}'")
            print(f"Raw output: {output}")
            return jsonify({'error': 'AI did not return a valid score or feedback.', 'raw': output}), 500

        # Update session data in database
        db.update_session_data_with_analysis(
            session.get('user_id'),
            session.get('resume_filename', 'N/A'),
            session.get('resume_text', ''),
            session.get('job_role', 'Software Engineer'),
            interview_score=score
        )
        return jsonify({'evaluation': f"{score}/10 - {feedback}"})
    except Exception as e:
        print(f"Error in evaluate_answer: {e}")
        import traceback
        traceback.print_exc()
        
        # Return sample evaluation if API call fails
        sample_score = 7
        sample_feedback = "Good answer with room for improvement. Consider providing more specific examples."
        
        # Update session data in database
        try:
            db.update_session_data_with_analysis(
                session.get('user_id'),
                session.get('resume_filename', 'N/A'),
                session.get('resume_text', ''),
                session.get('job_role', 'Software Engineer'),
                interview_score=sample_score
            )
        except Exception as db_error:
            print(f"Database error in evaluate_answer fallback: {db_error}")
        
        return jsonify({'evaluation': f"{sample_score}/10 - {sample_feedback}"})

@app.route('/check_ats', methods=['POST'])
def check_ats():
    # Check if user is authenticated
    if 'user' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    file = request.files.get('resume')
    if not file:
        return jsonify({'score': 0, 'feedback': 'No file uploaded'}), 400
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Invalid file format. Only PDF files are allowed.'}), 400

    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text()

    session['resume_text'] = text
    session['resume_filename'] = file.filename

    job_role = request.form.get('job_role', session.get('job_role', 'Software Engineer'))
    session['job_role'] = job_role

    user_session_data = db.get_session_data(session.get('user_id'))
    for record in user_session_data:
        if record.get('resume_filename') == file.filename and record.get('ats_score') is not None:
            return jsonify({
                'score': record['ats_score'], 
                'feedback': record['ats_feedback'],
                'skill_gaps': record.get('skill_gaps', ''),
                'recommendations': record.get('recommendations', '')
            })

    if not cohere_api_key:
        sample_score = 75
        sample_feedback = (
            "Sample ATS analysis: Skills-40%, Education-25%, Experience-35% (Total: 100%). "
            "Your resume covers most required skills and education, but could benefit from more detailed experience descriptions."
        )
        
        # Get sample skill analysis
        skill_analysis = analyze_skill_gaps(text, job_role, sample_score)
        
        try:
            db.update_session_data_with_analysis(
                session.get('user_id'),
                file.filename,
                text,
                job_role,
                ats_score=sample_score,
                ats_feedback=sample_feedback,
                skill_gaps=skill_analysis['skill_gaps'],
                recommendations=skill_analysis['recommendations']
            )
        except Exception as db_error:
            print(f"Database error in sample case: {db_error}")
        
        return jsonify({
            'score': sample_score, 
            'feedback': sample_feedback,
            'skill_gaps': skill_analysis['skill_gaps'],
            'recommendations': skill_analysis['recommendations']
        })

    try:
        prompt = f"""
        You are an advanced ATS system evaluating a resume for the role of {job_role}.
        First line: return only a numeric score out of 100 like this format -> 85/100
        Second line: give a detailed, accurate feedback in 2-3 sentences. 
        Feedback must include: 
        - strengths (skills, education, experience, formatting, keywords)
        - weaknesses or gaps (missing skills, unclear sections, lack of quantifiable achievements)
        - a breakdown of the score (e.g. skills-40%, education-25%, experience-35% = 100%)
        Resume:
        {text}
        Score:
        """.strip()

        response = co.chat(
            model="command-nightly",
            message=prompt,
            max_tokens=200,
            temperature=0.5
        )

        output = response.text.strip()
        lines = output.splitlines()
        score = None
        feedback = ""

        for i, line in enumerate(lines):
            # Look for patterns like "**Score:** 85/100", "**82/100**", "**Score: 82/100**", "82/100", or "Score: 82/100"
            match = re.search(r'(?:Score:?\s*)?(?:\*\*)?(\d{1,3})\s*/\s*100(?:\*\*)?', line, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                # Collect feedback from next lines, skip empty lines but continue
                feedback_lines = []
                for feedback_line in lines[i+1:]:
                    # Remove markdown formatting from feedback lines
                    clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', feedback_line.strip())
                    if clean_line:  # Only add non-empty lines
                        feedback_lines.append(clean_line)
                feedback = ' '.join(feedback_lines).strip()
                break
        
        # If no match found with the above pattern, try a more flexible approach
        if score is None:
            # Look for any line containing a number followed by /100
            for i, line in enumerate(lines):
                match = re.search(r'(\d{1,3})\s*/\s*100', line)
                if match:
                    score = int(match.group(1))
                    # Collect feedback from remaining lines, skip empty lines but continue
                    feedback_lines = []
                    for feedback_line in lines[i+1:]:
                        # Remove markdown formatting from feedback lines
                        clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', feedback_line.strip())
                        if clean_line:  # Only add non-empty lines
                            feedback_lines.append(clean_line)
                    feedback = ' '.join(feedback_lines).strip()
                    break

        if score is None or not feedback:
            return jsonify({'error': 'AI did not return a valid score or feedback.', 'raw': output}), 500

        skill_analysis = analyze_skill_gaps(text, job_role, score)
        
        # Update session data with analysis
        try:
            db.update_session_data_with_analysis(
                session.get('user_id'),
                file.filename,
                text,
                job_role,
                ats_score=score,
                ats_feedback=feedback,
                skill_gaps=skill_analysis['skill_gaps'],
                recommendations=skill_analysis['recommendations']
            )
        except Exception as db_error:
            print(f"Database update error: {db_error}")
            # Continue with response even if DB update fails
        
        return jsonify({
            'score': score, 
            'feedback': feedback,
            'skill_gaps': skill_analysis['skill_gaps'],
            'recommendations': skill_analysis['recommendations']
        })
    except Exception as e:
        print(f"Error in check_ats: {e}")
        import traceback
        traceback.print_exc()
        
        sample_score = 75
        sample_feedback = (
            "Sample ATS analysis: Skills-40%, Education-25%, Experience-35% (Total: 100%). "
            "Your resume covers most required skills and education, but could benefit from more detailed experience descriptions."
        )
        
        # Try to update database with sample data
        try:
            skill_analysis = analyze_skill_gaps(text, job_role, sample_score)
            db.update_session_data_with_analysis(
                session.get('user_id'),
                file.filename,
                text,
                job_role,
                ats_score=sample_score,
                ats_feedback=sample_feedback,
                skill_gaps=skill_analysis['skill_gaps'],
                recommendations=skill_analysis['recommendations']
            )
        except Exception as db_error:
            print(f"Database error in fallback: {db_error}")
            skill_analysis = {
                'skill_gaps': 'Analysis temporarily unavailable',
                'recommendations': 'Please try again later'
            }
        
        return jsonify({
            'score': sample_score, 
            'feedback': sample_feedback,
            'skill_gaps': skill_analysis['skill_gaps'],
            'recommendations': skill_analysis['recommendations']
        })

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/'), 403

    # Get all session data with user profile information
    users = db.get_all_session_data_with_profiles()
    ats_scores = [u['ats_score'] for u in users if u.get('ats_score') is not None]
    interview_scores = [u['interview_score'] for u in users if u.get('interview_score') is not None]
    average_ats = round(sum(ats_scores) / len(ats_scores), 2) if ats_scores else 0
    highest_interview = max(interview_scores) if interview_scores else 0

    # Group data by job roles for analytics
    job_roles = {}
    for user in users:
        role = user.get('job_role', 'Not Specified')
        if role not in job_roles:
            job_roles[role] = {'count': 0, 'avg_ats': 0, 'avg_interview': 0}
        job_roles[role]['count'] += 1
        if user.get('ats_score'):
            job_roles[role]['avg_ats'] += user['ats_score']
        if user.get('interview_score'):
            job_roles[role]['avg_interview'] += user['interview_score']
    
    # Calculate averages
    for role in job_roles:
        if job_roles[role]['count'] > 0:
            job_roles[role]['avg_ats'] = round(job_roles[role]['avg_ats'] / job_roles[role]['count'], 2)
            job_roles[role]['avg_interview'] = round(job_roles[role]['avg_interview'] / job_roles[role]['count'], 2)

    return render_template(
        'admin_dashboard.html',
        data=users,
        ats_scores=ats_scores,
        interview_scores=interview_scores,
        average_ats=average_ats,
        highest_interview=highest_interview,
        job_roles=job_roles
    )

@app.route('/download_pdf')
def download_pdf():
    if session.get('role') != 'admin':
        return redirect('/'), 403

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("Admin Dashboard Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    data = [['User', 'Interview Score', 'ATS Score', 'Resume Filename']]

    # Get all session data from database
    all_data = db.get_all_session_data()
    for record in all_data:
        row = [
            record['username'],
            f"{record['interview_score']}/50",
            record['ats_score'] if record['ats_score'] is not None else 'Pending',
            record.get('resume_filename', 'N/A')
        ]
        data.append(row)

    table = Table(data, colWidths=[100, 100, 80, 250])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="admin_dashboard_report.pdf", mimetype='application/pdf')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login'), 302

@app.route('/api/database/status')
def database_status():
    """API endpoint to check database status (admin only)"""
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        stats = db.get_database_stats()
        health = db.verify_database_health()
        
        return jsonify({
            'status': 'healthy' if health else 'warning',
            'connection': db.connection.is_connected() if db.connection else False,
            'stats': stats,
            'timestamp': db.connection.get_server_info() if db.connection else 'Unknown'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'connection': False,
            'error': str(e)
        }), 500

@app.before_first_request
def initialize_database():
    """Initialize database on first request"""
    try:
        # Verify database health on startup
        if hasattr(db, 'verify_database_health'):
            db.verify_database_health()
        
        # Get and log database stats
        if hasattr(db, 'get_database_stats'):
            stats = db.get_database_stats()
            print(f"📊 Database initialized with {stats.get('total_users', 0)} users, {stats.get('total_sessions', 0)} sessions")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")

@app.teardown_appcontext
def close_db(error):
    """Close database connection when app context ends"""
    try:
        if hasattr(db, 'connection') and db.connection and db.connection.is_connected():
            db.connection.close()
    except Exception as e:
        print(f"Error closing database connection: {e}")

if __name__ == '__main__':
    app.run(debug=True)
