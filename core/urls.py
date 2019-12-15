from django.urls import path
# from .views import home, products, checkout
from .views import (
    checkout,
    HomeView,
    ItemDetailView,
    add_to_cart,
    remove_from_cart
)

app_name = 'core'

# urlpatterns = [
#     path('', item_list, name='item-list'),
    
   
# ]

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', checkout, name='checkout'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'), # the reason for slug is detailview which takes <pk> or <slug> in a classbased view
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart')
]