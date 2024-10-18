from rest_framework import serializers
from .models import Task, Reward, Dispute

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'campaign', 'trainer', 'reviewer', 'task_data', 'result_data', 'review_data', 'status', 'created_at', 'updated_at', 'on_chain_signature']

class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ['id', 'task', 'trainer_reward', 'reviewer_reward', 'is_released']

class DisputeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ['id', 'task', 'company', 'reason', 'status', 'created_at', 'resolved_at']