Running unit tests
----------------
Use the Google app engine test runner.

Described in this page: https://cloud.google.com/appengine/docs/standard/python/tools/localunittesting#setup
Found on GitHub: https://github.com/GoogleCloudPlatform/python-docs-samples/blob/6f5f3bcb81779679a24e0964a6c57c0c7deabfac/appengine/standard/localtesting/runner.py

Note: the test runner need to be changed to find the test file. Test runner expects test files to be named *_test.py but tests here are named test*.py
Therefore change:
- default='*_test.py'
to
- default='test*.py'

I normally install the runner in some utils directory in my path.
And create a second shortcut (which I call gpytest and grant exec permissions):

python ~/Utils/runner.py /Users/allan/Documents/develop/google-cloud-sdk/platform/google_appengine/

Running locally
-----------------
dev_appserver.py app.yaml

* Logging in

Logging in is commonly handled via Firebase
But when running locally this can be difficult because Firebase calls back to the real live app not the local.
Therefore /loginb provides a basic login (using the app development environment) for use locally
The same mechanism will work in live but isn't publicised.

Deploy to Google
-----------------
deploy.sh script does deployment to Google
- gcloud app deploy --project mimas-aotb app_live.yaml

Project (mimas-aotb) is the Google name in the cloud: if you deploy Mimas to your own instance this will need changing
- Mimas has never been deployed to another instance so I expect there are some more places where mimas-aotb has been coded

app.yaml (checkedin) is a dummy as API keys need to be included
app_live.yaml is the same file with the specific keys as environment variables (not checked in for obvious reasons)

Firebase
----------

Third party logins (Twitter, FaceBook, Google) are managed via Firebase.
This means Firebase must be configured with application keys for those providers.

Dependencies
--------------
Third party libs (in libs)

requests
python-http-client
sendgrid-python -- bulk email sending
cloudstorage -- file storage in Google Cloud
xlsxwriter -- excel export

Libraries used indirectly (by other libs)

cachetools -- oauth
pyasn1 -- google authentication
rsa - google authentication

certifi -- used by requests
chardet -- requests
idna -- used by requests

Libraries from App Engine standard offering (see app.yaml)
- webapp2
- jinja2
- numpy
- ssl

Google Non-app engine google imports
- google.auth
- google.auth.transport.requests
- google.oauth2.id_token

Repositories
--------------
Until January 2020 Mimas lived in closed BitBucket repsotitory: https://bitbucket.org/allankellynet/mima
This archive remains closed.

In Januuary 2020 Mimas was mmoved to GitHub and OpenSourced.

Appologies
------------
I'm sharing this code because I want others to have access to it.
I want others to have the option of maintaining this code - or perhaps shaing with me.

I'm not sharing this code because it is high quality or because I did everything right. I wish I had known then.

So I'm sorry.

Much of this code is not canonical Python - not Pythonic, and it probably breaks a lot of Google App Engine rules too.

This was written by an old C++ programmer who was entending his knowledge of Python (and App Engine) as he went along.
Yes there is a lot that could be done better, a lot that could be refactored, even a lot that I would do differently now.
But I was learning.

Or, since I can hear Pete and Liam in my ears already, yes it is rubbish.
I'm only half the programmer I'd like to think I am.
I am Jay. I am Andy. Sorry.

(Where the code better, had I had time (and motivation) to make it better, then I would have open sourced it a lot sooner.)
