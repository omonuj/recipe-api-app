"""Vercel serverless entrypoint for the Django WSGI application.

Vercel's @vercel/python runtime looks for a module-level ``app`` callable.
The Django project lives in the sibling ``app/`` directory, so we add it to
the import path before building the WSGI application.
"""
import os
import sys
from pathlib import Path

# Make the Django project package (../app) importable.
PROJECT_DIR = Path(__file__).resolve().parent.parent / 'app'
sys.path.insert(0, str(PROJECT_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402

app = get_wsgi_application()
