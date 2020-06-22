from xml.dom.minidom import Document
from xml.dom import minidom
from django.http import HttpRequest, HttpResponseRedirect
# from urllib2 import Request, urlopen, HTTPError, URLError
from urllib.request import Request, urlopen, HTTPError, URLError
import base64

from cart.models import CartItem
from cart import cart
from ecomstore import settings
from checkout.models import Order


USD = settings.USD_RATE


if Order.objects.all():
    Number = int(Order.objects.all().count()) + 1
    InvNo = 'INV-' + str(Number)
else:
    InvNo = 'INV-1'


def create_authnet_checkout_request(request):
    url = settings.AUTHNET_POST_URL
    cart = _build_xml_shopping_cart(request)
    print(cart)
    header = {'Content-Type': 'text/xml; charset=UTF-8'}
    req = Request(url=url, data=cart, headers=header)
    # req.add_header('Content-Type', 'application/xml; charset=UTF-8')
    return req


def _build_xml_shopping_cart(request):
    doc = Document()

    if request.POST:
        postdata = request.POST.copy()
        card_num = postdata.get('credit_card_number', '')
        exp_month = postdata.get('credit_card_expire_month', '')
        exp_year = postdata.get('credit_card_expire_year', '')
        exp_date = exp_year + '-' + exp_month
        cvv = postdata.get('credit_card_cvv', '')
        emailaddr = postdata.get('email', '')
        # billing info
        bname = postdata.get('billing_name', '')
        fullname = bname.split(' ')
        fname = fullname[0]
        if len(fullname) > 1:
            lname = fullname[len(fullname) - 1]
        bcity = postdata.get('shipping_city', '')
        bstate = postdata.get('shipping_state', '')
        bzip = postdata.get('shipping_zip', '')
        bcountry = postdata.get('shipping_country', '')
        baddress1 = postdata.get('billing_address_1', '')
        baddress2 = postdata.get('billing_address_2', '')
        baddress = str(baddress1) + ' ' + str(baddress2)
        # shipping info
        sname = postdata.get('shipping_name', '')
        sfullname = sname.split(' ')
        sfname = sfullname[0]
        if len(sfullname) > 1:
            slname = sfullname[len(sfullname) - 1]
        scity = postdata.get('billing_city', '')
        sstate = postdata.get('billing_state', '')
        szip = postdata.get('billing_zip', '')
        scountry = postdata.get('billing_country', '')
        saddress1 = postdata.get('billing_address_1', '')
        saddress2 = postdata.get('billing_address_2', '')
        saddress = str(saddress1) + ' ' + str(saddress2)

    root = doc.createElement('createTransactionRequest')
    root.setAttribute('xmlns', 'AnetApi/xml/v1/schema/AnetApiSchema.xsd')
    doc.appendChild(root)

    merchantauthentication = doc.createElement('merchantAuthentication')
    root.appendChild(merchantauthentication)

    name = doc.createElement('name')
    name_text = doc.createTextNode(str(settings.AUTHNET_LOGIN))
    name.appendChild(name_text)
    merchantauthentication.appendChild(name)

    transactionkey = doc.createElement('transactionKey')
    transactionkey_text = doc.createTextNode(str(settings.AUTHNET_KEY))
    transactionkey.appendChild(transactionkey_text)
    merchantauthentication.appendChild(transactionkey)

    transactionrequest = doc.createElement('transactionRequest')
    root.appendChild(transactionrequest)

    transactiontype = doc.createElement('transactionType')
    transactiontype_text = doc.createTextNode(str(settings.AUTHNET_TTYPE))
    transactiontype.appendChild(transactiontype_text)
    transactionrequest.appendChild(transactiontype)

    amount = doc.createElement('amount')
    amount_text = doc.createTextNode(str(cart.cart_subtotal(request)/USD))
    amount.appendChild(amount_text)
    transactionrequest.appendChild(amount)

    payment = doc.createElement('payment')
    transactionrequest.appendChild(payment)

    creditcard = doc.createElement('creditCard')
    payment.appendChild(creditcard)

    cardnumber = doc.createElement('cardNumber')
    cardnumber_text = doc.createTextNode(str(card_num))
    cardnumber.appendChild(cardnumber_text)
    creditcard.appendChild(cardnumber)

    expirationdate = doc.createElement('expirationDate')
    expirationdate_text = doc.createTextNode(str(exp_date))
    expirationdate.appendChild(expirationdate_text)
    creditcard.appendChild(expirationdate)

    cardcode = doc.createElement('cardCode')
    cardcode_text = doc.createTextNode(cvv)
    cardcode.appendChild(cardcode_text)
    creditcard.appendChild(cardcode)

    order = doc.createElement('order')
    transactionrequest.appendChild(order)

    invoicenumber = doc.createElement('invoiceNumber')
    invoicenumber_text = doc.createTextNode(str(InvNo))
    invoicenumber.appendChild(invoicenumber_text)
    order.appendChild(invoicenumber)

    description = doc.createElement('description')
    description_text = doc.createTextNode('Modern Musician Invoice')
    description.appendChild(description_text)
    order.appendChild(description)

    lineitems = doc.createElement('lineItems')
    transactionrequest.appendChild(lineitems)

    cart_items = cart.get_cart_items(request)
    for cart_item in cart_items:
        lineitem = doc.createElement('lineItem')
        lineitems.appendChild(lineitem)

        itemid = doc.createElement('itemId')
        itemid_text = doc.createTextNode(str(cart_item.product.id))
        itemid.appendChild(itemid_text)
        lineitem.appendChild(itemid)

        name = doc.createElement('name')
        name_text = doc.createTextNode(str(cart_item.name))
        name.appendChild(name_text)
        lineitem.appendChild(name)

        description = doc.createElement('description')
        description_text = doc.createTextNode(str(cart_item.description))
        description.appendChild(description_text)
        lineitem.appendChild(description)

        quantity = doc.createElement('quantity')
        quantity_text = doc.createTextNode(str(cart_item.quantity))
        quantity.appendChild(quantity_text)
        lineitem.appendChild(quantity)

        price = doc.createElement('unitPrice')
        price_text = doc.createTextNode(str(cart_item.price/USD))
        price.appendChild(price_text)
        lineitem.appendChild(price)

    customer = doc.createElement('customer')
    transactionrequest.appendChild(customer)

    id = doc.createElement('id')
    id_text = doc.createTextNode(str(request.user.id))
    id.appendChild(id_text)
    customer.appendChild(id)

    email = doc.createElement('email')
    email_text = doc.createTextNode(str(emailaddr))
    email.appendChild(email_text)
    customer.appendChild(email)

    billto = doc.createElement('billTo')
    transactionrequest.appendChild(billto)

    firstname = doc.createElement('firstName')
    firstname_text = doc.createTextNode(str(fname))
    firstname.appendChild(firstname_text)
    billto.appendChild(firstname)

    lastname = doc.createElement('lastName')
    lastnmae_text = doc.createTextNode(str(lname))
    lastname.appendChild(lastnmae_text)
    billto.appendChild(lastname)

    address = doc.createElement('address')
    address_text = doc.createTextNode(baddress)
    address.appendChild(address_text)
    billto.appendChild(address)

    city = doc.createElement('city')
    city_text = doc.createTextNode(str(bcity))
    city.appendChild(city_text)
    billto.appendChild(city)

    state = doc.createElement('state')
    state_text = doc.createTextNode(str(bstate))
    state.appendChild(state_text)
    billto.appendChild(state)

    zip = doc.createElement('zip')
    zip_text = doc.createTextNode(str(bzip))
    zip.appendChild(zip_text)
    billto.appendChild(zip)

    country = doc.createElement('country')
    country_text = doc.createTextNode(str(bcountry))
    country.appendChild(country_text)
    billto.appendChild(country)

    shipto = doc.createElement('shipTo')
    transactionrequest.appendChild(shipto)

    firstname = doc.createElement('firstName')
    firstname_text = doc.createTextNode(str(sfname))
    firstname.appendChild(firstname_text)
    shipto.appendChild(firstname)

    lastname = doc.createElement('lastName')
    lastnmae_text = doc.createTextNode(str(slname))
    lastname.appendChild(lastnmae_text)
    shipto.appendChild(lastname)

    address = doc.createElement('address')
    address_text = doc.createTextNode(saddress)
    address.appendChild(address_text)
    shipto.appendChild(address)

    city = doc.createElement('city')
    city_text = doc.createTextNode(str(scity))
    city.appendChild(city_text)
    shipto.appendChild(city)

    state = doc.createElement('state')
    state_text = doc.createTextNode(str(sstate))
    state.appendChild(state_text)
    shipto.appendChild(state)

    zip = doc.createElement('zip')
    zip_text = doc.createTextNode(str(szip))
    zip.appendChild(zip_text)
    shipto.appendChild(zip)

    country = doc.createElement('country')
    country_text = doc.createTextNode(str(scountry))
    country.appendChild(country_text)
    shipto.appendChild(country)
    return doc.toxml(encoding='utf-8')
