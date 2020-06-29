from checkout import authnet_response
from cart import cart
from checkout.models import Order, OrderItem
from checkout.forms import CheckoutForm
from checkout import authnet
from ecomstore import settings
from django.urls import reverse
import urllib
import xml
from . import authnet_response
from accounts import profile


# returns the URL from the checkout module for cart
def get_checkout_url(request):
    return reverse('show_checkout', args=[request.POST.copy()['submit1']])


def process(request):
    # Transaction results
    APPROVED = '1'
    DECLINED = '2'
    ERROR = '3'
    HELD_FOR_REVIEW = '4'
    NETWORK = '5'
    results = {}
    response1 = ''
    try:
        response1 = authnet.do_auth_capture(request).read()
    except Exception as e:
        response1 = open('error.xml').read().replace("ï»¿", "")
    print(response1)
    response = xml.dom.minidom.parseString(response1)
    print(response)
    if authnet_response.get_messages_result_code(response) == 'Ok' and \
            authnet_response.get_tr_response_code(response) == APPROVED:
        transaction_id = authnet_response.get_tr_trans_id(response)
        order = create_order(request, transaction_id)
        results = {'order_number': order.id, 'message': str(authnet_response.get_tr_msgs_msg_desc(response))}
    if authnet_response.get_tr_response_code(response) == DECLINED:
        results = {'order_number': 0, 'message': 'There is a problem with your credit card: '
                                                 + str(authnet_response.get_tr_errors_error_text(response))}
    if authnet_response.get_tr_response_code(response) == ERROR or\
            authnet_response.get_tr_response_code(response) == HELD_FOR_REVIEW:
        results = {'order_number': 0, 'message': 'Error processing your order: '
                                                 + str(authnet_response.get_tr_errors_error_text(response)) + ''}
    if authnet_response.get_tr_response_code(response) == NETWORK:
        results = {'order_number': 0, 'message': 'Server Error: '
                                                 + str(authnet_response.get_tr_msgs_msg_desc(response)) + ''}
    return results


def create_order(request, transaction_id):
    order = Order()
    checkout_form = CheckoutForm(request.POST, instance=order)
    order = checkout_form.save(commit=False)
    order.transaction_id = transaction_id
    order.ip_address = request.META.get('REMOTE_ADDR')
    order.user = None
    if request.user.is_authenticated:
        order.user = request.user
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
        # save profile info for future orders
        if request.user.is_authenticated:
            profile.set(request)
    # return the new order object
    return order
