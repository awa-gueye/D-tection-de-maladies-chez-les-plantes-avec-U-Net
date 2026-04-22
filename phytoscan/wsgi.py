"""Configuration WSGI pour le projet PhytoScan AI."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phytoscan.settings')
application = get_wsgi_application()
