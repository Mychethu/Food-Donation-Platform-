"""
WSGI config for food_donation_project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_donation_project.settings')

application = get_wsgi_application()
