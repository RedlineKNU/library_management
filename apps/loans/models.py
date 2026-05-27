from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


class Loan(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_RETURNED = 'returned'
    STATUS_OVERDUE = 'overdue'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Активна'),
        (STATUS_RETURNED, 'Повернена'),
        (STATUS_OVERDUE, 'Прострочена'),
    ]

    book = models.ForeignKey(
        'books.Book', on_delete=models.PROTECT,
        verbose_name='Книга', related_name='loans'
    )
    reader = models.ForeignKey(
        'readers.Reader', on_delete=models.PROTECT,
        verbose_name='Читач', related_name='loans'
    )
    loan_date = models.DateField('Дата видачі', default=timezone.now)
    due_date = models.DateField('Дата повернення')
    return_date = models.DateField('Фактична дата повернення', null=True, blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    issued_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True,
        verbose_name='Видав', related_name='issued_loans'
    )
    notes = models.TextField('Нотатки', blank=True)

    class Meta:
        verbose_name = 'Позика'
        verbose_name_plural = 'Позики'
        ordering = ['-loan_date']

    def __str__(self):
        return f'{self.book.title} — {self.reader.full_name} ({self.loan_date})'

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now().date() + timedelta(
                days=getattr(settings, 'LOAN_DURATION_DAYS', 14)
            )
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.status == self.STATUS_RETURNED:
            return False
        return timezone.now().date() > self.due_date

    @property
    def overdue_days(self):
        if not self.is_overdue:
            return 0
        end = self.return_date or timezone.now().date()
        return max(0, (end - self.due_date).days)

    def calculate_fine(self):
        fine_per_day = getattr(settings, 'FINE_PER_DAY', 5)
        return self.overdue_days * fine_per_day

    def return_book(self, return_date=None):
        self.return_date = return_date or timezone.now().date()
        self.status = self.STATUS_RETURNED
        self.book.copies_available += 1
        self.book.save()
        self.save()

        if self.overdue_days > 0:
            Fine.objects.get_or_create(
                loan=self,
                defaults={'amount': self.calculate_fine()}
            )


class Fine(models.Model):
    loan = models.OneToOneField(
        Loan, on_delete=models.CASCADE,
        verbose_name='Позика', related_name='fine'
    )
    amount = models.DecimalField('Сума штрафу', max_digits=8, decimal_places=2)
    is_paid = models.BooleanField('Сплачено', default=False)
    paid_date = models.DateField('Дата сплати', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Штраф'
        verbose_name_plural = 'Штрафи'
        ordering = ['-created_at']

    def __str__(self):
        status = 'сплачено' if self.is_paid else 'не сплачено'
        return f'Штраф {self.amount} грн — {self.loan} ({status})'

    def pay(self):
        self.is_paid = True
        self.paid_date = timezone.now().date()
        self.save()
