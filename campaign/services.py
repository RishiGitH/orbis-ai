from decimal import Decimal
from django.db import transaction
from .models import Campaign, CampaignPool, CampaignType
from users.models import User
from tasks.models import Task
import boto3
import json

class CampaignService:
    @staticmethod
    @transaction.atomic
    def create_campaign(company: User, campaign_type_id: int, title: str, description: str, total_pool: Decimal, reward_per_task: Decimal, campaign_data: dict):
        campaign_type = CampaignType.objects.get(id=campaign_type_id)
        
        campaign = Campaign.objects.create(
            company=company,
            campaign_type=campaign_type,
            title=title,
            description=description,
            total_pool=total_pool,
            reward_per_task=reward_per_task,
            campaign_data=campaign_data
        )
        
        developer_fee = total_pool * Decimal('0.1')
        burn_amount = total_pool * Decimal('0.1')
        remaining_pool = total_pool - developer_fee - burn_amount
        
        CampaignPool.objects.create(
            campaign=campaign,
            usdc_amount=remaining_pool * Decimal('0.5'),
            platform_token_amount=remaining_pool * Decimal('0.5'),
            developer_fee=developer_fee,
            burn_amount=burn_amount
        )
        
        return campaign

    @staticmethod
    def complete_campaign(campaign_id: int):
        campaign = Campaign.objects.get(id=campaign_id)
        campaign.status = 'completed'
        campaign.save()
        
        # TODO: Implement logic to release staked rewards

    @staticmethod
    def dispute_campaign(campaign_id: int):
        campaign = Campaign.objects.get(id=campaign_id)
        campaign.status = 'disputed'
        campaign.save()
        
        # TODO: Implement logic to handle disputes

    @staticmethod
    def get_campaign_types():
        return CampaignType.objects.all()

    @staticmethod
    def create_task(campaign_id: int, task_data: dict):
        campaign = Campaign.objects.get(id=campaign_id)
        task_schema = campaign.campaign_type.task_schema

        # Validate task_data against task_schema
        # TODO: Implement proper validation

        # Handle file uploads
        for field, value in task_data.items():
            if task_schema[field].get('type') == 'file':
                file_content = value.read()
                s3_client = boto3.client('s3')
                s3_key = f"campaigns/{campaign_id}/tasks/{field}/{value.name}"
                s3_client.put_object(Bucket='your-s3-bucket-name', Key=s3_key, Body=file_content)
                task_data[field] = s3_key

        task = Task.objects.create(
            campaign=campaign,
            task_data=task_data
        )
        return task

    @staticmethod
    def complete_task(task_id: int, trainer: User, result_data: dict):
        task = Task.objects.get(id=task_id)
        completion_schema = task.campaign.campaign_type.completion_schema

        # Validate result_data against completion_schema
        # TODO: Implement proper validation

        task.trainer = User.objects.get(id=trainer)
        task.result_data = result_data
        task.status = 'completed'
        task.save()

        return task

    @staticmethod
    def review_task(task_id: int, reviewer: User, review_data: dict):
        task = Task.objects.get(id=task_id)
        review_schema = task.campaign.campaign_type.review_schema

        # Validate review_data against review_schema
        # TODO: Implement proper validation

        task.reviewer = User.objects.get(id=reviewer)
        task.review_data = review_data
        task.status = 'reviewed'
        task.save()

        return task