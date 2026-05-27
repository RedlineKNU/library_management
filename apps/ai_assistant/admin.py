from django.contrib import admin
from .models import ChatSession, ChatMessage, BookRecommendation


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BookRecommendation)
class BookRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'created_at')
    readonly_fields = ('created_at',)
