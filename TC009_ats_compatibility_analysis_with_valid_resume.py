import requests
from requests.exceptions import RequestException

BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/login"
CHECK_ATS_URL = f"{BASE_URL}/check_ats"
LOGOUT_URL = f"{BASE_URL}/logout"

VALID_USERNAME = "testuser"
VALID_PASSWORD = "testpassword"
JOB_ROLE = "Software Engineer"
RESUME_FILE_PATH = "valid_resume.pdf"


def test_tc009_ats_compatibility_analysis_with_valid_resume():
    session = requests.Session()
    try:
        # Login to get authenticated session
        login_data = {
            "username": VALID_USERNAME,
            "password": VALID_PASSWORD
        }
        login_resp = session.post(
            LOGIN_URL,
            data=login_data,
            timeout=30
        )
        assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}"
        assert "application/json" in login_resp.headers.get("Content-Type", ""), "Login response is not JSON"

        # Prepare file and data for ATS check
        with open(RESUME_FILE_PATH, "rb") as f:
            files = {"resume": ("valid_resume.pdf", f, "application/pdf")}
            data = {"job_role": JOB_ROLE}

            ats_resp = session.post(
                CHECK_ATS_URL,
                files=files,
                data=data,
                timeout=30
            )

        assert ats_resp.status_code == 200, f"/check_ats endpoint returned {ats_resp.status_code}"
        assert "application/json" in ats_resp.headers.get("Content-Type", ""), "Response is not JSON"

        ats_json = ats_resp.json()
        assert isinstance(ats_json, dict), "Response JSON is not an object"
        assert "compatibility_score" in ats_json, "Response missing 'compatibility_score'"
        assert "skill_gaps" in ats_json, "Response missing 'skill_gaps'"
        assert "recommendations" in ats_json, "Response missing 'recommendations'"

        # Validate compatibility_score type and range
        score = ats_json.get("compatibility_score")
        assert isinstance(score, (int, float)), "'compatibility_score' is not a number"
        assert 0 <= score <= 100, "'compatibility_score' should be between 0 and 100"

        # Validate skill_gaps is a list (empty or not)
        skill_gaps = ats_json.get("skill_gaps")
        assert isinstance(skill_gaps, list), "'skill_gaps' should be a list"

        # Validate recommendations is a list or dict with actionable items
        recommendations = ats_json.get("recommendations")
        assert isinstance(recommendations, (list, dict)), "'recommendations' should be a list or dict"

    except RequestException as e:
        assert False, f"Request exception occurred: {e}"

    finally:
        # Logout to terminate session
        try:
            logout_resp = session.get(LOGOUT_URL, timeout=30, allow_redirects=False)
            # Expecting redirect status 302 for logout
            assert logout_resp.status_code in {302, 200}, f"Logout returned unexpected status {logout_resp.status_code}"
        except Exception:
            pass


test_tc009_ats_compatibility_analysis_with_valid_resume()