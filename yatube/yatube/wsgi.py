import os
import sys

from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler

application = StaticFilesHandler(get_wsgi_application())

path = 'C:/Users/kasum/Dev/hw02_community/yatube'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yatube.settings')

application = get_wsgi_application()
