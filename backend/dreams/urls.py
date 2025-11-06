from django.urls import path
from .views import list_dreams, purchase_dream, admin_list_dreams, admin_create_dream, admin_delete_dream

urlpatterns = [
    path('dreams', list_dreams),
    path('matches/<str:match_id>/dreams/purchase', purchase_dream),
    # Admin
    path('admin/dreams', admin_list_dreams),
    path('admin/dreams/', admin_create_dream),
    path('admin/dreams/<str:id>', admin_delete_dream),
]
