from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
import uuid
import random

from .models import GameRooms, GamePlayers
from accounts.models import Users
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def _ensure_player_tokens(player: GamePlayers):
    if not player.tokens:
        player.tokens = [0, 0, 0, 0]


# Yellow-strip indices based on docs (serpentine symmetric pairs) incl. endpoints used in UI
YELLOW_STRIPS = set([1, 80, 5, 76, 11, 70, 19, 62, 25, 56, 32, 49, 38, 43, 48, 33, 54, 27, 59, 22, 66, 15, 71, 10, 77, 4])


def _is_yellow(idx: int) -> bool:
    return idx in YELLOW_STRIPS


# Asset profit constants from product spec
ASSET_PROFIT = {
    "a1": 320,  # Campus Printing Shop
    "a2": 220,  # Online Tasking Platform
    "a3": 170,  # Monetized YouTube Channel
    "a4": 220,  # Peer to Peer Lending Fund
    "a5": 240,  # Cryptocurrency Portfolio
}


def _furthest_token(tokens: list[int]) -> int:
    return max(tokens or [0])


def _phase_of(idx: int) -> int:
    # spots 1..10 => phase 1, 11..20 => phase 2, etc.
    return (max(1, idx) - 1) // 10 + 1


def _next_phase_window(purchase_spot: int) -> set[int]:
    next_phase = _phase_of(purchase_spot) + 1
    start = (next_phase - 1) * 10 + 1
    end = start + 9
    # returns only on odd tiles per rules
    return set([i for i in range(start, end + 1) if i % 2 == 1])


@api_view(["POST"])  # POST /matches
def create_match(request):
    data = request.data or {}
    player_count = int(data.get("numPlayers", 2))
    room = GameRooms.objects.create(
        id=uuid.uuid4(),
        status="waiting",
        created_at=timezone.now(),
        player_count=player_count,
    )
    return Response({"matchId": str(room.id)}, status=status.HTTP_201_CREATED)


@api_view(["POST"])  # POST /matches/:id/join
def join_match(request, match_id: str):
    data = request.data or {}
    user_id = data.get("userId")
    is_ai = bool(data.get("isAi", False))
    seat = int(data.get("seatPosition", 0))

    try:
        room = GameRooms.objects.get(id=match_id)
    except GameRooms.DoesNotExist:
        return Response({"detail": "match not found"}, status=404)

    user = None
    if not is_ai:
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({"detail": "user not found"}, status=404)

    # Create player entry
    player = GamePlayers.objects.create(
        id=uuid.uuid4(),
        room=room,
        user=user,
        seat=seat,
        starting_points=1200,
        current_points=1200,
        savings=0,
        liabilities=0,
        assets=[],
        spending_cards=[],
        savings_cards=[],
        tokens=[0, 0, 0, 0],
        color=None,
        is_cpu=is_ai,
        ready=True,
    )

    return Response({"ok": True})


@api_view(["POST"])  # POST /matches/:id/start
def start_match(request, match_id: str):
    try:
        room = GameRooms.objects.get(id=match_id)
    except GameRooms.DoesNotExist:
        return Response({"detail": "match not found"}, status=404)
    room.status = "active"
    room.started_at = timezone.now()
    room.current_turn = 0
    room.save(update_fields=["status", "started_at", "current_turn"])
    # Broadcast turn_change
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"match_{match_id}",
        {
            "type": "game_event",
            "payload": {"type": "turn_change", "matchId": match_id, "data": {"nextPlayerSeat": 0}, "timestamp": int(timezone.now().timestamp() * 1000)},
        },
    )
    return Response({"ok": True})


