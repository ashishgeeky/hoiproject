from django.db import models
from myapp.configuration import status_choices, priority_choices
import datetime

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=200,default = "In Progress", choices = status_choices)
    due_date = models.DateField(default=datetime.date.today, blank=False)
    priority = models.CharField(max_length=200,default = "Low", choices = priority_choices)


    def __str__(self):
        return self.title
