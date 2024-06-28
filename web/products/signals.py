import requests
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import logging

from web.models.products import Product, Category

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def revalidate_product_cache(sender, instance, **kwargs):
    next_js_url = 'http://localhost:3000/api/webhooks/revalidate'
    try:
        product_details_tag = f'product-{instance.slug}'
        products_by_category_tag = f'products-{instance.category.slug}'
        products_by_prev_category_tag = f'products-{instance.prev_category.slug}'
        tags = ['products', product_details_tag, products_by_category_tag, products_by_prev_category_tag, 'menu-items']
        response = requests.post(next_js_url, json={'tags': tags})
        response.raise_for_status()
        logger.info(f"Successfully revalidated cache for product {instance.slug} and tags {tags}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error revalidating cache for product {instance.id}: {e}")



## Next.js cache revalidation for categories is not working for client side navigation
# @receiver(post_save, sender=Category)
# @receiver(post_delete, sender=Category)
# def revalidate_product_cache(sender, instance, **kwargs):
#     next_js_url = 'http://localhost:3000/api/webhooks/revalidate'
#     try:
#         menu_items_category = f'menu-items-{instance.parent.slug}' if instance.parent else 'root'
#         products_by_category = f'products-{instance.slug}' 
#         tags = ['menu-items', menu_items_category, products_by_category, 'products']
#         response = requests.post(next_js_url, json={"tags": tags})
#         response.raise_for_status()
#         logger.info(f"Successfully revalidated cache for category {instance.slug} and tags {tags}")
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Error revalidating cache for category {instance.id}: {e}")