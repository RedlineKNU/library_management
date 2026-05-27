from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Book, Author, Genre
from .forms import BookSearchForm


class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        queryset = Book.objects.prefetch_related('authors', 'genres')
        form = BookSearchForm(self.request.GET)

        if form.is_valid():
            query = form.cleaned_data.get('query')
            genre = form.cleaned_data.get('genre')
            available_only = form.cleaned_data.get('available_only')
            year_from = form.cleaned_data.get('year_from')
            year_to = form.cleaned_data.get('year_to')

            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(authors__first_name__icontains=query) |
                    Q(authors__last_name__icontains=query) |
                    Q(isbn__icontains=query) |
                    Q(publisher__icontains=query)
                ).distinct()

            if genre:
                queryset = queryset.filter(genres=genre)

            if available_only:
                queryset = queryset.filter(copies_available__gt=0)

            if year_from:
                queryset = queryset.filter(year_published__gte=year_from)

            if year_to:
                queryset = queryset.filter(year_published__lte=year_to)

        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = BookSearchForm(self.request.GET)
        ctx['total_books'] = Book.objects.count()
        ctx['available_books'] = Book.objects.filter(copies_available__gt=0).count()
        return ctx


class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'

    def get_queryset(self):
        return Book.objects.prefetch_related('authors', 'genres')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'reader_profile'):
            reader = self.request.user.reader_profile
            ctx['user_has_active_loan'] = self.object.loans.filter(
                reader=reader, status='active'
            ).exists()
        return ctx


class AuthorDetailView(DetailView):
    model = Author
    template_name = 'books/author_detail.html'
    context_object_name = 'author'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['books'] = self.object.books.prefetch_related('genres')
        return ctx


class GenreListView(ListView):
    model = Genre
    template_name = 'books/genre_list.html'
    context_object_name = 'genres'

    def get_queryset(self):
        return Genre.objects.prefetch_related('books')
