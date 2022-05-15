import random

from oauthlib.oauth2 import LegacyApplicationClient
import requests
from requests_oauthlib import OAuth2Session

from .config import BASE_URL


expected_success = {"success": True}


def random_alphanum(length=16) -> str:
    """Return a random alphanumeric string."""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(random.choice(chars) for i in range(length))


def test_register_login_logout():
    """Test that a new user can be registered and logged in."""
    # Generate a user we want
    desired_user = {
        "username": random_alphanum(),
        "password": random_alphanum(),
    }

    # Register the user
    resp = requests.post(f"{BASE_URL}/register", json=desired_user)
    assert resp.status_code == 200, resp.text
    assert resp.json() == expected_success, resp.text

    # Log the user in
    oauth = OAuth2Session(client=LegacyApplicationClient(client_id=""))
    token = oauth.fetch_token(
        token_url=f"{BASE_URL}/login",
        username=desired_user["username"],
        password=desired_user["password"],
        client_id="",
        client_secret="",
    )
    assert token, token
    auth_header = {"Authorization": f"Bearer {token['access_token']}"}

    # Log the user out
    resp = requests.post(f"{BASE_URL}/logout", headers=auth_header)
    assert resp.status_code == 200, resp.text
    assert resp.json() == expected_success, resp.text
