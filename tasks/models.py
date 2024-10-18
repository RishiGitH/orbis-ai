from django.db import models
from django.db.models import JSONField
from campaign.models import Campaign
from users.models import User

class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('reviewed', 'Reviewed'),
        ('disputed', 'Disputed'),
    )
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    trainer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='trained_tasks')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reviewed_tasks')
    task_data = JSONField(default=dict)
    result_data = JSONField(default=dict)
    review_data = JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    on_chain_signature = models.CharField(max_length=132, null=True, blank=True)

    def __str__(self):
        return f"Task {self.id} for {self.campaign.title}"
        
    def save(self, *args, **kwargs):
        if self.review_data and self.status != 'reviewed':
            self.status = 'reviewed'
        super().save(*args, **kwargs)

class Reward(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    trainer_reward = models.DecimalField(max_digits=18, decimal_places=6)
    reviewer_reward = models.DecimalField(max_digits=18, decimal_places=6)
    is_released = models.BooleanField(default=False)

    def __str__(self):
        return f"Reward for Task {self.task.id}"

class Dispute(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
    )
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    company = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Dispute for Task {self.task.id}"