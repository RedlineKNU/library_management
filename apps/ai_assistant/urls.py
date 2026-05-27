from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('recommendations/', views.recommendations_view, name='recommendations'),
]
