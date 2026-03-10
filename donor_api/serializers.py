from rest_framework import serializers
from .models import DonateForm, DistributionRecord, DonationTracker


class DonateFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonateForm
        fields = [
            'id', 'donation_id', 'full_name', 'cont_no', 'food_type',
            'cdt', 'pdt', 'ploc', 'status', 'team', 'created_at',
            'updated_at', 'distribution_center', 'people_served',
            'satisfaction_rating', 'notes'
        ]
        read_only_fields = ['donation_id', 'created_at', 'updated_at']


class DistributionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributionRecord
        fields = [
            'id', 'donation', 'distribution_center', 'distribution_date',
            'people_served', 'adults', 'children', 'senior_citizens',
            'satisfaction_rating', 'food_quality', 'hygiene_maintained',
            'team_leader_name', 'team_leader_contact', 'volunteers_count',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DonationTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationTracker
        fields = ['id', 'donation', 'view_count', 'last_viewed']
