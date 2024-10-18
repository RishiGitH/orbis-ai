from rest_framework import serializers
from .models import Campaign, CampaignPool, CampaignType

class CampaignTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignType
        fields = ['id', 'name', 'description', 'task_schema', 'creation_schema', 'completion_schema', 'review_schema']

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ['id', 'company', 'campaign_type', 'title', 'description', 'total_pool', 'reward_per_task', 'status', 'created_at', 'updated_at', 'campaign_data']

class CampaignPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignPool
        fields = ['id', 'campaign', 'usdc_amount', 'platform_token_amount', 'developer_fee', 'burn_amount']