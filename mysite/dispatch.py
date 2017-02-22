import os
import requests

from google.cloud import _helpers
# TODO rename internal call dispatch or something

DEFAULT_BUCKET = r'pequod'
TEMP_TXT_BUCKET = r'pequodtexttmp'
TEMP_IMG_BUCKET = r'pequodimgtmp'
BAD_VALUE = r'na'




def local_host():
    """
    Is this a local or live environment?
    """

    return not os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/')

def project_id():
    """Returns the current google project"""
    return _helpers._determine_default_project()

LIVE_ADDRESS = r'https://' + project_id() + '.appspot.com'


def absolute_path(relative_path):
    host = r'http://localhost:8000'
    if not local_host():
        host = LIVE_ADDRESS
    return host + relative_path
        


# TODO make absolut_path a decorator
def post(relative_path, data):
    address = absolute_path(relative_path)
    return requests.post(address, data)


# TODO make absolut_path a decorator
def get(relative_path):
    address = absolute_path(relative_path)
    return requests.get(address)


