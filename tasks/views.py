from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task, Reward, Dispute
from .serializers import TaskSerializer, RewardSerializer, DisputeSerializer
from campaign.services import CampaignService
from rest_framework.parsers import MultiPartParser, JSONParser
from campaign.models import Campaign
from utils.s3_utils import upload_file_to_s3
import json
import uuid


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    parser_classes = (MultiPartParser, JSONParser)

    def create(self, request, *args, **kwargs):
        data = request.data
        campaign_id = data.get('campaign')
        if not campaign_id:
            return Response({'error': 'Campaign ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            return Response({'error': 'Invalid campaign ID'}, status=status.HTTP_400_BAD_REQUEST)

        task_schema = campaign.campaign_type.task_schema
        task_data = {}

        for field, field_schema in task_schema.items():
            if field_schema.get('type') == 'file':
                file = request.FILES.get(field)
                if file:
                    s3_url = upload_file_to_s3(file,file.name+'_'+campaign_id+'_'+str(uuid.uuid4()))
                    if not s3_url:
                        return Response({'error': f'Failed to upload {field}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    task_data[field] = s3_url
                else:
                    task_data[field] = data.get(field)
            else:
                task_data[field] = data.get(field)

        serializer = self.get_serializer(data={'campaign': campaign.id, 'task_data': task_data})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        completed_task = CampaignService.complete_task(
            task_id=task.id,
            trainer=request.data['trainer'],
            result_data=request.data
        )
        serializer = self.get_serializer(completed_task)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        task = self.get_object()
        reviewed_task = CampaignService.review_task(
            task_id=task.id,
            reviewer=request.data['reviewer'],
            review_data=request.data
        )
        serializer = self.get_serializer(reviewed_task)
        return Response(serializer.data)

class RewardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    

class DisputeViewSet(viewsets.ModelViewSet):
    queryset = Dispute.objects.all()
    serializer_class = DisputeSerializer
    

    def perform_create(self, serializer):
        serializer.save(company=serializer.validated_data['company'])

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        dispute = self.get_object()
        dispute.status = 'resolved'
        dispute.save()
        serializer = self.get_serializer(dispute)
        return Response(serializer.data)