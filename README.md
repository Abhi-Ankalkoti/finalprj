# AI Resume Interview System

An intelligent Flask web application that analyzes resumes and conducts AI-powered interviews using Cohere's language model.

## Features

- **Resume Upload & Analysis**: Upload PDF resumes and extract text content
- **ATS Compatibility Check**: Evaluate resume compatibility with Applicant Tracking Systems
- **AI Interview Questions**: Generate contextual interview questions based on resume content
- **Answer Evaluation**: AI-powered evaluation of interview answers with scoring
- **Admin Dashboard**: Monitor user performance and generate reports
- **PDF Report Generation**: Export admin dashboard data as PDF reports

## Prerequisites

- Python 3.7+
- MySQL Server (5.7+ or 8.0+)
- Cohere API key (optional - for full AI functionality)

## Installation

1. **Clone or download the project**

2. **Install dependencies**:
   ```bash
   pip install flask cohere PyPDF2 reportlab werkzeug python-dotenv mysql-connector-python
   ```

3. **Set up MySQL Database**:
   ```bash
   python setup_mysql.py
   ```
   This will guide you through setting up the MySQL database and tables.

4. **Set up environment variables**:
   - The setup script will create/update the `.env` file automatically
   - Or manually add your Cohere API key:
     ```
     COHERE_API_KEY=your_cohere_api_key_here
     ```
   - Get your API key from: https://console.cohere.ai/

## Usage

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Access the application**:
   - Open your browser and go to: `http://127.0.0.1:5000/`
   - Register a new account or use the default admin account:
     - Username: `admin`
     - Password: `admin123`

3. **Using the system**:
   - **Upload Resume**: Upload a PDF resume for analysis
   - **ATS Check**: Evaluate resume compatibility with ATS systems
   - **Interview Mode**: Answer AI-generated questions based on your resume
   - **Admin Dashboard**: View all user data and performance metrics

## Default Credentials

- **Admin Account**:
  - Username: `admin`
  - Password: `admin123`

## API Integration

The application uses Cohere's AI model for:
- Generating interview questions from resume content
- Evaluating interview answers with scoring
- Analyzing ATS compatibility

**Note**: If no Cohere API key is provided, the application will use sample data for demonstration purposes.

## Project Structure

```
ai_interview_system/
├── app.py              # Main Flask application
├── database.py         # MySQL database operations
├── setup_mysql.py      # MySQL setup script
├── .env                # Environment variables
├── templates/          # HTML templates
├── static/            # CSS, JS, and static assets
└── README.md          # This file
```

## Features in Detail

### Resume Analysis
- PDF text extraction using PyPDF2
- Content analysis and keyword identification
- ATS compatibility scoring

### Interview System
- Contextual question generation based on resume
- Real-time answer evaluation
- Scoring system (0-10 scale)
- Performance tracking

### Admin Features
- User performance monitoring
- Resume analysis statistics
- PDF report generation
- Data export capabilities

## Troubleshooting

1. **MySQL Connection Issues**: 
   - Make sure MySQL server is running
   - Check your database credentials in `.env`
   - Run `python setup_mysql.py` to test connection
2. **API Key Issues**: If you see "Bearer" errors, make sure your Cohere API key is properly set in the `.env` file
3. **PDF Upload Issues**: Ensure uploaded files are valid PDFs
4. **Port Conflicts**: If port 5000 is busy, modify the port in `app.py`

## Security Notes

- Change the default admin password in production
- Use environment variables for sensitive data
- Implement proper session management for production use

## License

This project is for educational purposes. Please ensure compliance with Cohere's API terms of service.
