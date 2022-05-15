import random
from typing import Dict, Optional

from oauthlib.oauth2 import LegacyApplicationClient
import requests
from requests_oauthlib import OAuth2Session

from .config import BASE_URL


expected_success = {"success": True}


def _assert_good_resp(resp):
    """Assert a response is good."""
    assert resp.status_code == 200, resp.text
    assert resp.json() == expected_success, resp.text


def _random_alphanum(length=16) -> str:
    """Return a random alphanumeric string."""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(random.choice(chars) for i in range(length))


def _register_random() -> Optional[Dict[str, str]]:
    """Register a random user, return username and password if successful."""
    # Generate a user we want
    desired_user = {
        "username": _random_alphanum(),
        "password": _random_alphanum(),
    }

    # Register the user
    resp = requests.post(f"{BASE_URL}/register", json=desired_user)
    if resp.status_code != 200 or resp.json() != expected_success:
        print(f"Failed to register, maybe expected - {resp.text}")

    return desired_user


def _login(username: str, password: str) -> Optional[Dict[str, str]]:
    """Log a user in, return Auth header if successful."""
    try:
        oauth = OAuth2Session(client=LegacyApplicationClient(client_id=""))
        token = oauth.fetch_token(
            token_url=f"{BASE_URL}/login",
            username=username,
            password=password,
            client_id="",
            client_secret="",
        )
        if not token or "access_token" not in token:
            return None
        return {"Authorization": f"Bearer {token['access_token']}"}
    except Exception as e:
        print(f"Failed to log in, maybe expected - {str(e)}")
        return None


def test_register_login_logout():
    """Test that a new user can be registered and logged in."""
    # Register a random user
    login_data = _register_random()
    assert login_data is not None, "Failed to register"

    # Log the user in
    auth_header = _login(**login_data)
    assert auth_header is not None, "Failed to log in"

    # Log the user out
    resp = requests.post(f"{BASE_URL}/logout", headers=auth_header)
    _assert_good_resp(resp)

    # Ensure the user is still logged out
    resp = requests.post(f"{BASE_URL}/logout", headers=auth_header)
    assert resp.status_code != 200, "Token should be invalid"


def test_change_password():
    """Test that a user can have their password changed."""
    login_data = _register_random()
    assert login_data is not None, "Failed to register"

    # Log the user in
    auth_header = _login(**login_data)
    assert auth_header is not None, "Failed to log in"

    # Change the password
    new_password = _random_alphanum()
    resp = requests.post(
        f"{BASE_URL}/change_password",
        headers=auth_header,
        json={"new_password": new_password},
    )
    _assert_good_resp(resp)

    # Log the user out
    resp = requests.post(f"{BASE_URL}/logout", headers=auth_header)
    _assert_good_resp(resp)

    # Ensure the user is still logged out
    resp = requests.post(f"{BASE_URL}/logout", headers=auth_header)
    assert resp.status_code != 200, "Token should be invalid"

    # Ensure old password doesn't work
    should_fail = _login(**login_data)
    assert should_fail is None, "Old password worked when it shouldn't"

    # Ensure new password works
    login_data["password"] = new_password
    auth_header = _login(**login_data)
    assert auth_header is not None, "Failed to log in with new password"

    # Ensure log out works
    resp = requests.post(f"{BASE_URL}/logout", headers=auth_header)
    _assert_good_resp(resp)
