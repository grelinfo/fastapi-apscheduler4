from fastapi import FastAPI
from fastapi_apscheduler4 import SchedulerConfig
from fastapi_apscheduler4.app import SchedulerApp
from fastapi_apscheduler4.config import (
    DataStoreType,
    EventBrokerType,
    PostgresConfig,
    RedisConfig,
    SchedulerAPIConfig,
)
from pydantic import SecretStr

scheduler_config = SchedulerConfig(
    auto_start=True,
    event_broker=EventBrokerType.REDIS,
    data_store=DataStoreType.POSTGRES,
)
redis_config = RedisConfig(
    host="localhost",
    username="redis",
    password=SecretStr("postgres"),
    db=0,
)
postgres = PostgresConfig(
    host="localhost",
    username="postgres",
    password=SecretStr("postgres"),
    db="scheduler",
)
api_config = SchedulerAPIConfig(
    enabled=True,
    prefix="/",
    tags=["scheduler"],
    include_in_schema=True,
)

scheduler_app = SchedulerApp(scheduler=scheduler_config, redis=redis_config, postgres=postgres, api=api_config)
app = FastAPI(lifespan=scheduler_app.lifespan)
