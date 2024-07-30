from django.urls import path
from .views import create_cart, update_cart, total_price, cart_items, remove_cart


urlpatterns = [
   path('create', create_cart, name='create_cart'),
   path('update', update_cart, name='update_cart'),
   path('total-price', total_price, name='total_price'),
   path('cart-items', cart_items, name='cart_items'),
   path('remove-cart', remove_cart, name='remove_cart'),
]