@api_view(["GET"])  # GET /matches/:id/state
def get_state(request, match_id: str):
    try:
        room = GameRooms.objects.get(id=match_id)
    except GameRooms.DoesNotExist:
        return Response({"detail": "match not found"}, status=404)

    players = GamePlayers.objects.filter(room=room).select_related("user")
    payload = {
        "matchId": str(room.id),
        "status": room.status,
        "playerCount": room.player_count,
        "players": [],
        "currentTurn": room.current_turn or 0,
    }
    for p in players:
        _ensure_player_tokens(p)
        payload["players"].append({
            "userId": str(p.user.id) if p.user_id else None,
            "seat": p.seat or 0,
            "isAi": bool(p.is_cpu),
            "tokens": p.tokens,
            "savings": p.savings or 0,
            "liabilities": p.liabilities or 0,
            "currentPoints": p.current_points or 0,
            "assets": p.assets or [],
        })

    return Response(payload)


@api_view(["POST"])  # POST /matches/:id/roll
def roll_dice(request, match_id: str):
    try:
        room = GameRooms.objects.get(id=match_id)
    except GameRooms.DoesNotExist:
        return Response({"detail": "match not found"}, status=404)
    data = request.data or {}
    user_id = data.get("userId")
    # Validate turn by user seat
    try:
        player = GamePlayers.objects.get(room=room, user_id=user_id)
    except GamePlayers.DoesNotExist:
        return Response({"detail": "player not found"}, status=404)
    if (player.seat or 0) != (room.current_turn or 0):
        return Response({"detail": "not your turn"}, status=403)

    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    # Broadcast dice_result
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"match_{match_id}",
        {
            "type": "game_event",
            "payload": {"type": "dice_result", "matchId": match_id, "data": {"die1": d1, "die2": d2, "sum": d1 + d2}, "timestamp": int(timezone.now().timestamp() * 1000)},
        },
    )
    return Response({"dice": [d1, d2], "sum": d1 + d2})


@api_view(["POST"])  # POST /matches/:id/move
def move_token(request, match_id: str):
    data = request.data or {}
    user_id = data.get("userId")
    token_index = int(data.get("tokenIndex", 0))
    steps = int(data.get("steps", 0))

    try:
        room = GameRooms.objects.get(id=match_id)
    except GameRooms.DoesNotExist:
        return Response({"detail": "match not found"}, status=404)

    try:
        player = GamePlayers.objects.select_for_update().get(room=room, user_id=user_id)
    except GamePlayers.DoesNotExist:
        return Response({"detail": "player not found"}, status=404)

    # Turn validation
    if (player.seat or 0) != (room.current_turn or 0):
        return Response({"detail": "not your turn"}, status=403)

    with transaction.atomic():
        _ensure_player_tokens(player)
        tokens = player.tokens
        if token_index < 0 or token_index >= len(tokens):
            return Response({"detail": "invalid token index"}, status=400)

        # Yellow-strip priority check: does any token land on yellow with this dice?
        can_land_yellow = False
        for i, pos in enumerate(tokens):
            target = max(0, pos + steps)
            if _is_yellow(target):
                can_land_yellow = True
                break

        target_pos = max(0, tokens[token_index] + steps)
        skipped_yellow = can_land_yellow and not _is_yellow(target_pos)

        # Apply move
        tokens[token_index] = target_pos
        player.tokens = tokens

        # Apply -20 penalty to liabilities if skipped yellow when a yellow move existed
        if skipped_yellow:
            player.liabilities = (player.liabilities or 0) + 20

        # Resolve asset returns: for any owned asset with returns window containing current tile (odd-only), up to 5 returns
        # Expect player.assets to be list of objects {assetId, purchaseSpot, returnsCollected}
        new_assets = []
        returns_events = []
        for a in (player.assets or []):
            if isinstance(a, dict):
                asset_id = a.get("assetId")
                purchase_spot = int(a.get("purchaseSpot", 0))
                collected = int(a.get("returnsCollected", 0))
            else:
                # legacy: store as id only; keep as-is
                new_assets.append(a)
                continue
            if collected < 5:
                window = _next_phase_window(purchase_spot)
                if target_pos in window and (target_pos % 2 == 1):
                    amount = ASSET_PROFIT.get(asset_id, 0)
                    player.current_points = (player.current_points or 0) + amount
                    collected += 1
                    returns_events.append({"assetId": asset_id, "amount": amount, "returnsCollected": collected})
            new_assets.append({"assetId": asset_id, "purchaseSpot": purchase_spot, "returnsCollected": collected})

        player.assets = new_assets
        player.save(update_fields=["tokens", "liabilities", "current_points", "assets"])

        # Advance turn
        room.current_turn = ((room.current_turn or 0) + 1) % (room.player_count or 1)
        room.save(update_fields=["current_turn"])

    # Broadcast move_event and state_update and any asset_return
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"match_{match_id}",
        {
            "type": "game_event",
            "payload": {"type": "move_event", "matchId": match_id, "data": {"userId": user_id, "tokenIndex": token_index, "steps": steps, "position": target_pos}, "timestamp": int(timezone.now().timestamp() * 1000)},
        },
    )
    for ev in returns_events:
        async_to_sync(channel_layer.group_send)(
            f"match_{match_id}",
            {"type": "game_event", "payload": {"type": "asset_return", "matchId": match_id, "data": ev, "timestamp": int(timezone.now().timestamp() * 1000)}},
        )
    async_to_sync(channel_layer.group_send)(
        f"match_{match_id}",
        {"type": "game_event", "payload": {"type": "turn_change", "matchId": match_id, "data": {"nextPlayerSeat": room.current_turn}, "timestamp": int(timezone.now().timestamp() * 1000)}},
    )


