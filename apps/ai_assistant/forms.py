from django import forms


class RecommendationForm(forms.Form):
    preferences = forms.CharField(
        label='Ваші вподобання',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Опишіть що вам подобається читати: жанр, теми, автори...',
        }),
        max_length=1000,
    )
