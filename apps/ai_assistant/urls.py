from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
    path('chat/send/', views.send_message, name='send_message'),
    path('chat/new/', views.new_chat_session, name='new_chat'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
]
