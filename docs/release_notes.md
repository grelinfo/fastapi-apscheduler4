# Release Notes

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
