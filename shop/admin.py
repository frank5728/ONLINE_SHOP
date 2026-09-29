from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Order, Size


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "image_preview")
    search_fields = ("name",)
    filter_horizontal = ("sizes",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" '
                'style="object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return "No image"

    image_preview.short_description = "Image"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order_reference",
        "customer_name",
        "phone",
        "location",
        "product",
        "product_image",
        "size",
        "quantity",
        "total_price",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "order_reference",
        "customer_name",
        "phone",
        "location",
        "product__name",
    )

    readonly_fields = (
        "order_reference",
        "customer_name",
        "phone",
        "location",
        "product",
        "product_image",
        "size",
        "quantity",
        "total_price",
        "created_at",
    )

    def product_image(self, obj):
        if obj.product and obj.product.image:
            return format_html(
                '<img src="{}" width="100" height="100" '
                'style="object-fit: cover; border-radius: 8px;" />',
                obj.product.image.url
            )
        return "No image"

    product_image.short_description = "Product Image"