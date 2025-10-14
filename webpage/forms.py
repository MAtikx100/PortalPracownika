from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Event, Notice
import datetime

# Generate time choices for every 30 minutes
TIME_CHOICES = []
for hour in range(24):
    for minute in (0, 30):
        time_val = datetime.time(hour, minute)
        time_str = time_val.strftime('%H:%M')
        TIME_CHOICES.append((time_val, time_str))

class EventForm(forms.ModelForm):
    start_time = forms.ChoiceField(choices=TIME_CHOICES, widget=forms.Select())
    end_time = forms.ChoiceField(choices=TIME_CHOICES, widget=forms.Select())

    class Meta:
        model = Event
        fields = ['event_type', 'title', 'description', 'start_time', 'end_time']

class ManagerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'first_name', 'last_name']

class EmployeeCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'first_name', 'last_name']

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content']
