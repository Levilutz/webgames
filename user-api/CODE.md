# Code structure

Read through this before doing development on user-api source code.


## migrations

This is pretty simple, and most of the base migrations code should never need touching. Just in case:
* [entrypoint.py](container/migrations/entrypoint.py) - The base code to discover executed and available migrations, diff, and run each needed migration in its own transaction.
* [migration.py](container/migrations/migration.py) - A migration base class for use in each migration.
* [template.py](container/migrations/template.py) - A template that's copied into the migrations folder when you run `create_migration.sh`.
* [migrations/\*](container/migrations/migrations) - Where migrations are written.

For normal development purposes, you should only ever have to run `bash create_migration.sh <migration name>` (from the `user-api/container` directory) and develop in the blank migration file.


## user_api

There are three layers to user_api, for separation of concerns. These layers correspond to four subfolders:
* [routers](container/user_api/routers) - The highest layer, defining endpoint object shapes and basic calls into the internal layer. This layer should contain little to no business logic. Most of the meat here is reshaping objects from the interface to internal functions, doing validation, and wrangling FastAPI dependencies. Most of these endpoints should use the `sanitize_excs` context manager (demonstrated in [routers/users.py](container/user_api/routers/users.py)) for security and client-friendliness.
* [internal](container/user_api/internal) - The middle layer, containing practically all of the business logic. This layer is called from routers, and usually calls down to daos (to access the database) or services (to access external services) to accomplish its goals. It should handle any anticipated exceptions and re-raise them as `ClientError`s if the user is at fault. `InternalError`s raised by lower layers can be allowed to propagate upwards. This layer should never create / use database cursors, but is expected to create database connections which are passed to DAO calls, as transactions are logically attached to business logic.
* [daos](container/user_api/daos) - The first part of the lowest layer. This is a fairly structured layer, where each file corresponds to a similarly-named database table. Each file contains a pydantic model, which defines the table columns (field order and types MUST match database). Each model object also defines various methods / classmethods for accomplishing its goals. These methods should receive a database connection and create a database cursor, as database transactions are above the logical responsibility of the DAO objects. These objects should also catch any anticipated exceptions and re-raise as descriptive `InternalError`s.
* [services](container/user_api/services) - The second part of the lowest layer. This layer defines interaction with external APIs. Currently this is only Sendgrid's API, used for sending emails.


## tests

Three kinds of tests are defined in files / folders here:
* [lint](container/tests/lint.sh) - Linting, specifically mypy, black, and flake8 for python and shellcheck for bash.
* [unit](container/tests/unit) - Unit tests for any python stuff here. Should call specific functions, mocking dependencies as needed.
* [integration](container/tests/integ) - Integration tests. Responsible for the integration between the API and its database, and accordingly operate by making HTTP calls to the API REST endpoints and evaluating the responses.


## stubs

These are type stubs for python dependencies without type hinting, allowing us to use `mypy --strict`. These can be a bit lenient for functions we don't often call, but overall should match the library being stubbed as accurately as possible. Currently stubbed libraries are:
* [sendgrid](container/stubs/sendgrid) - Sendgrid email API.
