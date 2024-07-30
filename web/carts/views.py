# views.py
import uuid
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from web.carts.cart import Cart
from web.models.products import Product, ProductVariant as Variant
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView


class CartCreateView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        body = request.data
        product_id = body.get('product_id')
        quantity = int(body.get('quantity', 1))
        variant_id = body.get('variant_id')

        product = get_object_or_404(Product, id=product_id)
        variant = None
        if variant_id:
            variant = get_object_or_404(Variant, id=variant_id)

        cart_item = {
            "id": product_id,
            'name': product.name,
            'price': str(product.current_price),
            'variant': variant.name if variant else None,
            'quantity': quantity,
        }

        cart = Cart(request)
        cart.add_product(cart_item)
        
        unique_cart_id = str(uuid.uuid4())
        response = JsonResponse({'cart_id': unique_cart_id}, status=201)
        
        response.set_cookie('sessionid', request.session.session_key, httponly=True, samesite='Lax')
        return response


class CartUpdateView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        
        body = request.data

        cart_id = body.get('cart_id')
        product_id = body.get('product_id')
        quantity = int(body.get('quantity', 1))
        variant_id = body.get('variant_id')
        
        cart = Cart(request)
        
        if not cart:
            return JsonResponse({'error': 'Cart ID not provided'}, status=400)

        product = get_object_or_404(Product, id=product_id)

        variant = None
        if variant_id:
            variant = get_object_or_404(Variant, id=variant_id)

        cart_item = {
            "id": product_id,
            'name': product.name,
            'price': str(product.current_price),
            'variant': variant.name if variant else None,
            'quantity': quantity,
        }
        
        cart.update_items(cart_item)
        return JsonResponse({'cart_id': cart_id}, status=200)


class GetCartitemsView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        cart_items = cart.get_items()
        return JsonResponse({'cart_items': cart_items}, status=200)
    
    
class TotalPriceView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        total_price = cart.get_total_price()
        return JsonResponse({'total_price': total_price}, status=200)
    

class CartDeleteView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        cart.delete_session()
        return JsonResponse({'message': 'Cart deleted'}, status=200)
    
    
create_cart = CartCreateView.as_view()
update_cart = CartUpdateView.as_view()
cart_items = GetCartitemsView.as_view()
total_price = TotalPriceView.as_view()
remove_cart = CartDeleteView.as_view()
