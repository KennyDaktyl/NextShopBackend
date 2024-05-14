from django.contrib import admin

from web.models.accounts import Profile
from web.models.prices import ProductPrice
from web.models.products import Product


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
