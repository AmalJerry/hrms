"""
WSGI config for HRMS project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os,sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HRMS.settings')
sys.path.append('/var/www/hrms/HRMS/HRMS')
sys.path.append('/var/www/hrms/HRMS')

application = get_wsgi_application()
