from django.db import models

class Dreams(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.TextField(unique=True)
    slug = models.TextField(unique=True)
    cost = models.BigIntegerField()
    order_index = models.IntegerField(unique=True)
    image_url = models.TextField()
    description = models.TextField(blank=True, null=True)
    prerequisite_dream = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dreams'

class UserDreams(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey('accounts.Users', models.DO_NOTHING, blank=True, null=True)
    dream = models.ForeignKey(Dreams, models.DO_NOTHING, blank=True, null=True)
    unlocked_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'user_dreams'
        unique_together = (('user', 'dream'),)