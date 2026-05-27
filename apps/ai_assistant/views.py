from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import BookRecommendation
from .services import get_book_recommendations
from .forms import RecommendationForm


@login_required
def recommendations_view(request):
    recommendation = None
    form = RecommendationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        preferences = form.cleaned_data['preferences']
        try:
            recommendation = get_book_recommendations(preferences)
            BookRecommendation.objects.create(
                user=request.user,
                query=preferences,
                response=recommendation,
            )
        except Exception as e:
            form.add_error(None, f'Помилка AI: {str(e)}')

    past = BookRecommendation.objects.filter(user=request.user)[:5]
    return render(request, 'ai_assistant/recommendations.html', {
        'form': form,
        'recommendation': recommendation,
        'past_recommendations': past,
    })
