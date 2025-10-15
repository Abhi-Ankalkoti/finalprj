import requests

def test_user_login_with_invalid_credentials():
    base_url = "http://localhost:5000"
    login_url = f"{base_url}/login"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "username": "invalid_user_xyz",
        "password": "wrongpassword123"
    }
    try:
        response = requests.post(login_url, data=payload, headers=headers, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 401, f"Expected status code 401, got {response.status_code}"

# Call the test function

test_user_login_with_invalid_credentials()