import os
from venv import logger

import requests
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from web.models.heros import Hero


@receiver(post_save, sender=Hero)
@receiver(post_delete, sender=Hero)
def revalidate_hero_cache(sender, instance, **kwargs):
    next_js_url = (
        os.environ.get("NEXTJS_BASE_URL") + "/api/webhooks/revalidate"
    )
    try:
        tags = []
        first_page_tag = "first-page"
        tags.append(first_page_tag)

        response = requests.post(next_js_url, json={"tags": tags})
        response.raise_for_status()
        logger.info(
            f"Successfully revalidated cache for instance {instance} and tags {tags}"
        )
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Error revalidating cache for instance {instance.id}: {e}"
        )
