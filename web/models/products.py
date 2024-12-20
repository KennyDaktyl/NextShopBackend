import os
from datetime import timedelta

from django.conf import settings
from django.db import IntegrityError, models
from django.db.models import Min
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

from web.constants import VARIANT_COLORS
from web.models.categories import Category
from web.models.images import generate_thumbnails
from web.models.prices import ProductPrice


class Tag(models.Model):
    name = models.CharField(verbose_name="Nazwa tagu", max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tagi"
        ordering = ["name"]


class Brand(models.Model):
    name = models.CharField(verbose_name="Nazwa marki", max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Marka"
        verbose_name_plural = "Marki"
        ordering = ["name"]


class Size(models.Model):
    name = models.CharField(verbose_name="Rozmiar", max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Rozmiar"
        verbose_name_plural = "Rozmiary"
        ordering = ["name"]


class Material(models.Model):
    name = models.CharField(verbose_name="Nazwa materiału", max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Materiał"
        verbose_name_plural = "Materiały"
        ordering = ["name"]


class ProductOption(models.Model):
    name = models.CharField(verbose_name="Nazwa opcji", max_length=255)

    class Meta:
        verbose_name = "Opcja produktu"
        verbose_name_plural = "Opcje produktu"

    def __str__(self):
        return self.name


class ProductOptionItem(models.Model):
    feature = models.ForeignKey(
        ProductOption,
        verbose_name="Opcja produktu",
        on_delete=models.CASCADE,
        related_name="options",
    )
    name = models.CharField(
        verbose_name="Nazwa elementu opcji", max_length=255
    )
    order = models.IntegerField(verbose_name="Kolejność", default=1)

    class Meta:
        verbose_name = "Opcje element"
        verbose_name_plural = "Opcje elementy"
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.feature.name} - {self.name}"


class Product(models.Model):
    created_date = models.DateTimeField(
        verbose_name="Data utworzenia", auto_now_add=True
    )
    modified_date = models.DateTimeField(
        verbose_name="Data modyfikacji", auto_now=True
    )
    meta_title = models.CharField(
        verbose_name="Meta title dla produktu",
        blank=True,
        null=True,
        max_length=60,
    )
    meta_description = models.CharField(
        verbose_name="Meta description dla produktu",
        blank=True,
        null=True,
        max_length=160,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Kategoria",
        db_index=True,
        related_name="products",
    )
    google_product_category = models.CharField(
        verbose_name="Kategoria produktu w Google Merchant",
        max_length=255,
        blank=True,
        null=True,
    )
    prev_category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Poprzednia kategoria",
        db_index=True,
        related_name="prev_products",
        null=True,
        blank=True,
    )
    h1_tag = models.CharField(
        verbose_name="Tag H1", max_length=255, blank=True, null=True
    )
    name = models.CharField(
        verbose_name="Nazwa", max_length=255, db_index=True
    )
    slug = models.SlugField(
        "Slug", max_length=255, unique=True, blank=True, null=True
    )
    qty = models.IntegerField(verbose_name="Ilość", default=0)
    description = models.TextField(
        verbose_name="Opis produktu", blank=True, null=True
    )
    seo_text = models.TextField(
        verbose_name="Tekst SEO", blank=True, null=True
    )
    color = models.IntegerField(
        verbose_name="Kolor wariantu", choices=VARIANT_COLORS, default=0
    )
    accessories = models.ManyToManyField(
        "self",
        verbose_name="Akcesoria dla produktu: ",
        symmetrical=False,
        related_name="is_accessory_for",
        blank=True,
    )
    tags = models.ManyToManyField("Tag", verbose_name="Tagi", blank=True)
    size = models.ForeignKey(
        "Size",
        verbose_name="Rozmiar",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    brand = models.ForeignKey(
        "Brand",
        verbose_name="Marka",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    material = models.ForeignKey(
        "Material",
        verbose_name="Materiał",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    oryg_image = models.ImageField(
        verbose_name="Zdjęcie główne", upload_to="products", blank=True
    )
    image_alt = models.CharField(
        verbose_name="Tekst alternatywny zdjęcia",
        max_length=255,
        blank=True,
        null=True,
    )
    image_title = models.CharField(
        verbose_name="Tytuł zdjęcia", max_length=255, blank=True, null=True
    )
    is_active = models.BooleanField(verbose_name="Czy aktywny", default=True)
    on_first_page = models.BooleanField(
        default=False, verbose_name="Na 1 stronie?"
    )
    thumbnails = models.JSONField(default=dict, blank=True, null=True)

    variant_label = models.CharField(
        verbose_name="Etykieta wariantu", max_length=255, blank=True, null=True
    )
    show_variant_label = models.BooleanField(
        verbose_name="Pokazuj etykietę wariantu", default=False
    )
    product_option = models.ForeignKey(
        ProductOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product_options",
    )
    free_delivery = models.BooleanField(
        verbose_name="Darmowa dostawa", default=False
    )
    is_service = models.BooleanField(verbose_name="Usługa", default=False)

    class Meta:
        verbose_name = "Produkt"
        verbose_name_plural = "Produkty"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        is_new_instance = not self.pk
        old_image = None
        old_name = None

        if self.pk:
            if not self.oryg_image:
                self.thumbnails = {}
            old_product = Product.objects.get(pk=self.pk)
            old_name = old_product.name
            old_image = old_product.oryg_image

            if old_product.category != self.category:
                self.prev_category = old_product.category

            if (
                old_product.oryg_image
                and old_product.oryg_image != self.oryg_image
            ):
                old_image = old_product.oryg_image

            if old_product.name != self.name:
                old_name = old_product.name

            if not self.oryg_image or old_image != self.oryg_image:
                thumbs = self.product_thumbnails.filter(
                    main=True, is_variant=False
                )
                if thumbs:
                    thumbs.delete()
        super().save(*args, **kwargs)

        if is_new_instance or old_name != self.name or self.slug is None:
            self.slug = f"{slugify(self.name.replace('ł', 'l').replace('Ł', 'L'))}-id-{self.id}"

        if is_new_instance or old_image != self.oryg_image and self.oryg_image:
            if self.oryg_image:
                self.thumbnails = generate_thumbnails(
                    self,
                    True,
                    False,
                    "product",
                    self.oryg_image,
                    alt=self.image_alt,
                    title=self.image_title,
                )

        if is_new_instance:
            if self.show_variant_label:
                try:
                    variant = ProductVariant()
                    variant.product = self
                    variant.name = "Domyślny"
                    variant.slug = "domyslny"
                    variant.color = self.color
                    variant.qty = self.qty
                    variant.is_main = True
                    variant.image = self.oryg_image
                    variant.thumbnails = self.thumbnails
                    variant.save()
                except IntegrityError as e:
                    print(
                        f"IntegrityError podczas tworzenia ProductVariant: {e}"
                    )
                    raise

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_full_image_url(self, request):
        if self.oryg_image:
            return request.build_absolute_uri(
                settings.MEDIA_URL + self.oryg_image.url
            )
        return ""

    @property
    def current_price(self):
        try:
            latest_price = self.prices.latest("created_date")
            return latest_price.price
        except ProductPrice.DoesNotExist:
            return None

    @property
    def min_price_last_30(self):
        thirty_days_ago = timezone.now() - timedelta(days=30)

        min_price_query = (
            self.prices.filter(
                expired_date__gte=thirty_days_ago  
            )
            .aggregate(min_price=Min("price"))["min_price"]
        )

        return min_price_query if min_price_query is not None else self.current_price

    @property
    def images(self):
        if self.show_variant_label:
            image_main = self.product_thumbnails.filter(
                width_expected=650, height_expected=650, is_variant=False
            )
            image_variants = self.product_thumbnails.filter(
                width_expected=650, height_expected=650, is_variant=True
            )
            return image_main.union(image_variants).order_by(
                "order",
                "is_variant",
            )

        return self.product_thumbnails.filter(
            width_expected=650, height_expected=650, is_variant=False
        ).order_by("order")

    @property
    def variants(self):
        return self.variants.all()

    @property
    def image(self):
        return self.product_thumbnails.filter(
            width_expected=350,
            height_expected=350,
            main=True,
            is_variant=False,
        ).last()

    @property
    def item_image(self):
        if self.show_variant_label:
            return self.product_thumbnails.filter(
                width_expected=350,
                height_expected=350,
                main=True,
                is_variant=False,
            ).last()

        return self.product_thumbnails.filter(
            width_expected=350,
            height_expected=350,
            main=True,
            is_variant=False,
        ).last()

    @property
    def full_path(self):
        if self.is_service:
            return f"/usluga/{self.slug}"
        return f"/produkt/{self.slug}"


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    name = models.CharField(max_length=255, verbose_name="Nazwa wariantu")
    slug = models.SlugField(max_length=255, blank=True, null=True)
    order = models.IntegerField(verbose_name="Kolejność", default=1)
    color = models.IntegerField(
        verbose_name="Kolor wariantu", choices=VARIANT_COLORS, default=0
    )
    size = models.ForeignKey(
        "Size",
        verbose_name="Rozmiar",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    material = models.ForeignKey(
        "Material",
        verbose_name="Materiał",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    qty = models.IntegerField(verbose_name="Ilość", default=0)
    oryg_image = models.ImageField(
        verbose_name="Zdjęcie wariantu", upload_to="variants", blank=True
    )
    image_alt = models.CharField(
        verbose_name="Tekst alternatywny",
        max_length=255,
        blank=True,
        null=True,
    )
    image_title = models.CharField(
        verbose_name="Tytuł zdjęcia", max_length=255, blank=True, null=True
    )
    thumbnails = models.JSONField(default=dict, blank=True, null=True)
    tags = models.ManyToManyField("Tag", verbose_name="Tagi", blank=True)
    is_main = models.BooleanField(verbose_name="Czy główny", default=False)

    class Meta:
        verbose_name = "Wariant produktu"
        verbose_name_plural = "Warianty produktów"
        ordering = ["-is_main", "order", "name"]

    def save(self, *args, **kwargs):
        is_new_instance = not self.pk
        old_image = None
        old_name = None

        if self.pk:
            self.thumbnails = {}
            old_variant = ProductVariant.objects.get(pk=self.pk)
            old_image = old_variant.oryg_image
            old_name = old_variant.name

        if old_image and old_image != self.oryg_image:
            thumbs = self.variant_thumbnails.all()
            if thumbs:
                thumbs.delete()

        if is_new_instance or old_image != self.oryg_image and self.oryg_image:
            if is_new_instance:
                super().save(*args, **kwargs)
            if self.oryg_image:
                file_name = self.product.slug + "-wariant-" + self.name
                self.thumbnails = generate_thumbnails(
                    self,
                    True,
                    self.order,
                    "variant",
                    self.oryg_image,
                    file_name=file_name,
                    alt=self.image_alt,
                    title=self.image_title,
                )
        if old_name != self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    @property
    def images(self):
        return self.variant_thumbnails.filter(
            width_expected=650, height_expected=650, is_variant=True
        )

    @property
    def item_image(self):
        return self.variant_thumbnails.filter(
            width_expected=350, height_expected=350, is_variant=True, main=True
        ).first()


class ProductReview(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews', db_index=True)
    name = models.CharField(max_length=255, verbose_name="Imię", blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveSmallIntegerField() 
    message = models.TextField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['product']),
        ]
        unique_together = ('product', 'user') 
        verbose_name = "Opinia o produkcie"
        verbose_name_plural = "Opinie o produkcie"
        ordering = ['-created_at']
         
    
    def __str__(self):
        return f'{self.product.name} - {self.rating}'
    
    
@receiver(models.signals.pre_save, sender=Product)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Product.objects.get(pk=instance.pk).oryg_image
        new_file = instance.oryg_image
        if old_file and not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except Product.DoesNotExist:
        return False

    except Product.DoesNotExist:
        return False


@receiver(models.signals.post_delete, sender=Product)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.oryg_image:
        if os.path.isfile(instance.oryg_image.path):
            os.remove(instance.oryg_image.path)


@receiver(models.signals.pre_save, sender=ProductVariant)
def auto_delete_file_on_change_variant(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = ProductVariant.objects.get(pk=instance.pk).oryg_image
        new_file = instance.oryg_image
        if old_file and not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except ProductVariant.DoesNotExist:
        return False

    except ProductVariant.DoesNotExist:
        return False


@receiver(models.signals.post_delete, sender=ProductVariant)
def auto_delete_file_on_delete_variant(sender, instance, **kwargs):
    if instance.oryg_image:
        if os.path.isfile(instance.oryg_image.path):
            os.remove(instance.oryg_image.path)
