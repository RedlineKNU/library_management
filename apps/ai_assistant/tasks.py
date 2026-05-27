from celery import shared_task
from .services import get_book_recommendations
from .models import BookRecommendation
from django.contrib.auth.models import User


@shared_task
def generate_book_recommendations_task(user_id: int, preferences: str) -> str:
    try:
        user = User.objects.get(pk=user_id)
        response = get_book_recommendations(preferences)
        BookRecommendation.objects.create(
            user=user,
            query=preferences,
            response=response,
        )
        return response
    except Exception as e:
        return f"Помилка генерації рекомендацій: {str(e)}"
