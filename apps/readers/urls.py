from django.urls import path
from . import views

app_name = 'readers'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('list/', views.ReaderListView.as_view(), name='list'),
    path('<int:pk>/', views.ReaderDetailView.as_view(), name='detail'),
]
