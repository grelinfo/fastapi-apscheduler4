# Release Notes

## 0.3.2

### Fixes

* 🐛 Add `sniffio` to the `postgres` extra. APScheduler 4.0.0a6 imports it in its
  SQLAlchemy data store without declaring it, and recent `anyio` releases no longer
  pull it in, so `fastapi-apscheduler4[postgres]` failed to import on a fresh install.

### Internal

* ⬆️ Upgrade the lockfile with 43 dependency updates, including ty 0.0.13 to 0.0.69,
  pydantic 2.12.4 to 2.13.4, sqlalchemy 2.0.46 to 2.0.51 and starlette 1.3.1 to 1.4.1
* 🏷️ Replace a leftover mypy `type: ignore` with the ty equivalent
* 🩹 Use `testcontainers.community.postgres` to fix a deprecation warning
* 👷 Run ruff in the CI lint job, which previously only ran the type checker
* 🚨 Ignore `CPY001` and allow the extra positional argument on `cron` for ruff 0.16

## 0.3.1

No source changes. Documentation and dependency refresh only.

### Docs

* 📝 Add grelmicro related project section
* 📝 Note APScheduler 4 has not released since 4.0.0a6 (April 2025)
* ✏️ Fix documentation typo

### Internal

* ⬆️ Bump codecov/codecov-action from 5 to 6
* ⬆️ Bump fastapi from 0.124.4 to 0.128.0
* ⬆️ Bump sqlalchemy from 2.0.45 to 2.0.46
* ⬆️ Bump pydantic-extra-types from 2.10.6 to 2.11.0
* ⬆️ Bump ruff from 0.14.9 to 0.14.14
* ⬆️ Bump pre-commit from 4.5.0 to 4.5.1
* 🔒️ Bump pygments to 2.20.0 to fix a ReDoS advisory
* 🔒️ Bump the uv group with 7 updates, closing starlette, urllib3, idna,
  pydantic-settings, pymdown-extensions and python-dotenv advisories
* 🔧 Add step to fetch and merge remote gh-pages in release workflow
* ⬆️ Align ruff and uv pre-commit hooks with the project versions
* 👷 Add the pre-commit ecosystem to Dependabot updates

## 0.3.0

### Features

* 🦺 Add model validator to ensure pagination limits are respected
* ✨ Add optional dependencies for PostgreSQL and Redis
* 📌 Update apscheduler dependency to allow for minor version updates

### Fixes

* 🐛 Fix tasks router list endpoint calling wrong method
* 🐛 Fix conditional auto-start for APScheduler in SchedulerApp
* 🩹 Fix testcontainers deprecation warnings

### Internal

* ♻️ Refactor tests: consolidate and enhance integration and unit tests
* ♻️ Extract API pagination limits and SCHEDULE_PREFIX constant to constants.py
* ♻️ Refactor Import Error with MissingDependencyError
* 🏷️ Remove all type ignore comments by fixing underlying type issues
* 👷 Replace mypy with Astral ty for the type checker
* 👷 Add flags to Codecov uploads for better coverage tracking
* 👷 Organize ruff configuration and rearrange import statements
* 👷 Refactor integration tests step in CI workflow
* 💚 Update release workflow and CI formatting
* 🙈 Update .gitignore
* ➖ Remove typer dependency from development requirements
 ⬆️ Bump pytest, ruff, fastapi, sqlalchemy, and uv dependencies
 * 🔧 Update default Python version to 3.14 in pre-commit configuration

### Docs

* ✏️ Fix typos in README.md and code comments

## 0.2.0

### Features

* 📌 Upgrade APScheduler to v4.0.0a6 by [@grelinfo](https://github.com/grelinfo) in [#8](https://github.com/grelinfo/fastapi-apscheduler4/pull/8)

### Internal

* 🧱 Replace Rye with UV as build tool by [@grelinfo](https://github.com/grelinfo) in [#2](https://github.com/grelinfo/fastapi-apscheduler4/pull/2)
* 👷 Add Dependabot config by [@grelinfo](https://github.com/grelinfo) in [#3](https://github.com/grelinfo/fastapi-apscheduler4/pull/3)
* 👷 Add CI workflow for linting and testing with UV by [@grelinfo](https://github.com/grelinfo) in [#6](https://github.com/grelinfo/fastapi-apscheduler4/pull/6)
* 👷 Refactor CI workflows and release process by [@grelinfo](https://github.com/grelinfo) in [#7](https://github.com/grelinfo/fastapi-apscheduler4/pull/7)

## 0.1.0

### Breaking Changes

* 🔥 Change the config models to simplify the environment variables configuration.
* 🔥 Change the `SchedulerApp` class to simplify the initialization.

### Features

* ✨ Add `APSchedulerBuilder` class to simplify the initialization of the `AsyncScheduler` of APScheduler.
* ✨ Add support for both USER and USERNAME environment variables for PostgreSQL and Redis (e.g., `POSTGRES_USER` and `POSTGRES_USERNAME`).

### Docs

* 📝 Add this release notes file.
* 📝 Update the documentation to the new configuration models and `SchedulerApp` class.

## 0.0.9

This is the first public release of the project.
