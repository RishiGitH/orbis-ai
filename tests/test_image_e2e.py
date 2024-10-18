import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User
from campaign.models import CampaignType, Campaign
from tasks.models import Task
import json
import tempfile
from PIL import Image
import io

@pytest.mark.django_db
class TestE2EWorkflow:
    def setup_method(self, method):
        self.client = APIClient()
        self.company = User.objects.create(
            username='company1',
            wallet_address='0x1234567890123456789012345678901234567890',
            user_type='company'
        )
        self.trainer = User.objects.create(
            username='trainer1',
            wallet_address='0x0987654321098765432109876543210987654321',
            user_type='trainer'
        )
        self.reviewer = User.objects.create(
            username='reviewer1',
            wallet_address='0x1111111111111111111111111111111111111111',
            user_type='reviewer'
        )
        
        self.image_labeling_type = CampaignType.objects.create(
            name="Image Labeling",
            description="Label images with predefined tags and attributes",
            task_schema={
                "image": {"type": "file", "formats": ["jpg", "png"]},
                "available_tags": {"type": "array", "items": {"type": "string"}}
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

        self.text_classification_type = CampaignType.objects.create(
            name="Text Classification",
            description="Classify text into predefined categories",
            task_schema={
                "text": {"type": "string"},
                "categories": {"type": "array", "items": {"type": "string"}}
            },
            creation_schema={
                "available_categories": {"type": "array", "items": {"type": "string"}}
            },
            completion_schema={
                "selected_category": {"type": "string"}
            },
            review_schema={
                "accuracy": {"type": "integer", "minimum": 1, "maximum": 5},
                "comment": {"type": "string"}
            }
        )

    def test_image_labeling_workflow(self):
        # Create campaign
        campaign_data = {
            "campaign_type": self.image_labeling_type.id,
            "company": self.company.id,
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

        # Create task with image upload
        image = Image.new('RGB', (100, 100), color='red')
        img_file = io.BytesIO()
        image.save(img_file, format='JPEG')
        img_file.seek(0)

        task_data = {
                "campaign": campaign_id,
                "available_tags": ["lion", "elephant", "giraffe", "zebra", "rhino"]
        }
        task_data['image'] = img_file

        response = self.client.post(reverse('task-list'), data=task_data, format='multipart')
        print("image_upload_response",response.data)
        assert response.status_code == status.HTTP_201_CREATED
        task_id = response.data['id']

        # Trainer completes the task
        completion_data = {
            "trainer": self.trainer.id,
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
        response = self.client.post(reverse('task-complete', kwargs={'pk': task_id}), data=json.dumps(completion_data), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK

        # Reviewer reviews the task
        review_data = {
            "reviewer": self.reviewer.id,
            "review_data": {
                "accuracy_rating": 4,
                "completeness_rating": 5,
                "feedback": "Good job identifying the animals and their activities."
            }
        }
        response = self.client.post(reverse('task-review', kwargs={'pk': task_id}), data=json.dumps(review_data), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK

        # Verify final states
        response = self.client.get(reverse('task-detail', kwargs={'pk': task_id}))
        assert response.status_code == status.HTTP_200_OK
        task_data = response.data
        assert task_data['status'] == 'reviewed'

    def test_text_classification_workflow(self):

        # Create campaign
        campaign_data = {
            "campaign_type": self.text_classification_type.id,
            "company": self.company.id,
            "title": "Sentiment Analysis",
            "description": "Classify text sentiment",
            "total_pool": "1000.00",
            "reward_per_task": "0.50",
            "campaign_data": {
                "available_categories": ["positive", "neutral", "negative"]
            }
        }
        response = self.client.post(reverse('campaign-list'), data=json.dumps(campaign_data), content_type='application/json')
        print("response",response.data)
        assert response.status_code == status.HTTP_201_CREATED
        campaign_id = response.data['id']

        # Create task
        task_data = {
            "campaign": campaign_id,
            "task_data": {
                "text": "I love this product!",
                "categories": ["positive", "neutral", "negative"]
            }
        }
        response = self.client.post(reverse('task-list'), data=json.dumps(task_data), content_type='application/json')
        print("response",response.data)
        assert response.status_code == status.HTTP_201_CREATED
        task_id = response.data['id']

        # Trainer completes the task
        completion_data = {
            "trainer": self.trainer.id,
            "result_data": {
                "selected_category": "positive"
            }
        }
        response = self.client.post(reverse('task-complete', kwargs={'pk': task_id}), data=json.dumps(completion_data), content_type='application/json')
        print("response",response.data)
        assert response.status_code == status.HTTP_200_OK

        # Reviewer reviews the task
        review_data = {
            "reviewer": self.reviewer.id,
            "review_data": {
                "accuracy": 5,
                "comment": "Correct classification."
            }
        }
        response = self.client.post(reverse('task-review', kwargs={'pk': task_id}), data=json.dumps(review_data), content_type='application/json')
        print("response",response.data)
        assert response.status_code == status.HTTP_200_OK

        # Verify final states
        response = self.client.get(reverse('task-detail', kwargs={'pk': task_id}))
        print("response",response.data)
        assert response.status_code == status.HTTP_200_OK
        task_data = response.data
        assert task_data['status'] == 'reviewed'