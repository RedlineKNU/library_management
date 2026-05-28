from django.db import models
from django.contrib.auth.models import User
import uuid


class Reader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reader_profile')
    library_card_number = models.CharField(
        'Номер читацького квитка', max_length=20, unique=True, blank=True
    )
    phone = models.CharField('Телефон', max_length=20, blank=True)
    address = models.TextField('Адреса', blank=True)
    date_of_birth = models.DateField('Дата народження', null=True, blank=True)
    registration_date = models.DateField('Дата реєстрації', auto_now_add=True)
    is_blocked = models.BooleanField('Заблокований', default=False)

    class Meta:
        verbose_name = 'Читач'
        verbose_name_plural = 'Читачі'
        ordering = ['user__last_name', 'user__first_name']
        permissions = [
            ('can_manage_readers', 'Може керувати читачами'),
            ('can_view_all_loans', 'Може переглядати всі позики'),
        ]

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.library_card_number})'

    def save(self, *args, **kwargs):
        if not self.library_card_number:
            self.library_card_number = self._generate_card_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_card_number():
        return f'LIB-{uuid.uuid4().hex[:8].upper()}'

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def active_loans_count(self):
        return self.loans.filter(status='active').count()

    @property
    def unpaid_fines_total(self):
        from apps.loans.models import Fine
        total = Fine.objects.filter(loan__reader=self, is_paid=False).aggregate(
            total=models.Sum('amount')
        )['total']
        return total or 0
