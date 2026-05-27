from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.utils import timezone
from django.db import transaction
from .models import Loan, Fine
from .forms import LoanCreateForm, LoanReturnForm
from apps.books.models import Book
from apps.readers.models import Reader


class LoanListView(PermissionRequiredMixin, ListView):
    model = Loan
    template_name = 'loans/loan_list.html'
    context_object_name = 'loans'
    permission_required = 'readers.can_view_all_loans'
    paginate_by = 20

    def get_queryset(self):
        queryset = Loan.objects.select_related('book', 'reader__user').order_by('-loan_date')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_filter'] = self.request.GET.get('status', '')
        ctx['overdue_count'] = Loan.objects.filter(
            status='active', due_date__lt=timezone.now().date()
        ).count()
        return ctx


@login_required
@permission_required('readers.can_view_all_loans', raise_exception=True)
def issue_book(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)

    if not book.is_available:
        messages.error(request, 'Ця книга зараз недоступна для видачі.')
        return redirect('books:detail', pk=book_pk)

    if request.method == 'POST':
        form = LoanCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                loan = form.save(commit=False)
                loan.book = book
                loan.issued_by = request.user
                loan.save()
                book.copies_available -= 1
                book.save()
            messages.success(request, f'Книгу "{book.title}" успішно видано читачу {loan.reader.full_name}.')
            return redirect('loans:detail', pk=loan.pk)
    else:
        form = LoanCreateForm()

    return render(request, 'loans/issue_book.html', {'form': form, 'book': book})


@login_required
@permission_required('readers.can_view_all_loans', raise_exception=True)
def return_book(request, loan_pk):
    loan = get_object_or_404(Loan, pk=loan_pk, status=Loan.STATUS_ACTIVE)

    if request.method == 'POST':
        form = LoanReturnForm(request.POST, instance=loan)
        if form.is_valid():
            with transaction.atomic():
                loan.return_book(form.cleaned_data.get('return_date'))
            if hasattr(loan, 'fine') and loan.fine:
                messages.warning(
                    request,
                    f'Книга повернена. Нараховано штраф: {loan.fine.amount} грн.'
                )
            else:
                messages.success(request, f'Книгу "{loan.book.title}" успішно повернено.')
            return redirect('loans:detail', pk=loan.pk)
    else:
        form = LoanReturnForm(instance=loan)

    return render(request, 'loans/return_book.html', {'form': form, 'loan': loan})


class LoanDetailView(LoginRequiredMixin, DetailView):
    model = Loan
    template_name = 'loans/loan_detail.html'
    context_object_name = 'loan'

    def get_queryset(self):
        return Loan.objects.select_related('book', 'reader__user', 'issued_by')


class MyLoansView(LoginRequiredMixin, ListView):
    model = Loan
    template_name = 'loans/my_loans.html'
    context_object_name = 'loans'

    def get_queryset(self):
        reader = get_object_or_404(Reader, user=self.request.user)
        return Loan.objects.filter(reader=reader).select_related('book').order_by('-loan_date')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        reader = get_object_or_404(Reader, user=self.request.user)
        ctx['unpaid_fines'] = Fine.objects.filter(
            loan__reader=reader, is_paid=False
        ).select_related('loan__book')
        return ctx


class FineListView(PermissionRequiredMixin, ListView):
    model = Fine
    template_name = 'loans/fine_list.html'
    context_object_name = 'fines'
    permission_required = 'readers.can_view_all_loans'
    paginate_by = 20

    def get_queryset(self):
        queryset = Fine.objects.select_related('loan__book', 'loan__reader__user')
        if self.request.GET.get('unpaid'):
            queryset = queryset.filter(is_paid=False)
        return queryset


@login_required
@permission_required('readers.can_view_all_loans', raise_exception=True)
def pay_fine(request, fine_pk):
    fine = get_object_or_404(Fine, pk=fine_pk, is_paid=False)
    fine.pay()
    messages.success(request, f'Штраф {fine.amount} грн сплачено.')
    return redirect('loans:fine_list')
