# Release Notes

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
