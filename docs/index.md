# fastapi-apscheduler4

FastAPI-APScheduler4 is a simple scheduled task manager for FastAPI based on APScheduler version 4.

[![PyPI - Version](https://img.shields.io/pypi/v/fastapi-apscheduler4)](https://pypi.org/project/fastapi-apscheduler4/)
[![PyPI - License](https://img.shields.io/pypi/l/fastapi-apscheduler4)](https://pypi.org/project/fastapi-apscheduler4/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fastapi-apscheduler4)](https://pypi.org/project/fastapi-apscheduler4/)
[![codecov](https://codecov.io/gh/grelinfo/fastapi-apscheduler4/branch/main/graph/badge.svg?token=UFQATSECSO)](https://codecov.io/gh/grelinfo/fastapi-apscheduler4)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)

---

**Documentation**: [https://grelinfo.github.io/fastapi-apscheduler4/](https://grelinfo.github.io/fastapi-apscheduler4/)

**Source Code**: [https://github.com/grelinfo/fastapi-apscheduler4](https://github.com/grelinfo/fastapi-apscheduler4)

---

The key feature are:

* **Easy**: Just add a decorator to your function and it will be scheduled.
* **No boilerplate**: Few lines of code to make it work.
* **Out-of-the-box**: Configuration can be done directly from environment variables (Twelve-Factor App standard).

## 🚧 WORK IN PROGRESS 🚧

The project is still in development and not ready for production. The API may change in the future.
Specifically, because APScheduler main dependency is not yet released and ready for production too.

APScheduler 4 has not moved since **4.0.0a6, released in April 2025**. No newer 4.x release has
been published since, so this project stays on that alpha and remains on hold until upstream ships
a stable 4.0.

Contributions are welcome! Feel free to open an issue or a pull request.

## 🚀 Related project

**[grelmicro](https://github.com/grelinfo/grelmicro)** — *Async-first toolkit. Microservice patterns inside.*

Distributed locks, cache, rate limiting, circuit breakers, transactional outbox, and observability for Python. Includes a [small task scheduler](https://grelmicro.grel.info/task/) too. ⏰
