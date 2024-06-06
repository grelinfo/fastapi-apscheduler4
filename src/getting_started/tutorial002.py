from fastapi import FastAPI
from fastapi_apscheduler4 import SchedulerConfig
from fastapi_apscheduler4.app import SchedulerApp
from fastapi_apscheduler4.config import (
    APIConfig,
    APSchedulerConfig,
    DataStoreType,
    EventBrokerType,
    PostgresConfig,
    RedisConfig,
)
from pydantic import SecretStr

config = SchedulerConfig(
    auto_start=True,
    apscheduler=APSchedulerConfig(
        event_broker=EventBrokerType.REDIS,
        data_store=DataStoreType.POSTGRES,
        postgres=PostgresConfig(
            host="localhost",
            user="postgres",
            password=SecretStr("postgres"),
            db="scheduler",
        ),
        redis=RedisConfig(
            host="localhost",
            user="redis",
            password=SecretStr("postgres"),
            db=0,
        ),
    ),
    api=APIConfig(
        enabled=True,
        prefix="/",
        tags=["scheduler"],
        include_in_schema=True,
        limit_default=500,
        limit_max=1000,
    ),
)

scheduler_app = SchedulerApp(config)
app = FastAPI(lifespan=scheduler_app.lifespan)
