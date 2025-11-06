from django.urls import path
from .views import (
    send_challenge,
    list_challenges,
    submit_answer,
    admin_list_questions,
    admin_create_question,
    admin_delete_question,
)

urlpatterns = [
    path('qa/challenge', send_challenge),
    path('qa/challenges', list_challenges),
    path('qa/answer', submit_answer),
    # Admin management
    path('admin/qa/questions', admin_list_questions),
    path('admin/qa/questions/', admin_create_question),
    path('admin/qa/questions/<str:id>', admin_delete_question),
]
