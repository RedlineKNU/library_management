from django.contrib import admin
from .models import Reader


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'library_card_number', 'phone', 'registration_date', 'is_blocked')
    list_filter = ('is_blocked', 'registration_date')
    search_fields = ('user__first_name', 'user__last_name', 'library_card_number', 'phone')
    readonly_fields = ('library_card_number', 'registration_date')

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'ПІБ'
