import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
from django.dispatch import receiver
from django.utils.text import slugify
from PIL import Image

from serwiswrybnej import settings

THUMBNAIL_SIZES = [
    (100, 100),
    (350, 350),
    (650, 650),
]


def generate_thumbnails(
    instance, main, order, relation_name, original_image, file_name=None
):
    if not file_name:
        file_name = instance.slug
    thumbnails = {}
    for size in THUMBNAIL_SIZES:
        thumbnail = create_thumbnail(
            relation=instance,
            relation_name=relation_name,
            size=size,
            main=main,
            order=order,
            original_image=original_image,
            file_name=file_name,
        )
        thumbnails.update(thumbnail)
    return thumbnails


class Photo(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    order = models.IntegerField(default=1)
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="photos",
        null=True,
        blank=True,
    )
    variant = models.ForeignKey(
        "ProductVariant",
        on_delete=models.CASCADE,
        related_name="photos",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="photos",
        null=True,
        blank=True,
    )
    oryg_image = models.ImageField(upload_to="photos/")
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    title_text = models.CharField(max_length=255, blank=True, null=True)
    thumbnails = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Zdjęcie"
        verbose_name_plural = "Zdjęcia"

    def save(self, *args, **kwargs):
        if self.product:
            instance_name = "product"
            instance = self.product
        elif self.variant:
            instance_name = "variant"
            instance = self.variant
        elif self.category:
            instance_name = "category"
            instance = self.category
        else:
            instance_name = "photo"
            instance = self

        if self.pk:
            old_photo = Photo.objects.get(pk=self.pk)
            if old_photo.oryg_image != self.oryg_image:
                delete_thumbnails(instance, instance_name)
            if old_photo.name != self.name:
                self.slug = slugify(
                    self.name.replace("ł", "l").replace("Ł", "L")
                )

                self.thumbnails = generate_thumbnails(
                    instance,
                    False,
                    self.order,
                    instance_name,
                    self.oryg_image,
                    self.slug,
                )
        else:
            title = self.name if self.name else instance.name
            self.slug = slugify(title.replace("ł", "l").replace("Ł", "L"))
            super().save(*args, **kwargs)
            self.thumbnails = generate_thumbnails(
                instance,
                False,
                self.order,
                instance_name,
                self.oryg_image,
                self.slug,
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image {self.id}"


class Thumbnail(models.Model):
    main = models.BooleanField(default=False)
    is_variant = models.BooleanField(default=False)
    order = models.IntegerField(default=1)
    photo = models.ForeignKey(
        "Photo",
        on_delete=models.CASCADE,
        related_name="photo_thumbnails",
        null=True,
        blank=True,
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="product_thumbnails",
        null=True,
        blank=True,
    )
    product_variant = models.ForeignKey(
        "ProductVariant",
        on_delete=models.CASCADE,
        related_name="variant_thumbnails",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="category_thumbnails",
        null=True,
        blank=True,
    )
    hero = models.ForeignKey(
        "Hero",
        on_delete=models.CASCADE,
        related_name="hero_thumbnails",
        null=True,
        blank=True,
    )
    width = models.IntegerField(verbose_name="Szerokość")
    height = models.IntegerField(verbose_name="Wysokość")
    width_expected = models.IntegerField(
        verbose_name="Szerokość", null=True, blank=True
    )
    height_expected = models.IntegerField(
        verbose_name="Wysokość", null=True, blank=True
    )
    oryg_image = models.ImageField(upload_to="thumbnails/")
    alt = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["-main", "order", "id"]
        verbose_name = "Miniatura"
        verbose_name_plural = "Miniatury"

    def __str__(self):
        return f"Thumbnail {self.id}"


def create_thumbnail(
    relation, relation_name, size, main, order, original_image, file_name
):
    thumbnail = Thumbnail()

    if not order:
        filter_kwargs = {relation_name: relation}
        order = (
            Thumbnail.objects.filter(
                width=size[0], height=size[1], **filter_kwargs
            ).count()
            + 1
        )

    img = Image.open(original_image)

    if relation_name == "product":
        thumbnail.product = relation
    elif relation_name == "variant":
        thumbnail.product_variant = relation
        thumbnail.product = relation.product
        thumbnail.is_variant = True
    elif relation_name == "category":
        thumbnail.category = relation
    elif relation_name == "photo":
        thumbnail.photo = relation
    elif relation_name == "hero":
        thumbnail.hero = relation
    else:
        raise ValueError(
            "Relation must be 'product', 'variant', 'category', 'hero' or 'photo'."
        )

    # Zmniejszenie obrazu zachowując proporcje
    img.thumbnail(size, Image.LANCZOS)

    # Zmiana rozmiaru obrazu, aby nie przekraczał podanej szerokości i wysokości, zachowując proporcje
    img_ratio = img.width / img.height
    target_ratio = size[0] / size[1]

    if img_ratio > target_ratio:
        new_width = size[0]
        new_height = int(new_width / img_ratio)
    else:
        new_height = size[1]
        new_width = int(new_height * img_ratio)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    thumbnail_dir = os.path.join(settings.MEDIA_ROOT, "thumbnails/")
    if not os.path.exists(thumbnail_dir):
        os.makedirs(thumbnail_dir)

    filename = (
        f"{file_name.replace(' ', '_').lower()}_{size[0]}x{size[1]}.webp"
    )
    thumbnail.main = main
    thumbnail.order = order
    thumbnail.width = new_width
    thumbnail.height = new_height
    thumbnail.width_expected = size[0]
    thumbnail.height_expected = size[1]

    temp_thumb = BytesIO()
    img.convert("RGBA").save(temp_thumb, "WEBP", quality=100, lossless=True)
    temp_thumb.seek(0)

    thumbnail.oryg_image.save(
        filename, ContentFile(temp_thumb.read()), save=False
    )
    thumbnail.save()

    temp_thumb.close()

    return {f"{new_width}x{new_height}": thumbnail.oryg_image.url}


def delete_thumbnails(instance, field_name):
    instance.thumbnails = {}

    filter_kwargs = {field_name: instance}
    thumbs = Thumbnail.objects.filter(**filter_kwargs)
    if thumbs:
        thumbs.delete()


@receiver(models.signals.post_delete, sender=Photo)
def auto_delete_file_on_delete_image(instance, **kwargs):
    thumbs = Thumbnail.objects.filter(photo=instance)
    if thumbs:
        thumbs.delete()
    if instance.oryg_image:
        if os.path.isfile(instance.oryg_image.path):
            try:
                os.remove(instance.oryg_image.path)
            except OSError:
                pass


@receiver(models.signals.pre_save, sender=Photo)
def auto_delete_file_on_change_image(instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_photo = Photo.objects.get(pk=instance.pk)
        old_file = old_photo.oryg_image
    except Photo.DoesNotExist:
        return False

    new_file = instance.oryg_image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            try:
                os.remove(old_file.path)
            except OSError:
                pass


@receiver(models.signals.post_delete, sender=Thumbnail)
def auto_delete_file_on_delete(instance, **kwargs):
    if instance.oryg_image:
        if os.path.isfile(instance.oryg_image.path):
            try:
                os.remove(instance.oryg_image.path)
            except OSError:
                pass


@receiver(models.signals.pre_save, sender=Thumbnail)
def auto_delete_file_on_change(instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Thumbnail.objects.get(pk=instance.pk).oryg_image
    except Thumbnail.DoesNotExist:
        return False

    new_file = instance.oryg_image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            try:
                os.remove(old_file.path)
            except OSError:
                pass
