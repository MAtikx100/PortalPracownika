from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from calendar import HTMLCalendar
from datetime import date, time
from .models import Day, Event, Profile, Timer, Notice
from .forms import EventForm, ManagerCreationForm, EmployeeCreationForm, ProfileEditForm, NoticeForm
from django.urls import reverse
from django.http import JsonResponse
import json

def index(request):
    return render(request, 'index.html')

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

@login_required
@permission_required('auth.add_user', raise_exception=True)
def create_user_view(request):
    user = request.user
    if user.groups.filter(name='Administrator').exists() or user.is_superuser:
        Form = ManagerCreationForm
        template_title = 'Create New Manager'
        submit_text = 'Create Manager'
        group_name = 'Manager'
    elif user.groups.filter(name='Manager').exists():
        Form = EmployeeCreationForm
        template_title = 'Create New Employee'
        submit_text = 'Create Employee'
        group_name = 'Regular User'
    else:
        return redirect('index') # Or a permission denied page

    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid():
            new_user = form.save()
            group = Group.objects.get(name=group_name)
            new_user.groups.add(group)
            if group_name == 'Regular User':
                new_user.profile.manager = user
                new_user.profile.save()
            return redirect('dashboard')
    else:
        form = Form()

    return render(request, 'user_form.html', {
        'form': form,
        'title': template_title,
        'submit_button_text': submit_text
    })

class DayClickableHTMLCalendar(HTMLCalendar):
    def __init__(self, year=None, month=None, user_username=None, target_user=None):
        super().__init__()
        self.year = year
        self.month = month
        self.user_username = user_username
        self.target_user = target_user
        self.events_by_day = {}
        if self.year and self.month and self.target_user:
            events = Event.objects.filter(
                user=self.target_user,
                day__date__year=self.year,
                day__date__month=self.month
            ).order_by('start_time').values_list('day__date__day', 'event_type', 'start_time', 'end_time')
            for day_num, event_type, start_time, end_time in events:
                if day_num not in self.events_by_day:
                    self.events_by_day[day_num] = []
                self.events_by_day[day_num].append({
                    'type': event_type,
                    'start': start_time,
                    'end': end_time
                })

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'
        else:
            if self.user_username:
                url = reverse('day_view_user', args=(self.user_username, self.year, self.month, day))
            else:
                url = reverse('day_view', args=(self.year, self.month, day))

            day_events = self.events_by_day.get(day, [])
            events_html = f'<a href="{url}">{day}</a>'
            events_html += '<div class="day-events">'
            for event in day_events:
                event_type_display = event['type'].capitalize()
                start_str = event['start'].strftime('%H:%M')
                end_str = event['end'].strftime('%H:%M')
                events_html += f'<div>{event_type_display}: {start_str} - {end_str}</div>'
            events_html += '</div>'

            return f'<td>{events_html}</td>'

    def formatmonth(self, theyear, themonth, withyear=True):
        self.year, self.month = theyear, themonth
        html_cal = super().formatmonth(theyear, themonth, withyear)
        html_cal = html_cal.replace('class="month"', 'class="month_calendar"')
        return html_cal

