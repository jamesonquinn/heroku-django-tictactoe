import os
import sys
import urlparse
from peewee import *

# Register database schemes in URLs.
urlparse.uses_netloc.append('postgres')
urlparse.uses_netloc.append('mysql')

DATABASES = {'default':{
                        'name': 'example.db',
                        'engine': 'peewee.SqliteDatabase',
                        }}

try:

    # Check to make sure DATABASES is set in settings.py file.
    # If not default to {}

    if 'DATABASES' not in locals():
        DATABASES = {}

    if 'DATABASE_URL' in os.environ:
        url = urlparse.urlparse(os.environ['DATABASE_URL'])

        # Ensure default database exists.
        DATABASES['default'] = DATABASES.get('default', {})

        # Update with environment configuration.
        DATABASES['default'].update({
            'NAME': url.path[1:],
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port,
        })
        if url.scheme == 'postgres':
            DATABASES['default']['ENGINE'] = 'peewee.PostgresqlDatabase'

        if url.scheme == 'mysql':
            DATABASES['default']['ENGINE'] = 'peewee.MySQLDatabase'
except Exception:
    print 'Unexpected error:', sys.exc_info()
    
DEBUG = True
SECRET_KEY = 'ssshhhh'
DATABASE = DATABASES['default']

DOMAIN = "bettercount.us"