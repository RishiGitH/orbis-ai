from django.db import models
from django.db.models import JSONField
from users.models import User

class CampaignType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    task_schema = JSONField()
    creation_schema = JSONField()
    completion_schema = JSONField()
    review_schema = JSONField()

    def __str__(self):
        return self.name

class Campaign(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('disputed', 'Disputed'),
    )
    
    company = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign_type = models.ForeignKey(CampaignType, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    total_pool = models.DecimalField(max_digits=18, decimal_places=6)
    reward_per_task = models.DecimalField(max_digits=18, decimal_places=6)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    campaign_data = JSONField(default=dict)

    def __str__(self):
        return self.title

class CampaignPool(models.Model):
    campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE)
    usdc_amount = models.DecimalField(max_digits=18, decimal_places=6)
    platform_token_amount = models.DecimalField(max_digits=18, decimal_places=6)
    developer_fee = models.DecimalField(max_digits=18, decimal_places=6)
    burn_amount = models.DecimalField(max_digits=18, decimal_places=6)

    def __str__(self):
        return f"Pool for {self.campaign.title}"