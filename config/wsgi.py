"""
WSGI config for users project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/virtualenv/sessions-api-env/local/lib/python2.7/site-packages')

# Add the projevct onto the syspath
sys.path.append('/env/sessions/sessions-api')
sys.path.append('/env/sessions/sessions-model')
sys.path.append('/env/sessions/users-model')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Activate teh users-env virtual env
activate_env=os.path.expanduser("/virtualenv/sessions-api-env/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
