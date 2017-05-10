import datetime
from django.db import models
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
import sox
storage = FileSystemStorage(location='/home/django/django_project/media/media/')

class Document(models.Model):
    description = models.CharField(max_length=255)
    document = models.FileField(upload_to='media')
    date = models.DateTimeField(default=timezone.now, editable=False)
    def date_uploaded(self):
        self.date = timezone.now()
        self.save() 
    def __str__(self): # call on the string description of object
        return self.description
