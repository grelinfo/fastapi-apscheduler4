from fastapi import FastAPI

from fastapi_apscheduler4 import SchedulerApp

scheduler_app = SchedulerApp()
app = FastAPI(lifespan=scheduler_app.lifespan)


@scheduler_app.interval(seconds=5)
def say_hello_world() -> None:
    print("test1")
