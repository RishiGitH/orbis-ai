from django.contrib import admin
from .models import CampaignType, Campaign

class CampaignTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'campaign_type', 'company', 'total_pool', 'reward_per_task', 'status')
    list_filter = ('campaign_type', 'status')
    search_fields = ('title', 'description', 'company__username')
    raw_id_fields = ('company',)

admin.site.register(CampaignType, CampaignTypeAdmin)
admin.site.register(Campaign, CampaignAdmin)