from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils import timezone
from django.db import models
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import DonateForm, DistributionRecord, DonationTracker
from .serializers import DonateFormSerializer, DistributionRecordSerializer
import json


@csrf_exempt
@csrf_exempt
@require_http_methods(["POST", "GET"])
def submit_donation(request):
    """Handle donation form submission"""
    if request.method == 'POST':
        try:
            # Print all received data for debugging
            print("POST data:", request.POST)
            print("FILES data:", request.FILES)
            
            # Get form data from request (both regular and file data)
            full_name = request.POST.get('full_name', '').strip()
            cont_no = request.POST.get('cont_no', '').strip()
            food_type = request.POST.get('food_type', '').strip()
            preparation_time = request.POST.get('preparation_time', '').strip()
            food_photo = request.FILES.get('food_photo')
            cdt = request.POST.get('cdt', '').strip()
            pdt = request.POST.get('pdt', '').strip()
            ploc = request.POST.get('ploc', '').strip()
            
            print(f"Received data - name: {full_name}, cont: {cont_no}, food: {food_type}, prep: {preparation_time}, photo: {food_photo}, cdt: {cdt}, pdt: {pdt}, loc: {ploc}")
            
            # Detailed validation with specific error messages
            missing_fields = []
            
            if not full_name:
                missing_fields.append('full_name')
            if not cont_no:
                missing_fields.append('cont_no')
            if not food_type:
                missing_fields.append('food_type')
            if not preparation_time:
                missing_fields.append('preparation_time')
            if not food_photo:
                missing_fields.append('food_photo')
            if not cdt:
                missing_fields.append('cdt')
            if not pdt:
                missing_fields.append('pdt')
            if not ploc:
                missing_fields.append('ploc')
            
            if missing_fields:
                print(f"Missing fields: {missing_fields}")
                return JsonResponse({
                    'success': False,
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                }, status=400)
            
            # Create donation record with user link
            donation = DonateForm.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=full_name,
                cont_no=cont_no,
                food_type=food_type,
                preparation_time=preparation_time,
                food_photo=food_photo,
                cdt=cdt,
                pdt=pdt,
                ploc=ploc,
                status='pending_approval'
            )
            
            print(f"Donation created: {donation.donation_id}")
            
            # Create tracker
            DonationTracker.objects.create(donation=donation)
            
            return JsonResponse({
                'success': True,
                'message': 'Donation submitted successfully! Waiting for admin verification.',
                'donation_id': donation.donation_id,
                'created_at': donation.created_at.isoformat()
            }, status=201)
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error in submit_donation: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
@require_http_methods(["GET"])
def track_donation(request):
    """Track donation status"""
    donation_id = request.GET.get('donation_id')
    
    if not donation_id:
        return JsonResponse({
            'success': False,
            'message': 'Donation ID is required'
        }, status=400)
    
    try:
        donation = DonateForm.objects.get(donation_id=donation_id)
        
        # Update tracker
        tracker = donation.tracker
        tracker.view_count += 1
        tracker.last_viewed = timezone.now()
        tracker.save()
        
        # Get distribution info if exists
        distribution = None
        if hasattr(donation, 'distribution'):
            distribution = {
                'center': donation.distribution.distribution_center,
                'date': donation.distribution.distribution_date.isoformat(),
                'people_served': donation.distribution.people_served,
                'satisfaction': donation.distribution.satisfaction_rating,
                'quality': donation.distribution.food_quality
            }
        
        return JsonResponse({
            'success': True,
            'donation': {
                'donation_id': donation.donation_id,
                'full_name': donation.full_name,
                'cont_no': donation.cont_no,
                'food_type': donation.food_type,
                'cdt': donation.cdt,
                'pdt': donation.pdt,
                'ploc': donation.ploc,
                'status': donation.status,
                'team': donation.team,
                'created_at': donation.created_at.isoformat(),
                'distribution': distribution
            }
        }, status=200)
    
    except DonateForm.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Donation not found'
        }, status=404)


