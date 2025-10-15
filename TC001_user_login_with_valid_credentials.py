import requests

BASE_URL = "http://localhost:5000"
TIMEOUT = 30

def test_user_login_with_valid_credentials():
    url = f"{BASE_URL}/login"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "username": "validuser",
        "password": "validpassword"
    }

    try:
        response = requests.post(url, headers=headers, data=data, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to /login failed: {e}"

    # Verify response status code for successful login
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"


test_user_login_with_valid_credentials()
