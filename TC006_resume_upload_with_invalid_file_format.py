import requests

BASE_URL = "http://localhost:5000"
UPLOAD_ENDPOINT = f"{BASE_URL}/upload_resume"
TIMEOUT = 30

def test_resume_upload_with_invalid_file_format():
    # Prepare an invalid file (non-PDF, e.g., a text file)
    invalid_file_content = b"This is not a PDF file content"
    files = {
        "resume": ("invalid_resume.txt", invalid_file_content, "text/plain")
    }
    # Populate other required form fields with valid dummy data
    data = {
        "question_count": "5",
        "job_role": "Software Engineer",
        "include_hr_questions": "true"
    }
    headers = {
        "Accept": "application/json"
    }
    try:
        response = requests.post(UPLOAD_ENDPOINT, files=files, data=data, headers=headers, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        assert False, f"Request failed: {e}"

    # Assert the response status code is 400 indicating invalid file
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"

    # Assert response is JSON and contains an error message about invalid file
    try:
        json_resp = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    assert "error" in json_resp or "message" in json_resp, "Error message missing in response"
    error_msg = json_resp.get("error") or json_resp.get("message")
    assert isinstance(error_msg, str) and len(error_msg) > 0, "Error message is empty or not a string"

test_resume_upload_with_invalid_file_format()