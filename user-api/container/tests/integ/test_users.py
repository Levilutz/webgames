import random
from typing import Dict, Optional, Tuple
from uuid import uuid4

import requests

from .config import BASE_URL


def _assert_good_resp(resp):
    """Assert a response is good."""
    assert resp.status_code == 200, resp.text
    assert not resp.text


def _random_alphanum(length=16) -> str:
    """Return a random alphanumeric string."""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(random.choice(chars) for i in range(length))


def _random_digits_not(length: int, not_match: str):
    """Get a given number of random digits, not matching the provided."""
    output = "".join([str(random.randint(0, 9)) for i in range(length)])
    while output == not_match:
        print("Collision!")
        output = "".join([str(random.randint(0, 9)) for i in range(length)])
    return output


def _random_email() -> str:
    """Return a random email address."""
    user_chars = "abcdefghijklmnopqrstuvwxyz0123456789_.+-"
    user = "".join(random.choice(user_chars) for i in range(12))
    domain = ".".join(
        [
            _random_alphanum(length=random.randint(2, 6))
            for i in range(random.randint(2, 4))
        ]
    )
    return f"{user}@{domain}"


def _register_random() -> Optional[Tuple[str, str]]:
    """Register a random user, return email and password if successful."""
    # Generate a user we want
    email = _random_email()
    password = _random_alphanum()

    # Pre-register the user
    body = {"email_address": email}
    resp = requests.post(f"{BASE_URL}/pre_users", json=body)
    if resp.status_code != 200:
        print(f"Failed to pre-register, maybe expected - {resp.text}")
        return None

    # When email disabled, verify code passed directly back from pre-register
    verify_code = resp.json().get("verify_code")

    if verify_code in ["", None]:
        raise Exception("Received blank verify code, may have email mistakenly enabled")

    # Verify the code
    body = {
        "email_address": email,
        "verify_code": verify_code,
    }
    resp = requests.post(f"{BASE_URL}/pre_users/verify", json=body)
    if resp.status_code != 200:
        print(f"Failed to verify code, maybe expected - {resp.text}")
        return None

    # Register the user
    body = {
        "email_address": email,
        "password": password,
        "first_name": "Johnny",
        "last_name": "Peter-Schmidt",
        "verify_code": verify_code,
    }
    resp = requests.post(f"{BASE_URL}/users", json=body)
    if resp.status_code != 200:
        print(f"Failed to register, maybe expected - {resp.text}")
        return None

    return email, password


def _login_json(email_address: str, password: str) -> Optional[Dict[str, str]]:
    """Log a user in, return client token if successful."""
    body = {
        "email_address": email_address,
        "password": password,
    }
    resp = requests.post(f"{BASE_URL}/users/login", json=body)
    if resp.status_code != 200 or "client_token" not in resp.json():
        print(f"Failed to log in, maybe expected - {resp.text}")
        return None
    return resp.json()["client_token"]


def test_register_login_logout():
    """Test that a new user can be registered and logged in."""
    # Register a random user
    login_data = _register_random()
    assert login_data is not None, "Failed to register"
    email, password = login_data

    # Log the user in
    client_token = _login_json(email, password)
    assert client_token is not None, "Failed to log in"

    # Log the user out
    resp = requests.delete(f"{BASE_URL}/tokens/{client_token}")
    _assert_good_resp(resp)

    # Ensure the user is still logged out
    resp = requests.delete(f"{BASE_URL}/tokens/{client_token}")
    assert resp.status_code != 200, "Token should be invalid"


def test_change_password():
    """Test that a user can have their password changed."""
    login_data = _register_random()
    assert login_data is not None, "Failed to register"
    email, password = login_data

    # Log the user in
    client_token = _login_json(email, password)
    assert client_token is not None, "Failed to log in"

    # Change the password
    new_password = _random_alphanum()
    body = {"email_address": email, "password": new_password}
    resp = requests.put(f"{BASE_URL}/users", json=body)
    _assert_good_resp(resp)

    # Log the user out
    resp = requests.delete(f"{BASE_URL}/tokens/{client_token}")
    _assert_good_resp(resp)

    # Ensure the user is still logged out
    resp = requests.delete(f"{BASE_URL}/tokens/{client_token}")
    assert resp.status_code != 200, "Token should be invalid"

    # Ensure old password doesn't work
    should_fail = _login_json(email, password)
    assert should_fail is None, "Old password worked when it shouldn't"

    # Ensure new password works
    client_token = _login_json(email, new_password)
    assert client_token is not None, "Failed to log in with new password"

    # Ensure log out works
    resp = requests.delete(f"{BASE_URL}/tokens/{client_token}")
    _assert_good_resp(resp)


