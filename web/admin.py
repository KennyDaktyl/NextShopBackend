from django.contrib import admin

from web.models.accounts import Profile
from web.models.carts import Cart, CartItem
from web.models.categories import Category
from web.models.orders import Order, OrderItem
from web.models.prices import PriceGroup, ProductPrice
from web.models.products import Product
from web.models.shipments import Shipment


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


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductPriceInline]
    list_display = [f.name for f in Product._meta.fields]
    search_fields = ["name", "pk"]


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
