import requests
import io

BASE_URL = "http://localhost:5000"
TIMEOUT = 30

# Minimal valid PDF content as bytes (1-page blank PDF)
MINIMAL_PDF_BYTES = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Count 1 /Kids [3 0 R] >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 72 72] >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000061 00000 n \n0000000116 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n171\n%%EOF"

def test_resume_upload_with_valid_pdf_and_parameters():
    pdf_buffer = io.BytesIO(MINIMAL_PDF_BYTES)

    files = {
        "resume": ("test_resume.pdf", pdf_buffer, "application/pdf")
    }
    data = {
        "question_count": 5,
        "job_role": "Software Engineer",
        # The API expects boolean; use True instead of string 'true'
        "include_hr_questions": True
    }
    headers = {
        "Accept": "application/json"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/upload_resume",
            files=files,
            data=data,
            headers=headers,
            timeout=TIMEOUT
        )
        # Validate response status code for success
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

        # Validate response content-type is JSON
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, f"Expected JSON response, got {content_type}"

        # Validate JSON body has expected keys related to questions generation
        json_data = response.json()
        assert isinstance(json_data, dict), "Response JSON is not a dictionary"
        assert "questions" in json_data, "'questions' key not in response JSON"
        questions = json_data.get("questions")
        assert isinstance(questions, list), "'questions' should be a list"
        assert len(questions) == data["question_count"], f"Expected {data['question_count']} questions, got {len(questions)}"

        # Optionally check that questions include HR questions if included
        if data["include_hr_questions"] == True:
            hr_questions_present = any("hr" in q.get("type", "").lower() for q in questions if isinstance(q, dict))
            assert hr_questions_present, "HR questions expected but not found in questions list"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"


test_resume_upload_with_valid_pdf_and_parameters()
