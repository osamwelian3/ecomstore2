from django.shortcuts import render, render_to_response
from django.template import RequestContext
from cart import cart
from django.views.decorators.csrf import csrf_exempt
from checkout import checkout
from ecomstore import settings
from django.http import HttpResponseRedirect


# Create your views here.
@csrf_exempt
def show_cart(request, template_name="cart/cart.html"):
    if request.method == 'POST':
        postdata = request.POST.copy()
        if postdata['submit'] == 'Remove':
            cart.remove_from_cart(request)
        if postdata['submit'] == 'Update':
            try:
                int(postdata['quantity'])
                cart.update_cart(request)
            except:
                if cart.cart_distinct_item_count(request) > 0:
                    qerror = 'Invalid Quantity Value'
        if postdata['submit'] == 'Card Checkout':
            checkout_url = checkout.get_checkout_url(request)
            return HttpResponseRedirect(checkout_url)
        if postdata['submit'] == 'Mpesa Checkout':
            checkout_url = checkout.get_checkout_url(request)
            return HttpResponseRedirect(checkout_url)
    cart_items = cart.get_cart_items(request)
    page_title = 'Shopping Cart'
    cart_subtotal = cart.cart_subtotal(request)
    return render(request, template_name, locals(), RequestContext(request))
