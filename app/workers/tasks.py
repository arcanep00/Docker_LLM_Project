from app.workers.celery_app import celery

@celery.task
def test_task():
    print("Worker Running")

    return "Done"