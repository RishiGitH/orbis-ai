import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User
from campaign.models import CampaignType, Campaign
from tasks.models import Task
import json

@pytest.mark.django_db
class TestE2EWorkflow:
    def setup_method(self, method):
        self.client = APIClient()
        # Create a campaign type directly in the database
        self.campaign_type = CampaignType.objects.create(
            name="Image Labeling",
            description="Label images with predefined tags and attributes",
            task_schema={
                "image_url": {"type": "string", "format": "uri"},
                "available_tags": {"type": "array", "items": {"type": "string"}},
                "attributes": {"type": "object"}
            },
            creation_schema={
                "available_tags": {"type": "array", "items": {"type": "string"}},
                "attributes": {"type": "object"}
            },
            completion_schema={
                "selected_tags": {"type": "array", "items": {"type": "string"}},
                "attribute_values": {"type": "object"}
            },
            review_schema={
                "accuracy_rating": {"type": "integer", "minimum": 1, "maximum": 5},
                "completeness_rating": {"type": "integer", "minimum": 1, "maximum": 5},
                "feedback": {"type": "string"}
            }
        )

    def test_complete_workflow(self):
        # Step 1: Create users
        company_data = {
            "username": "company1",
            "wallet_address": "0x1234567890123456789012345678901234567890",
            "user_type": "company"
        }
        response = self.client.post(reverse('user-list'), data=json.dumps(company_data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        company_id = response.data['id']

        trainer_data = {
            "username": "trainer1",
            "wallet_address": "0x0987654321098765432109876543210987654321",
            "user_type": "trainer"
        }
        response = self.client.post(reverse('user-list'), data=json.dumps(trainer_data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        trainer_id = response.data['id']

        reviewer_data = {
            "username": "reviewer1",
            "wallet_address": "0x1111111111111111111111111111111111111111",
            "user_type": "reviewer"
        }
        response = self.client.post(reverse('user-list'), data=json.dumps(reviewer_data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        reviewer_id = response.data['id']

        # Step 2: Create a campaign
        campaign_data = {
            "campaign_type": self.campaign_type.id,
            "company": company_id,
            "title": "Wildlife Image Labeling",
            "description": "Label wildlife images with species and attributes",
            "total_pool": "5000.00",
            "reward_per_task": "2.50",
            "campaign_data": {
                "available_tags": ["lion", "elephant", "giraffe", "zebra", "rhino"],
                "attributes": {
                    "age": ["young", "adult", "old"],
                    "activity": ["resting", "feeding", "moving"]
                }
            }
        }
        response = self.client.post(reverse('campaign-list'), data=json.dumps(campaign_data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        campaign_id = response.data['id']

        # Step 3: Create a task
        task_data = {
            "campaign": campaign_id,
            "task_data": {
                "image_url": "https://example.com/wildlife-image-1.jpg",
                "available_tags": ["lion", "elephant", "giraffe", "zebra", "rhino"],
                "attributes": {
                    "age": ["young", "adult", "old"],
                    "activity": ["resting", "feeding", "moving"]
                }
            }
        }
        response = self.client.post(reverse('task-list'), data=json.dumps(task_data), content_type='application/json')
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        task_id = response.data['id']

        # Step 4: Trainer completes the task
        completion_data = {
            "trainer": trainer_id,
            "result_data": {
                "selected_tags": ["elephant", "zebra"],
                "attribute_values": {
                    "age": {
                        "elephant": "adult",
                        "zebra": "young"
                    },
                    "activity": {
                        "elephant": "feeding",
                        "zebra": "moving"
                    }
                }
            }
        }
        response = self.client.patch(reverse('task-detail', kwargs={'pk': task_id}), data=json.dumps(completion_data), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK

        # Step 5: Reviewer reviews the task
        review_data = {
            "reviewer": reviewer_id,
            "review_data": {
                "accuracy_rating": 4,
                "completeness_rating": 5,
                "feedback": "Good job identifying the animals and their activities. The age estimation for the elephant looks accurate."
            }
        }
        response = self.client.patch(reverse('task-detail', kwargs={'pk': task_id}), data=json.dumps(review_data), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK

        # Step 6: Verify final states
        response = self.client.get(reverse('task-detail', kwargs={'pk': task_id}))
        assert response.status_code == status.HTTP_200_OK
        task_data = response.data
        assert task_data['status'] == 'reviewed'
        assert task_data['result_data'] == completion_data['result_data']
        assert task_data['review_data'] == review_data['review_data']

        # Step 7: Complete the campaign
        response = self.client.post(reverse('campaign-complete', kwargs={'pk': campaign_id}))
        assert response.status_code == status.HTTP_200_OK

        # Step 8: Verify campaign status
        response = self.client.get(reverse('campaign-detail', kwargs={'pk': campaign_id}))
        assert response.status_code == status.HTTP_200_OK
        campaign_data = response.data
        assert campaign_data['status'] == 'completed'

        # Step 9: Create a dispute
        dispute_data = {
            "task": task_id,
            "company": company_id,
            "reason": "Inaccurate labeling of zebra's age"
        }
        response = self.client.post(reverse('dispute-list'), data=json.dumps(dispute_data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        dispute_id = response.data['id']

        # Step 10: Resolve the dispute
        resolve_data = {
            "status": "resolved"
        }
        response = self.client.patch(reverse('dispute-detail', kwargs={'pk': dispute_id}), data=json.dumps(resolve_data), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK

        # Step 11: Verify dispute resolution
        response = self.client.get(reverse('dispute-detail', kwargs={'pk': dispute_id}))
        assert response.status_code == status.HTTP_200_OK
        dispute_data = response.data
        assert dispute_data['status'] == 'resolved'

        # You can add more assertions here to check user balances, stakes, or campaign pool distribution

        # Step 12: Verify dispute resolution
        response = self.client.get(reverse('dispute-detail', kwargs={'pk': dispute_id}))
        assert response.status_code == status.HTTP_200_OK
        dispute_data = response.data
        assert dispute_data['status'] == 'resolved'

        # Step 13: Check user balances or stakes (if implemented)
        response = self.client.get(reverse('user-detail', kwargs={'pk': trainer_id}))
        assert response.status_code == status.HTTP_200_OK
        trainer_data = response.data
        # Assert trainer's balance or stake has increased 

        response = self.client.get(reverse('user-detail', kwargs={'pk': reviewer_id}))
        assert response.status_code == status.HTTP_200_OK
        reviewer_data = response.data
        # Assert reviewer's balance or stake has increased 

        # Step 14: Verify campaign pool distribution (if implemented)
        response = self.client.get(reverse('campaign-detail', kwargs={'pk': campaign_id}))
        assert response.status_code == status.HTTP_200_OK
        campaign_data = response.data
        # Assert campaign pool 
