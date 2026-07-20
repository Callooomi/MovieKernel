from django.urls import path
from . import views

app_name = 'networks'

urlpatterns = [
    path('', views.latest, name='latest'),
    path('<int:board_id>/', views.play_board, name='play'),
    path('<int:board_id>/submit/', views.submit_path, name='submit'),
    path('<int:board_id>/reset/', views.reset_lives, name='reset'),
    path('<int:board_id>/reset/', views.reset_lives, name='reset_lives'),
    path('<int:board_id>/reveal/', views.reveal_answers, name='reveal'),
]
