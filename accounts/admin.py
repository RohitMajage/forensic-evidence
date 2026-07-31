from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Contact, Team, Case, Evidence, Person, MatchResult
)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number',)}),  
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number',)}),
    )


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'case_name', 'team', 'created_by')
    search_fields = ('case_number', 'case_name')
    list_filter = ('team',)
    exclude = ('created_by',)  # Hide from admin form

    def save_model(self, request, obj, form, change):
        if not change or not obj.created_by:  # Only set if creating
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('case', 'type', 'uploaded_by', 'uploaded_at')
    list_filter = ('type', 'uploaded_at')
    search_fields = ('description',)
    filter_horizontal = ('viewers',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('members',)
    
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Contact)
admin.site.register(Person)
admin.site.register(MatchResult)