def select_asset(request, match_id: str):
    data = request.data or {}
    user_id = data.get("userId")
    asset_id = data.get("assetId")

    try:
        room = GameRooms.objects.get(id=match_id)
    except GameRooms.DoesNotExist:
        return Response({"detail": "match not found"}, status=404)

    try:
        player = GamePlayers.objects.select_for_update().get(room=room, user_id=user_id)
    except GamePlayers.DoesNotExist:
        return Response({"detail": "player not found"}, status=404)

    with transaction.atomic():
        _ensure_player_tokens(player)
        purchase_spot = _furthest_token(player.tokens)
        assets = player.assets or []
        # Store structured asset instance with purchaseSpot and returnsCollected
        if asset_id and all((getattr(a, "get", None) and a.get("assetId") != asset_id) or (not isinstance(a, dict) and a != asset_id) for a in assets):
            assets.append({"assetId": asset_id, "purchaseSpot": purchase_spot, "returnsCollected": 0})
        player.assets = assets
        player.save(update_fields=["assets"])

        # Buying an asset counts as playing your turn -> advance turn
        room.current_turn = ((room.current_turn or 0) + 1) % (room.player_count or 1)
        room.save(update_fields=["current_turn"])
    # Broadcast asset_purchase, state_update, and turn_change
    channel_layer = get_channel_layer()
    now_ts = int(timezone.now().timestamp() * 1000)
    async_to_sync(channel_layer.group_send)(
        f"match_{match_id}",
        {"type": "game_event", "payload": {"type": "asset_purchase", "matchId": match_id, "data": {"userId": user_id, "assetId": asset_id, "purchaseSpot": purchase_spot}, "timestamp": now_ts}},
    )
    # Snapshot
    players = GamePlayers.objects.filter(room=room).values('user_id', 'seat', 'current_points', 'savings', 'liabilities', 'assets', 'tokens')
    snapshot = {"matchId": match_id, "currentTurn": room.current_turn, "players": list(players)}
    async_to_sync(channel_layer.group_send)(
        f"match_{match_id}",
        {"type": "game_event", "payload": {"type": "state_update", "matchId": match_id, "data": snapshot, "timestamp": now_ts}},
    )
    async_to_sync(channel_layer.group_send)(
        f"match_{match_id}",
        {"type": "game_event", "payload": {"type": "turn_change", "matchId": match_id, "data": {"nextPlayerSeat": room.current_turn}, "timestamp": now_ts}},
    )

    return Response({"ok": True, "assets": player.assets, "currentTurn": room.current_turn})
