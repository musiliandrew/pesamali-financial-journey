from django.db import models


class QaQuestions(models.Model):
    id = models.UUIDField(primary_key=True)
    profession = models.TextField()
    question = models.TextField()
    options = models.JSONField()
    correct_option = models.IntegerField()
    explanation = models.TextField(blank=True, null=True)
    difficulty = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'qa_questions'


class UserQaAnswers(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey('accounts.Users', models.DO_NOTHING, blank=True, null=True)
    question = models.ForeignKey(QaQuestions, models.DO_NOTHING, blank=True, null=True)
    selected_option = models.IntegerField(blank=True, null=True)
    is_correct = models.BooleanField(blank=True, null=True)
    answered_at = models.DateTimeField(blank=True, null=True)
    answered_date = models.DateField()
    points_earned = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'user_qa_answers'
        unique_together = (('user', 'question', 'answered_date'),)