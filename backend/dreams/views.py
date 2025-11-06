from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction

from .models import Dreams, UserDreams
from game.models import GameRooms, GamePlayers
from accounts.models import Users
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def _broadcast(match_id: str, payload: dict):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"match_{match_id}", {"type": "game_event", "payload": payload}
    )


def _state_snapshot(room: GameRooms):
    from game.models import GamePlayers  # local import to avoid cycles
    players = GamePlayers.objects.filter(room=room).values(
        'user_id', 'seat', 'current_points', 'savings', 'liabilities', 'assets', 'tokens'
    )
    return {
        "matchId": str(room.id),
        "currentTurn": room.current_turn,
        "players": list(players),
    }


@api_view(["GET"])  # GET /dreams
def list_dreams(request):
    items = Dreams.objects.order_by("order_index").all()
    return Response([
        {"id": str(d.id), "name": d.name, "slug": d.slug, "cost": d.cost, "image_url": d.image_url, "description": d.description}
        for d in items
    ])


@api_view(["POST"])  # POST /matches/<matchId>/dreams/purchase
def purchase_dream(request, match_id: str):
    data = request.data or {}
    user_id = data.get("userId")
    dream_id = data.get("dreamId")
    if not user_id or not dream_id:
        return Response({"detail": "userId and dreamId required"}, status=400)

    try:
        room = GameRooms.objects.get(id=match_id)
    except GameRooms.DoesNotExist:
        return Response({"detail": "match not found"}, status=404)
    try:
        player = GamePlayers.objects.select_for_update().get(room=room, user_id=user_id)
    except GamePlayers.DoesNotExist:
        return Response({"detail": "player not found"}, status=404)
    try:
        dream = Dreams.objects.get(id=dream_id)
    except Dreams.DoesNotExist:
        return Response({"detail": "dream not found"}, status=404)

    with transaction.atomic():
        # Win condition checks (as per docs)
        has_two_assets = len(player.assets or []) >= 2
        liabilities_cleared = (player.liabilities or 0) == 0
        savings_ok = (player.savings or 0) >= 500

        if not has_two_assets:
            return Response({"detail": "must have purchased 2 assets"}, status=400)
        if not liabilities_cleared:
            return Response({"detail": "liabilities must be cleared"}, status=400)
        if not savings_ok:
            return Response({"detail": "savings must be at least 500"}, status=400)

        # Enforce dream purchase using on-hand points (asset profits), not from savings
        on_hand = int(player.current_points or 0)
        if on_hand < int(dream.cost or 0):
            return Response({"detail": "insufficient on-hand points for dream"}, status=400)

        # Deduct and record unlock
        player.current_points = on_hand - int(dream.cost)
        player.save(update_fields=["current_points"])

        user = Users.objects.get(id=user_id)
        UserDreams.objects.get_or_create(user=user, dream=dream, defaults={"unlocked_at": timezone.now()})

    # Broadcast dream purchase + game_end
    payload_purchase = {
        "type": "dream_purchase",
        "matchId": match_id,
        "data": {"userId": user_id, "dreamId": str(dream.id), "cost": int(dream.cost)},
        "timestamp": int(timezone.now().timestamp() * 1000),
    }
    _broadcast(match_id, payload_purchase)

    payload_end = {
        "type": "game_end",
        "matchId": match_id,
        "data": {"winnerId": user_id, "dreamId": str(dream.id)},
        "timestamp": int(timezone.now().timestamp() * 1000),
    }
    _broadcast(match_id, payload_end)

    # consolidated state update snapshot
    snapshot = _state_snapshot(room)
    _broadcast(match_id, {"type": "state_update", "matchId": match_id, "data": snapshot, "timestamp": payload_purchase["timestamp"]})

    return Response({"ok": True, "winnerId": user_id, "dreamId": str(dream.id)})


# --- Admin Dreams Management ---

def _require_staff(request):
    if not request.user or not request.user.is_authenticated or not request.user.is_staff:
        return Response({"detail": "forbidden"}, status=403)
    return None


@api_view(["GET"])  # GET /admin/dreams
def admin_list_dreams(request):
    forb = _require_staff(request)
    if forb: return forb
    items = Dreams.objects.order_by("order_index").all()
    return Response([
        {"id": str(d.id), "name": d.name, "slug": d.slug, "cost": d.cost, "order_index": d.order_index, "image_url": d.image_url, "description": d.description, "prerequisite_dream": str(d.prerequisite_dream_id) if d.prerequisite_dream_id else None}
        for d in items
    ])


@api_view(["POST"])  # POST /admin/dreams
def admin_create_dream(request):
    forb = _require_staff(request)
    if forb: return forb
    data = request.data or {}
    d = Dreams.objects.create(
        id=data.get("id") or None,
        name=data.get("name"),
        slug=data.get("slug"),
        cost=int(data.get("cost", 0)),
        order_index=int(data.get("order_index", 0)),
        image_url=data.get("image_url"),
        description=data.get("description"),
        prerequisite_dream_id=data.get("prerequisite_dream"),
    )
    return Response({"id": str(d.id)}, status=201)


@api_view(["DELETE"])  # DELETE /admin/dreams/<id>
def admin_delete_dream(request, id: str):
    forb = _require_staff(request)
    if forb: return forb
    try:
        Dreams.objects.get(id=id).delete()
        return Response({"ok": True})
    except Dreams.DoesNotExist:
        return Response({"detail": "not found"}, status=404)