@csrf_exempt
@require_http_methods(["GET"])
def get_donation_details(request, donation_id):
    """Get donation details including photo URL"""
    try:
        donation = DonateForm.objects.get(donation_id=donation_id)
        
        food_photo_url = donation.food_photo.url if donation.food_photo else None
        
        return JsonResponse({
            'success': True,
            'donation_id': donation_id,
            'food_photo': food_photo_url,
            'full_name': donation.full_name,
            'food_type': donation.food_type,
            'preparation_time': str(donation.preparation_time) if donation.preparation_time else None,
            'cdt': donation.cdt,
            'pdt': donation.pdt,
            'food_condition': donation.food_condition,
            'status': donation.status,
            'rejection_reason': donation.rejection_reason or None
        }, status=200)
    
    except DonateForm.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Donation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
    """Update donation status (admin/team use)"""
    try:
        data = json.loads(request.body)
        donation_id = data.get('donation_id')
        new_status = data.get('status')
        
        donation = DonateForm.objects.get(donation_id=donation_id)
        
        # Validate status
        valid_statuses = ['pending', 'picked_up', 'in_transit', 'delivered', 'completed']
        if new_status not in valid_statuses:
            return JsonResponse({
                'success': False,
                'message': 'Invalid status'
            }, status=400)
        
        donation.status = new_status
        team = data.get('team', '').strip()
        location = data.get('location', '').strip()
        people_served = data.get('people_served', 0)
        
        # If delivery team is assigned/updated, automatically change status to 'delivered'
        if team and not donation.team:
            # Team is being assigned for the first time
            donation.team = team
            donation.status = 'delivered'  # Auto-set to delivered when team assigned
        elif team != donation.team:
            # Team is being changed
            donation.team = team
            donation.status = new_status  # Use the provided status
        else:
            # Team not changed, use provided status
            donation.team = team if team else donation.team
            donation.status = new_status
        
        # Update location/distribution center
        if location:
            donation.distribution_center = location
        
        # Update people served
        if people_served and people_served > 0:
            donation.people_served = people_served
        
        if data.get('notes'):
            donation.notes = data.get('notes')
        
        donation.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Donation updated - Status: {donation.status}, Team: {donation.team or "Unassigned"}',
            'donation_id': donation.donation_id,
            'status': donation.status,
            'team': donation.team
        }, status=200)
    
    except DonateForm.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Donation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def record_distribution(request):
    """Record food distribution details"""
    try:
        data = json.loads(request.body)
        donation_id = data.get('donation_id')
        
        donation = DonateForm.objects.get(donation_id=donation_id)
        
        # Create or update distribution record
        distribution, created = DistributionRecord.objects.update_or_create(
            donation=donation,
            defaults={
                'distribution_center': data.get('distribution_center'),
                'distribution_date': data.get('distribution_date'),
                'people_served': data.get('people_served'),
                'adults': data.get('adults', 0),
                'children': data.get('children', 0),
                'senior_citizens': data.get('senior_citizens', 0),
                'satisfaction_rating': data.get('satisfaction_rating'),
                'food_quality': data.get('food_quality'),
                'hygiene_maintained': data.get('hygiene_maintained', True),
                'team_leader_name': data.get('team_leader_name'),
                'team_leader_contact': data.get('team_leader_contact'),
                'volunteers_count': data.get('volunteers_count', 2),
                'notes': data.get('notes'),
            }
        )
        
        # Update donation status to completed
        donation.status = 'completed'
        donation.distribution_center = data.get('distribution_center')
        donation.distribution_date = data.get('distribution_date')
        donation.people_served = data.get('people_served')
        donation.satisfaction_rating = data.get('satisfaction_rating')
        donation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Distribution recorded successfully',
            'donation_id': donation.donation_id
        }, status=201)
    
    except DonateForm.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Donation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def update_donation_status(request):
    """Update donation status with team assignment and distribution details"""
    try:
        data = json.loads(request.body)
        donation_id = data.get('donation_id')
        status = data.get('status')
        team = data.get('team', '').strip()
        location = data.get('location', '').strip()
        people_served = data.get('people_served', 0)
        notes = data.get('notes', '').strip()
        
        if not donation_id:
            return JsonResponse({
                'success': False,
                'message': 'Donation ID is required'
            }, status=400)
        
        donation = DonateForm.objects.get(donation_id=donation_id)
        
        # Update status
        if status:
            donation.status = status
        
        # Update team assignment
        if team:
            donation.team = team
            donation.allocated_at = timezone.now()
        
        # Update distribution details
        if location:
            donation.distribution_center = location
        
        if people_served > 0:
            donation.people_served = people_served
        
        if notes:
            donation.notes = notes
        
        donation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Donation updated successfully',
            'donation_id': donation.donation_id,
            'status': donation.status
        }, status=200)
    
    except DonateForm.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Donation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def get_all_donations(request):
    """Get all donations (admin view)"""
    try:
        donations = DonateForm.objects.all().order_by('-created_at')
        donations_data = []
        
        for donation in donations:
            donations_data.append({
                'id': donation.id,
                'donation_id': donation.donation_id,
                'full_name': donation.full_name,
                'cont_no': donation.cont_no,
                'food_type': donation.food_type,
                'status': donation.status,
                'team': donation.team,
                'created_at': donation.created_at.isoformat(),
                'people_served': donation.people_served
            })
        
        return JsonResponse({
            'success': True,
            'total': len(donations_data),
            'donations': donations_data
        }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


def home(request):
    """Home page view"""
    total_donations = DonateForm.objects.count()
    completed_donations = DonateForm.objects.filter(status='completed').count()
    people_served = DonateForm.objects.filter(people_served__isnull=False).aggregate(
        total=models.Sum('people_served')
    )['total'] or 0
    
    context = {
        'total_donations': total_donations,
        'completed_donations': completed_donations,
        'people_served': people_served
    }
    
    return render(request, 'home.html', context)


def donation_form(request):
    """Donation form page"""
    return render(request, 'donation_form.html')


def track_page(request):
    """Donation tracking page"""
    return render(request, 'track_donation.html')


def admin_dashboard(request):
    """Admin dashboard view"""
    if not request.user.is_authenticated:
        return redirect('donor_api:login')
    
    from donor_api.models import DeliveryTeam
    
    donations = DonateForm.objects.all().order_by('-created_at')
    teams = DeliveryTeam.objects.all()
    
    context = {
        'donations': donations,
        'teams': teams,
        'total': donations.count(),
        'pending': donations.filter(status='pending').count(),
        'picked_up': donations.filter(status='picked_up').count(),
        'in_transit': donations.filter(status='in_transit').count(),
        'completed': donations.filter(status='completed').count(),
    }
    return render(request, 'admin_dashboard.html', context)


# ==================== AUTHENTICATION VIEWS ====================

@csrf_protect
def donor_login(request):
    """Donor login page"""
    if request.user.is_authenticated:
        return redirect('donor_api:donor_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        try:
            # Find user by email
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('donor_api:donor_dashboard')
            else:
                context = {'error': 'Invalid email or password', 'email': email}
                return render(request, 'login.html', context)
        
        except User.DoesNotExist:
            context = {'error': 'Email not registered', 'email': email}
            return render(request, 'login.html', context)
    
    return render(request, 'login.html')


@csrf_protect
def donor_signup(request):
    """Donor signup/registration page"""
    if request.user.is_authenticated:
        return redirect('donor_api:donor_dashboard')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        # Validation
        errors = {}
        
        if not full_name:
            errors['full_name'] = 'Full name is required'
        if not email:
            errors['email'] = 'Email is required'
        if User.objects.filter(email=email).exists():
            errors['email'] = 'Email already registered'
        if not password:
            errors['password'] = 'Password is required'
        if len(password) < 6:
            errors['password'] = 'Password must be at least 6 characters'
        if password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match'
        
        if errors:
            context = {
                'errors': errors,
                'full_name': full_name,
                'email': email,
                'phone': phone
            }
            return render(request, 'signup.html', context)
        
        # Create user
        username = email.split('@')[0]  # Use email prefix as username
        counter = 1
        original_username = username
        
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name.split()[0] if full_name else ''
        )
        
        # Store phone in profile (using first_name/last_name)
        if len(full_name.split()) > 1:
            user.last_name = ' '.join(full_name.split()[1:])
        user.save()
        
        # Authenticate and login
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('donor_api:donor_dashboard')
    
    return render(request, 'signup.html')


@login_required(login_url='donor_api:login')
def donor_dashboard(request):
    """Donor dashboard - view their donations"""
    # Get donations directly linked to the logged-in user
    user_donations = DonateForm.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'user': request.user,
        'donations': user_donations,
        'total_donations': user_donations.count(),
        'completed': user_donations.filter(status='completed').count(),
        'pending': user_donations.filter(status='pending').count(),
        'in_progress': user_donations.exclude(status__in=['completed', 'pending']).count(),
    }
    
    return render(request, 'donor_dashboard.html', context)


