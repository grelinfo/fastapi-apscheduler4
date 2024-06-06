from fastapi import FastAPI
from fastapi_apscheduler4 import SchedulerApp

from .schedulers import hello

scheduler_app = SchedulerApp()
scheduler_app.include(hello.scheduler)

app = FastAPI(lifespan=scheduler_app.lifespan)
