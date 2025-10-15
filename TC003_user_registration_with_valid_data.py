import requests
from requests.exceptions import RequestException

BASE_URL = "http://localhost:5000"
TIMEOUT = 30

def test_user_registration_with_valid_data():
    url = f"{BASE_URL}/register"
    import random, string
    # Generate a unique username for testing
    username = "testuser_" + "".join(random.choices(string.ascii_letters + string.digits, k=8))
    password = "StrongP@ssw0rd!"

    data = {
        "username": username,
        "password": password
    }

    try:
        response = requests.post(url, data=data, timeout=TIMEOUT)
        # Validate response status code 200 or 201 (successful creation)
        assert response.status_code in (200, 201), f"Unexpected status code: {response.status_code}"
    except RequestException as e:
        assert False, f"Request to /register failed: {str(e)}"


test_user_registration_with_valid_data()
