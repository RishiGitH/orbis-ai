from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Stake
from .serializers import UserSerializer, StakeSerializer
from .services import UserService

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    

    def perform_create(self, serializer):
        user = UserService.create_user(
            wallet_address=serializer.validated_data['wallet_address'],
            user_type=serializer.validated_data['user_type']
        )
        serializer.instance = user

    @action(detail=True, methods=['post'])
    def stake(self, request, pk=None):
        user = self.get_object()
        stake = UserService.stake_tokens(
            user_id=user.id,
            amount=request.data.get('amount')
        )
        serializer = StakeSerializer(stake)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def unstake(self, request, pk=None):
        user = self.get_object()
        UserService.unstake_tokens(
            user_id=user.id,
            amount=request.data.get('amount')
        )
        return Response({'status': 'tokens unstaked'})

class StakeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stake.objects.all()
    serializer_class = StakeSerializer
    