import os
import django
import random
from django.utils import timezone
from decimal import Decimal

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orbis_ai.settings")
django.setup()

from users.models import User
from campaign.models import CampaignType, Campaign
from tasks.models import Task, Dispute

def create_users():
    user_types = [
        ('company', 5),
        ('trainer', 20),
        ('reviewer', 10)
    ]
    users = []
    for user_type, count in user_types:
        for i in range(count):
            user = User.objects.create(
                username=f"{user_type}{i+1}",
                wallet_address=f"0x{os.urandom(20).hex()}",
                user_type=user_type
            )
            users.append(user)
    print(f"Created {len(users)} users")
    return users

def create_campaign_types():
    code_review_type = CampaignType.objects.create(
        name="Code Review",
        description="Review code snippets for quality and best practices",
        task_schema={
            "code_snippet": {"type": "string"},
            "language": {"type": "string"},
            "prompt1": {"type": "string"},
            "prompt2": {"type": "string"}
        },
        creation_schema={
            "supported_languages": {"type": "array", "items": {"type": "string"}}
        },
        completion_schema={
            "rating1": {"type": "integer", "minimum": 1, "maximum": 10},
            "rating2": {"type": "integer", "minimum": 1, "maximum": 10},
            "comment1": {"type": "string"},
            "comment2": {"type": "string"},
            "overall_feedback": {"type": "string"}
        },
        review_schema={
            "review_quality_rating": {"type": "integer", "minimum": 1, "maximum": 5},
            "feedback_quality_rating": {"type": "integer", "minimum": 1, "maximum": 5},
            "reviewer_comment": {"type": "string"}
        }
    )

    image_labeling_type = CampaignType.objects.create(
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
    
    print("Created 2 campaign types")
    return [code_review_type, image_labeling_type]

def create_campaigns(campaign_types, companies):
    campaigns = []
    
    # Code Review Campaign
    code_campaign = Campaign.objects.create(
        campaign_type=campaign_types[0],
        company=random.choice(companies),
        title="Python Code Quality Review",
        description="Review Python code snippets for quality, efficiency, and adherence to PEP 8",
        total_pool=Decimal('10000.00'),
        reward_per_task=Decimal('5.00'),
        campaign_data={
            "supported_languages": ["python"],
            "focus_areas": ["efficiency", "readability", "best practices"]
        }
    )
    campaigns.append(code_campaign)

    # Image Labeling Campaign
    image_campaign = Campaign.objects.create(
        campaign_type=campaign_types[1],
        company=random.choice(companies),
        title="Wildlife Image Classification",
        description="Label wildlife images with species and attributes",
        total_pool=Decimal('5000.00'),
        reward_per_task=Decimal('2.50'),
        campaign_data={
            "available_tags": ["lion", "elephant", "giraffe", "zebra", "rhino"],
            "attributes": {
                "age": ["young", "adult", "old"],
                "activity": ["resting", "feeding", "moving"]
            }
        }
    )
    campaigns.append(image_campaign)
    
    print(f"Created {len(campaigns)} campaigns")
    return campaigns

def create_tasks(campaigns, trainers, reviewers):
    tasks = []
    
    # Code Review Tasks
    code_snippets = [
        ("""
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
        """, "Evaluate the code's efficiency. Suggest improvements if necessary.",
            "Assess the code's readability and adherence to PEP 8 guidelines."),
        ("""
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

print(quicksort([3, 6, 8, 10, 1, 2, 1]))
        """, "Analyze the time and space complexity of this quicksort implementation.",
            "Suggest potential optimizations or alternative sorting algorithms."),
    ]
    
    for snippet, prompt1, prompt2 in code_snippets:
        task = Task.objects.create(
            campaign=campaigns[0],
            task_data={
                "code_snippet": snippet,
                "language": "python",
                "prompt1": prompt1,
                "prompt2": prompt2
            }
        )
        tasks.append(task)
    
    # Image Labeling Tasks
    image_urls = [
        "https://example.com/wildlife/image1.jpg",
        "https://example.com/wildlife/image2.jpg",
        "https://example.com/wildlife/image3.jpg",
    ]
    
    for url in image_urls:
        task = Task.objects.create(
            campaign=campaigns[1],
            task_data={
                "image_url": url,
                "available_tags": campaigns[1].campaign_data["available_tags"],
                "attributes": campaigns[1].campaign_data["attributes"]
            }
        )
        tasks.append(task)
    
    # Simulate task completion and review for some tasks
    for task in tasks[:3]:
        task.trainer = random.choice(trainers)
        if task.campaign.campaign_type.name == "Code Review":
            task.result_data = {
                "rating1": random.randint(1, 10),
                "rating2": random.randint(1, 10),
                "comment1": "The code could be more efficient. Consider using dynamic programming.",
                "comment2": "Good adherence to PEP 8, but docstrings could be improved.",
                "overall_feedback": "Solid implementation, but there's room for optimization."
            }
        else:  # Image Labeling
            task.result_data = {
                "selected_tags": random.sample(task.task_data["available_tags"], 2),
                "attribute_values": {
                    "age": random.choice(task.task_data["attributes"]["age"]),
                    "activity": random.choice(task.task_data["attributes"]["activity"])
                }
            }
        task.status = 'completed'
        task.save()

        # Add review
        task.reviewer = random.choice(reviewers)
        if task.campaign.campaign_type.name == "Code Review":
            task.review_data = {
                "review_quality_rating": random.randint(1, 5),
                "feedback_quality_rating": random.randint(1, 5),
                "reviewer_comment": "Thorough review with good suggestions for improvement."
            }
        else:  # Image Labeling
            task.review_data = {
                "accuracy_rating": random.randint(1, 5),
                "completeness_rating": random.randint(1, 5),
                "feedback": "Good identification of species and attributes."
            }
        task.status = 'reviewed'
        task.save()
    
    print(f"Created {len(tasks)} tasks, with {len([t for t in tasks if t.status == 'reviewed'])} reviewed")
    return tasks

def create_disputes(tasks, companies):
    disputes = []
    for task in random.sample(list(Task.objects.filter(status='reviewed')), 2):
        dispute = Dispute.objects.create(
            task=task,
            company=random.choice(companies),
            reason="Disagreement with the review assessment",
            status=random.choice(['pending', 'resolved'])
        )
        disputes.append(dispute)
    print(f"Created {len(disputes)} disputes")
    return disputes

if __name__ == "__main__":
    users = create_users()
    companies = [user for user in users if user.user_type == 'company']
    trainers = [user for user in users if user.user_type == 'trainer']
    reviewers = [user for user in users if user.user_type == 'reviewer']
    
    campaign_types = create_campaign_types()
    campaigns = create_campaigns(campaign_types, companies)
    tasks = create_tasks(campaigns, trainers, reviewers)
    disputes = create_disputes(tasks, companies)
    
    print("Seed data creation completed")