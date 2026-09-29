from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('shop/', views.shop_home, name='shop_home'),

    path('order/', views.order, name='order'),

    path(
        'product-sizes/',
        views.product_sizes,
        name='product_sizes'
    ),

    path(
        'cancel-order/<int:order_id>/',
        views.cancel_order,
        name='cancel_order'
    ),

    path(
        'order-status/<int:order_id>/',
        views.order_status,
        name='order_status'
    ),

    path(
        'my-orders/',
        views.my_orders,
        name='my_orders'
    ),

    path(
        'chatbot/',
        views.chatbot,
        name='chatbot'
    ),

    path(
        'chatbot/api/',
        views.chatbot_api,
        name='chatbot_api'
    ),
]