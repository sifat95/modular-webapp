from django.db import models

# Create your models here.
class APILimit(models.Model):
    limit = models.IntegerField(default=0)

    def __str__(self):
        return str(self.limit)