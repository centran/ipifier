from django.db import models

class Record(models.Model):
  name = models.CharField(max_length=255)
  type = models.CharField(max_length=10)
  content = models.CharField(max_length=64000)
  ttl = models.IntegerField()
  pri = models.IntegerField()
  changedate = models.IntegerField()
