from django.contrib import admin
from .models import BookRecommendation


@admin.register(BookRecommendation)
class BookRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'created_at')
    readonly_fields = ('created_at',)
