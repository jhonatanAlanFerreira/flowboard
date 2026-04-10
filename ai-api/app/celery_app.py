from celery import Celery

celery = Celery(
    "app",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    timezone="UTC",
    enable_utc=True,

    task_acks_late=True,             
    worker_prefetch_multiplier=1,   
    task_track_started=True,          

    task_reject_on_worker_lost=True,

    result_expires=3600,            

    broker_transport_options={
        "visibility_timeout": 3600,  
    },
)

celery.conf.task_routes = {
    "app.tasks.chunk_tasks.*": {"queue": "tagging"},
    "app.tasks.generate_collection_workspace_task.*": {"queue": "collection_workspace"},
    "app.tasks.generate_workflow_workspace_task.*": {"queue": "workflow_workspace"},
    "app.tasks.search_strategist_task.*": {"queue": "search_strategist"}
}

celery.autodiscover_tasks(["app.tasks"])