from email_api.services.email_utils import send_email


def test_main():
    assert send_email is not None