def test_delete_user():
    """Test that a user can be deleted."""
    login_data = _register_random()
    assert login_data is not None, "Failed to register"
    email, password = login_data

    # Log the user in
    client_token = _login_json(email, password)
    assert client_token is not None, "Failed to log in"

    # Delete the user
    body = {
        "email_address": email,
    }
    resp = requests.delete(f"{BASE_URL}/users", params=body)
    _assert_good_resp(resp)

    # Ensure log out fails
    resp = requests.delete(f"{BASE_URL}/tokens/{client_token}")
    assert resp.status_code != 200, "Session shouldn't exist after user delete"

    # Ensure re-login fails
    client_token = _login_json(email, password)
    assert client_token is None, "Logged in to deleted user - uh oh"


def test_get_token():
    """Test that a token's associated user can be found."""
    login_data = _register_random()
    assert login_data is not None, "Failed to register"
    email, password = login_data

    # Log the user in
    client_token = _login_json(email, password)
    assert client_token is not None, "Failed to log in"

    # Get the token's associated email
    resp = requests.get(f"{BASE_URL}/tokens/{client_token}")
    assert resp.status_code == 200, "Failed to find email for token"
    assert resp.json()["email_address"] == email


def _ensure_locked_out(email: str, verify_code: str):
    # Ensure cannot send another email
    body = {"email_address": email}
    resp = requests.post(f"{BASE_URL}/pre_users", json=body)
    assert resp.status_code != 200, "Expected failure after n mistakes"
    assert "Maximum failed registrations" in resp.json()["detail"]

    # Ensure cannot verify code
    body = {
        "email_address": email,
        "verify_code": verify_code,
    }
    resp = requests.post(f"{BASE_URL}/pre_users/verify", json=body)
    assert resp.status_code != 200, "Expected failure after n mistakes"
    assert "Maximum failed registrations" in resp.json()["detail"]

    # Ensure cannot register
    body = {
        "email_address": email,
        "password": _random_alphanum(16),
        "first_name": "Johnny",
        "last_name": "Peter-Schmidt",
        "verify_code": verify_code,
    }
    resp = requests.post(f"{BASE_URL}/users", json=body)
    assert resp.status_code != 200, "Expected failure after n mistakes"
    assert "Maximum failed registrations" in resp.json()["detail"]


def test_pre_register_lockout():
    """Test that sending too many verify emails leads to failure."""
    email = _random_email()

    # Pre-register the user enough times to exhaust allowed failures
    for i in range(6):
        body = {"email_address": email}
        resp = requests.post(f"{BASE_URL}/pre_users", json=body)
        assert resp.status_code == 200, "Expected first 6 attempts to pass"
        verify_code = resp.json().get("verify_code")
        if verify_code in ["", None]:
            raise Exception(
                "Received blank verify code, may have email mistakenly enabled"
            )

    # Ensure locked out
    _ensure_locked_out(email, verify_code)


def test_verify_lockout():
    """Test that trying to verify too many codes leads to failure."""
    email = _random_email()

    # Pre-register the user
    body = {"email_address": email}
    resp = requests.post(f"{BASE_URL}/pre_users", json=body)
    assert resp.status_code == 200, "Expected pre-register to pass"
    verify_code = resp.json().get("verify_code")
    if verify_code in ["", None]:
        raise Exception("Received blank verify code, may have email mistakenly enabled")

    # Verify the user enough times to exhaust allowed failures
    for i in range(5):
        body = {
            "email_address": email,
            "verify_code": _random_digits_not(6, verify_code),
        }
        resp = requests.post(f"{BASE_URL}/pre_users/verify", json=body)
        assert resp.json()["detail"] == "Verification code invalid"

    # Ensure locked out
    _ensure_locked_out(email, verify_code)


