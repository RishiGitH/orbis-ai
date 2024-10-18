from celery import shared_task
from .models import Task
from .services import TaskService

@shared_task
def process_completed_tasks():
    completed_tasks = Task.objects.filter(status='completed')
    for task in completed_tasks:
        TaskService.review_task(task.id, None, True)  # Auto-approve tasks for now

@shared_task
def release_rewards(campaign_id):
    from .services import RewardService
    RewardService.release_rewards(campaign_id)