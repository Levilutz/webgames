import os

default_base_path = "http://localhost:8008/api/auth"  # For local runs on port-forward
BASE_URL = os.getenv("BASE_URL", default=default_base_path)

# Set insecure transport if necessary for oauthlib to shut up
if BASE_URL.startswith("http://"):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
elif not BASE_URL.startswith("https://"):
    raise Exception("Path must start with 'http://' or 'https://'")
