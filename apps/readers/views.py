from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView
from .models import Reader
from .forms import ReaderRegistrationForm, ReaderProfileForm, LibrarianLoginForm


def register(request):
    if request.method == 'POST':
        form = ReaderRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Реєстрацію успішно завершено!')
            return redirect('books:list')
    else:
        form = ReaderRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LibrarianLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'books:list')
            return redirect(next_url)
    else:
        form = LibrarianLoginForm(request)
    return render(request, 'registration/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('readers:login')


@login_required
def profile(request):
    reader = get_object_or_404(Reader, user=request.user)
    if request.method == 'POST':
        form = ReaderProfileForm(request.POST, instance=reader)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль оновлено!')
            return redirect('readers:profile')
    else:
        form = ReaderProfileForm(instance=reader)

    active_loans = reader.loans.filter(status='active').select_related('book')
    return render(request, 'readers/profile.html', {
        'reader': reader,
        'form': form,
        'active_loans': active_loans,
    })


class ReaderListView(PermissionRequiredMixin, ListView):
    model = Reader
    template_name = 'readers/reader_list.html'
    context_object_name = 'readers'
    permission_required = 'readers.can_manage_readers'
    paginate_by = 20

    def get_queryset(self):
        queryset = Reader.objects.select_related('user')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(library_card_number__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query'] = self.request.GET.get('q', '')
        return ctx


class ReaderDetailView(PermissionRequiredMixin, DetailView):
    model = Reader
    template_name = 'readers/reader_detail.html'
    context_object_name = 'reader'
    permission_required = 'readers.can_manage_readers'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['loans'] = self.object.loans.select_related('book').order_by('-loan_date')
        return ctx
