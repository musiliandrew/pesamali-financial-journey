from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
import uuid

from .models import QaQuestions, UserQaAnswers
from accounts.models import Users, UserProfiles


@api_view(["POST"])  # POST /qa/challenge
def send_challenge(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"detail": "unauthenticated"}, status=401)
    data = request.data or {}
    to_user_id = data.get("toUserId")
    profession = data.get("profession")
    if not to_user_id:
        return Response({"detail": "toUserId required"}, status=400)
    try:
        to_user = Users.objects.get(id=to_user_id)
        to_profile = UserProfiles.objects.get(user=to_user)
    except (Users.DoesNotExist, UserProfiles.DoesNotExist):
        return Response({"detail": "recipient not found"}, status=404)

    prof = profession or to_profile.profession
    question = QaQuestions.objects.filter(Q(profession=prof) | Q(profession="any")).order_by('?').first()
    if not question:
        return Response({"detail": "no questions available"}, status=404)

    with transaction.atomic():
        challenge = UserQaAnswers.objects.create(
            id=uuid.uuid4(),
            user=to_user,
            question=question,
            selected_option=None,
            is_correct=None,
            answered_at=None,
            answered_date=timezone.now().date(),
            points_earned=0,
        )

    return Response({
        "id": str(challenge.id),
        "question": {
            "id": str(question.id),
            "profession": question.profession,
            "question": question.question,
            "options": question.options,
        }
    }, status=201)


@api_view(["GET"])  # GET /qa/challenges
def list_challenges(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"detail": "unauthenticated"}, status=401)
    try:
        page = max(1, int(request.GET.get('page', '1')))
        page_size = max(1, min(100, int(request.GET.get('page_size', '50'))))
    except ValueError:
        page, page_size = 1, 50
    qs = UserQaAnswers.objects.select_related('question').filter(user=request.user, is_correct__isnull=True).order_by('-answered_date')
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    items = qs[start:end]
    return Response({
        "entries": [
            {
                "id": str(x.id),
                "question": {
                    "id": str(x.question.id),
                    "profession": x.question.profession,
                    "question": x.question.question,
                    "options": x.question.options,
                },
                "assignedDate": x.answered_date.isoformat(),
            }
            for x in items
        ],
        "meta": {"page": page, "page_size": page_size, "total": total},
    })


@api_view(["POST"])  # POST /qa/answer
def submit_answer(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"detail": "unauthenticated"}, status=401)
    data = request.data or {}
    challenge_id = data.get("challengeId")
    selected = data.get("selectedOption")
    if challenge_id is None or selected is None:
        return Response({"detail": "challengeId and selectedOption required"}, status=400)
    try:
        ans = UserQaAnswers.objects.select_related('question').get(id=challenge_id, user=request.user)
    except UserQaAnswers.DoesNotExist:
        return Response({"detail": "challenge not found"}, status=404)
    if ans.is_correct is not None:
        return Response({"detail": "already answered"}, status=400)

    correct = (int(selected) == int(ans.question.correct_option))
    points = 10 if correct else 0
    with transaction.atomic():
        ans.selected_option = int(selected)
        ans.is_correct = bool(correct)
        ans.answered_at = timezone.now()
        ans.points_earned = points
        ans.save(update_fields=["selected_option", "is_correct", "answered_at", "points_earned"])
        if points:
            profile = UserProfiles.objects.get(user=request.user)
            profile.pesa_points = (profile.pesa_points or 0) + points
            profile.save(update_fields=["pesa_points"])

    return Response({"ok": True, "is_correct": correct, "points": points})


# --- Admin QA Management ---

@api_view(["GET"])  # GET /admin/qa/questions
def admin_list_questions(request):
    if not request.user or not request.user.is_authenticated or not request.user.is_staff:
        return Response({"detail": "forbidden"}, status=403)
    items = QaQuestions.objects.all().order_by('profession')[:1000]
    return Response([
        {
            "id": str(q.id),
            "profession": q.profession,
            "question": q.question,
            "options": q.options,
            "correct_option": q.correct_option,
            "difficulty": q.difficulty,
        }
        for q in items
    ])


@api_view(["POST"])  # POST /admin/qa/questions
def admin_create_question(request):
    if not request.user or not request.user.is_authenticated or not request.user.is_staff:
        return Response({"detail": "forbidden"}, status=403)
    data = request.data or {}
    try:
        q = QaQuestions.objects.create(
            id=uuid.uuid4(),
            profession=data.get("profession") or "any",
            question=data.get("question") or "",
            options=data.get("options") or [],
            correct_option=int(data.get("correct_option", 0)),
            explanation=data.get("explanation"),
            difficulty=int(data.get("difficulty", 1)),
        )
    except Exception as e:
        return Response({"detail": str(e)}, status=400)
    return Response({"id": str(q.id)}, status=201)


@api_view(["DELETE"])  # DELETE /admin/qa/questions/<id>
def admin_delete_question(request, id: str):
    if not request.user or not request.user.is_authenticated or not request.user.is_staff:
        return Response({"detail": "forbidden"}, status=403)
    try:
        q = QaQuestions.objects.get(id=id)
    except QaQuestions.DoesNotExist:
        return Response({"detail": "not found"}, status=404)
    q.delete()
    return Response({"ok": True})
