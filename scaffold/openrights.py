#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports

# framework imports

# app imports
from scaffold import userrightsnames, userrights


# A version of UserRights which opens permissions
# For us in testing and demo'ing the system
class OpenRights(userrights.UserRights):

    def has_permission(self, name, permission):
        if (permission == userrightsnames.CONF_CREATOR):
            return userrights.UserRights.has_permission(self, name, permission)
        else:
            return True

    def can_view_all(self, name):
        return True

    def has_special_rights(self, user):
        return True

