from django import forms


class RecommendationForm(forms.Form):
    preferences = forms.CharField(
        label='Ваші вподобання',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Опишіть що вам подобається читати: жанр, теми, автори, настрій книги...',
        }),
        max_length=1000,
    )


class ChatMessageForm(forms.Form):
    message = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Напишіть запитання про книги...',
            'autocomplete': 'off',
        }),
        max_length=2000,
    )
