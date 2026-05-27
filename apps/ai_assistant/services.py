import anthropic
from django.conf import settings
from apps.books.models import Book, Genre


def get_library_context():
    genres = list(Genre.objects.values_list('name', flat=True))
    total_books = Book.objects.count()
    available_books = Book.objects.filter(copies_available__gt=0).count()
    return (
        f"Ти — бібліотечний асистент системи управління бібліотекою. "
        f"У бібліотеці є {total_books} книг, з них {available_books} доступні для видачі. "
        f"Жанри: {', '.join(genres)}. "
        f"Допомагай читачам знайти потрібні книги, давай рекомендації та відповідай на питання про бібліотеку. "
        f"Відповідай українською мовою."
    )


def chat_with_assistant(messages_history: list[dict], user_message: str) -> str:
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    system_prompt = get_library_context()

    messages = messages_history + [{"role": "user", "content": user_message}]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )

    return response.content[0].text


def get_book_recommendations(user_preferences: str, available_books_only: bool = True) -> str:
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    books_query = Book.objects.prefetch_related('authors', 'genres')
    if available_books_only:
        books_query = books_query.filter(copies_available__gt=0)

    books_info = []
    for book in books_query[:50]:
        authors = book.authors_display
        genres = ', '.join(g.name for g in book.genres.all())
        books_info.append(
            f'"{book.title}" — {authors} ({book.year_published or "?"}) [{genres}]'
        )

    catalog_text = '\n'.join(books_info) if books_info else 'Каталог порожній.'

    prompt = (
        f"Ти — бібліотечний асистент. На основі переваг читача та каталогу бібліотеки "
        f"запропонуй 3-5 книг для читання.\n\n"
        f"Переваги читача: {user_preferences}\n\n"
        f"Доступні книги в каталозі:\n{catalog_text}\n\n"
        f"Надай конкретні рекомендації з коротким поясненням чому ці книги підійдуть. "
        f"Відповідай українською мовою."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text
