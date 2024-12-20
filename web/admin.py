from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from web.models.accounts import Profile

# from web.models.carts import Cart, CartItem
from web.models.articles import Article
from web.models.categories import Category
from web.models.deliveries import Delivery
from web.models.heros import Hero
from web.models.images import Photo, Thumbnail
from web.models.orders import Invoice, Order, OrderItem
from web.models.payments import Payment
from web.models.prices import PriceGroup, ProductPrice
from web.models.products import (
    Brand,
    Material,
    Product,
    ProductOption,
    ProductOptionItem,
    ProductReview,
    ProductVariant,
    Size,
    Tag,
)
from web.utils import generate_invoice_for_order


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Hero._meta.fields]
    search_fields = ("name",)
    list_filter = ["is_active"]


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "profile"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Profile._meta.fields]
    search_fields = (
        "user__username",
        "user__email",
        "company",
        "nip",
        "street",
        "city",
        "postal_code",
    )
    list_filter = ["user__is_active", "status", "newsletter", "send_emails"]

    # Definiowanie fieldsets dla sekcji
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "status",
                    "mobile",
                    "newsletter",
                    "price_group",
                    "send_emails",
                )
            },
        ),
        (
            "Dane adresowe",
            {
                "classes": ("collapse",),
                "fields": (
                    "street",
                    "house_number",
                    "local_number",
                    "city",
                    "postal_code",
                    "inpost_code",
                ),
            },
        ),
        (
            "Dane do faktury",
            {
                "classes": ("collapse",),
                "fields": (
                    "make_invoice",
                    "company",
                    "company_payer",
                    "nip",
                    "invoice_street",
                    "invoice_house_number",
                    "invoice_local_number",
                    "invoice_city",
                    "invoice_postal_code",
                ),
            },
        ),
    )


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
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(PriceGroup)
class PriceGroupAdmin(admin.ModelAdmin):
    list_display = [f.name for f in PriceGroup._meta.fields]
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "meta_title",
        "meta_description",
        "parent",
        "description",
        "is_active",
        "is_main",
    )
    search_fields = ("name",)
    list_filter = ["is_active", "is_main"]
    readonly_fields = ("created_date", "modified_date")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "parent" in form.base_fields:
            form.base_fields["parent"].queryset = (
                Category.objects.all().order_by("name")
            )
        return form


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
    list_display = (
        "id",
        "name",
        "qty",
        "category",
        "on_first_page",
    )
    search_fields = ["name", "pk"]
    list_filter = ["on_first_page", "is_service"]
    readonly_fields = ("created_date", "modified_date")

    autocomplete_fields = ['category', 'prev_category']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "category" in form.base_fields:
            form.base_fields["category"].queryset = Category.objects.filter(
                children__isnull=True
            ).order_by("name")
        return form


admin.register(ProductPrice)


class ProductPriceAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ProductPrice._meta.fields]
    search_fields = ["product__name", "price"]
    list_filter = ["product__name"]


# class ItemInline(admin.TabularInline):
#     model = CartItem
#     extra = 1


# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = (
#         "id",
#         "client",
#         "created_date",
#         "amount",
#         "amount_with_discount",
#         "discount",
#     )
#     search_fields = ("client__username", "client__email")
#     list_filter = ("created_date", "updated_date")
#     inlines = [ItemInline]


# @admin.register(CartItem)
# class ItemAdmin(admin.ModelAdmin):
#     list_display = ("id", "cart", "name", "qty", "price", "discount")
#     search_fields = ("name", "cart__client__username")
#     list_filter = ("cart__created_date",)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "name",
        "qty",
        "price",
        "discount",
    )
    search_fields = ("name", "order__order_number")
    list_filter = ("order__created_date",)
    
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
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
        "uid",
    )
    list_filter = (
        "status",
        "created_date",
        "updated_date",
        "delivery_method",
        "payment_method",
        "status",
    )
    readonly_fields = ("created_date", "updated_date", "uid")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uid",
                    "order_number",
                    "status",
                    "prev_status",
                    "client",
                    "client_name",
                    "client_email",
                    "client_mobile",
                    "amount",
                    "amount_with_discount",
                    "discount",
                    "info",
                    "delivery_method",
                    "payment_method",
                    "payment_price",
                    "delivery_price",
                    "cart_items_price",
                    "cart_items",
                    "link",
                )
            },
        ),
        (
            "Payment Information",
            {
                "fields": (
                    "payment_date",
                    "checkout_session_id",
                    "is_paid",
                ),
            },
        ),
        (
            "Address",
            {
                "fields": (
                    "inpost_box_id",
                    "street",
                    "house_number",
                    "local_number",
                    "city",
                    "postal_code",
                ),
            },
        ),
        (
            "Invoice",
            {
                "fields": (
                    "make_invoice",
                    "invoice_created",
                    "company",
                    "company_payer",
                    "nip",
                    "invoice_street",
                    "invoice_house_number",
                    "invoice_local_number",
                    "invoice_city",
                    "invoice_postal_code",
                ),
            },
        ),
        (
            "Overriden",
            {
                "fields": (
                    "email_notification",
                    "overriden_invoice_number",
                    "overriden_invoice_date",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_date", "updated_date")}),
    )


@admin.action(description="Utwórz fakturę")
def create_invoice(modeladmin, request, queryset):
    for invoice in queryset:
        generate_invoice_for_order(invoice.order, admin=True)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Invoice._meta.fields]
    search_fields = ("number",)
    actions = [
        create_invoice,
    ]


@admin.register(Thumbnail)
class ThumbnailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "width",
        "height",
        "main",
        "order",
        "is_variant",
        "product",
        "category",
        "product_variant",
        "photo",
        "hero",
        "delivery",
        "payment",
        "article",
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
    search_fields = (
        "name",
        "product__name",
        "category__name",
        "variant__name",
    )


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


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "created_date",
        "modified_date",
    )
    search_fields = ("name", "category__name")
    list_filter = ("created_date",)
    readonly_fields = ("created_date", "modified_date")


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "user",
        "rating",
        "created_at",
    )
    search_fields = ("product__name", "user__username")
    list_filter = ("created_at",)