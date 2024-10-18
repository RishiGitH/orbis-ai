from django.urls import path, include
from rest_framework.routers import DefaultRouter
from campaign.views import CampaignViewSet, CampaignPoolViewSet
from tasks.views import TaskViewSet, RewardViewSet, DisputeViewSet
from users.views import UserViewSet, StakeViewSet

router = DefaultRouter()
router.register(r'campaigns', CampaignViewSet)
router.register(r'campaign-pools', CampaignPoolViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'rewards', RewardViewSet)
router.register(r'disputes', DisputeViewSet)
router.register(r'users', UserViewSet)
router.register(r'stakes', StakeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]