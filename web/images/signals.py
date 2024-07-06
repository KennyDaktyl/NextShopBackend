import requests
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import logging

from web.models.images import Thumbnail, Photo

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Thumbnail)
@receiver(post_delete, sender=Thumbnail)
def revalidate_product_cache(sender, instance, **kwargs):
    next_js_url = 'http://localhost:3000/api/webhooks/revalidate'
    try:
        tags = []
        if instance.product:
            main_products_tag = 'products'
            tags.append(main_products_tag)
            
            product_details_tag = f'product-{instance.product.slug}'
            tags.append(product_details_tag)

            # Dodajemy tagi dla wszystkich rodziców kategorii produktu
            current_category = instance.product.category
            while current_category:
                menu_items_category = f'products-{current_category.slug}'
                tags.append(menu_items_category)
                current_category = current_category.parent

        if instance.category:
            main_products_tag = 'products'
            tags.append(main_products_tag)
            
            products_by_category_tag = f'products-{instance.category.slug}'
            tags.append(products_by_category_tag)

            # Dodajemy tagi dla wszystkich rodziców kategorii
            current_category = instance.category
            while current_category:
                menu_items_category = f'products-{current_category.slug}'
                tags.append(menu_items_category)
                current_category = current_category.parent
        
        response = requests.post(next_js_url, json={'tags': tags})
        response.raise_for_status()
        logger.info(f"Successfully revalidated cache for instance {instance} and tags {tags}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error revalidating cache for instance {instance.id}: {e}")



# @receiver(post_save, sender=Photo)
# @receiver(post_delete, sender=Photo)
# def revalidate_product_cache(sender, instance, **kwargs):
#     next_js_url = 'http://localhost:3000/api/webhooks/revalidate'
#     try:
#         tags = []
#         if instance.product:
#             product_details_tag = f'product-{instance.product.slug}'
#             menu_items_category = f'menu-items-{instance.product.category.parent.slug}' if instance.product.category.parent else 'none'
#             menu_items_prev_category = f'menu-items-{instance.product.prev_category.parent.slug}' if instance.product.prev_category and instance.product.prev_category.parent else 'none'
            
#             tags.append(product_details_tag)
#             tags.append(menu_items_category)
#             tags.append(menu_items_prev_category)
        
#         if instance.category:
#             products_by_category_tag = f'products-{instance.slug}'
#             menu_items_category = f'menu-items-{instance.parent.slug}' if instance.parent else 'none'
        
#             tags.append(products_by_category_tag)
#             tags.append(menu_items_category)
            
#         response = requests.post(next_js_url, json={"tags": tags})
#         response.raise_for_status()
#         logger.info(f"Successfully revalidated cache for category {instance.slug} and tags {tags}")
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Error revalidating cache for category {instance.id}: {e}")