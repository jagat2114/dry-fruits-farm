from django.contrib import admin
from .models import Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'category',
        'price',
        'stock',
        'stock_status',
        'created_at'
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    list_filter = (
        'category',
        'available'
    )

    search_fields = (
        'name',
        'description'
    )

    def stock_status(self, obj):
        if obj.available and obj.stock > 0:
            return "🟢 In Stock"
        return "🔴 Out of Stock"

    stock_status.short_description = "Stock Status"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'customer_name',
        'mobile',
        'total_amount',
        'status',
        'created_at'
    )

    list_filter = (
        'status',
        'created_at'
    )

    search_fields = (
        'customer_name',
        'mobile',
        'user__username'
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'order',
        'product_name',
        'price',
        'quantity'
    )
