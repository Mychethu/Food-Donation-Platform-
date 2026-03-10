# Generated migration for approval workflow

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('donor_api', '0002_donateform_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donateform',
            name='status',
            field=models.CharField(choices=[('pending_approval', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('picked_up', 'Picked Up'), ('in_transit', 'In Transit'), ('delivered', 'Delivered'), ('completed', 'Completed')], default='pending_approval', max_length=20),
        ),
        migrations.AddField(
            model_name='donateform',
            name='food_condition',
            field=models.CharField(choices=[('fresh', 'Fresh'), ('good', 'Good'), ('acceptable', 'Acceptable'), ('not_verified', 'Not Verified')], default='not_verified', max_length=20),
        ),
        migrations.AddField(
            model_name='donateform',
            name='admin_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='donateform',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_donations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='donateform',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='donateform',
            name='rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='donateform',
            name='allocated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
