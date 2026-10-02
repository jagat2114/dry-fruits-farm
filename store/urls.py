from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),

    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),

    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/increase/<int:product_id>/', views.cart_increase, name='cart_increase'),
    path('cart/decrease/<int:product_id>/', views.cart_decrease, name='cart_decrease'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/', views.cart_detail, name='cart_detail'),

    #order
path('order/', views.place_order, name='place_order'),
path('order/success/<int:order_id>/', views.order_success, name='order_success'),
path('my-orders/', views.my_orders, name='my_orders'),
path('my-orders/<int:order_id>/', views.order_detail, name='order_detail'),
path('my-orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]