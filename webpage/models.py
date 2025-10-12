from django.db import models
from django.contrib.auth.models import User

class Day(models.Model):
    date = models.DateField(unique=True)

    def __str__(self):
        return str(self.date)

class Event(models.Model):
    EVENT_TYPE_CHOICES = (
        ("praca", "Praca"),
        ("urlop", "Urlop"),
    )

    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES, default='praca')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.get_event_type_display()} for {self.user.username} on {self.day.date}"
