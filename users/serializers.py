from rest_framework import serializers
from .models import User, Stake

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'wallet_address', 'user_type', 'staked_amount']
        read_only_fields = ['id', 'staked_amount']

class StakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stake
        fields = ['id', 'user', 'amount', 'locked_until']
        read_only_fields = ['id', 'user']