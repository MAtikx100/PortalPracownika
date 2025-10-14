from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

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

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, related_name='employees', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Check if the user has a profile, which might not be the case for a new user being created
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # If the profile doesn't exist, create it. This is a fallback.
        Profile.objects.create(user=instance)

class Timer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.user.username} - {self.time}'

class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': "Manager"})
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
