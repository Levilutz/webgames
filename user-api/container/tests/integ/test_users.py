import random
from typing import Dict, Optional

from oauthlib.oauth2 import LegacyApplicationClient
import pytest
import requests
from requests_oauthlib import OAuth2Session

from .config import BASE_URL


def _assert_good_resp(resp):
    """Assert a response is good."""
    assert resp.status_code == 200, resp.text
    assert not resp.text


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
    if resp.status_code != 200:
        print(f"Failed to register, maybe expected - {resp.text}")

    return desired_user


def _login_oauth2(username: str, password: str) -> Optional[Dict[str, str]]:
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


def _login_json(username: str, password: str) -> Optional[Dict[str, str]]:
    """Log a user in, return Auth header if successful."""
    resp = requests.post(
        f"{BASE_URL}/login_json", json={"username": username, "password": password}
    )
    if resp.status_code != 200 or "client_token" not in resp.json():
        print(f"Failed to log in, maybe expected - {resp.text}")
        return None
    return {"Authorization": f"Bearer {resp.json()['client_token']}"}


@pytest.mark.parametrize("auth_method", [_login_oauth2, _login_json])
def test_register_login_logout(auth_method):
    """Test that a new user can be registered and logged in."""
    # Register a random user
    login_data = _register_random()
    assert login_data is not None, "Failed to register"

    # Log the user in
    auth_header = auth_method(**login_data)
    assert auth_header is not None, "Failed to log in"

    # Log the user out
    resp = requests.post(f"{BASE_URL}/logout", headers=auth_header)
    _assert_good_resp(resp)

    # Ensure the user is still logged out
    resp = requests.post(f"{BASE_URL}/logout", headers=auth_header)
    assert resp.status_code != 200, "Token should be invalid"


@pytest.mark.parametrize("auth_method", [_login_oauth2, _login_json])
def test_change_password(auth_method):
    """Test that a user can have their password changed."""
    login_data = _register_random()
    assert login_data is not None, "Failed to register"

    # Log the user in
    auth_header = auth_method(**login_data)
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
    should_fail = auth_method(**login_data)
    assert should_fail is None, "Old password worked when it shouldn't"

    # Ensure new password works
    login_data["password"] = new_password
    auth_header = auth_method(**login_data)
    assert auth_header is not None, "Failed to log in with new password"

    # Ensure log out works
    resp = requests.post(f"{BASE_URL}/logout", headers=auth_header)
    _assert_good_resp(resp)


@pytest.mark.parametrize("auth_method", [_login_oauth2, _login_json])
def test_delete_user(auth_method):
    """Test that a user can be deleted."""
    login_data = _register_random()
    assert login_data is not None, "Failed to register"

    # Log the user in
    auth_header = auth_method(**login_data)
    assert auth_header is not None, "Failed to log in"

    # Delete the user
    resp = requests.post(f"{BASE_URL}/delete", headers=auth_header)
    _assert_good_resp(resp)

    # Ensure log out fails
    resp = requests.post(f"{BASE_URL}/logout", headers=auth_header)
    assert resp.status_code != 200, "Session shouldn't exist after user delete"

    # Ensure re-login fails
    auth_header = auth_method(**login_data)
    assert auth_header is None, "Logged in to deleted user - uh oh"
