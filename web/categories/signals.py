import logging
import os

import requests
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from web.models.categories import Category

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def revalidate_product_cache_category(sender, instance, **kwargs):
    next_js_url = (
        os.environ.get("NEXTJS_BASE_URL") + "/api/webhooks/revalidate"
    )
    try:
        tags = []
        main_products_tag = "products"
        tags.append(main_products_tag)

        first_page_tag = "first-page"
        tags.append(first_page_tag)

        category_meta_tag = "category-meta"
        tags.append(category_meta_tag)

        categories_link_path = "categories-path"
        tags.append(categories_link_path)

        current_category = instance
        while current_category:
            products_category = f"products-{current_category.slug}"
            tags.append(products_category)
            menu_items = f"menu-items-{current_category.slug}"
            tags.append(menu_items)
            current_category = current_category.parent

        response = requests.post(next_js_url, json={"tags": tags})
        response.raise_for_status()
        logger.info(
            f"Successfully revalidated cache for category {instance.slug} and tags {tags}"
        )
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Error revalidating cache for category {instance.id}: {e}"
        )
