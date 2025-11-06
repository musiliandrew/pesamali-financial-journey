from django.contrib import admin
from .models import QaQuestions, UserQaAnswers


@admin.register(QaQuestions)
class QaQuestionsAdmin(admin.ModelAdmin):
    list_display = ("id", "profession", "question", "correct_option", "difficulty")
    list_filter = ("profession", "difficulty")
    search_fields = ("question",)


@admin.register(UserQaAnswers)
class UserQaAnswersAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question", "selected_option", "is_correct", "answered_at")
    list_filter = ("is_correct",)

# Register your models here.
