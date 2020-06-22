from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.urls import reverse
from django.http import HttpResponseRedirect

from checkout.forms import CheckoutForm, MpesaCheckoutForm
from checkout.models import Order, OrderItem, PendingMpesa
from checkout import checkout
from cart import cart
from . import mpesa_processor
from django_tools.middlewares import ThreadLocal
from threading import local
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@csrf_exempt
def show_checkout(request, checkout_type, template_name="checkout/checkout.html"):
    print(request.GET.copy())
    user = request.session['cart_id']
    request1 = locals()
    print(request1)
    print('ian')
    print(request)
    if cart.is_empty(request):
        cart_url = reverse('show_cart')
        return HttpResponseRedirect(cart_url)
    if request.method == 'POST' and request.POST.copy()['submit'] == "Mpesa Payment":
        postdata = request.POST.copy()
        form = MpesaCheckoutForm(postdata)
        if form.is_valid():
            response = mpesa_processor.process(request)
            order_number = response.get('order_number', 0)
            error_message = response.get('message', '')
            if order_number:
                request.session['order_number'] = order_number
                receipt_url = reverse('checkout_receipt')
                CART_ID_SESSION_KEY = cart.CART_ID_SESSION_KEY
                pending = PendingMpesa.objects.filter(cart=request.session[CART_ID_SESSION_KEY])
                pending.delete()
                return HttpResponseRedirect(receipt_url)
        else:
            error_message = "Correct the errors below"
    if request.method == 'POST' and request.POST.copy()['submit'] == "Place Order":
        postdata = request.POST.copy()
        form = CheckoutForm(postdata)
        if form.is_valid():
            response = checkout.process(request)
            order_number = response.get('order_number', 0)
            error_message = response.get('message', '')
            if order_number:
                request.session['order_number'] = order_number
                receipt_url = reverse('checkout_receipt')
                return HttpResponseRedirect(receipt_url)
        else:
            error_message = 'Correct the errors below'
    else:
        form = CheckoutForm()
    page_title = 'Checkout'
    if request.method == 'POST':
        postdata = request.POST.copy()
        form = MpesaCheckoutForm(postdata)
    if request.GET and checkout_type == "Lipa":
        form = MpesaCheckoutForm()
    checkout_type = checkout_type
    return render(request, template_name, locals(), RequestContext(request, dict_=request))


def receipt(request, template_name='checkout/receipt.html'):
    order_number = request.session.get('order_number', '')
    if order_number:
        order = Order.objects.filter(id=order_number)[0]
        order_items = OrderItem.objects.filter(order=order)
        del request.session['order_number']
    else:
        cart_url = reverse('show_cart')
        return HttpResponseRedirect(cart_url)
    page_title = 'Receipt'
    return render(request, template_name, locals(), RequestContext(request))
