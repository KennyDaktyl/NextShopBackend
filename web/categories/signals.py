from web.models.categories import Category

import requests
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import logging

from web.models.products import Category

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def revalidate_product_cache(sender, instance, **kwargs):
    next_js_url = 'http://localhost:3000/api/webhooks/revalidate'
    try:
        tags = []
        main_products_tag = 'products'
        tags.append(main_products_tag)
        
        current_category = instance
        while current_category:
            menu_items_category = f'products-{current_category.slug}'
            tags.append(menu_items_category)
            current_category = current_category.parent
        
        response = requests.post(next_js_url, json={"tags": tags})
        response.raise_for_status()
        logger.info(f"Successfully revalidated cache for category {instance.slug} and tags {tags}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error revalidating cache for category {instance.id}: {e}")