@login_required(login_url='donor_api:login')
def donor_profile(request):
    """Donor profile page"""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        
        if full_name:
            name_parts = full_name.split()
            request.user.first_name = name_parts[0]
            if len(name_parts) > 1:
                request.user.last_name = ' '.join(name_parts[1:])
            request.user.save()
        
        context = {
            'user': request.user,
            'success': 'Profile updated successfully'
        }
        return render(request, 'profile.html', context)
    
    context = {'user': request.user}
    return render(request, 'profile.html', context)


@login_required(login_url='donor_api:login')
def donor_logout(request):
    """Logout donor"""
    logout(request)
    return redirect('donor_api:home')


@csrf_exempt
@require_http_methods(["POST"])
def verify_food_condition(request):
    """Admin verifies food condition based on donor's photo"""
    try:
        data = json.loads(request.body)
        donation_id = data.get('donation_id')
        food_condition = data.get('food_condition')  # 'fresh', 'good', 'acceptable'
        admin_notes = data.get('admin_notes', '')
        
        if not donation_id:
            return JsonResponse({
                'success': False,
                'message': 'Donation ID is required'
            }, status=400)
        
        donation = DonateForm.objects.get(donation_id=donation_id)
        
        # Validate food condition
        valid_conditions = ['fresh', 'good', 'acceptable']
        if food_condition not in valid_conditions:
            return JsonResponse({
                'success': False,
                'message': 'Invalid food condition'
            }, status=400)
        
        # Update donation with verification details
        donation.food_condition = food_condition
        donation.admin_notes = admin_notes
        donation.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Food condition verified as {food_condition}',
            'donation_id': donation.donation_id,
            'food_condition': donation.food_condition
        }, status=200)
    
    except DonateForm.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Donation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def approve_donation(request):
    """Admin approves a donation after verifying food condition"""
    try:
        data = json.loads(request.body)
        donation_id = data.get('donation_id')
        
        donation = DonateForm.objects.get(donation_id=donation_id)
        
        # Check if food condition is verified
        if donation.food_condition == 'not_verified':
            return JsonResponse({
                'success': False,
                'message': 'Food condition must be verified before approval'
            }, status=400)
        
        # Update donation status to approved
        donation.status = 'approved'
        donation.approved_by = request.user if request.user.is_authenticated else None
        donation.approved_at = timezone.now()
        donation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Donation approved successfully!',
            'donation_id': donation.donation_id,
            'status': donation.status,
            'approved_at': donation.approved_at.isoformat()
        }, status=200)
    
    except DonateForm.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Donation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def reject_donation(request):
    """Admin rejects a donation with reason"""
    try:
        data = json.loads(request.body)
        donation_id = data.get('donation_id')
        rejection_reason = data.get('rejection_reason', '')
        
        donation = DonateForm.objects.get(donation_id=donation_id)
        
        # Update donation status to rejected
        donation.status = 'rejected'
        donation.rejection_reason = rejection_reason
        donation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Donation rejected',
            'donation_id': donation.donation_id,
            'status': donation.status
        }, status=200)
    
    except DonateForm.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Donation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def allocate_to_team(request):
    """Allocate approved donation to delivery team"""
    try:
        data = json.loads(request.body)
        donation_id = data.get('donation_id')
        team = data.get('team')
        
        donation = DonateForm.objects.get(donation_id=donation_id)
        
        # Check if donation is approved
        if donation.status != 'approved':
            return JsonResponse({
                'success': False,
                'message': 'Only approved donations can be allocated to teams'
            }, status=400)
        
        # Allocate to team
        donation.team = team
        donation.allocated_at = timezone.now()
        donation.status = 'picked_up'  # Move to next status
        donation.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Donation allocated to team: {team}',
            'donation_id': donation.donation_id,
            'team': donation.team,
            'status': donation.status,
            'allocated_at': donation.allocated_at.isoformat()
        }, status=200)
    
    except DonateForm.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Donation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@csrf_protect
