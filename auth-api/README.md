# auth-api

A simple API to re-expose [user-api](../user-api) endpoints to external consumers, but with some security and reshaping.


## Technologies

Python HTTP API built with [FastAPI](https://fastapi.tiangolo.com/) and [Pydantic](https://pydantic-docs.helpmanual.io/). This API is notably not very RESTful, intending instead to be "user-friendly".


## Structure

The [container](container) folder contains the source code for the python api. The contents of this folder are built into the auth_api container. It contains a couple subfolders:
* [auth_api](container/auth_api) Is the API itself, accessed with the command `uvicorn <args> auth_api.routers.main:app` Code structure docs at [CODE.md](CODE.md)
* [tests](container/tests) Has the source for linting, unit tests, and integration tests.

The [helm](helm) folder contains the helm chart for auth_api.


## Usage

Attaches to `https://<domain>/api/auth`. For more detail, see interactive API docs at [https://games.levilutz.com/api/auth/docs](https://games.levilutz.com/api/auth/docs).


## Development

Before any development work, read the code docs at [CODE.md](CODE.md).

1. Ensure garden is installed - [installation docs](https://docs.garden.io/getting-started/1-installation).
2. Ensure you have the latest kubernetes cluster configuration in your `~/.kube`.
3. Navigate to the webgames repository root.
4. To test, run `garden test auth-api`. To develop, run `garden deploy auth-api --dev-mode`.

Deploying in dev-mode should make auth-api available at [http://localhost:8008/api/auth](http://localhost:8008/api/auth), with docs available at [http://localhost:8008/api/auth/docs](http://localhost:8008/api/auth/docs). Code will synchronize live between your local auth_api source and the remote cluster deployment, allowing development without having to wait for container rebuilds. 
