from django.urls import path
from . import views

urlpatterns = [
    path("", views.shop, name="shop"),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('orders/', views.user_orders, name='user_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('payment_cod/', views.payment_cod, name='payment_cod'),
    path('payment/', views.payment, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
]
