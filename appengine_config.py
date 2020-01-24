# appengine_config.py

# Following upgrade of Google App Engine and some libraries
# And PyCharm upgrade
# Mimas has problems loading google.auth (package not found)
# Eventually this https://github.com/googleapis/google-auth-library-python/issues/169
# Applying this fix seems to work
# Quite likely there is a package conflict somewhere
# Upgrade to Python 3 is coming soon so intend to resolve this issue properly then
# Until then use this fix
# (However numpy is now failing to load but that can be engineered out)

import os
import google
from google.appengine.ext import vendor

lib_directory = os.path.dirname(__file__) + '/lib'

# Change where to find the google package (point to the lib/ directory)
google.__path__ = [os.path.join(lib_directory, 'google')] + google.__path__

# Add any libraries install in the "lib" folder.
vendor.add(lib_directory)

# Before problems lib was added very simply:
# vendor.add('lib')
# - that is all there was in this file
