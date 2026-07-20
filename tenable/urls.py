from django.urls import path
from . import views

app_name = 'tenable'

urlpatterns = [
    path('', views.latest_tenable, name='latest'),
    path('<int:question_id>/', views.play_tenable, name='play'),
]
