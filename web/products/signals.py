import logging
import os

import requests
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from web.models.products import Product, ProductVariant

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def revalidate_product_cache_product(sender, instance, **kwargs):
    next_js_url = (
        os.environ.get("NEXTJS_BASE_URL") + "/api/webhooks/revalidate"
    )
    try:
        tags = []
        main_products_tag = "products"
        tags.append(main_products_tag)

        product_details_tag = f"product-{instance.slug}"
        tags.append(product_details_tag)

        first_page_tag = "first-page"
        tags.append(first_page_tag)

        products_link_path = "products-path"
        tags.append(products_link_path)

        product_category = instance.category
        while product_category:
            menu_items_category = f"menu-items-{product_category.slug}"
            tags.append(menu_items_category)
            products_category = f"products-{product_category.slug}"
            tags.append(products_category)
            product_category = product_category.parent

        if instance.prev_category:
            prev_category = instance.prev_category
            while prev_category:
                menu_items_prev_category = f"menu-items-{prev_category.slug}"
                tags.append(menu_items_prev_category)
                prev_category = prev_category.parent

        response = requests.post(next_js_url, json={"tags": tags})
        response.raise_for_status()
        logger.info(
            f"Successfully revalidated cache for product {instance.slug} and tags {tags}"
        )
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Error revalidating cache for product {instance.id}: {e}"
        )


@receiver(post_save, sender=ProductVariant)
@receiver(post_delete, sender=ProductVariant)
def revalidate_product_cache_variant(sender, instance, **kwargs):
    next_js_url = (
        os.environ.get("NEXTJS_BASE_URL") + "/api/webhooks/revalidate"
    )
    try:
        tags = []
        main_products_tag = "products"
        tags.append(main_products_tag)

        paths_tag = "products-path"
        tags.append(paths_tag)

        product_details_tag = f"product-{instance.product.slug}"
        tags.append(product_details_tag)

        first_page_tag = "first-page"
        tags.append(first_page_tag)

        product_category = instance.product.category
        while product_category:
            menu_items_category = f"menu-items-{product_category.slug}"
            tags.append(menu_items_category)
            products_category = f"products-{product_category.slug}"
            tags.append(products_category)
            product_category = product_category.parent

        response = requests.post(next_js_url, json={"tags": tags})
        response.raise_for_status()
        logger.info(
            f"Successfully revalidated cache for product {instance.slug} and tags {tags}"
        )
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Error revalidating cache for product {instance.id}: {e}"
        )
