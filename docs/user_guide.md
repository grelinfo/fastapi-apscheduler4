# User Guide

This user guide shows you how to use FastAPI-APScheduler4 with most of its features.

## Multiple Files

If you are building an application with multiple files, you can use the `Scheduler` class to manage the scheduled tasks.

```python title="app/schedulers/hello.py"
{!> src/user_guide/multiple_files/app/schedulers/hello.py !}
```

Just need  to import the `Scheduler` and include it in the `SchedulerApp`.

```python title="app/main.py"
{!> src/user_guide/multiple_files/app/main.py !}
```
