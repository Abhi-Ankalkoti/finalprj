import requests

BASE_URL = "http://localhost:5000"
TIMEOUT = 30

def test_user_logout_functionality():
    session = requests.Session()
    register_url = f"{BASE_URL}/register"
    login_url = f"{BASE_URL}/login"
    logout_url = f"{BASE_URL}/logout"

    # Test user credentials
    user_data = {
        'username': 'testuser',
        'password': 'testpassword'
    }

    try:
        # Register the user first to ensure user exists
        register_response = session.post(register_url, data=user_data, timeout=TIMEOUT)
        # It's okay if user already exists, so no assertion on register_response

        # Login to create a session
        login_response = session.post(login_url, data=user_data, timeout=TIMEOUT)
        assert login_response.status_code == 200, f"Login failed with status code {login_response.status_code}"
        assert 'session' in session.cookies or login_response.cookies, "No session cookie set after login"

        # Logout and verify redirect to login page
        logout_response = session.get(logout_url, allow_redirects=False, timeout=TIMEOUT)
        assert logout_response.status_code == 302, f"Logout did not redirect properly, got status code {logout_response.status_code}"
        location = logout_response.headers.get('Location', '')
        assert 'login' in location.lower(), f"Logout redirect location does not point to login page, got {location}"
    finally:
        session.close()


test_user_logout_functionality()
