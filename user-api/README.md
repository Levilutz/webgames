# user-api

A single source API to provide data about users and authentication. Meant for use by internal clients only. Endpoints are re-exposed to external consumers by [auth-api](../auth-api).


## Technologies

Python REST API built with [FastAPI](https://fastapi.tiangolo.com/) and [Pydantic](https://pydantic-docs.helpmanual.io/), persistence in a [PostgresQL](https://www.postgresql.org/) database. The API uses [Psycopg3](https://www.psycopg.org/psycopg3/) to interface with the database.


## Structure

The [container](container) folder contains the source code for the python api. The contents of this folder are built into the user_api container, and the various functions of the container are accessed through different commands/entrypoints. It contains a few subfolders:
* [user_api](container/user_api) Is the API itself, accessed with the command `uvicorn <args> user_api.routers.main:app`. Code structure docs at [CODE.md](CODE.md)
* [migrations](container/migrations) Is the source code for database migrations, accessed with the command `python3 -m migrations.entrypoint`. Create new migrations with `bash user-api/container/create_migration.sh <migration name>`, run from repository root.
* [tests](container/tests) Has the source for linting, unit tests, and integration tests.

The [helm](helm) folder contains the helm chart for user_api and the subchart for the database:
* [user-api](helm/user-api) Is the chart for the API deployment itself.
* [postgres](helm/user-api/charts/postgres) Is the subchart of user-api responsible for deploying the postgresql database and running migrations post-install/upgrade.


## Usage

In dev environments, attaches to `https://<domain>/dev/user-api`. For more detail, see interactive API docs at [http://localhost:8008/dev/user-api/docs](http://localhost:8008/dev/user-api/docs) once you're connected to a dev environment.


## Development

Before any development work, read the code docs at [CODE.md](CODE.md).

1. Ensure garden is installed - [installation docs](https://docs.garden.io/getting-started/1-installation).
2. Ensure you have the latest kubernetes cluster configuration in your `~/.kube`.
3. Navigate to the webgames repository root.
4. To test, run `garden test user-api`. To develop, run `garden deploy user-api --dev-mode`.

Deploying in dev-mode should make user-api available at [http://localhost:8008/dev/user-api](http://localhost:8008/dev/user-api), with docs available at [http://localhost:8008/dev/user-api/docs](http://localhost:8008/dev/user-api/docs). Code will synchronize live between your local user_api source and the remote cluster deployment, allowing development without having to wait for container rebuilds. 
