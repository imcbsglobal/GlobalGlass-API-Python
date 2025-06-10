from django.db import models

class AccUsers(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    pass_field = models.CharField(max_length=100, db_column='pass')
    role = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = 'acc_users'
        managed = False

    def __str__(self):
        return self.id