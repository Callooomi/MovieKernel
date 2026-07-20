from django.urls import path
from . import views

app_name = 'higherorlower'  # The namespace for the app

urlpatterns = [
    path('', views.higher_or_lower, name='higher_or_lower'),  # Named 'higher_or_lower' for easy reference
]
