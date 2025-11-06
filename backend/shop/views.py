from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import uuid

from .models import ShopItems, ShopPurchases
from accounts.models import Users, UserProfiles


@api_view(["GET"])  # GET /shop/items
def list_items(request):
    items = ShopItems.objects.all()[:200]
    return Response([
        {
            "id": str(i.id),
            "name": i.name,
            "description": i.description,
            "price": i.price_points,
            "image": i.image_url,
            "rarity": i.rarity,
        }
        for i in items
    ])


@api_view(["POST"])  # POST /shop/purchase
def purchase_item(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"detail": "unauthenticated"}, status=401)
    data = request.data or {}
    item_id = data.get("itemId")
    if not item_id:
        return Response({"detail": "itemId required"}, status=400)
    try:
        item = ShopItems.objects.get(id=item_id)
        profile = UserProfiles.objects.get(user=request.user)
    except (ShopItems.DoesNotExist, UserProfiles.DoesNotExist):
        return Response({"detail": "not found"}, status=404)

    if (profile.pesa_points or 0) < int(item.price_points or 0):
        return Response({"detail": "insufficient points"}, status=400)

    with transaction.atomic():
        profile.pesa_points -= int(item.price_points or 0)
        profile.save(update_fields=["pesa_points"])
        ShopPurchases.objects.create(
            id=uuid.uuid4(), user=request.user, item=item, price_points=item.price_points
        )
    return Response({"ok": True, "remainingPoints": profile.pesa_points})


@api_view(["GET"])  # GET /shop/purchases
def list_purchases(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"detail": "unauthenticated"}, status=401)
    owned = ShopPurchases.objects.select_related('item').filter(user=request.user).order_by('-purchased_at')
    return Response([
        {
            "id": str(p.id),
            "item": {
                "id": str(p.item.id),
                "name": p.item.name,
                "image": p.item.image_url,
                "price": p.item.price_points,
                "rarity": p.item.rarity,
            },
            "purchased_at": p.purchased_at.isoformat(),
        }
        for p in owned
    ])


@api_view(["POST"])  # POST /shop/apply
def apply_item(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"detail": "unauthenticated"}, status=401)
    data = request.data or {}
    item_id = data.get("itemId")
    if not item_id:
        return Response({"detail": "itemId required"}, status=400)
    # Must own the item
    try:
        purchase = ShopPurchases.objects.select_related('item').get(user=request.user, item_id=item_id)
        profile = UserProfiles.objects.get(user=request.user)
    except (ShopPurchases.DoesNotExist, UserProfiles.DoesNotExist):
        return Response({"detail": "not owned or profile missing"}, status=400)
    # Apply avatar/skin using image_url if present
    if purchase.item.image_url:
        profile.avatar_url = purchase.item.image_url
        profile.save(update_fields=["avatar_url"])
    return Response({"ok": True, "avatar": profile.avatar_url})


# --- Admin Shop Management ---

def _require_staff(request):
    if not request.user or not request.user.is_authenticated or not request.user.is_staff:
        return Response({"detail": "forbidden"}, status=403)
    return None


@api_view(["GET"])  # GET /admin/shop/items
def admin_list_items(request):
    forb = _require_staff(request)
    if forb: return forb
    items = ShopItems.objects.all()[:1000]
    return Response([
        {
            "id": str(i.id),
            "name": i.name,
            "description": i.description,
            "price": i.price_points,
            "image": i.image_url,
            "rarity": i.rarity,
        }
        for i in items
    ])


@api_view(["POST"])  # POST /admin/shop/items
def admin_create_item(request):
    forb = _require_staff(request)
    if forb: return forb
    data = request.data or {}
    i = ShopItems.objects.create(
        id=data.get("id") or None,
        name=data.get("name"),
        description=data.get("description"),
        price_points=int(data.get("price", 0)),
        image_url=data.get("image"),
        rarity=data.get("rarity"),
    )
    return Response({"id": str(i.id)}, status=201)


@api_view(["DELETE"])  # DELETE /admin/shop/items/<id>
def admin_delete_item(request, id: str):
    forb = _require_staff(request)
    if forb: return forb
    try:
        ShopItems.objects.get(id=id).delete()
        return Response({"ok": True})
    except ShopItems.DoesNotExist:
        return Response({"detail": "not found"}, status=404)
