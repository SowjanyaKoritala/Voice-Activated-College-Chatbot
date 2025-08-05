from django.db import models

class Branch(models.Model):
    name = models.CharField(max_length=100)
    fee = models.IntegerField()

    def __str__(self):
        return self.name

class Timetable(models.Model):
    file = models.FileField(upload_to='timetables/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
