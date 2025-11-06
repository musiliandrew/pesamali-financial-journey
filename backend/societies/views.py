from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
import uuid

from .models import Societies
from accounts.models import Users, UserProfiles


@api_view(["GET", "POST"])  # GET/POST /societies
def societies_collection(request):
    if request.method == "GET":
        items = []
        for s in Societies.objects.all().order_by('name'):
            member_total = UserProfiles.objects.filter(societies=s).count()
            items.append({
                "id": str(s.id),
                "name": s.name,
                "slogan": s.slogan,
                "leaderId": str(s.leader_id) if s.leader_id else None,
                "member_count": member_total,
            })
        return Response(items)
    # POST create
    data = request.data or {}
    name = data.get('name')
    leader_id = data.get('leaderId')
    if not name or not leader_id:
        return Response({"detail": "name and leaderId required"}, status=400)
    try:
        leader = Users.objects.get(id=leader_id)
    except Users.DoesNotExist:
        return Response({"detail": "leader not found"}, status=404)
    with transaction.atomic():
        society = Societies.objects.create(
            id=uuid.uuid4(),
            name=name,
            slogan=data.get('slogan'),
            leader=leader,
            created_at=timezone.now(),
            member_count=0,
        )
    return Response({"id": str(society.id), "name": society.name}, status=201)


@api_view(["POST"])  # POST /societies/<id>/join
def join_society(request, id: str):
    data = request.data or {}
    user_id = data.get('userId')
    if not user_id:
        return Response({"detail": "userId required"}, status=400)
    try:
        society = Societies.objects.get(id=id)
    except Societies.DoesNotExist:
        return Response({"detail": "society not found"}, status=404)
    try:
        user = Users.objects.get(id=user_id)
        profile = UserProfiles.objects.get(user=user)
    except (Users.DoesNotExist, UserProfiles.DoesNotExist):
        return Response({"detail": "user not found"}, status=404)
    with transaction.atomic():
        profile.societies.add(society)
        # Update cached count
        society.member_count = UserProfiles.objects.filter(societies=society).count()
        society.save(update_fields=["member_count"])
    return Response({"ok": True, "member_count": society.member_count})


@api_view(["GET"])  # GET /societies/<id>
def get_society(request, id: str):
    try:
        society = Societies.objects.get(id=id)
    except Societies.DoesNotExist:
        return Response({"detail": "society not found"}, status=404)
    members = UserProfiles.objects.select_related('user').filter(societies=society).order_by('-pesa_points')[:100]
    return Response({
        "id": str(society.id),
        "name": society.name,
        "slogan": society.slogan,
        "leaderId": str(society.leader_id) if society.leader_id else None,
        "member_count": society.member_count,
        "leaderboard": [
            {"rank": idx + 1, "id": str(m.user.id), "username": m.user.username, "pesaPoints": m.pesa_points}
            for idx, m in enumerate(members)
        ]
    })
