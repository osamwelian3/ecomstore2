import json
from mpesa_api.mpesa_credentials import validated_mpesa_access_token, LipanaMpesaPpassword, MpesaC2bCredential
from cart import cart
import http.client
from django.views.decorators.csrf import csrf_exempt
from mpesa_api.models import MpesaPayment
from .models import Order, OrderItem, PendingMpesa
from .forms import MpesaCheckoutForm


def lipa_na_mpesa_online(request):
    postdata = request.POST.copy()
    phone = postdata['phone']
    if phone[0] == "0":
        phone = phone.replace('0', '254', 1)
    elif phone[0:4] == "+254":
        phone = phone.replace('+254', '254', 1)
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
                  "\"Amount\": " + str(cart.cart_subtotal(request)) + ",\r\n        " \
                  "\"PartyA\": " + str(phone) + ",\r\n        " \
                  "\"PartyB\": " + str(LipanaMpesaPpassword.Business_short_code) + ",\r\n        " \
                  "\"PhoneNumber\": " + str(phone) + ",\r\n        " \
                  "\"CallBackURL\": \"https://873e2d51dd67.ngrok.io/api/v1/c2b/confirmation/\",\r\n        " \
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
    if 'ResponseCode' in values:
        MerchantRequestID = values['MerchantRequestID']
        CheckoutRequestID = values['CheckoutRequestID']
        ResponseCode = values['ResponseCode']
        ResponseDescription = values['ResponseDescription']
        CustomerMessage = values['CustomerMessage']
        if ResponseCode == "0":
            CART_ID_SESSION_KEY = cart.CART_ID_SESSION_KEY
            pending = PendingMpesa()
            pending.phone = phone
            pending.checkoutid = CheckoutRequestID
            pending.cart = request.session[CART_ID_SESSION_KEY]
            pending.save()
            message = query_lipa(request, CheckoutRequestID)
    if 'errorMessage' in values:
        message = 23
    return message


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
    conn.request("POST", MpesaC2bCredential.querystk, request1, headers)
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
        message = 3
    if values['ResultDesc'] == "Request cancelled by user":
        message = 1
    if values['ResultDesc'] == "The service request is processed successfully.":
        message = 0
    if values['ResultDesc'] == "System busy. The service request is rejected.":
        message = 26
    print(request1)
    print(data)
    return message


def process(request):
    paid = 0
    cancelled = 1
    timeout = 3
    failed = 5
    busy = 26
    lockfail = 23
    results = {}
    response = ''
    try:
        message = lipa_na_mpesa_online(request)
    except Exception:
        message = 4
    if message == paid:
        transaction_id = "MPESA-" + str(Order.objects.all().count() + 1) + ""
        order = create_order(request, transaction_id)
        results = {"order_number": order.id, 'message': "Payment Successfull. Your Order has been Placed"}
    if message == cancelled:
        results = {"order_number": 0, 'message': "You cancelled the MPESA request. Continue shopping or try"
                                                         " again and enter your MPESA pin to checkout"}
    if message == timeout:
        results = {"order_number": 0, 'message': "You did not enter the MPESA pin on time. Please try again"}
    if message == failed:
        results = {"order_number": 0, 'message': "We are having trouble reaching MPESA, "
                                                  "sorry for any inconvenience caused"}
    if message == busy:
        results = {"order_number": 0, 'message': "MPESA ERROR: System busy. The service request is rejected."}
    if message == lockfail:
        results = {"order_number": 0, 'message': "MPESA ERROR: Unable to lock subscriber,"
                                                 " a transaction is already in process for the current subscriber"}
    return results


def create_order(request, transaction_id):
    postdata = request.POST.copy()
    order = Order()
    checkout_form = MpesaCheckoutForm(request.POST, instance=order)
    order = checkout_form.save(commit=False)
    order.billing_name = postdata['shipping_name']
    order.billing_address_1 = postdata['shipping_address_1']
    order.billing_address_2 = postdata['shipping_address_2']
    order.billing_city = postdata['shipping_city']
    order.billing_zip = postdata['shipping_zip']
    order.billing_country = postdata['shipping_country']
    order.transaction_id = transaction_id
    order.ip_address = request.META.get('REMOTE_ADDR')
    order.user = None
    order.status = Order.SUBMITTED
    order.save()
    # if the order save succeeded
    if order.pk:
        cart_items = cart.get_cart_items(request)
        for ci in cart_items:
            # create order item for each cart item
            oi = OrderItem()
            oi.order = order
            oi.quantity = ci.quantity
            oi.price = ci.price  # now using @property
            oi.product = ci.product
            oi.save()
        # all set, empty cart
        cart.empty_cart(request)
    # return the new order object
    return order
