from django.contrib import admin
from Shop.models import Product, Cart, CartItem, Order, OrderItem

# Register your models here.
admin.site.register(Product)

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ['product', 'price', 'quantity', 'total_price']
    readonly_fields = ['price', 'total_price']

    def price(self, obj):
        return obj.product.price
    price.short_description = 'Price'

    def total_price(self, obj):
        return obj.get_total_price()
    total_price.short_description = 'Total Price'

class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ('formatted_user', 'create_at')  # Add status to the list display

    def formatted_user(self, obj):
        return f"Cart of {obj.user.username}"
    formatted_user.short_description = 'User'

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'price', 'total_price')
    readonly_fields = ['price', 'total_price']

    def price(self, obj):
        return obj.product.price
    price.short_description = 'Price'

    def total_price(self, obj):
        return obj.get_total_price()
    total_price.short_description = 'Total Price'

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing item
            return ['cart', 'price', 'total_price']  # Read-only fields
        else:
            return self.readonly_fields

admin.site.register(Cart, CartAdmin)



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'quantity', 'price', 'total_price']
    readonly_fields = ['price', 'total_price']

    def save_model(self, request, obj, form, change):
            obj.price = obj.product.price
            obj.total_price = obj.price * obj.quantity  # Calculate the total price
            super().save_model(request, obj, form, change)
            

    def price(self, obj):
        return obj.product.price
    price.short_description = 'Price'

    def total_price(self, obj):
        return obj.get_total_price()
    total_price.short_description = 'Total Price'

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('user', 'name', 'email', 'phone', 'total_price','payment_method', 'created_at','status')
    readonly_fields = ['billing_address', 'name', 'email', 'phone', 'note', 'total_price', 'created_at']
    
    list_filter = ['status']  # Enables filtering by Pending/Complete in the sidebar
    
    actions = ['mark_as_complete', 'mark_as_cancel']

    @admin.action(description='Mark selected orders as Complete')
    def mark_as_complete(self, request, queryset):
        queryset.update(status='Complete')

    @admin.action(description='Mark selected orders as Cancel')
    def mark_as_cancel(self, request, queryset):
        queryset.update(status='Cancel')

admin.site.register(Order, OrderAdmin)