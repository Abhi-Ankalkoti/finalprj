import requests
from requests.exceptions import RequestException

BASE_URL = "http://localhost:5000"
TIMEOUT = 30

def test_admin_dashboard_access_control_and_data_display():
    session = requests.Session()

    admin_credentials = {
        "username": "admin",
        "password": "admin_password"  # Replace with valid admin credentials
    }
    user_credentials = {
        "username": "normaluser",
        "password": "user_password"  # Replace with valid non-admin user credentials
    }

    try:
        # Attempt login as admin user
        admin_login_resp = session.post(
            f"{BASE_URL}/login",
            data=admin_credentials,
            timeout=TIMEOUT,
            allow_redirects=False,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        # Check authentication status code and session cookie presence
        assert admin_login_resp.status_code == 200, "Admin login failed"
        assert "session" in session.cookies.get_dict(), "No session cookie after admin login"

        # Access admin_dashboard as admin
        admin_dashboard_resp = session.get(
            f"{BASE_URL}/admin_dashboard",
            timeout=TIMEOUT,
            headers={"Accept": "application/json"}
        )
        assert admin_dashboard_resp.status_code == 200, "Admin access to dashboard denied"
        # Ensure response is JSON
        try:
            data = admin_dashboard_resp.json()
        except ValueError:
            assert False, "Admin dashboard response is not valid JSON"

        # Check expected keys in the JSON related to analytics and reports (heuristic)
        assert isinstance(data, dict), "Admin dashboard JSON root is not an object"
        assert any(key in data for key in ("user_analytics", "reports", "analytics", "user_data")), \
            "Admin dashboard JSON missing analytics or reports data"

        # Logout admin user to clear session before user test
        session.get(f"{BASE_URL}/logout", timeout=TIMEOUT)

        # Attempt login as normal non-admin user
        user_login_resp = session.post(
            f"{BASE_URL}/login",
            data=user_credentials,
            timeout=TIMEOUT,
            allow_redirects=False,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert user_login_resp.status_code == 200, "User login failed"
        assert "session" in session.cookies.get_dict(), "No session cookie after user login"

        # Access admin_dashboard as normal user
        user_dashboard_resp = session.get(
            f"{BASE_URL}/admin_dashboard",
            timeout=TIMEOUT,
            headers={"Accept": "application/json"},
            allow_redirects=False,
        )
        # Non-admin users should NOT have access; expect redirect or forbidden status
        assert user_dashboard_resp.status_code in (302, 403), \
            f"Non-admin user access to admin dashboard should be denied, got {user_dashboard_resp.status_code}"
        # If redirected, location header should indicate login or unauthorized page
        if user_dashboard_resp.status_code == 302:
            location = user_dashboard_resp.headers.get("Location", "")
            assert any(x in location for x in ["/login", "/unauthorized"]), \
                f"Redirect for non-admin user to unexpected location: {location}"

    except RequestException as e:
        assert False, f"Request failed: {e}"

test_admin_dashboard_access_control_and_data_display()