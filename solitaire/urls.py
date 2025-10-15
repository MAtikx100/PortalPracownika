from django.urls import path
from . import views

urlpatterns = [
    path('', views.solitaire_view, name='solitaire'),
]
