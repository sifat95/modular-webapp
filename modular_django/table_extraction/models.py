from django.db import models

# Create your models here.
class TableData(models.Model):
    image_uri = models.TextField()
    table_data_str = models.TextField()

    def __str__(self):
        return self.table_data_str