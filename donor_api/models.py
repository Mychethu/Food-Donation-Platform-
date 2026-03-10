from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
import string
import random


class DeliveryTeam(models.Model):
    """Model for managing delivery teams"""
    name = models.CharField(max_length=100, unique=True)
    leader_name = models.CharField(max_length=100, null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'delivery_team'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_donation_count(self):
        """Get count of donations assigned to this team"""
        from donor_api.models import DonateForm
        return DonateForm.objects.filter(team=self.name).count()


class DonateForm(models.Model):
    STATUS_CHOICES = [
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
    ]
    
    FOOD_CONDITION_CHOICES = [
        ('fresh', 'Fresh'),
        ('good', 'Good'),
        ('acceptable', 'Acceptable'),
        ('not_verified', 'Not Verified'),
    ]

    # Auto-generated fields
    id = models.AutoField(primary_key=True)
    donation_id = models.CharField(max_length=20, unique=True, editable=False)
    
    # User link (new field)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='donations')
    
    # Donor Information
    full_name = models.CharField(max_length=100)
    cont_no = models.CharField(max_length=20)
    
    # Food Information
    food_type = models.TextField()
    cdt = models.CharField(max_length=50)  # Cooking Date & Time
    pdt = models.CharField(max_length=50)  # Pickup Date & Time
    ploc = models.TextField()  # Pickup Location
    
    # Food Preparation Details
    preparation_time = models.TimeField(null=True, blank=True)  # Time when food was prepared
    food_photo = models.ImageField(upload_to='food_donations/', null=True, blank=True)  # Photo of the food
    
    # Approval & Verification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_approval')
    food_condition = models.CharField(max_length=20, choices=FOOD_CONDITION_CHOICES, default='not_verified')
    admin_notes = models.TextField(null=True, blank=True)  # Admin's verification notes
    verification_photo = models.ImageField(upload_to='verification/', null=True, blank=True)  # Photo taken during verification
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_donations')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    
    # Team assignment
    team = models.CharField(max_length=100, null=True, blank=True)
    allocated_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Distribution Information
    distribution_center = models.CharField(max_length=200, null=True, blank=True)
    distribution_date = models.CharField(max_length=50, null=True, blank=True)
    people_served = models.IntegerField(null=True, blank=True)
    satisfaction_rating = models.IntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'donateform'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.donation_id:
            self.donation_id = self.generate_donation_id()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_donation_id():
        """Generate unique donation ID in format DON-XXXXXXXX"""
        characters = string.ascii_uppercase + string.digits
        random_code = ''.join(random.choice(characters) for _ in range(8))
        donation_id = f"DON-{random_code}"
        
        # Ensure uniqueness
        while DonateForm.objects.filter(donation_id=donation_id).exists():
            random_code = ''.join(random.choice(characters) for _ in range(8))
            donation_id = f"DON-{random_code}"
        
        return donation_id
    
    def __str__(self):
        return f"{self.donation_id} - {self.full_name}"


class DistributionRecord(models.Model):
    donation = models.OneToOneField(DonateForm, on_delete=models.CASCADE, related_name='distribution')
    distribution_center = models.CharField(max_length=200)
    distribution_date = models.DateTimeField()
    people_served = models.IntegerField()
    adults = models.IntegerField(default=0)
    children = models.IntegerField(default=0)
    senior_citizens = models.IntegerField(default=0)
    satisfaction_rating = models.IntegerField()
    food_quality = models.CharField(max_length=50, choices=[
        ('fresh', 'Fresh'),
        ('good', 'Good'),
        ('acceptable', 'Acceptable'),
    ])
    hygiene_maintained = models.BooleanField(default=True)
    team_leader_name = models.CharField(max_length=100)
    team_leader_contact = models.CharField(max_length=20)
    volunteers_count = models.IntegerField(default=2)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'distribution_record'
    
    def __str__(self):
        return f"Distribution for {self.donation.donation_id}"


class DonationTracker(models.Model):
    donation = models.OneToOneField(DonateForm, on_delete=models.CASCADE, related_name='tracker')
    view_count = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'donation_tracker'
    
    def __str__(self):
        return f"Tracker for {self.donation.donation_id}"


class DonationReport(models.Model):
    """Model for storing generated donation reports"""
    donation = models.OneToOneField(DonateForm, on_delete=models.CASCADE, related_name='report')
    report_date = models.DateTimeField(auto_now_add=True)
    donor_name = models.CharField(max_length=100)
    food_type = models.TextField()
    quantity = models.CharField(max_length=100, null=True, blank=True)
    team_name = models.CharField(max_length=100, null=True, blank=True)
    people_served = models.IntegerField(default=0)
    distribution_center = models.CharField(max_length=200, null=True, blank=True)
    distribution_date = models.DateTimeField(null=True, blank=True)
    satisfaction_rating = models.IntegerField(null=True, blank=True)
    impact_summary = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, default='generated')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'donation_report'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report for {self.donation.donation_id}"
