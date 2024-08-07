from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from web.models.accounts import Profile
from web.models.carts import Cart, CartItem
from web.models.categories import Category
from web.models.heros import Hero
from web.models.images import Photo, Thumbnail
from web.models.orders import Order, OrderItem
from web.models.prices import PriceGroup, ProductPrice
from web.models.products import (Brand, Material, Product, ProductOption,
                                 ProductOptionItem, ProductVariant, Size, Tag)
from web.models.shipments import Shipment


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Hero._meta.fields]
    search_fields = ("name",)
    list_filter = ["is_active"]


class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-id",)
    readonly_fields = ("date_joined",)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(PriceGroup)
class PriceGroupAdmin(admin.ModelAdmin):
    list_display = [f.name for f in PriceGroup._meta.fields]
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Category._meta.fields]
    search_fields = ("name",)
    list_filter = ["is_active", "is_main"]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Profile._meta.fields]
    search_fields = (
        "user__username",
        "user__email",
        "company",
        "nip",
        "address",
        "city",
        "postal_code",
    )
    list_filter = ["user__is_active", "status", "newsletter"]


class ProductPriceInline(admin.TabularInline):
    model = ProductPrice
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ProductOption._meta.fields]
    search_fields = ["name", "pk"]


@admin.register(ProductOptionItem)
class ProductOptionItemAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ProductOptionItem._meta.fields]
    search_fields = ["name", "pk"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariantInline, ProductPriceInline]
    list_display = [f.name for f in Product._meta.fields]
    search_fields = ["name", "pk"]
    list_filter = ["on_first_page"]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "category" in form.base_fields:
            form.base_fields["category"].queryset = Category.objects.filter(
                children__isnull=True
            )
        return form


admin.register(ProductPrice)


class ProductPriceAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ProductPrice._meta.fields]
    search_fields = ["product__name", "price"]
    list_filter = ["product__name"]


class ItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "created_date",
        "amount",
        "amount_with_discount",
        "discount",
    )
    search_fields = ("client__username", "client__email")
    list_filter = ("created_date", "updated_date")
    inlines = [ItemInline]


@admin.register(CartItem)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "name", "qty", "price", "discount")
    search_fields = ("name", "cart__client__username")
    list_filter = ("cart__created_date",)


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "status",
        "client",
        "client_name",
        "created_date",
        "amount",
        "amount_with_discount",
        "delivery_method",
        "payment_method",
    )
    search_fields = (
        "order_number",
        "client__username",
        "client_email",
        "client_name",
    )
    list_filter = (
        "status",
        "created_date",
        "updated_date",
        "delivery_method",
        "payment_method",
    )
    readonly_fields = ("created_date", "updated_date")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "order_number",
                    "status",
                    "client",
                    "client_name",
                    "client_email",
                    "client_phone",
                    "client_address",
                    "amount",
                    "amount_with_discount",
                    "discount",
                    "info",
                    "delivery_method",
                    "payment_method",
                )
            },
        ),
        (
            "Payment Information",
            {
                "fields": (
                    "payment_date",
                    "payment_id",
                    "order_code",
                    "invoice",
                    "email_notification",
                    "overriden_invoice_number",
                    "overriden_invoice_date",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_date", "updated_date")}),
    )

    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "name", "qty", "price", "discount")
    search_fields = ("name", "order__order_number", "product__name")
    list_filter = ("order", "product", "price", "discount")
    readonly_fields = ("order", "product")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "order",
                    "product",
                    "name",
                    "qty",
                    "price",
                    "discount",
                    "info",
                )
            },
        ),
    )


@admin.register(Thumbnail)
class ThumbnailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "width",
        "height",
        "product",
        "category",
        "product_variant",
        "photo",
        "hero",
        "oryg_image",
    )
    search_fields = (
        "product__name",
        "category__name",
        "product_variant__name",
    )
    list_filter = ("width_expected", "height_expected", "main")


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "order",
        "product",
        "variant",
        "category",
        "oryg_image",
    )
    search_fields = ("product_name", "category_name", "photo_name")


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "name", "size", "material", "qty")
    search_fields = ("product__name", "size__name", "material__name")
    list_filter = ("size", "material")
