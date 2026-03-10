from django.urls import path
from . import views

app_name = 'donor_api'

urlpatterns = [
    # Frontend views
    path('', views.home, name='home'),
    path('donate/', views.donation_form, name='donation_form'),
    path('track/', views.track_page, name='track_page'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Authentication views
    path('login/', views.donor_login, name='login'),
    path('signup/', views.donor_signup, name='signup'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('profile/', views.donor_profile, name='profile'),
    path('logout/', views.donor_logout, name='logout'),
    
    # API endpoints
    path('api/submit-donation/', views.submit_donation, name='submit_donation'),
    path('api/track-donation/', views.track_donation, name='track_donation'),
    path('api/get-donation/<str:donation_id>/', views.get_donation_details, name='get_donation_details'),
    path('api/update-status/', views.update_donation_status, name='update_status'),
    path('api/record-distribution/', views.record_distribution, name='record_distribution'),
    path('api/all-donations/', views.get_all_donations, name='all_donations'),
    
    # Approval workflow endpoints
    path('api/verify-food-condition/', views.verify_food_condition, name='verify_food_condition'),
    path('api/approve-donation/', views.approve_donation, name='approve_donation'),
    path('api/reject-donation/', views.reject_donation, name='reject_donation'),
    path('api/allocate-to-team/', views.allocate_to_team, name='allocate_to_team'),
    
    # Team management endpoints
    path('api/create-team/', views.create_team, name='create_team'),
    path('api/delete-team/', views.delete_team, name='delete_team'),
    
    # Report generation endpoints
    path('api/generate-report/', views.generate_donation_report, name='generate_report'),
    path('api/get-report/', views.get_donation_report, name='get_report'),
]
