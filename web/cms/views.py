
from django.http import JsonResponse
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Max, Q

from web.models.images import Photo, Thumbnail
from web.models.products import Product
from .forms import PhotoForm, ProductPriceForm, ProductUpdateForm


@csrf_exempt
def generate_seo_data(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        form = ProductUpdateForm(instance=product)

        # Wyciąganie nazwy i URL zdjęcia
        name = product.name
        image_url = request.build_absolute_uri(product.oryg_image.url) if product.oryg_image else "brak zdjęcia"

        # Generowanie danych SEO
        seo_data = form.generate_seo_data(name, image_url, product.category.name)

        if seo_data:
            return JsonResponse({'success': True, 'seo_data': seo_data})
        return JsonResponse({'success': False, 'error': 'Nie udało się wygenerować danych SEO.'})
    return JsonResponse({'success': False, 'error': 'Metoda POST wymagana.'})


class ProductListView(ListView):
    model = Product
    template_name = 'cms/product_list.html'
    context_object_name = 'products'
    paginate_by = 50

    def get_queryset(self):
        return Product.objects.filter(is_active=True).order_by('name')
    

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductUpdateForm
    template_name = 'cms/forms/product_update.html'
    success_url = reverse_lazy('product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['price_form'] = ProductPriceForm()
        context['current_price'] = self.object.prices.filter(expired_date__isnull=True).first()
        context['gallery_images'] = Photo.objects.filter(product=self.object).order_by('order')
        return context
    

@csrf_exempt
def product_add_price(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductPriceForm(request.POST)
        if form.is_valid():
            new_price = form.save(commit=False)
            new_price.product = product
            new_price.save()
            product.save()
    return redirect('product_update', pk=product.id)


def add_photo_to_gallery(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.product = product
            
            # # Ustal kolejność (order)
            # max_order = Photo.objects.filter(product=product).aggregate(max_order=Max('order'))['max_order']
            # photo.order = (max_order or 0) + 1
            
            photo.save()
            messages.success(request, 'Zdjęcie zostało pomyślnie dodane.')
            return redirect('product_update', pk=product.id)
        else:
            messages.error(request, 'Wystąpił błąd w formularzu.')
    
    return redirect('product_update', pk=product.id)


def edit_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)

    if request.method == 'POST':
        form = PhotoForm(request.POST, instance=photo)
        if form.is_valid():
            form.save()
            thumbnails = Thumbnail.objects.filter(product=photo.product, order=photo.order)
            for thumbnail in thumbnails:
                thumbnail.alt = photo.image_alt
                thumbnail.title = photo.image_title
                thumbnail.save()
                
            messages.success(request, 'Zdjęcie oraz powiązane miniatury zostały zaktualizowane.')
        else:
            messages.error(request, 'Wystąpił błąd podczas edycji zdjęcia.')
        return redirect('product_update', pk=photo.product.id)

    messages.error(request, 'Nieprawidłowa metoda żądania.')
    return redirect('product_update', pk=photo.product.id)


def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)

    if request.method == 'POST':
        photo.delete()
        
        thumbnails = Thumbnail.objects.filter(product=photo.product, order=photo.order)
        for thumbnail in thumbnails:
            thumbnail.delete()
            
        messages.success(request, 'Zdjęcie oraz powiązane miniatury zostały usunięte.')
        return redirect('product_update', pk=photo.product.id)

    messages.error(request, 'Nieprawidłowa metoda żądania.')
    return redirect('product_update', pk=photo.product.id)
        
    

product_list = ProductListView.as_view()
product_update = ProductUpdateView.as_view()
