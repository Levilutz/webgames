import requests

from .config import BASE_URL


def test_ping():
    """Test pinging the application."""
    result = requests.get(BASE_URL + "/ping")
    assert result.status_code == 200
    assert result.text == "pong"
