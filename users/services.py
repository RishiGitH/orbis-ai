from django.db import transaction
from .models import User, Stake
from decimal import Decimal

class UserService:
    @staticmethod
    @transaction.atomic
    def create_user(wallet_address: str, user_type: str):
        user = User.objects.create(
            username=wallet_address,
            wallet_address=wallet_address,
            user_type=user_type
        )
        return user

    @staticmethod
    @transaction.atomic
    def stake_tokens(user_id: int, amount: Decimal):
        user = User.objects.get(id=user_id)
        stake = Stake.objects.create(
            user=user,
            amount=amount
        )
        user.staked_amount += amount
        user.save()
        return stake

    @staticmethod
    @transaction.atomic
    def unstake_tokens(user_id: int, amount: Decimal):
        user = User.objects.get(id=user_id)
        if user.staked_amount < amount:
            raise ValueError("Insufficient staked amount")
        
        user.staked_amount -= amount
        user.save()
        
        # TODO: Implement logic to transfer unstaked tokens back to user's wallet

    @staticmethod
    @transaction.atomic
    def slash_stake(user_id: int, amount: Decimal):
        user = User.objects.get(id=user_id)
        if user.staked_amount < amount:
            raise ValueError("Insufficient staked amount")
        
        user.staked_amount -= amount
        user.save()
        
        # TODO: Implement logic to transfer slashed tokens to refund pool