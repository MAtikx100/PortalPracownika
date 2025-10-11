from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from calendar import HTMLCalendar
from datetime import date
from .models import Day, Event
from .forms import EventForm
from django.urls import reverse

def index(request):
    return render(request, 'index.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

class DayClickableHTMLCalendar(HTMLCalendar):
    def __init__(self, year=None, month=None, user_username=None):
        super().__init__()
        self.year = year
        self.month = month
        self.user_username = user_username

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'
        else:
            if self.user_username:
                url = reverse('day_view_user', args=(self.user_username, self.year, self.month, day))
            else:
                url = reverse('day_view', args=(self.year, self.month, day))
            return f'<td><a href="{url}">{day}</a></td>'

    def formatmonth(self, theyear, themonth, withyear=True):
        self.year, self.month = theyear, themonth
        return super().formatmonth(theyear, themonth, withyear)

@login_required
def calendar_view(request, year=None, month=None, username=None):
    target_user = request.user
    if username:
        target_user = get_object_or_404(User, username=username)
        if not request.user.has_perm('webpage.view_event') and request.user != target_user:
            return redirect('index') # Or a permission denied page

    if year is None or month is None:
        today = date.today()
        year, month = today.year, today.month
    else:
        year, month = int(year), int(month)

    cal = DayClickableHTMLCalendar(year, month, username).formatmonth(year, month)

    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1

    return render(request, 'calendar.html', {
        'calendar': cal,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'target_user': target_user,
        'username': username,
    })

@login_required
def day_view(request, year, month, day, username=None):
    target_user = request.user
    if username:
        target_user = get_object_or_404(User, username=username)
        if not request.user.has_perm('webpage.view_event') and request.user != target_user:
            return redirect('index') # Or a permission denied page

    day_date = date(year, month, day)
    day_obj, created = Day.objects.get_or_create(date=day_date)
    events = Event.objects.filter(day=day_obj, user=target_user).order_by('start_time')

    hours = []
    for hour in range(24):
        hour_events = events.filter(start_time__hour=hour)
        hours.append({
            'time': hour,
            'events': hour_events
        })

    return render(request, 'day.html', {
        'day': day_obj,
        'hours': hours,
        'year': year,
        'month': month,
        'target_user': target_user,
        'username': username,
    })

@login_required
def add_event_view(request, year, month, day):
    day_date = date(year, month, day)
    day_obj, created = Day.objects.get_or_create(date=day_date)

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.day = day_obj
            event.user = request.user
            event.save()
            return redirect('day_view', year=year, month=month, day=day)
    else:
        form = EventForm()

    return render(request, 'add_event.html', {'form': form, 'day': day_obj})

@login_required
@permission_required('webpage.view_event', raise_exception=True)
def dashboard_view(request):
    employees = User.objects.all().order_by('username')
    return render(request, 'dashboard.html', {'employees': employees})
