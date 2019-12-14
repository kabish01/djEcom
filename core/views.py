from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Item, Order, OrderItem
from django.utils import timezone

# Create your views here.

# def products(request):
#     context = {
#         'item': Item.objects.all()
#     }
#     return render(request, "product-page.html", context)

def checkout(request):
    return render(request, 'checkout.html')



# def home(request):
#     context = {
#         'object_list': Item.objects.all()
#     }
#     return render(request, "home.html", context)


class HomeView(ListView):
    model = Item
    template_name = 'home.html'



class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item = OrderItem.objects.create(item=item)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)

    return redirect("core:product", slug=slug)