def test_register_lockout():
    """Test that trying to register too many times leads to failure."""
    email = _random_email()

    # Pre-register the user
    body = {"email_address": email}
    resp = requests.post(f"{BASE_URL}/pre_users", json=body)
    assert resp.status_code == 200, "Expected pre-register to pass"
    verify_code = resp.json().get("verify_code")
    if verify_code in ["", None]:
        raise Exception("Received blank verify code, may have email mistakenly enabled")

    # Verify the code
    body = {
        "email_address": email,
        "verify_code": verify_code,
    }
    resp = requests.post(f"{BASE_URL}/pre_users/verify", json=body)
    assert resp.status_code == 200

    # Register the user enough times to exhaust allowed failures
    for i in range(5):
        body = {
            "email_address": email,
            "password": _random_alphanum(16),
            "first_name": "Johnny",
            "last_name": "Peter-Schmidt",
            "verify_code": _random_digits_not(6, verify_code),
        }
        resp = requests.post(f"{BASE_URL}/users", json=body)
        assert resp.status_code != 200
        assert resp.json()["detail"] == "Verification code invalid"

    # Ensure locked out
    _ensure_locked_out(email, verify_code)


def request_password_reset() -> Tuple[str, str, str]:
    login_data = _register_random()
    assert login_data is not None, "Failed to register"
    email, password = login_data

    # Log the user in
    client_token = _login_json(email, password)
    assert client_token is not None, "Failed to log in"

    # Request a password reset
    body = {
        "email_address": email,
    }
    resp = requests.post(f"{BASE_URL}/password_resets", json=body)
    assert resp.status_code == 200, resp.text
    reset_code = resp.json().get("reset_code")
    if reset_code in ["", None]:
        raise Exception("Received blank reset code, may have email mistakenly enabled")

    return email, password, reset_code


def test_password_reset():
    """Test that a user can reset their password."""
    email, password, reset_code = request_password_reset()

    # Submit the password reset
    new_password = _random_alphanum()
    body = {
        "email_address": email,
        "password": new_password,
        "reset_code": reset_code,
    }
    resp = requests.post(f"{BASE_URL}/users/reset_password", json=body)
    assert resp.status_code == 200

    # Ensure old password doesn't work
    client_token = _login_json(email, password)
    assert client_token is None, "Old password should not work"

    # Ensure new password works
    client_token = _login_json(email, new_password)
    assert client_token is not None, "New password should work"


def test_password_reset_fails():
    """Test that the wrong reset code does not work."""
    email, password, reset_code = request_password_reset()

    # Submit a bad password reset
    new_password = _random_alphanum()
    body = {
        "email_address": email,
        "password": new_password,
        "reset_code": str(uuid4()),
    }
    resp = requests.post(f"{BASE_URL}/users/reset_password", json=body)
    assert resp.status_code != 200
    assert "Password reset code invalid" in resp.json()["detail"]

    # Ensure old password still works
    client_token = _login_json(email, password)
    assert client_token is not None, "Old password should still work"

    # Ensure new password does not work
    client_token = _login_json(email, new_password)
    assert client_token is None, "New password should not work"


def test_password_reset_fails_multiuser():
    """Test that one user's reset code can't be used for another."""
    email_1, password_1, reset_code_1 = request_password_reset()
    email_2, password_2, reset_code_2 = request_password_reset()

    # Submit a bad password reset for user 1
    new_password = _random_alphanum()
    body = {
        "email_address": email_1,
        "password": new_password,
        "reset_code": reset_code_2
    }
    resp = requests.post(f"{BASE_URL}/users/reset_password", json=body)
    assert resp.status_code != 200
    assert "Password reset code invalid" in resp.json()["detail"]

    # Submit a bad password reset for user 2
    new_password = _random_alphanum()
    body = {
        "email_address": email_2,
        "password": new_password,
        "reset_code": reset_code_1
    }
    resp = requests.post(f"{BASE_URL}/users/reset_password", json=body)
    assert resp.status_code != 200
    assert "Password reset code invalid" in resp.json()["detail"]


def test_password_reset_no_multiple():
    """Test that no more than one password reset request can be subnitted."""
    email, password, reset_code = request_password_reset()

    # Request another password reset
    body = {
        "email_address": email,
    }
    resp = requests.post(f"{BASE_URL}/password_resets", json=body)
    assert resp.status_code != 200, resp.text
    assert "already pending" in resp.json()["detail"]
