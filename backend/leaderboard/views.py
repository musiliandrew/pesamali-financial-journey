from rest_framework.decorators import api_view
from rest_framework.response import Response
from accounts.models import UserProfiles


def _paginate(qs, request):
    try:
        page = max(1, int(request.GET.get('page', '1')))
    except ValueError:
        page = 1
    try:
        page_size = max(1, min(100, int(request.GET.get('page_size', '50'))))
    except ValueError:
        page_size = 50
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    return qs[start:end], {"page": page, "page_size": page_size, "total": total}


@api_view(["GET"])  # GET /leaderboard/global
def leaderboard_global(request):
    qs = UserProfiles.objects.select_related("user").order_by('-pesa_points')
    profiles, meta = _paginate(qs, request)
    data = [
        {
            "rank": idx + 1,
            "userId": str(p.user.id),
            "username": p.user.username,
            "pesaPoints": p.pesa_points,
            "profession": p.profession,
            "avatar": p.avatar_url,
        }
        for idx, p in enumerate(profiles)
    ]
    return Response({"entries": data, "meta": meta})


@api_view(["GET"])  # GET /leaderboard/profession/<profession>
def leaderboard_by_profession(request, profession: str):
    qs = (
        UserProfiles.objects.select_related("user")
        .filter(profession=profession)
        .order_by('-pesa_points')
    )
    profiles, meta = _paginate(qs, request)
    data = [
        {
            "rank": idx + 1,
            "userId": str(p.user.id),
            "username": p.user.username,
            "pesaPoints": p.pesa_points,
            "profession": p.profession,
            "avatar": p.avatar_url,
        }
        for idx, p in enumerate(profiles)
    ]
    return Response({"entries": data, "meta": meta})
