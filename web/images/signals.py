import logging
import os

import requests
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from web.models.images import Thumbnail

logger = logging.getLogger(__name__)


def revalidate_cache(tags):
    next_js_url = (
        os.environ.get("NEXTJS_BASE_URL") + "/api/webhooks/revalidate"
    )
    try:
        response = requests.post(next_js_url, json={"tags": tags})
        response.raise_for_status()
        logger.info(f"Successfully revalidated cache for tags {tags}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error revalidating cache: {e}")


@receiver(pre_delete, sender=Thumbnail)
def cache_thumbnail_info_before_delete(sender, instance, **kwargs):
    instance._product_slug = (
        instance.product.slug if instance.product else None
    )
    instance._category_slug = (
        instance.category.slug if instance.category else None
    )
    instance._variant_slug = (
        instance.product_variant.slug if instance.product_variant else None
    )
    instance._hero_id = instance.hero.id if instance.hero else None
    instance._delivery_id = instance.delivery.id if instance.delivery else None
    instance._payment_id = instance.payment.id if instance.payment else None
    instance._article_id = instance.article.id if instance.article else None


@receiver(post_delete, sender=Thumbnail)
def revalidate_product_cache_thumbnail(sender, instance, **kwargs):
    tags = []

    if hasattr(instance, "_product_slug") and instance._product_slug:
        tags.append(f"product-{instance._product_slug}")
        tags.append("products")

    if hasattr(instance, "_category_slug") and instance._category_slug:
        tags.append(f"products-{instance._category_slug}")

    if hasattr(instance, "_variant_slug") and instance._variant_slug:
        tags.append(f"product-variant-{instance._variant_slug}")

    if hasattr(instance, "_hero_id") and instance._hero_id:
        tags.append(f"hero-{instance._hero_id}")

    if hasattr(instance, "_delivery_id") and instance._delivery_id:
        tags.append(f"delivery-{instance._delivery_id}")

    if hasattr(instance, "_payment_id") and instance._payment_id:
        tags.append(f"payment-{instance._payment_id}")
    if hasattr(instance, "_article_id") and instance._article_id:
        tags.append(f"article-{instance._article_id}")
        tags.append(f"articles")

    revalidate_cache(tags)


@receiver(post_save, sender=Thumbnail)
def revalidate_product_cache_thumbnail_save(sender, instance, **kwargs):
    tags = []

    if instance.product:
        tags.append(f"product-{instance.product.slug}")

    if instance.category:
        tags.append(f"products-{instance.category.slug}")

    if instance.product_variant:
        tags.append(f"product-variant-{instance.product_variant.slug}")

    if instance.hero:
        tags.append(f"hero-{instance.hero.id}")

    if instance.delivery:
        tags.append(f"delivery-{instance.delivery.id}")

    if instance.payment:
        tags.append(f"payment-{instance.payment.id}")

    revalidate_cache(tags)
