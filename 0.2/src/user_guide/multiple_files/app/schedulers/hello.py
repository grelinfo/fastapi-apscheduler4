from fastapi_apscheduler4 import Scheduler

scheduler = Scheduler()


@scheduler.interval(seconds=5)
def hello() -> None:
    print("Hello, world!")
