# Code structure

Read through this before doing development on auth-api source code.


## auth_api

There are two layers to auth_api, for separation of concerns. These layers correspond to two subfolders:
* [routers](container/auth_api/routers) - The higher layer, defining endpoint object shapes and basic calls into the services layer. Most of the meat here is reshaping objects from the external interface to the internal functions. This layer is also responsible for authorization (which is made smoother through use of FastAPI's dependency injection system). Most of these endpoints should use the `sanitize_excs` context manager (demonstrated in [routers/main.py](container/auth_api/routers/main.py)) for security and user-friendliness.
* [services/user_api](container/auth_api/services/user_api) - The lower layer, defining interaction with the user-api service. HTTP status codes from user-api are converted into `InternalError`s, `ClientError`s, and `NotFoundError`s. These are converted back to HTTP status codes by `sanitize_excs` in the router layer.


## tests

Three kinds of tests are defined in files / folders here:
* [lint](container/tests/lint.sh) - Linting, specifically mypy, black, and flake8 for python and shellcheck for bash.
* [unit](container/tests/unit) - Unit tests for any python stuff here. Should call specific functions, mocking dependencies as needed.
* [integration](container/tests/integ) - Integration tests. Responsible for the integration between auth-api and user-api, and accordingly operate by making HTTP calls to the API endpoints and evaluating the responses.
