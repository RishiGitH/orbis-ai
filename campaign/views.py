from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Campaign, CampaignPool, CampaignType
from .serializers import CampaignSerializer, CampaignPoolSerializer, CampaignTypeSerializer
from .services import CampaignService

class CampaignTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CampaignType.objects.all()
    serializer_class = CampaignTypeSerializer
    

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    

    def perform_create(self, serializer):
        campaign = CampaignService.create_campaign(
            company=serializer.validated_data['company'],
            campaign_type_id=serializer.validated_data['campaign_type'].id,
            title=serializer.validated_data['title'],
            description=serializer.validated_data['description'],
            total_pool=serializer.validated_data['total_pool'],
            reward_per_task=serializer.validated_data['reward_per_task'],
            campaign_data=serializer.validated_data.get('campaign_data', {})
        )
        serializer.instance = campaign

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        campaign = self.get_object()
        CampaignService.complete_campaign(campaign.id)
        return Response({'status': 'campaign completed'})

    @action(detail=True, methods=['post'])
    def dispute(self, request, pk=None):
        campaign = self.get_object()
        CampaignService.dispute_campaign(campaign.id)
        return Response({'status': 'campaign disputed'})

    @action(detail=True, methods=['post'])
    def create_task(self, request, pk=None):
        campaign = self.get_object()
        task = CampaignService.create_task(campaign.id, request.data)
        return Response({'status': 'task created', 'task_id': task.id})

class CampaignPoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CampaignPool.objects.all()
    serializer_class = CampaignPoolSerializer
    