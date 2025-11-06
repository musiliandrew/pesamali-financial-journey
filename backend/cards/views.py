from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone

from .models import EventCards, SavingsCards, SpendingCards, AssetCards
from game.models import GameRooms, GamePlayers
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def _broadcast(match_id: str, payload: dict):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"match_{match_id}", {"type": "game_event", "payload": payload}
    )


def _state_snapshot(room: GameRooms):
    players = GamePlayers.objects.filter(room=room).values(
        'user_id', 'seat', 'current_points', 'savings', 'liabilities', 'assets', 'tokens'
    )
    return {
        "matchId": str(room.id),
        "currentTurn": room.current_turn,
        "players": list(players),
    }


@api_view(["POST"])  # POST /matches/<matchId>/cards/draw
def draw_playing_card(request, match_id: str):
    data = request.data or {}
    user_id = data.get("userId")
    try:
        room = GameRooms.objects.get(id=match_id)
    except GameRooms.DoesNotExist:
        return Response({"detail": "match not found"}, status=404)

    try:
        player = GamePlayers.objects.select_for_update().get(room=room, user_id=user_id)
    except GamePlayers.DoesNotExist:
        return Response({"detail": "player not found"}, status=404)

    # Draw simplest: cheapest strategy — first or random
    card = EventCards.objects.order_by('?').first()
    if not card:
        return Response({"detail": "no event cards"}, status=404)

    with transaction.atomic():
        effect = int(card.effect_points or 0)
        # Advanced rules: no movement, only points effects
        if effect >= 0:
            player.current_points = (player.current_points or 0) + effect
        else:
            player.liabilities = (player.liabilities or 0) + abs(effect)
        player.save(update_fields=["current_points", "liabilities"])

    payload = {
        "type": "card_draw",
        "matchId": match_id,
        "data": {
            "cardId": str(card.id),
            "title": card.title,
            "message": card.message,
            "effect_points": effect,
        },
        "timestamp": int(timezone.now().timestamp() * 1000),
    }
    _broadcast(match_id, payload)
    # consolidated state update
    snapshot = _state_snapshot(room)
    _broadcast(match_id, {"type": "state_update", "matchId": match_id, "data": snapshot, "timestamp": payload["timestamp"]})
    return Response({"ok": True, "card": payload["data"], "currentPoints": player.current_points, "liabilities": player.liabilities})


@api_view(["POST"])  # POST /matches/<matchId>/cards/savings
def play_savings_card(request, match_id: str):
    data = request.data or {}
    user_id = data.get("userId")
    card_id = data.get("cardId")
    amount = int(data.get("amount", 0))
    if amount <= 0:
        return Response({"detail": "invalid amount"}, status=400)

    try:
        room = GameRooms.objects.get(id=match_id)
    except GameRooms.DoesNotExist:
        return Response({"detail": "match not found"}, status=404)
    try:
        player = GamePlayers.objects.select_for_update().get(room=room, user_id=user_id)
    except GamePlayers.DoesNotExist:
        return Response({"detail": "player not found"}, status=404)
    try:
        card = SavingsCards.objects.get(id=card_id)
    except SavingsCards.DoesNotExist:
        return Response({"detail": "card not found"}, status=404)

    with transaction.atomic():
        # Deduct from on-hand points
        if (player.current_points or 0) < amount:
            return Response({"detail": "insufficient points"}, status=400)
        player.current_points = (player.current_points or 0) - amount
        player.savings = (player.savings or 0) + amount

        # Apply bonus if threshold met and condition satisfied
        bonus = 0
        threshold = int(card.save_threshold or 0)
        if amount >= threshold:
            cond = card.bonus_condition or {}
            cond_type = cond.get("type") if isinstance(cond, dict) else None
            cond_bonus = int(cond.get("bonus", 0)) if isinstance(cond, dict) else 0
            if cond_type == "if_owns_asset":
                has_asset = bool(player.assets)
                if has_asset:
                    bonus = cond_bonus
            elif cond_type == "flat_bonus":
                bonus = cond_bonus
        if bonus > 0:
            player.savings += bonus
        player.save(update_fields=["current_points", "savings"])

    payload = {
        "type": "savings_play",
        "matchId": match_id,
        "data": {"cardId": str(card.id), "amount": amount, "bonus": bonus},
        "timestamp": int(timezone.now().timestamp() * 1000),
    }
    _broadcast(match_id, payload)
    snapshot = _state_snapshot(room)
    _broadcast(match_id, {"type": "state_update", "matchId": match_id, "data": snapshot, "timestamp": payload["timestamp"]})
    return Response({"ok": True, "savings": player.savings, "currentPoints": player.current_points})


