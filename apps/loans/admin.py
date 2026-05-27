from django.contrib import admin
from .models import Loan, Fine


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'reader', 'loan_date', 'due_date', 'status', 'is_overdue')
    list_filter = ('status', 'loan_date')
    search_fields = ('book__title', 'reader__user__last_name', 'reader__library_card_number')
    readonly_fields = ('loan_date',)

    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Прострочена'


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('loan', 'amount', 'is_paid', 'paid_date', 'created_at')
    list_filter = ('is_paid',)
    readonly_fields = ('created_at',)
