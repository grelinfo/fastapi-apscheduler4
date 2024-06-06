# Getting Started

## Installation

Installation is as simple as:

=== "pip"

    ```bash
    pip install fastapi-apscheduler4
    ```
=== "rye"

    ```bash
    rye add fastapi-apscheduler4
    ```
=== "poetry"

    ```bash
    poetry add fastapi-apscheduler4
    ```

FastAPI-APScheduler4 has the following main dependencies:

* [FastAPI](https://fastapi.tiangolo.com/)
* [APScheduler v4](https://apscheduler.readthedocs.io/en/master/)
* [Pydantic v2](https://pydantic-docs.helpmanual.io/)
* [Pydantic Settings](https://pydantic-settings.readthedocs.io/en/latest/)

This is not intended to use with earlier versions of APScheduler or Pydantic. The goals is to provide the latest features.

### Optional Dependencies

If you are running FastAPI-APScheduler4 in multiple nodes (i.e. Kubernetes, Docker Swarm, etc.), you must have a shared database to store the scheduled tasks and
a event broker to distribute the tasks between the nodes. Otherwise, the tasks will be executed multiple times.

Currently the following dependencies are supported:

* **[SQLAlchemy](https://www.sqlalchemy.org/)**: Needed for APScheduler data store.
* **[Redis](https://redis.io/)**: Needed for APScheduler event broker.

=== "pip"


    ```bash
    pip install sqlalchemy redis
    ```

=== "rye"

    ```bash
    rye add sqlalchemy redis
    ```

=== "poetry"

    ```bash
    poetry add sqlalchemy redis
    ```

## Usage


Quick start with configuration from environment variables:

```python
{!> src/getting_started/tutorial001.py!}
```

## Configuration

The following configuration options are available.

=== "Environment Variables"

    General:

    * **`SCHEDULER_AUTO_START`**: If `True`, the scheduler will start automatically with FastAPI. Default is `True`.
    * **`SCHEDULER_EVENT_BROKER`**: The event broker to use. By default, it will be selected automatically.
    * **`SCHEDULER_DATA_STORE`**: The data store to use. By default, it will be selected automatically.

    Scheduler API:

    * **`SCHEDULER_API_ENABLED`**: If `True`, the API routes will be added. Default is `True`.
    * **`SCHEDULER_API_PREFIX`**: The API prefix. Default is `/api/v1/`.
    * **`SCHEDULER_API_TAGS`**: The API tags. Default is `scheduler`.
    * **`SCHEDULER_API_LIMIT_DEFAULT`**: The API pagination default limit. Default is `100`.
    * **`SCHEDULER_API_LIMIT_MAX`**: The API pagination max limit. Default is `1000`.
    * **`SCHEDULER_API_INCLUDE_IN_SCHEMA`**: If `True`, the API will be included in the schema. Default is `True`.

    PostgreSQL:

    * **`POSTGRES_HOST`**: The PostgreSQL host.
    * **`POSTGRES_PORT`**: The PostgreSQL port. Default is `5432`.
    * **`POSTGRES_USER`**: The PostgreSQL user.
    * **`POSTGRES_PASSWORD`**: The PostgreSQL password.
    * **`POSTGRES_DB`**: The PostgreSQL database.

    Redis:

    * **`REDIS_HOST`**: The Redis host.
    * **`REDIS_PORT`**: The Redis port. Default is `6379`.
    * **`REDIS_USER`**: The Redis user.
    * **`REDIS_PASSWORD`**: The Redis password.
    * **`REDIS_DB`**: The Redis database.
    * **`SCHEDULER_REDIS_CHANNEL`**: The Redis channel. Default is `apscheduler`.

=== "Configuration models"

    The configuration models are available in the `fastapi_apscheduler.config` module.

    * **`SchedulerConfig`**: The main configuration model.
    * **`SchedulerAPIConfig`**: The API configuration model.
    * **`PostgresConfig`**: The PostgreSQL configuration model.
    * **`RedisConfig`**: The Redis configuration model.
    * **`RedisChannelConfig`**: The Redis channel configuration model when providing a redis client.

    You can use these models to create your own configuration.

    Example:

    ```python
    {!> src/getting_started/tutorial002.py!}
    ```
