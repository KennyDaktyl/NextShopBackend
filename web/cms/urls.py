from django.urls import path

from .views import product_list, product_update, product_add_price, generate_seo_data, add_photo_to_gallery, delete_photo, edit_photo
from .views_api import update_gallery_order


urlpatterns = [
    path("lista-produktow", product_list, name="product_list"),
    path('product/update/<int:pk>/', product_update, name='product_update'),
    path('product/<int:product_id>/add-price/', product_add_price, name='product_add_price'),
    path('product/<int:product_id>/generate-seo-data/', generate_seo_data, name='generate_seo_data'),
    path('product/<int:product_id>/add_photo/', add_photo_to_gallery, name='add_photo_to_gallery'),
    
    # PHOTO GALLERY
    path('photo/<int:photo_id>/edit/', edit_photo, name='edit_photo'),
    path('photo/<int:photo_id>/delete/', delete_photo, name='delete_photo'),
    # API
    path('product/<int:product_id>/update-gallery-order/', update_gallery_order, name='update_gallery_order'),
]