@require_http_methods(["GET", "POST"])
def admin_login(request):
    """Admin login page"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('donor_api:admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect('donor_api:admin_dashboard')
            else:
                return render(request, 'adminlogin.html', {
                    'error': 'This account does not have admin privileges.'
                })
        else:
            return render(request, 'adminlogin.html', {
                'error': 'Invalid username or password.'
            })
    
    return render(request, 'adminlogin.html')


# ==================== TEAM MANAGEMENT ====================

@csrf_exempt
@require_http_methods(["POST"])
def create_team(request):
    """Create a new delivery team"""
    try:
        from donor_api.models import DeliveryTeam
        
        data = json.loads(request.body)
        team_name = data.get('team_name', '').strip()
        team_leader = data.get('team_leader', '').strip()
        team_contact = data.get('team_contact', '').strip()
        
        if not team_name:
            return JsonResponse({
                'success': False,
                'message': 'Team name is required'
            }, status=400)
        
        # Check if team already exists
        if DeliveryTeam.objects.filter(name=team_name).exists():
            return JsonResponse({
                'success': False,
                'message': f'Team "{team_name}" already exists'
            }, status=400)
        
        # Create new team
        team = DeliveryTeam.objects.create(
            name=team_name,
            leader_name=team_leader or None,
            contact_number=team_contact or None,
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Team "{team_name}" created successfully',
            'team_id': team.id,
            'team_name': team.name
        }, status=201)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def delete_team(request):
    """Delete a delivery team"""
    try:
        from donor_api.models import DeliveryTeam
        
        data = json.loads(request.body)
        team_id = data.get('team_id')
        
        if not team_id:
            return JsonResponse({
                'success': False,
                'message': 'Team ID is required'
            }, status=400)
        
        team = DeliveryTeam.objects.get(id=team_id)
        team_name = team.name
        
        # Check if team has any active donations
        donation_count = DonateForm.objects.filter(team=team_name).count()
        if donation_count > 0:
            return JsonResponse({
                'success': False,
                'message': f'Cannot delete team with {donation_count} active donation(s). Please reassign donations first.'
            }, status=400)
        
        team.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Team "{team_name}" deleted successfully'
        }, status=200)
    
    except DeliveryTeam.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Team not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


# ==================== REPORT GENERATION ====================

@csrf_exempt
@require_http_methods(["POST"])
def generate_donation_report(request):
    """Generate a report for a completed donation"""
    try:
        from donor_api.models import DonationReport
        
        data = json.loads(request.body)
        donation_id = data.get('donation_id')
        
        if not donation_id:
            return JsonResponse({
                'success': False,
                'message': 'Donation ID is required'
            }, status=400)
        
        donation = DonateForm.objects.get(donation_id=donation_id)
        
        # Create impact summary
        impact_summary = f"Donation from {donation.full_name} ({donation.food_type}) was successfully distributed"
        if donation.people_served:
            impact_summary += f" to {donation.people_served} people"
        if donation.distribution_center:
            impact_summary += f" at {donation.distribution_center}"
        impact_summary += "."
        
        # Check if report already exists and update it, otherwise create new
        report, created = DonationReport.objects.update_or_create(
            donation=donation,
            defaults={
                'donor_name': donation.full_name,
                'food_type': donation.food_type,
                'team_name': donation.team,
                'people_served': donation.people_served or 0,
                'distribution_center': donation.distribution_center,
                'distribution_date': donation.distribution_date,
                'satisfaction_rating': donation.satisfaction_rating,
                'impact_summary': impact_summary,
                'status': 'generated'
            }
        )
        
        if created:
            message = 'Report generated successfully'
        else:
            message = 'Report updated with latest information'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'report_id': report.id,
            'report_date': report.report_date.isoformat()
        }, status=201)
    
    except DonateForm.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Donation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def get_donation_report(request):
    """Get report for a specific donation"""
    try:
        from donor_api.models import DonationReport
        
        donation_id = request.GET.get('donation_id')
        
        if not donation_id:
            return JsonResponse({
                'success': False,
                'message': 'Donation ID is required'
            }, status=400)
        
        donation = DonateForm.objects.get(donation_id=donation_id)
        
        try:
            report = DonationReport.objects.get(donation=donation)
            return JsonResponse({
                'success': True,
                'report': {
                    'id': report.id,
                    'donor_name': report.donor_name,
                    'food_type': report.food_type,
                    'team_name': report.team_name,
                    'people_served': report.people_served,
                    'distribution_center': report.distribution_center,
                    'distribution_date': report.distribution_date.isoformat() if report.distribution_date else None,
                    'satisfaction_rating': report.satisfaction_rating,
                    'impact_summary': report.impact_summary,
                    'report_date': report.report_date.isoformat()
                }
            }, status=200)
        except DonationReport.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'No report found for this donation'
            }, status=404)
    
    except DonateForm.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Donation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

