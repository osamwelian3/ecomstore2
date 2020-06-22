from ecomstore import settings
import http.client
import urllib
from .authnet_checkout import create_authnet_checkout_request
from urllib.request import Request, urlopen, HTTPError, URLError
import ssl


"""def do_auth_capture():
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    post_url = settings.AUTHNET_POST_URL
    post_path = settings.AUTHNET_POST_PATH
    cn = http.client.HTTPSConnection(post_url, http.client.HTTPS_PORT)
    cn.request('POST', post_path, cart, headers)
    return cn.getresponse().read()"""


def do_auth_capture(request):
    req = create_authnet_checkout_request(request)
    gcontext = ssl.SSLContext()
    try:
        response_xml = urlopen(req, context=gcontext)
        print('ian')
        # print(response_xml.read())
    except HTTPError as err:
        raise HTTPError(err)
    except URLError as err:
        raise URLError(err)
    return response_xml
