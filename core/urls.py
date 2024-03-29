from django.urls import path
# from .views import home, products, checkout
from .views import (
    CheckoutView,
    HomeView,
    ItemDetailView,
    OrderSummaryView, 
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView, 
    # add_coupon is replaced by AddCouponView
    AddCouponView,
    RequestRefundView
)

app_name = 'core'

# urlpatterns = [
#     path('', item_list, name='item-list'),
    
   
# ]

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'), # the reason for slug is detailview which takes <pk> or <slug> in a classbased view
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    # path('add-coupon/', add_coupon, name='add-coupon'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('payment/<payment_option>', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund')
    # path('accounts/', include('allauth.urls'))
]