import requests

BASE_URL = "http://localhost:5000"
TIMEOUT = 30

def test_evaluate_interview_answer_with_valid_data():
    url_login = f"{BASE_URL}/login"
    url_evaluate = f"{BASE_URL}/evaluate_answer"
    session = requests.Session()

    # Test credentials (assuming valid user exists for testing)
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }

    # 1. Login user to get session cookie/authentication
    response_login = session.post(url_login, data=login_data, timeout=TIMEOUT)
    assert response_login.status_code == 200, f"Login failed with status {response_login.status_code}"
    assert "session" in session.cookies or "sessionid" in session.cookies or len(session.cookies) > 0, \
        "No session cookie received on login"

    # 2. Prepare valid payload for /evaluate_answer endpoint
    payload = {
        "answer": "I am highly motivated and have strong problem-solving skills.",
        "question_index": 0
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # 3. Call /evaluate_answer endpoint
    response_eval = session.post(url_evaluate, json=payload, headers=headers, timeout=TIMEOUT)

    # 4. Assertions for response
    assert response_eval.status_code == 200, f"Evaluate answer failed with status {response_eval.status_code}"
    try:
        json_resp = response_eval.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # Check typical keys in evaluation response (score, feedback) - Adjust if API docs specify differently
    assert isinstance(json_resp, dict), "Response JSON is not a dictionary"
    assert "score" in json_resp, "Response JSON missing 'score' field"
    assert "feedback" in json_resp, "Response JSON missing 'feedback' field"
    assert isinstance(json_resp["score"], (int, float)), "'score' should be a number"
    assert isinstance(json_resp["feedback"], str), "'feedback' should be a string"

test_evaluate_interview_answer_with_valid_data()