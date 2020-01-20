#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# library imports
from google.appengine.api import app_identity


# local imports
# none

def is_running_local():
    host = app_identity.get_default_version_hostname()
    if (host == None):
        # probably running a test
        return True

    return host.find("localhost") >= 0


def home_url():
    if None == app_identity.get_default_version_hostname():
        return ""
    else:
        return app_identity.get_default_version_hostname()


def is_system_admin(user):
    sys_admins = ["test@example.com",
                  "allankellynet@gmail.com",
                  ]

    if (user in sys_admins):
        return True

    return False
