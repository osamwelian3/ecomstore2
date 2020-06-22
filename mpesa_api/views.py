from django.shortcuts import render, reverse
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import urllib.parse
from urllib.request import Request, urlopen, HTTPError, URLError
import base64
from ecomstore import settings
import json
from .mpesa_credentials import validated_mpesa_access_token, LipanaMpesaPpassword, MpesaC2bCredential
from cart import cart
import http.client
from django.views.decorators.csrf import csrf_exempt
from .models import MpesaPayment


# Create your views here.
def getAccessToken(request):
    url = settings.OAUTH_API
    auth = base64.b64encode(bytes('%s:%s' % (settings.CONSUMER_KEY, settings.CONSUMER_SECRET), 'ascii'))
    print(auth)
    req = Request(url)
    req.add_header("Authorization", "Basic %s" % auth.decode('utf-8'))
    result = urlopen(req).read()
    print(result)
    r = result.decode(encoding='utf-8', errors='ignore')
    print(r)
    mpesa_access_token = json.loads(r)
    validated_mpesa_access_token = mpesa_access_token['access_token']
    return HttpResponse(validated_mpesa_access_token)


def lipa_na_mpesa_online(request):
    access_token = validated_mpesa_access_token()
    api_url = MpesaC2bCredential.MPESA_URL
    headers = {
        "Authorization": "Bearer %s" % access_token,
        'Content-Type': 'application/json'
    }
    conn = http.client.HTTPSConnection(api_url)
    requestbody = "{\r\n        " \
                  "\"BusinessShortCode\": " + str(LipanaMpesaPpassword.Business_short_code) + ",\r\n        " \
                  "\"Password\": \"" + str(LipanaMpesaPpassword.decode_password) + "\",\r\n        " \
                  "\"Timestamp\": \"" + str(LipanaMpesaPpassword.lipa_time) + "\",\r\n        " \
                  "\"TransactionType\": \"CustomerPayBillOnline\",\r\n        " \
                  "\"Amount\": 1,\r\n        " \
                  "\"PartyA\": 254796525626,\r\n        " \
                  "\"PartyB\": " + str(LipanaMpesaPpassword.Business_short_code) + ",\r\n        " \
                  "\"PhoneNumber\": 254796525626,\r\n        " \
                  "\"CallBackURL\": \"https://4b655c571beb.ngrok.io/api/v1/c2b/callback\",\r\n        " \
                  "\"AccountReference\": \"SAMIAN LTD\",\r\n        " \
                  "\"TransactionDesc\": \"Test\"\r\n    " \
                  "}"
    conn.request("POST", MpesaC2bCredential.stk_uri, requestbody, headers)
    response = conn.getresponse()
    response_data = response.read()
    print(requestbody)
    print(response_data.decode('utf-8'))
    data = response_data.decode('utf-8')
    values = json.loads(data)
    MerchantRequestID = values['MerchantRequestID']
    CheckoutRequestID = values['CheckoutRequestID']
    ResponseCode = values['ResponseCode']
    ResponseDescription = values['ResponseDescription']
    CustomerMessage = values['CustomerMessage']
    if ResponseCode == "0":
        return HttpResponseRedirect(reverse('qlipa', args=[CheckoutRequestID]))
    return HttpResponse(CustomerMessage)


