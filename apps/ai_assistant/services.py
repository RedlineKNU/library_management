from groq import Groq
from django.conf import settings
from apps.books.models import Book


def get_book_recommendations(user_preferences: str) -> str:
    client = Groq(api_key=settings.GROQ_API_KEY)

    books_query = Book.objects.filter(copies_available__gt=0).prefetch_related('authors', 'genres')

    books_info = []
    for book in books_query[:50]:
        genres = ', '.join(g.name for g in book.genres.all())
        books_info.append(f'"{book.title}" — {book.authors_display} [{genres}]')

    catalog_text = '\n'.join(books_info) if books_info else 'Каталог порожній.'

    prompt = (
        f"Ти — бібліотечний асистент. На основі переваг читача та каталогу бібліотеки "
        f"запропонуй 3-5 книг для читання.\n\n"
        f"Переваги читача: {user_preferences}\n\n"
        f"Доступні книги:\n{catalog_text}\n\n"
        f"Дай конкретні рекомендації з коротким поясненням. Відповідай українською мовою."
    )

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )

    return response.choices[0].message.content
