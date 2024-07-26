from datetime import timedelta
import os

from django.conf import settings
from django.db import IntegrityError, models
from django.db.models import Min
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from web.constants import VARIANT_COLORS
from web.models.categories import Category
from web.models.images import create_thumbnail, delete_thumbnails, generate_thumbnails
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
        
        
class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Kategoria",
        db_index=True,
        related_name="products",
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
    color = models.IntegerField(verbose_name='Kolor wariantu', choices=VARIANT_COLORS, default=0)
    accessories = models.ManyToManyField('self', verbose_name="Akcesoria dla produktu: ", symmetrical=False, related_name='is_accessory_for', blank=True)
    tags = models.ManyToManyField('Tag', verbose_name="Tagi", blank=True)
    size = models.ForeignKey('Size', verbose_name="Rozmiar", on_delete=models.CASCADE, blank=True, null=True)
    brand = models.ForeignKey('Brand', verbose_name="Marka", on_delete=models.CASCADE, blank=True, null=True)
    material = models.ForeignKey('Material', verbose_name="Materiał", on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(verbose_name="Zdjęcie główne", upload_to="products", blank=True)
    is_active = models.BooleanField(verbose_name="Czy aktywny", default=True)
    thumbnails = models.JSONField(default=dict, blank=True, null=True)
    
    variant_label = models.CharField(verbose_name="Etykieta wariantu", max_length=255, blank=True, null=True)
    show_variant_label = models.BooleanField(verbose_name="Pokazuj etykietę wariantu", default=False)

    class Meta:
        verbose_name = "Produkt"
        verbose_name_plural = "Produkty"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        is_new_instance = not self.pk
        old_image = None
        old_name = None
        
        if self.pk:
            if not self.image:
                self.thumbnails = {}
            old_product = Product.objects.get(pk=self.pk)
            old_name = old_product.name
            old_image = old_product.image
            
            if old_product.category != self.category:
                self.prev_category = old_product.category

            if old_product.image and old_product.image != self.image:
                old_image = old_product.image

            if old_product.name != self.name:
                old_name = old_product.name
        
        if old_image and old_image != self.image:
            thumbs = self.product_thumbnails.filter(main=True)
            if thumbs:
                thumbs.delete()
        super().save(*args, **kwargs)
        
        if is_new_instance or old_name != self.name or self.slug is None:
            self.slug = f"{slugify(self.name.replace('ł', 'l').replace('Ł', 'L'))}-id-{self.id}"
        
        if is_new_instance or old_image != self.image and self.image:
            if self.image:
                self.thumbnails = generate_thumbnails(self, True, False, "product", self.image)
            
        if is_new_instance:
            if self.show_variant_label:
                try:
                    # Sprawdzanie, czy ProductVariant już istnieje
                    variant = ProductVariant()
                    variant.product = self
                    variant.name = "Domyślny"
                    variant.slug="domyslny"
                    variant.color=self.color
                    variant.qty=self.qty
                    variant.is_main=True
                    variant.image=self.image
                    variant.thumbnails=self.thumbnails
                    variant.save()
                except IntegrityError as e:
                    # Logowanie błędu dla lepszego zrozumienia problemu
                    print(f"IntegrityError podczas tworzenia ProductVariant: {e}")
                    raise
                
        super().save(*args, **kwargs)
            
        
    def __str__(self):
        return self.name

    def get_full_image_url(self, request):
        if self.image:
            return request.build_absolute_uri(
                settings.MEDIA_URL + self.image.url
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
        current_price = self.current_price
        min_price_query = (
            self.prices.filter(created_date__gte=thirty_days_ago)
            .exclude(price=current_price)
            .aggregate(min_price=Min("price"))["min_price"]
        )
        return (
            min_price_query if min_price_query is not None else current_price
        )

    @property
    def images(self):
        if self.show_variant_label:
            return self.product_thumbnails.filter(width_expected=650, height_expected=650, main=False)
        return self.product_thumbnails.filter(width_expected=650, height_expected=650)
    
    @property
    def variants(self):
        return self.variants.all()
    
    @property
    def image_list_item(self):
        return self.product_thumbnails.filter(width_expected=350, height_expected=350, main=True).first()
    
    def get_absolute_url(self):
        return f"/produkt/{self.slug}"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=255, verbose_name='Nazwa wariantu')
    slug = models.SlugField(max_length=255, blank=True, null=True)
    order = models.IntegerField(verbose_name='Kolejność', default=1)
    color = models.IntegerField(verbose_name='Kolor wariantu', choices=VARIANT_COLORS, default=0)
    size = models.ForeignKey('Size', verbose_name='Rozmiar', on_delete=models.CASCADE, blank=True, null=True)
    material = models.ForeignKey('Material', verbose_name='Materiał', on_delete=models.CASCADE, blank=True, null=True)
    qty = models.IntegerField(verbose_name='Ilość', default=0)
    image = models.ImageField(verbose_name='Zdjęcie wariantu', upload_to='variants', blank=True)
    thumbnails = models.JSONField(default=dict, blank=True, null=True)
    tags = models.ManyToManyField('Tag', verbose_name="Tagi", blank=True)
    is_main = models.BooleanField(verbose_name='Czy główny', default=False)

    class Meta:
        verbose_name = 'Wariant produktu'
        verbose_name_plural = 'Warianty produktów'
        ordering = ['-is_main', 'order', 'name']

    def save(self, *args, **kwargs):
        is_new_instance = not self.pk
        old_image = None
        old_name = None

        if self.pk:
            old_variant = ProductVariant.objects.get(pk=self.pk)
            old_image = old_variant.image
            old_name = old_variant.name

        if old_image and old_image != self.image:
            thumbs = self.variant_thumbnails.all()
            if thumbs:
                thumbs.delete()

        if is_new_instance or old_image != self.image and self.image:
            if is_new_instance:
                super().save(*args, **kwargs)
            if self.image:
                file_name = self.product.slug + "-wariant-" + self.name
                self.thumbnails = generate_thumbnails(self, False, self.order, 'variant', self.image, file_name=file_name)
        if old_name != self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
        
    def __str__(self):
        return f'{self.product.name} - {self.name}'
    
    @property
    def images(self):
        return self.variant_thumbnails.filter(width_expected=650, height_expected=650, is_variant=True)


@receiver(models.signals.pre_save, sender=Product)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Product.objects.get(pk=instance.pk).image
        new_file = instance.image
        if old_file and not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except Product.DoesNotExist:
        return False

    except Product.DoesNotExist:
        return False  


@receiver(models.signals.post_delete, sender=Product)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
            

@receiver(models.signals.pre_save, sender=ProductVariant)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = ProductVariant.objects.get(pk=instance.pk).image
        new_file = instance.image
        if old_file and not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except ProductVariant.DoesNotExist:
        return False

    except ProductVariant.DoesNotExist:
        return False  


@receiver(models.signals.post_delete, sender=ProductVariant)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)