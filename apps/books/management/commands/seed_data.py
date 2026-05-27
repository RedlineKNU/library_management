import io
from datetime import date, timedelta

from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.books.models import Author, Book, Genre
from apps.loans.models import Fine, Loan
from apps.readers.models import Reader


BOOKS = [
    {
        'title': 'Воно',
        'author': ('Стівен', 'Кінг'),
        'genres': ['Жахи'],
        'year': 1986,
        'copies': 3,
        'color': (180, 40, 40),
        'description': 'Роман про групу дітей у містечку Дері, яких переслідує давнє зло.',
    },
    {
        'title': 'Сяйво',
        'author': ('Стівен', 'Кінг'),
        'genres': ['Жахи'],
        'year': 1977,
        'copies': 2,
        'color': (60, 40, 120),
        'description': 'Родина охоронців готелю опиняється в ізоляції серед зими.',
    },
    {
        'title': 'Володар перснів',
        'author': ('Дж.Р.Р.', 'Толкієн'),
        'genres': ['Фантастика', 'Пригоди'],
        'year': 1954,
        'copies': 4,
        'color': (40, 100, 60),
        'description': 'Епічна фентезі-сага про знищення Персня всевладдя.',
    },
    {
        'title': 'Собака Баскервілів',
        'author': ('Артур Конан', 'Дойл'),
        'genres': ['Детектив'],
        'year': 1902,
        'copies': 2,
        'color': (80, 60, 30),
        'description': 'Шерлок Холмс розслідує таємниче прокляття роду Баскервілів.',
    },
    {
        'title': 'Вбивство у Східному Експресі',
        'author': ('Агата', 'Крісті'),
        'genres': ['Детектив'],
        'year': 1934,
        'copies': 3,
        'color': (30, 80, 120),
        'description': 'Еркюль Пуаро розслідує вбивство в потязі під час снігової бурі.',
    },
    {
        'title': '1984',
        'author': ('Джордж', 'Оруелл'),
        'genres': ['Фантастика'],
        'year': 1949,
        'copies': 3,
        'color': (50, 50, 50),
        'description': 'Антиутопія про тоталітарне суспільство під наглядом Великого Брата.',
    },
]


def make_cover(title, color):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None

    img = Image.new('RGB', (200, 300), color=color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([8, 8, 192, 292], outline=(255, 255, 255), width=3)

    words = title.split()
    y = 130
    for word in words:
        w = len(word) * 9
        draw.text(((200 - w) // 2, y), word, fill=(255, 255, 255))
        y += 24

    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=90)
    buf.seek(0)
    return buf.read()


class Command(BaseCommand):
    help = 'Seed database with demo data'

    def handle(self, *args, **kwargs):
        self._create_genres()
        self._create_authors()
        self._create_books()
        librarian = self._create_librarian()
        reader = self._create_reader()
        self._create_loans(reader, librarian)
        self.stdout.write(self.style.SUCCESS('\nДані успішно створені!'))
        self.stdout.write('  Бібліотекар: librarian1 / lib12345')
        self.stdout.write('  Читач: reader1 / reader123')

    def _create_genres(self):
        names = ['Жахи', 'Фантастика', 'Детектив', 'Пригоди', 'Роман']
        for name in names:
            slug = slugify(name, allow_unicode=True) or name.lower().replace(' ', '-')
            Genre.objects.get_or_create(name=name, defaults={'slug': slug})
        self.stdout.write('  Жанри створено')

    def _create_authors(self):
        pairs = [
            ('Стівен', 'Кінг'),
            ('Дж.Р.Р.', 'Толкієн'),
            ('Артур Конан', 'Дойл'),
            ('Агата', 'Крісті'),
            ('Джордж', 'Оруелл'),
        ]
        for first, last in pairs:
            Author.objects.get_or_create(first_name=first, last_name=last)
        self.stdout.write('  Авторів створено')

    def _create_books(self):
        for data in BOOKS:
            book, created = Book.objects.get_or_create(
                title=data['title'],
                defaults={
                    'year_published': data['year'],
                    'copies_total': data['copies'],
                    'copies_available': data['copies'],
                    'description': data['description'],
                },
            )
            if created:
                first, last = data['author']
                author = Author.objects.get(first_name=first, last_name=last)
                book.authors.add(author)
                for gname in data['genres']:
                    genre = Genre.objects.filter(name=gname).first()
                    if genre:
                        book.genres.add(genre)

                cover_bytes = make_cover(data['title'], data['color'])
                if cover_bytes:
                    fname = data['title'].lower().replace(' ', '_') + '.jpg'
                    book.cover.save(fname, ContentFile(cover_bytes), save=True)
                else:
                    book.save()
        self.stdout.write('  Книги створено')

    def _create_librarian(self):
        user, created = User.objects.get_or_create(
            username='librarian1',
            defaults={
                'first_name': 'Марія',
                'last_name': 'Коваленко',
                'email': 'librarian@example.com',
                'is_staff': True,
            },
        )
        if created:
            user.set_password('lib12345')
            user.save()

        ct = ContentType.objects.get_for_model(Reader)
        for codename in ('can_manage_readers', 'can_view_all_loans'):
            perm = Permission.objects.filter(content_type=ct, codename=codename).first()
            if perm:
                user.user_permissions.add(perm)

        self.stdout.write('  Бібліотекаря створено')
        return user

    def _create_reader(self):
        user, created = User.objects.get_or_create(
            username='reader1',
            defaults={
                'first_name': 'Іван',
                'last_name': 'Петренко',
                'email': 'ivan@example.com',
            },
        )
        if created:
            user.set_password('reader123')
            user.save()

        reader, _ = Reader.objects.get_or_create(
            user=user,
            defaults={
                'phone': '+380501234567',
                'address': 'м. Київ, вул. Хрещатик, 1',
                'date_of_birth': date(1995, 3, 15),
            },
        )
        self.stdout.write('  Читача створено')
        return reader

    def _create_loans(self, reader, librarian):

        today = date.today()

        books = list(Book.objects.all())
        if len(books) < 3:
            self.stdout.write(self.style.WARNING('  Недостатньо книг для позик'))
            return

        # Active loan (in time)
        b0 = books[0]
        if not Loan.objects.filter(reader=reader, book=b0, status='active').exists():
            Loan.objects.create(
                book=b0, reader=reader, issued_by=librarian,
                loan_date=today - timedelta(days=5),
                due_date=today + timedelta(days=9),
                status=Loan.STATUS_ACTIVE,
            )
            b0.copies_available = max(0, b0.copies_available - 1)
            b0.save()

        # Returned loan (on time)
        b1 = books[1]
        if not Loan.objects.filter(reader=reader, book=b1, status='returned').exists():
            Loan.objects.create(
                book=b1, reader=reader, issued_by=librarian,
                loan_date=today - timedelta(days=25),
                due_date=today - timedelta(days=11),
                return_date=today - timedelta(days=13),
                status=Loan.STATUS_RETURNED,
            )

        # Overdue loan with fine
        b2 = books[2]
        if not Loan.objects.filter(reader=reader, book=b2, status='active').exists():
            loan = Loan.objects.create(
                book=b2, reader=reader, issued_by=librarian,
                loan_date=today - timedelta(days=30),
                due_date=today - timedelta(days=16),
                status=Loan.STATUS_ACTIVE,
            )
            b2.copies_available = max(0, b2.copies_available - 1)
            b2.save()
            days_overdue = 16
            Fine.objects.get_or_create(
                loan=loan,
                defaults={'amount': days_overdue * 5, 'is_paid': False},
            )

        self.stdout.write('  Позики та штраф створено')
