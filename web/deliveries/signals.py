import logging
import os

import requests
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from web.models.deliveries import Delivery

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Delivery)
@receiver(post_delete, sender=Delivery)
def revalidate_delivery_cache(sender, instance, **kwargs):
    next_js_url = (
        os.environ.get("NEXTJS_BASE_URL") + "/api/webhooks/revalidate"
    )
    try:
        tags = []
        main_delivery_tag = "delivery-methods"
        tags.append(main_delivery_tag)

        response = requests.post(next_js_url, json={"tags": tags})
        response.raise_for_status()
        logger.info(
            f"Successfully revalidated cache for delivery {instance.slug} and tags {tags}"
        )
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Error revalidating cache for delivery {instance.id}: {e}"
        )
