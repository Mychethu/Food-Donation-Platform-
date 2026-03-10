#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_donation_project.settings')
django.setup()

from django.contrib.auth.models import User

# Check if admin user exists
if User.objects.filter(username='admin').exists():
    # Update existing admin user
    admin_user = User.objects.get(username='admin')
    admin_user.set_password('admin123')
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    print("✓ Admin user updated successfully")
    print(f"  Username: admin")
    print(f"  Password: admin123")
    print(f"  Is Staff: {admin_user.is_staff}")
    print(f"  Is Superuser: {admin_user.is_superuser}")
else:
    # Create new admin user
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@fooddonation.local',
        password='admin123'
    )
    print("✓ Admin user created successfully")
    print(f"  Username: admin")
    print(f"  Password: admin123")
    print(f"  Is Staff: {admin_user.is_staff}")
    print(f"  Is Superuser: {admin_user.is_superuser}")

print("\n✓ You can now login to admin panel with:")
print("  URL: http://127.0.0.1:8000/admin-login/")
print("  Username: admin")
print("  Password: admin123")
