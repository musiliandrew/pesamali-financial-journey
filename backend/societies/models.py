from django.db import models

class Societies(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.TextField(unique=True)
    slogan = models.TextField(blank=True, null=True)
    leader = models.ForeignKey('accounts.Users', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    member_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'societies'