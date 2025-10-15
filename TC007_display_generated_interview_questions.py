import requests

BASE_URL = "http://localhost:5000"
TIMEOUT = 30

def test_display_generated_interview_questions():
    session = requests.Session()

    # Define test user credentials and resume upload data
    username = "testuser"
    password = "TestPass123!"

    # Register the user (ignore if already exists)
    reg_resp = session.post(
        f"{BASE_URL}/register",
        data={"username": username, "password": password},
        timeout=TIMEOUT
    )
    assert reg_resp.status_code in [200, 201, 400], f"Registration failed with status {reg_resp.status_code}"
    # If 400, possibly user exists; continue anyhow

    # Login to obtain session cookie/authentication
    login_resp = session.post(
        f"{BASE_URL}/login",
        data={"username": username, "password": password},
        timeout=TIMEOUT,
        allow_redirects=False
    )

    assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}"

    # Prepare a sample PDF resume file content (as simple bytes)
    # Minimal valid PDF header; for real test, replace with a valid PDF file content
    pdf_content = b'%PDF-1.4\n%Test PDF content\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF'

    try:
        # Upload resume with parameters to generate questions
        files = {
            "resume": ("resume.pdf", pdf_content, "application/pdf")
        }
        data = {
            "question_count": 3,
            "job_role": "Software Engineer",
            "include_hr_questions": 'true'
        }
        upload_resp = session.post(
            f"{BASE_URL}/upload_resume",
            files=files,
            data=data,
            timeout=TIMEOUT
        )
        assert upload_resp.status_code == 200, f"Resume upload failed with status {upload_resp.status_code}"
        assert upload_resp.headers.get("Content-Type", "").startswith("application/json") or upload_resp.headers.get("Content-Type", "").startswith("text/html") 

        # Access /questions endpoint to display generated interview questions
        questions_resp = session.get(
            f"{BASE_URL}/questions",
            timeout=TIMEOUT
        )
        assert questions_resp.status_code == 200, f"GET /questions failed with status {questions_resp.status_code}"
        content_type = questions_resp.headers.get("Content-Type", "")
        assert "html" in content_type or "json" in content_type, "Response Content-Type is not HTML or JSON"

        # Basic validation of returned content
        if "json" in content_type:
            questions_json = questions_resp.json()
            assert isinstance(questions_json, (dict, list)), "Questions JSON response is not a dict or list"
            assert len(questions_json) > 0, "Questions list is empty"
        else:
            # If HTML, check presence of known phrases in body text
            body_text = questions_resp.text.lower()
            assert "question" in body_text or "interview" in body_text, "HTML response does not appear to contain questions"

    finally:
        # Logout to clean up session
        logout_resp = session.get(f"{BASE_URL}/logout", timeout=TIMEOUT, allow_redirects=False)
        assert logout_resp.status_code in [302, 200], "Logout failed"

test_display_generated_interview_questions()
