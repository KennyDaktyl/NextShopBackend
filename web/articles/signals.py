import logging
import os

import requests
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from web.models.articles import Article

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
@receiver(post_delete, sender=Article)
def revalidate_product_cache_article(sender, instance, **kwargs):
    next_js_url = (
        os.environ.get("NEXTJS_BASE_URL") + "/api/webhooks/revalidate"
    )
    logger.info(
        f"Podejmuje próbę rewalidacji cache dla artykułu {instance.slug}"
    )
    try:
        tags = []
        main_articles_tag = "articles"
        tags.append(main_articles_tag)

        first_page_tag = "first-page"
        tags.append(first_page_tag)

        articles_link_path = "articles-path"
        tags.append(articles_link_path)

        article_details_tag = f"article-{instance.slug}"
        tags.append(article_details_tag)

        response = requests.post(next_js_url, json={"tags": tags})
        response.raise_for_status()
        logger.info(
            f"Successfully revalidated cache for article art {instance.slug} and tags {tags}"
        )
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Error revalidating cache for article {instance.id}: {e}"
        )


@receiver(pre_delete, sender=Article)
def cache_article_info_before_delete(sender, instance, **kwargs):
    next_js_url = (
        os.environ.get("NEXTJS_BASE_URL") + "/api/webhooks/revalidate"
    )
    try:

        tags = []
        main_articles_tag = "articles"
        tags.append(main_articles_tag)
        article_details_tag = f"article-{instance.slug}"
        tags.append(article_details_tag)

        response = requests.post(next_js_url, json={"tags": tags})
        response.raise_for_status()
        logger.info(
            f"Successfully revalidated cache for article art {instance.slug} and tags {tags}"
        )
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Error revalidating cache for article {instance.id}: {e}"
        )
