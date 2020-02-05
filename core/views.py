from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from .models import Item, Order, OrderItem, Address, Coupon, Refund
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .forms import CheckoutForm, CouponForm, RefundForm
import random
import string
import requests


# from khalti-web import KhaltiCheckout


# Create your views here.

# def products(request):
#     context = {
#         'item': Item.objects.all()
#     }
#     return render(request, "product-page.html", context)


# def checkout(request):
#     return render(request, 'checkout.html')


# def home(request):
#     context = {
#         'object_list': Item.objects.all()
#     }
#     return render(request, "home.html", context)

# To create a random ref_code:
def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=25))

# to prevent user from validating empty string to default value and saving wrong data:


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:

            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()

            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})
                # shipping_address_qs[0] represents first item of shipping address.

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})

            return render(self.request, "checkout.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect('core:checkout')
        # form

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if form.is_valid():
                # For defafult shipping:
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the default shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')

                else:
                    print("User is entering a new shipping address")

                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):

                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()
                        # Set new default shipping address:
                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                # For default billing

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')

                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None  # cloning the billing address that has same shipping address

                    billing_address.save()   # creating a new address for billing address
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the default billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('core:checkout')

                else:
                    print("User is entering a new billing address")

                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):

                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()
                        # Set new default billing address:
                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')

                # TODO: add a redirect to the selected payment option

                if payment_option == 'K':
                    return redirect('core:payment', payment_option='khalti')
                elif payment_option == 'E':
                    return redirect('core:payment', payment_option='esewa')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):

       
        order = Order.objects.get(user=self.request.user, ordered=False)

        # form = CheckoutForm()
        if order.billing_address:

            context = {
                # 'form': form,
                'order': order,
                'DISPLAY_COUPON_FORM': False

            }
            return render(self.request, "payment.html", context)

        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("core:checkout")
    


    def post(self, *args, **kwargs):

        order = Order.objects.get(user=self.request.user, ordered=False)

        # item = Item.objects.get(user=self.request.user, )
        # pub_key = 'test_public_key_4e38b46a170946d5a29516aa4100b194'
        # amt = int(order.get_total() * 100)
        # pid = order.pk()
        # pname = order.title()
        # purl = '/product'
        # pub_key = 'test_public_key_4e38b46a170946d5a29516aa4100b194'
        # amt = int(order.get_total() * 100)
        # pid = order.items.item.pk
        # pname = order.items.item.title
        # purl = '/product'

        # config = {
        #     publicKey= pub_key,
        #     productIdentity: pid,
        #     productName: pname,
        #     productUrl=None,
        #     amount: amt
        # }
        if order.billing_address:
            context = {

                'order': order,
                'item': item
                # 'config': config
            }
            return render(self.request, "paymemt.html", context)
            messages.success(self.request, "Your order was successful!")

            # Create the payment
            # url = "https://khalti.com/api/v2/merchant-transaction/"
            # payload = {}
            # headers = {
            # "Authorization": "Key test_secret_key_f59e8b7d18b4499ca40f68195a846e9b"                }

            # response = requests.get(url, payload, headers=headers)

            payment = Payment()
        # # payment.charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

        # # assign the payment to the order

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            # TODO: assign ref code
            order.ref_code = create_ref_code()

            order.save()
            return redirect("core:home")

        # pid = Order.objects.get(id=self.request.id)
        # pname = Order.objects.get(item=self.request.items)
        # # productUrl = None

        # amt = int(order.get_total()*100)

        # here

        # config = {
        #     "publicKey": "test_public_key_4e38b46a170946d5a29516aa4100b194",
        #     "productIdentity": productId,
        #     "productName": productName,
        #     "productUrl": productUrl,
        #     "eventHandler": {
        #         onSuccess(payload){

        #             # hit merchant api for initiating verfication
        #             console.log(payload)
        #             order.ordered = True

        #         }

        #         onError(error){
        #             console.log(payload)

        #         }
        #         onClose(){
        #             console.log("Widget is closing")
        #         }

        #     }
        # }

        # checkout = new KhaltiCheckout(config)
        # btn = document.getElementById("payment-button")
        # btn.onclick = function(){
        #     checkout.show(amount)
        # }

        # url="https://uat.esewa.com.np/epay/main"
        # d={'amt': amount,
        # 'pdc': 0,
        # 'psc': 0,
        # 'txAmt': 0.13*amount,
        # 'tAmt': ,
        # # 'pid': 'ee2c3ca1-696b-4cc5-a6be-2c40d929d453',

        # 'scd': 'epay_payment',
        # 'su': 'http://merchant.com.np/page/esewa_payment_success?q=su',
        # 'fu': 'http://merchant.com.np/page/esewa_payment_failed?q=fu',
        # }
        # resp=req.post(url, d)

        # From here


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = 'home.html'


# for decorator like usage in class we used LoginRequiredMixin as the first argument that our class inherits from
class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated")
            return redirect("core:order-summary")

        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )

    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart")
            return redirect("core:order-summary")
        else:
            # add a message saying the order does not exist
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)

    else:
        # add a message saying the user doesn't have an order
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )

    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()

            else:
                order.items.remove(order_item)
                order_item.save()
            messages.info(request, "This item was updated")
            return redirect("core:order-summary")
        else:
            # add a message saying the order does not exist
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)

    else:
        # add a message saying the user doesn't have an order
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


def get_coupon(request, code):

    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info("This coupon does not exist")
        return redirect('core:checkout')


# def add_coupon(request):
#     if request.method == "POST":
#         form = CouponForm(request.POST or None)
#         if form.is_valid():
#             try:
#                 code = form.cleaned_data.get('code')
#                 order = Order.objects.get(user=request.user, ordered=False)
#                 order.coupon = get_coupon(request, code)
#                 order.save()
#                 messages.success(request, "Successfuly added coupon")
#                 return redirect('core:checkout')
#             except ObjectDoesNotExist:
#                 messages.info(request, "You do not have an active order")
#                 return redirect('core:checkout')

#         # TODO: raise error
#         return None

class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False
                )
                order.coupon = get_coupon(
                    self.request, "Successfully added coupon")
                return redirect('core:checkout')
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect('core:checkout')


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your message was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")
