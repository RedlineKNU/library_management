from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.BookListView.as_view(), name='list'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='detail'),
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
    path('genres/', views.GenreListView.as_view(), name='genre_list'),
]
