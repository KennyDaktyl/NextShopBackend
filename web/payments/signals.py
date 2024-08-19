import logging
import os

import requests
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from web.models.payments import Payment

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Payment)
@receiver(post_delete, sender=Payment)
def revalidate_payment_cache(sender, instance, **kwargs):
    next_js_url = (
        os.environ.get("NEXTJS_BASE_URL") + "/api/webhooks/revalidate"
    )
    try:
        tags = []
        main_payment_tag = "payment-methods"
        tags.append(main_payment_tag)

        response = requests.post(next_js_url, json={"tags": tags})
        response.raise_for_status()
        logger.info(
            f"Successfully revalidated cache for Payment {instance.slug} and tags {tags}"
        )
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Error revalidating cache for Payment {instance.id}: {e}"
        )
