from django.contrib import admin
from .models import Project, Criteria, Visit, VisitAssessment, VisitPhoto, ProjectInvitation


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'created_at', 'finished_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'owner__email']
    readonly_fields = ['created_at', 'finished_at']
    filter_horizontal = ['collaborators']


@admin.register(Criteria)
class CriteriaAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'type', 'weight', 'order']
    list_filter = ['type', 'project']
    search_fields = ['name', 'project__name']
    ordering = ['project', 'order']


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'visit_date', 'created_by', 'created_at']
    list_filter = ['visit_date', 'project', 'created_at']
    search_fields = ['name', 'address', 'project__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(VisitAssessment)
class VisitAssessmentAdmin(admin.ModelAdmin):
    list_display = ['visit', 'criteria', 'get_value', 'created_at']
    list_filter = ['criteria__type', 'visit__project']
    search_fields = ['visit__name', 'criteria__name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_value(self, obj):
        return obj.get_value()
    get_value.short_description = 'Value'


@admin.register(VisitPhoto)
class VisitPhotoAdmin(admin.ModelAdmin):
    list_display = ['visit', 'caption', 'order', 'uploaded_at']
    list_filter = ['uploaded_at', 'visit__project']
    search_fields = ['visit__name', 'caption']
    readonly_fields = ['uploaded_at']


@admin.register(ProjectInvitation)
class ProjectInvitationAdmin(admin.ModelAdmin):
    list_display = ['project', 'email', 'invited_by', 'accepted', 'created_at']
    list_filter = ['accepted', 'created_at']
    search_fields = ['email', 'project__name', 'invited_by__email']
    readonly_fields = ['token', 'created_at', 'accepted_at']