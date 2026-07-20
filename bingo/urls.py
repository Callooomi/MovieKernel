from django.urls import path
from . import views

app_name = 'bingo'

urlpatterns = [
    path('', views.play_bingo, name='play'),
    path('reset/', views.reset_bingo, name='reset'),
    path('update_game_state/', views.update_game_state, name='update_game_state'),  # Add this line
]
