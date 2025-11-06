from django.urls import path
from .views import (
    draw_playing_card, play_savings_card, play_spending_card, decks_summary,
    list_savings_cards, list_spending_cards,
    admin_list_assets, admin_create_asset, admin_delete_asset,
    admin_list_event, admin_create_event, admin_delete_event,
    admin_list_savings, admin_create_savings, admin_delete_savings,
    admin_list_spending, admin_create_spending, admin_delete_spending,
)

urlpatterns = [
    path('matches/<str:match_id>/cards/draw', draw_playing_card),
    path('matches/<str:match_id>/cards/savings', play_savings_card),
    path('matches/<str:match_id>/cards/spending', play_spending_card),
    path('decks', decks_summary),
    path('cards/savings', list_savings_cards),
    path('cards/spending', list_spending_cards),
    # Admin management
    path('admin/cards/assets', admin_list_assets),
    path('admin/cards/assets/', admin_create_asset),
    path('admin/cards/assets/<str:id>', admin_delete_asset),
    path('admin/cards/event', admin_list_event),
    path('admin/cards/event/', admin_create_event),
    path('admin/cards/event/<str:id>', admin_delete_event),
    path('admin/cards/savings', admin_list_savings),
    path('admin/cards/savings/', admin_create_savings),
    path('admin/cards/savings/<str:id>', admin_delete_savings),
    path('admin/cards/spending', admin_list_spending),
    path('admin/cards/spending/', admin_create_spending),
    path('admin/cards/spending/<str:id>', admin_delete_spending),
]
