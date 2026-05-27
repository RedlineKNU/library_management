from django import forms
from django.utils import timezone
from .models import Loan
from apps.readers.models import Reader


class LoanCreateForm(forms.ModelForm):
    reader = forms.ModelChoiceField(
        queryset=Reader.objects.filter(is_blocked=False).select_related('user'),
        label='Читач',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Loan
        fields = ('reader', 'due_date', 'notes')
        widgets = {
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from datetime import timedelta
        self.fields['due_date'].initial = (timezone.now() + timedelta(days=14)).date()
        self.fields['due_date'].required = False


class LoanReturnForm(forms.ModelForm):
    return_date = forms.DateField(
        label='Дата повернення',
        initial=timezone.now,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    class Meta:
        model = Loan
        fields = ('return_date',)
