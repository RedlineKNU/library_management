from django import forms
from .models import Genre


class BookSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Назва, автор, ISBN...', 'class': 'form-control'})
    )
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        empty_label='Всі жанри',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    available_only = forms.BooleanField(
        required=False,
        label='Тільки доступні',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    year_from = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Від року', 'class': 'form-control'})
    )
    year_to = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'До року', 'class': 'form-control'})
    )