@login_required
def calendar_view(request, year=None, month=None, username=None):
    target_user = request.user
    if username:
        target_user = get_object_or_404(User, username=username)
        # Security checks
        is_manager_of_user = target_user.profile.manager == request.user
        is_admin = request.user.groups.filter(name='Administrator').exists() or request.user.is_superuser
        is_viewing_another_manager = request.user.groups.filter(name='Manager').exists() and target_user.groups.filter(name='Manager').exists()

        if not (is_manager_of_user or is_admin or target_user == request.user or is_viewing_another_manager):
            return redirect('index')

    if year is None or month is None:
        today = date.today()
        year, month = today.year, today.month
    else:
        year, month = int(year), int(month)

    cal = DayClickableHTMLCalendar(year, month, username, target_user).formatmonth(year, month)

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
        # Security checks
        is_manager_of_user = target_user.profile.manager == request.user
        is_admin = request.user.groups.filter(name='Administrator').exists() or request.user.is_superuser
        is_viewing_another_manager = request.user.groups.filter(name='Manager').exists() and target_user.groups.filter(name='Manager').exists()

        if not (is_manager_of_user or is_admin or target_user == request.user or is_viewing_another_manager):
            return redirect('index')

    day_date = date(year, month, day)
    day_obj, created = Day.objects.get_or_create(date=day_date)
    events = Event.objects.filter(day=day_obj, user=target_user).order_by('start_time')

    hours = []
    for hour in range(24):
        current_time_start = time(hour, 0)
        hour_events = events.filter(
            start_time__lt=time(hour + 1, 0) if hour < 23 else time(23, 59, 59),
            end_time__gt=current_time_start
        )
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
def add_event_view(request, year, month, day, username=None):
    target_user = request.user
    if username:
        target_user = get_object_or_404(User, username=username)
        # Security check: only a manager of the user or an admin can add an event
        is_manager_of_user = target_user.profile.manager == request.user
        is_admin = request.user.groups.filter(name='Administrator').exists() or request.user.is_superuser
        if not (is_manager_of_user or is_admin):
            return redirect('index')

    day_date = date(year, month, day)
    day_obj, created = Day.objects.get_or_create(date=day_date)

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.day = day_obj
            event.user = target_user # Assign event to the correct user
            event.save()
            if username:
                return redirect('day_view_user', username=username, year=year, month=month, day=day)
            else:
                return redirect('day_view', year=year, month=month, day=day)
    else:
        form = EventForm()

    return render(request, 'add_event.html', {
        'form': form, 
        'day': day_obj,
        'target_user': target_user
    })

@login_required
def delete_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event_owner = event.user
    day_date = event.day.date

    # Security check
    is_manager_of_owner = event_owner.profile.manager == request.user
    is_admin = request.user.groups.filter(name='Administrator').exists() or request.user.is_superuser

    if not (request.user == event_owner or is_manager_of_owner or is_admin):
        return redirect('index') # Or a permission denied page

    event.delete()

    # Redirect back to the correct day view
    if event_owner != request.user:
        return redirect('day_view_user', username=event_owner.username, year=day_date.year, month=day_date.month, day=day_date.day)
    else:
        return redirect('day_view', year=day_date.year, month=day_date.month, day=day_date.day)

@login_required
def dashboard_view(request):
    user = request.user
    context = {
        'dashboard_title': 'Dashboard',
    }

    is_admin = user.groups.filter(name='Administrator').exists() or user.is_superuser
    is_manager = user.groups.filter(name='Manager').exists()

    if is_admin or is_manager:
        if is_admin:
            context['dashboard_title'] = "All Users Dashboard"
        else:
            context['dashboard_title'] = "Company Dashboard"

        managers = User.objects.filter(groups__name='Manager')
        managers_with_teams = []
        for manager in managers:
            employees = User.objects.filter(profile__manager=manager)
            managers_with_teams.append({
                'manager': manager,
                'employees': employees
            })
        
        context['managers_with_teams'] = managers_with_teams
        context['unassigned_employees'] = User.objects.filter(groups__name='Regular User', profile__manager__isnull=True)

    return render(request, 'dashboard.html', context)

@login_required
def timer_view(request):
    return render(request, 'timer.html')

@login_required
def save_time(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        time = data.get('time')
        if time:
            Timer.objects.create(user=request.user, time=time)
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'})

@login_required
def get_times(request):
    times = Timer.objects.filter(user=request.user).values_list('time', flat=True)
    return JsonResponse(list(times), safe=False)

@login_required
def profile_view(request):
    user = request.user
    saved_times = Timer.objects.filter(user=user).order_by('-id')

    total_seconds = 0
    for timer_instance in saved_times:
        try:
            h, m, s = map(int, timer_instance.time.split(':'))
            total_seconds += h * 3600 + m * 60 + s
        except ValueError:
            continue

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    total_time_str = f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}'

    context = {
        'user': request.user,
        'saved_times': saved_times,
        'total_time': total_time_str,
    }
    return render(request, 'profile.html', context)

@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'profile_edit.html', {'form': form})

@login_required
def notice_board_view(request):
    notices = Notice.objects.order_by('-created_at')
    is_manager = request.user.groups.filter(name='Manager').exists()
    context = {
        'notices': notices,
        'is_manager': is_manager,
    }
    return render(request, 'notice_board.html', context)

@login_required
def add_notice_view(request):
    if not request.user.groups.filter(name='Manager').exists():
        return redirect('notice_board')

    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.author = request.user
            notice.save()
            return redirect('notice_board')
    else:
        form = NoticeForm()

    return render(request, 'add_notice.html', {'form': form})
