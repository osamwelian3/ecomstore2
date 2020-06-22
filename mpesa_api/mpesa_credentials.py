from urllib.request import Request, urlopen, HTTPError, URLError
import json
from datetime import datetime
import base64
from ecomstore import settings


class MpesaC2bCredential:
    consumer_key = settings.CONSUMER_KEY
    consumer_secret = settings.CONSUMER_SECRET
    API_URL = settings.OAUTH_API
    paybill = settings.PAYBILL_NO
    c2btestpaybill = settings.c2bpaybill
    pass_key = settings.pass_key
    MPESA_URL = settings.MPESA_URL
    stk_uri = settings.stkpush_uri
    register_uri = settings.REGISTER_URI
    querystk = settings.QUERYSTK
    c2b_uri = settings.C2B_URI


def validated_mpesa_access_token():
    url = MpesaC2bCredential.API_URL
    auth = base64.b64encode(bytes('%s:%s' % (MpesaC2bCredential.consumer_key, MpesaC2bCredential.consumer_secret),
                                  'ascii'))
    req = Request(url)
    req.add_header("Authorization", "Basic %s" % auth.decode('utf-8'))
    try:
        result = urlopen(req).read()
    except URLError as err:
        raise URLError(err)
    except HTTPError as err:
        raise HTTPError(err)
    r = result.decode(encoding='utf-8', errors='ignore')
    mpesa_access_token = json.loads(r)
    validated_mpesa_access_token1 = mpesa_access_token['access_token']
    return validated_mpesa_access_token1


class LipanaMpesaPpassword:
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = MpesaC2bCredential.paybill
    Testc2b_short_code = MpesaC2bCredential.c2btestpaybill
    passkey = MpesaC2bCredential.pass_key
    data_to_encode = Business_short_code + passkey + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')
