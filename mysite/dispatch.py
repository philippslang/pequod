import os
import requests

# TODO rename internal call dispatch or something

LIVE_ADDRESS = r'https://djangorest-157719.appspot.com'
DEFAULT_BUCKET = r'pequod'
TEMP_TXT_BUCKET = r'pequodtexttmp'
TEMP_IMG_BUCKET = r'pequodimgtmp'
BAD_VALUE = r'na'

def local_host():
    """
    Is this a local or live environment?
    """

    return not os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/')


def absolute_path(relative_path):
    host = r'http://localhost:8000'
    if not local_host():
        host = LIVE_ADDRESS
    return host + relative_path
        


# TODO make absolut_path a decorator
def post(relative_path, data):
    address = absolute_path(relative_path)
    return requests.post(address, data)