@api_view(["POST"])  # POST /matches/<matchId>/cards/spending
def play_spending_card(request, match_id: str):
    data = request.data or {}
    user_id = data.get("userId")
    card_id = data.get("cardId")

    try:
        room = GameRooms.objects.get(id=match_id)
    except GameRooms.DoesNotExist:
        return Response({"detail": "match not found"}, status=404)
    try:
        player = GamePlayers.objects.select_for_update().get(room=room, user_id=user_id)
    except GamePlayers.DoesNotExist:
        return Response({"detail": "player not found"}, status=404)
    try:
        card = SpendingCards.objects.get(id=card_id)
    except SpendingCards.DoesNotExist:
        return Response({"detail": "card not found"}, status=404)

    with transaction.atomic():
        # Advanced rule: spending increases liabilities; does not move pieces
        player.liabilities = (player.liabilities or 0) + int(card.total_cost or 0)
        player.save(update_fields=["liabilities"])

    payload = {
        "type": "spending_play",
        "matchId": match_id,
        "data": {"cardId": str(card.id), "total": int(card.total_cost or 0)},
        "timestamp": int(timezone.now().timestamp() * 1000),
    }
    _broadcast(match_id, payload)
    snapshot = _state_snapshot(room)
    _broadcast(match_id, {"type": "state_update", "matchId": match_id, "data": snapshot, "timestamp": payload["timestamp"]})
    return Response({"ok": True, "liabilities": player.liabilities})


@api_view(["GET"])  # GET /decks
def decks_summary(request):
    return Response({
        "assets": AssetCards.objects.count(),
        "event": EventCards.objects.count(),
        "spending": SpendingCards.objects.count(),
        "savings": SavingsCards.objects.count(),
    })


@api_view(["GET"])  # GET /cards/savings
def list_savings_cards(request):
    items = SavingsCards.objects.all()[:200]
    return Response([
        {"id": str(x.id), "name": x.name, "save_threshold": int(x.save_threshold or 0), "bonus_condition": x.bonus_condition}
        for x in items
    ])


@api_view(["GET"])  # GET /cards/spending
def list_spending_cards(request):
    items = SpendingCards.objects.all()[:200]
    return Response([
        {"id": str(x.id), "name": x.name, "total_cost": int(x.total_cost or 0)}
        for x in items
    ])


# --- Admin management (is_staff) ---

def _require_staff(request):
    if not request.user or not request.user.is_authenticated or not request.user.is_staff:
        return Response({"detail": "forbidden"}, status=403)
    return None


@api_view(["GET"])  # GET /admin/cards/assets
def admin_list_assets(request):
    forb = _require_staff(request)
    if forb: return forb
    items = AssetCards.objects.all()[:1000]
    return Response([{ "id": str(i.id), "name": i.name, "purchase_cost": i.purchase_cost, "profit_per_return": i.profit_per_return, "max_returns": i.max_returns, "image_url": i.image_url } for i in items])


@api_view(["POST"])  # POST /admin/cards/assets
def admin_create_asset(request):
    forb = _require_staff(request)
    if forb: return forb
    data = request.data or {}
    obj = AssetCards.objects.create(
        id=data.get("id") or None,
        name=data.get("name"),
        purchase_cost=int(data.get("purchase_cost", 0)),
        profit_per_return=int(data.get("profit_per_return", 0)),
        max_returns=int(data.get("max_returns", 5)) if data.get("max_returns") is not None else None,
        image_url=data.get("image_url"),
    )
    return Response({"id": str(obj.id)}, status=201)


