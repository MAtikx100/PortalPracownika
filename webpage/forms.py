from django import forms
from .models import Event
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
