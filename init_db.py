"""
This script initializes the database with sample data for testing
"""

import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_donation_project.settings')
django.setup()

from donor_api.models import DonateForm, DonationTracker

def create_sample_donations():
    """Create sample donation records for testing"""
    
    sample_donations = [
        {
            'full_name': 'Raj Kumar',
            'cont_no': '9876543210',
            'food_type': 'Rice (10kg), Dal (5kg), Vegetables (15kg)',
            'cdt': (datetime.now() - timedelta(hours=2)).isoformat(),
            'pdt': (datetime.now() - timedelta(hours=1)).isoformat(),
            'ploc': '123 Main Street, Delhi',
            'status': 'completed',
            'team': 'Team Alpha',
            'people_served': 40,
            'distribution_center': 'Sunrise Community Kitchen',
            'satisfaction_rating': 95,
            'notes': 'Great quality food. Well received by beneficiaries.'
        },
        {
            'full_name': 'Priya Singh',
            'cont_no': '9123456789',
            'food_type': 'Biryani (20kg), Raita (5kg)',
            'cdt': (datetime.now() - timedelta(hours=3)).isoformat(),
            'pdt': (datetime.now() - timedelta(hours=2)).isoformat(),
            'ploc': '456 Oak Avenue, Mumbai',
            'status': 'in_transit',
            'team': 'Team Beta',
            'notes': 'Food is on the way to distribution center'
        },
        {
            'full_name': 'Amit Patel',
            'cont_no': '9234567890',
            'food_type': 'Chapati (50 pieces), Sabzi (10kg), Daal (3kg)',
            'cdt': (datetime.now() + timedelta(hours=1)).isoformat(),
            'pdt': (datetime.now() + timedelta(hours=2)).isoformat(),
            'ploc': '789 Pine Road, Bangalore',
            'status': 'pending',
            'team': None,
            'notes': 'Awaiting team assignment'
        },
        {
            'full_name': 'Neha Sharma',
            'cont_no': '9345678901',
            'food_type': 'Fruits (Mixed, 15kg), Bread (20 loaves)',
            'cdt': (datetime.now() - timedelta(days=1, hours=2)).isoformat(),
            'pdt': (datetime.now() - timedelta(days=1, hours=1)).isoformat(),
            'ploc': '321 Elm Street, Pune',
            'status': 'completed',
            'team': 'Team Gamma',
            'people_served': 60,
            'distribution_center': 'NGO Food Bank',
            'satisfaction_rating': 98,
            'notes': 'Fresh and nutritious food. Highly appreciated.'
        },
        {
            'full_name': 'Vikram Desai',
            'cont_no': '9456789012',
            'food_type': 'Paneer Butter Masala (10kg), Rice (5kg)',
            'cdt': (datetime.now() - timedelta(hours=4)).isoformat(),
            'pdt': (datetime.now() - timedelta(hours=3)).isoformat(),
            'ploc': '654 Cedar Lane, Chennai',
            'status': 'delivered',
            'team': 'Team Delta',
            'people_served': 35,
            'notes': 'Ready for final distribution'
        },
    ]
    
    created_count = 0
    for donation_data in sample_donations:
        try:
            donation = DonateForm.objects.create(**donation_data)
            DonationTracker.objects.create(donation=donation)
            created_count += 1
            print(f"✓ Created donation: {donation.donation_id} - {donation.full_name}")
        except Exception as e:
            print(f"✗ Error creating donation: {e}")
    
    return created_count

if __name__ == '__main__':
    print("🍲 Food Donation Database Initialization")
    print("=" * 50)
    print()
    
    # Check if donations already exist
    existing_count = DonateForm.objects.count()
    if existing_count > 0:
        print(f"⚠️  Database already has {existing_count} donations")
        response = input("Do you want to clear and reinitialize? (yes/no): ").lower()
        if response != 'yes':
            print("Aborted.")
            exit()
        else:
            DonateForm.objects.all().delete()
            DonationTracker.objects.all().delete()
            print("✓ Cleared existing data")
            print()
    
    # Create sample donations
    print("Creating sample donations...")
    count = create_sample_donations()
    
    print()
    print(f"✓ Successfully created {count} sample donations")
    print()
    print("Database initialization complete!")
    print()
    print("You can now access:")
    print("- Home: http://localhost:8000/")
    print("- Admin: http://localhost:8000/admin/")
    print()