@api_view(["DELETE"])  # DELETE /admin/cards/assets/<id>
def admin_delete_asset(request, id: str):
    forb = _require_staff(request)
    if forb: return forb
    try:
        AssetCards.objects.get(id=id).delete()
        return Response({"ok": True})
    except AssetCards.DoesNotExist:
        return Response({"detail": "not found"}, status=404)


@api_view(["GET"])  # GET /admin/cards/event
def admin_list_event(request):
    forb = _require_staff(request)
    if forb: return forb
    items = EventCards.objects.all()[:1000]
    return Response([{ "id": str(i.id), "title": i.title, "effect_points": i.effect_points, "message": i.message, "type": i.type, "rarity": i.rarity } for i in items])


@api_view(["POST"])  # POST /admin/cards/event
def admin_create_event(request):
    forb = _require_staff(request)
    if forb: return forb
    data = request.data or {}
    obj = EventCards.objects.create(
        id=data.get("id") or None,
        title=data.get("title"),
        effect_points=int(data.get("effect_points", 0)),
        message=data.get("message"),
        type=data.get("type"),
        rarity=data.get("rarity"),
    )
    return Response({"id": str(obj.id)}, status=201)


@api_view(["DELETE"])  # DELETE /admin/cards/event/<id>
def admin_delete_event(request, id: str):
    forb = _require_staff(request)
    if forb: return forb
    try:
        EventCards.objects.get(id=id).delete()
        return Response({"ok": True})
    except EventCards.DoesNotExist:
        return Response({"detail": "not found"}, status=404)


@api_view(["GET"])  # GET /admin/cards/savings
def admin_list_savings(request):
    forb = _require_staff(request)
    if forb: return forb
    items = SavingsCards.objects.all()[:1000]
    return Response([{ "id": str(i.id), "name": i.name, "save_threshold": i.save_threshold, "bonus_condition": i.bonus_condition, "image_url": i.image_url } for i in items])


@api_view(["POST"])  # POST /admin/cards/savings
def admin_create_savings(request):
    forb = _require_staff(request)
    if forb: return forb
    data = request.data or {}
    obj = SavingsCards.objects.create(
        id=data.get("id") or None,
        name=data.get("name"),
        save_threshold=int(data.get("save_threshold", 0)),
        bonus_condition=data.get("bonus_condition"),
        image_url=data.get("image_url"),
    )
    return Response({"id": str(obj.id)}, status=201)


@api_view(["DELETE"])  # DELETE /admin/cards/savings/<id>
def admin_delete_savings(request, id: str):
    forb = _require_staff(request)
    if forb: return forb
    try:
        SavingsCards.objects.get(id=id).delete()
        return Response({"ok": True})
    except SavingsCards.DoesNotExist:
        return Response({"detail": "not found"}, status=404)


@api_view(["GET"])  # GET /admin/cards/spending
def admin_list_spending(request):
    forb = _require_staff(request)
    if forb: return forb
    items = SpendingCards.objects.all()[:1000]
    return Response([{ "id": str(i.id), "name": i.name, "total_cost": i.total_cost, "breakdown": i.breakdown, "image_url": i.image_url } for i in items])


@api_view(["POST"])  # POST /admin/cards/spending
def admin_create_spending(request):
    forb = _require_staff(request)
    if forb: return forb
    data = request.data or {}
    obj = SpendingCards.objects.create(
        id=data.get("id") or None,
        name=data.get("name"),
        total_cost=int(data.get("total_cost", 0)),
        breakdown=data.get("breakdown"),
        image_url=data.get("image_url"),
    )
    return Response({"id": str(obj.id)}, status=201)


@api_view(["DELETE"])  # DELETE /admin/cards/spending/<id>
def admin_delete_spending(request, id: str):
    forb = _require_staff(request)
    if forb: return forb
    try:
        SpendingCards.objects.get(id=id).delete()
        return Response({"ok": True})
    except SpendingCards.DoesNotExist:
        return Response({"detail": "not found"}, status=404)
