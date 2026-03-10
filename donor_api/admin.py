from django.contrib import admin
from .models import DonateForm, DistributionRecord, DonationTracker


@admin.register(DonateForm)
class DonateFormAdmin(admin.ModelAdmin):
    list_display = ('donation_id', 'full_name', 'status', 'team', 'created_at', 'people_served')
    list_filter = ('status', 'created_at')
    search_fields = ('donation_id', 'full_name', 'cont_no')
    readonly_fields = ('donation_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Donation Info', {
            'fields': ('donation_id', 'full_name', 'cont_no', 'created_at', 'updated_at')
        }),
        ('Food Details', {
            'fields': ('food_type', 'cdt', 'pdt', 'ploc')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'team', 'notes')
        }),
        ('Distribution Info', {
            'fields': ('distribution_center', 'distribution_date', 'people_served', 'satisfaction_rating'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DistributionRecord)
class DistributionRecordAdmin(admin.ModelAdmin):
    list_display = ('donation', 'distribution_center', 'distribution_date', 'people_served', 'satisfaction_rating')
    list_filter = ('distribution_date', 'food_quality')
    search_fields = ('donation__donation_id', 'distribution_center', 'team_leader_name')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Distribution Details', {
            'fields': ('donation', 'distribution_center', 'distribution_date')
        }),
        ('Beneficiaries', {
            'fields': ('people_served', 'adults', 'children', 'senior_citizens')
        }),
        ('Quality & Hygiene', {
            'fields': ('food_quality', 'hygiene_maintained', 'satisfaction_rating')
        }),
        ('Team Info', {
            'fields': ('team_leader_name', 'team_leader_contact', 'volunteers_count')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DonationTracker)
class DonationTrackerAdmin(admin.ModelAdmin):
    list_display = ('donation', 'view_count', 'last_viewed')
    search_fields = ('donation__donation_id',)
    readonly_fields = ('view_count', 'last_viewed')