@csrf_exempt
def query_lipa(request, cri):
    access_token = validated_mpesa_access_token()
    api_url = MpesaC2bCredential.MPESA_URL
    conn = http.client.HTTPSConnection(api_url)
    request1 = "{\r\n        " \
              "\"BusinessShortCode\": \"" + str(LipanaMpesaPpassword.Business_short_code) + "\",\r\n        " \
              "\"Password\": \"" + str(LipanaMpesaPpassword.decode_password) + "\",\r\n        " \
              "\"Timestamp\": \"" + str(LipanaMpesaPpassword.lipa_time) + "\",\r\n        " \
              "\"CheckoutRequestID\": \"" + str(cri) + "\"\r\n        " \
              "}"
    headers = {
        'Authorization': 'Bearer %s' % access_token,
        'Content-Type': 'application/json'
    }
    conn.request("POST", '/mpesa/stkpushquery/v1/query', request1, headers)
    response = conn.getresponse()
    response_data = response.read()
    data = response_data.decode('utf-8')
    values = json.loads(data)
    try:
        value = values['errorMessage']
    except Exception:
        value = values['ResponseCode']
    while value == "The transaction is being processed":
        conn.request("POST", '/mpesa/stkpushquery/v1/query', request1, headers)
        response = conn.getresponse()
        response_data = response.read()
        data = response_data.decode('utf-8')
        print(data)
        values = json.loads(data)
        if 'ResultDesc' in values:
            break
    if values['ResultDesc'] == "DS timeout.":
        message = "You took long to enter your pin. Please try again"
    if values['ResultDesc'] == "Request cancelled by user":
        message = "You cancelled the PIN request for the transaction Please try again"
    if values['ResultDesc'] == "The service request is processed successfully.":
        message = "Yey... Payment went through"
    print(request1)
    print(data)
    return HttpResponse(message)


@csrf_exempt
def register_urls(request):
    access_token = validated_mpesa_access_token()
    api_url = MpesaC2bCredential.MPESA_URL
    conn = http.client.HTTPSConnection(api_url)
    payload = "{\r\n        " \
              "\"ShortCode\": \"" + str(LipanaMpesaPpassword.Business_short_code) + "\",\r\n        " \
              "\"ResponseType\": \"Completed\",\r\n        " \
              "\"ConfirmationURL\": \"https://4b655c571beb.ngrok.io/api/v1/c2b/confirmation\",\r\n        " \
              "\"ValidationURL\": \"https://4b655c571beb.ngrok.io/api/v1/c2b/validation\"\r\n        " \
              "}"
    headers = {
        'Authorization': 'Bearer %s' % access_token,
        'Content-Type': 'application/json'
    }
    print(payload)
    conn.request("POST", MpesaC2bCredential.register_uri, payload, headers)
    response = conn.getresponse()
    response_data = response.read()
    data = response_data.decode('utf-8')
    print(data)
    values = json.loads(data)
    return HttpResponse(values['ResponseDescription'])


@csrf_exempt
def call_back(request):
    mpesa_body = request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)
    print(mpesa_payment)
    return HttpResponse(mpesa_payment)


@csrf_exempt
def c2b(request):
    access_token = validated_mpesa_access_token()
    api_url = MpesaC2bCredential.MPESA_URL
    conn = http.client.HTTPSConnection(api_url)
    request1 = "{\r\n        " \
              "\"ShortCode\": \"" + str(LipanaMpesaPpassword.Business_short_code) + "\",\r\n        " \
              "\"CommandID\": \"CustomerPayBillOnline\",\r\n        " \
              "\"Amount\": \"1\",\r\n        " \
              "\"Msisdn\": \"254708374149\",\r\n        " \
              "\"BillRefNumber\": \"Test c2b\"\r\n        " \
              "}"
    headers = {
        'Authorization': 'Bearer %s' % access_token,
        'Content-Type': 'application/json'
    }
    print(request1)
    conn.request("POST", MpesaC2bCredential.c2b_uri, request1, headers)
    response = conn.getresponse()
    response_data = response.read()
    data = response_data.decode('utf-8')
    print(data)
    values = json.loads(data)
    return HttpResponse(values)


@csrf_exempt
def validation(request):
    print(request.body)
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))


@csrf_exempt
def confirmation(request):
    print(request.body)
    mpesa_body = request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)

    payment = MpesaPayment(
        first_name=mpesa_payment['FirstName'],
        last_name=mpesa_payment['LastName'],
        middle_name=mpesa_payment['MiddleName'],
        description=mpesa_payment['TransID'],
        phone_number=mpesa_payment['MSISDN'],
        amount=mpesa_payment['TransAmount'],
        reference=mpesa_payment['BillRefNumber'],
        organization_balance=mpesa_payment['OrgAccountBalance'],
        type=mpesa_payment['TransactionType'],
    )
    payment.save()
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))
