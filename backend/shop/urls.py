from django.urls import path
from .views import list_items, purchase_item, list_purchases, apply_item, admin_list_items, admin_create_item, admin_delete_item

urlpatterns = [
    path('shop/items', list_items),
    path('shop/purchase', purchase_item),
    path('shop/purchases', list_purchases),
    path('shop/apply', apply_item),
    # Admin
    path('admin/shop/items', admin_list_items),
    path('admin/shop/items/', admin_create_item),
    path('admin/shop/items/<str:id>', admin_delete_item),
]
