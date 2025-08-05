import os
import sys
from django.core.wsgi import get_wsgi_application

# Add project path to sys.path
sys.path.append(os.path.dirname(__file__))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rms_project.settings')

# Get WSGI application
application = get_wsgi_application()