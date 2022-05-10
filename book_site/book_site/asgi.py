"""
ASGI config for book_site project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os, django

from django.core.asgi import get_asgi_application
# from channels.routing import get_default_application #new

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_site.settings')
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tabulator.settings') #new

# django.setup() #new
application = get_asgi_application()
# application = get_default_application() #new