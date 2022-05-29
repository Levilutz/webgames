from user_api_internal.routers import main


def test_app_exists():
    """Test that the app can be imported and exists."""
    assert main.app is not None
