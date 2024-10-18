import random
from django.db import transaction
from .models import Task, Reward, Dispute
from campaign.models import Campaign
from users.models import User

class TaskService:
    @staticmethod
    @transaction.atomic
    def create_task(campaign: Campaign, data: dict):
        task = Task.objects.create(
            campaign=campaign,
            data=data
        )
        return task

    @staticmethod
    @transaction.atomic
    def complete_task(task_id: int, trainer: User, result: dict, on_chain_signature: str):
        task = Task.objects.get(id=task_id)
        task.trainer = trainer
        task.result = result
        task.status = 'completed'
        task.on_chain_signature = on_chain_signature
        task.save()

        # Randomly select 10% of tasks for review
        if random.random() < 0.1:
            task.status = 'reviewed'
            task.save()
            # TODO: Implement logic to assign a reviewer

        reward = task.campaign.reward_per_task
        Reward.objects.create(
            task=task,
            trainer_reward=reward * 0.3,
            reviewer_reward=reward * 0.45
        )

        return task

    @staticmethod
    @transaction.atomic
    def review_task(task_id: int, reviewer: User, is_approved: bool):
        task = Task.objects.get(id=task_id)
        task.reviewer = reviewer
        task.status = 'reviewed'
        task.save()

        if not is_approved:
            # TODO: Implement logic for handling disapproved tasks
            pass

        return task

    @staticmethod
    @transaction.atomic
    def create_dispute(task_id: int, company: User, reason: str):
        task = Task.objects.get(id=task_id)
        dispute = Dispute.objects.create(
            task=task,
            company=company,
            reason=reason
        )
        task.status = 'disputed'
        task.save()

        return dispute

    @staticmethod
    @transaction.atomic
    def resolve_dispute(dispute_id: int, is_approved: bool):
        dispute = Dispute.objects.get(id=dispute_id)
        dispute.status = 'resolved'
        dispute.save()

        if not is_approved:
            # TODO: Implement logic for slashing stakes and updating rewards
            pass

        return dispute

class RewardService:
    @staticmethod
    @transaction.atomic
    def release_rewards(campaign_id: int):
        campaign = Campaign.objects.get(id=campaign_id)
        rewards = Reward.objects.filter(task__campaign=campaign, is_released=False)

        for reward in rewards:
            reward.is_released = True
            reward.save()

            # TODO: Implement logic to transfer rewards to users' wallets

        return rewards