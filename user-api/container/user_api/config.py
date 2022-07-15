import os


EXPECTED_PREFIX = os.getenv("EXPECTED_PREFIX") or ""
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_ADDRESS = os.getenv("DB_ADDRESS")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
SENDGRID_KEY = os.getenv("SENDGRID_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM") or "Web Games <no-reply@games.levilutz.com>"
ALLOWED_FAILED_VERIFICATIONS = int(os.getenv("ALLOWED_FAILED_VERIFICATIONS") or "5")
VERIFY_CODE_LENGTH = int(os.getenv("VERIFY_CODE_LENGTH") or "6")


# Env vars required for a full deployment, checked in app_startup
REQUIRED_ENV_FOR_DEPLOY = [
    DB_USER,
    DB_PASS,
    DB_ADDRESS,
    DB_PORT,
    DB_NAME,
]

EMAIL_ENABLED = SENDGRID_KEY not in [None, ""]
