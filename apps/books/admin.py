from django.contrib import admin
from .models import Book, Author, Genre


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    search_fields = ('last_name', 'first_name')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'authors_display', 'year_published', 'copies_total', 'copies_available')
    list_filter = ('genres', 'year_published')
    search_fields = ('title', 'isbn', 'authors__last_name')
    filter_horizontal = ('authors', 'genres')
    readonly_fields = ('created_at',)

    def authors_display(self, obj):
        return obj.authors_display
    authors_display.short_description = 'Автори'
