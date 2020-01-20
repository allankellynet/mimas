#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# system imports
import os

# App Engine imports

# local imports

def config_js_params():
    # Pick up firebase config from environment variables
    # Although at the moment Firebase is only used for login authentication
    # No firebase database or storage
    # So security is less
    return "var firebase_config = {" + \
           '    apiKey: "' + os.environ.get('FIREBASE_apiKey') + '", \n' + \
           '    authDomain: "' + os.environ.get('FIREBASE_authDomain') + '", \n' + \
           '    databaseURL: "' + os.environ.get('FIREBASE_databaseURL') + '", \n' + \
           '    projectId: "' + os.environ.get('FIREBASE_projectId') + '", \n' + \
           '    storageBucket: "' + os.environ.get('FIREBASE_storageBucket') + '", \n' + \
           '    messagingSenderId: "' + os.environ.get('FIREBASE_messagingSenderId') + '" };'
