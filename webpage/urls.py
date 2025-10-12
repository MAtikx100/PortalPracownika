from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create_user/', views.create_user_view, name='create_user'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/<int:year>/<int:month>/', views.calendar_view, name='calendar_nav'),
    path('calendar/<int:year>/<int:month>/<int:day>/', views.day_view, name='day_view'),
    path('calendar/<int:year>/<int:month>/<int:day>/add/', views.add_event_view, name='add_event'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('calendar/<str:username>/', views.calendar_view, name='calendar_user'),
    path('calendar/<str:username>/<int:year>/<int:month>/', views.calendar_view, name='calendar_nav_user'),
    path('calendar/<str:username>/<int:year>/<int:month>/<int:day>/', views.day_view, name='day_view_user'),
]
