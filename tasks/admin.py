from django.contrib import admin
from .models import Task, Dispute

class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'campaign', 'trainer', 'reviewer', 'status')
    list_filter = ('status', 'campaign__campaign_type')
    search_fields = ('id', 'campaign__title', 'trainer__username', 'reviewer__username')
    raw_id_fields = ('campaign', 'trainer', 'reviewer')

class DisputeAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'company', 'status')
    list_filter = ('status',)
    search_fields = ('id', 'task__id', 'company__username', 'reason')
    raw_id_fields = ('task', 'company')

admin.site.register(Task, TaskAdmin)
admin.site.register(Dispute, DisputeAdmin)