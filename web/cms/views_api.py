from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from web.models.images import Thumbnail
from web.models.products import Product


@csrf_exempt
def update_gallery_order(request, product_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = data.get('order', [])
            
            # Aktualizuj kolejność miniaturek
            for index, thumbnail_id in enumerate(order):
                Thumbnail.objects.filter(id=thumbnail_id).update(order=index + 1)
            product = Product.objects.get(id=product_id)
            product.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False}, status=405)
