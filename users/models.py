from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class UserType(models.TextChoices):
        COMPANY = 'company', 'Company'
        TRAINER = 'trainer', 'Trainer'
        REVIEWER = 'reviewer', 'Reviewer'

    wallet_address = models.CharField(max_length=54, unique=True)
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.TRAINER
    )
    staked_amount = models.DecimalField(max_digits=18, decimal_places=6, default=0)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

    def __str__(self):
        return f"{self.wallet_address} ({self.get_user_type_display()})"

    @property
    def is_company(self):
        return self.user_type == self.UserType.COMPANY

    @property
    def is_trainer(self):
        return self.user_type == self.UserType.TRAINER

    @property
    def is_reviewer(self):
        return self.user_type == self.UserType.REVIEWER

class Stake(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=6)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.wallet_address} - {self.amount}"