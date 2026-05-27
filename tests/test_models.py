import pytest
from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from apps.books.models import Author, Genre, Book
from apps.readers.models import Reader
from apps.loans.models import Loan, Fine


@pytest.fixture
def author(db):
    return Author.objects.create(first_name='Тарас', last_name='Шевченко')


@pytest.fixture
def genre(db):
    return Genre.objects.create(name='Поезія', slug='poetry')


@pytest.fixture
def book(db, author, genre):
    b = Book.objects.create(
        title='Кобзар',
        isbn='978-966-00-0123-4',
        copies_total=3,
        copies_available=3,
    )
    b.authors.add(author)
    b.genres.add(genre)
    return b


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        first_name='Іван',
        last_name='Петренко',
    )


@pytest.fixture
def reader(db, user):
    return Reader.objects.create(user=user)


@pytest.fixture
def loan(db, book, reader, user):
    return Loan.objects.create(
        book=book,
        reader=reader,
        issued_by=user,
        due_date=date.today() + timedelta(days=14),
    )


class TestAuthorModel:
    def test_str(self, author):
        assert str(author) == 'Шевченко Тарас'

    def test_full_name(self, author):
        assert author.full_name == 'Тарас Шевченко'


class TestGenreModel:
    def test_str(self, genre):
        assert str(genre) == 'Поезія'

    def test_slug_auto_generated(self, db):
        g = Genre.objects.create(name='Фантастика')
        assert g.slug != ''


class TestBookModel:
    def test_str(self, book):
        assert str(book) == 'Кобзар'

    def test_is_available(self, book):
        assert book.is_available is True

    def test_not_available_when_zero_copies(self, book):
        book.copies_available = 0
        book.save()
        assert book.is_available is False

    def test_authors_display(self, book, author):
        assert 'Шевченко' in book.authors_display


class TestReaderModel:
    def test_library_card_auto_generated(self, reader):
        assert reader.library_card_number.startswith('LIB-')
        assert len(reader.library_card_number) == 12

    def test_full_name(self, reader):
        assert reader.full_name == 'Іван Петренко'

    def test_unpaid_fines_zero_by_default(self, reader):
        assert reader.unpaid_fines_total == 0


class TestLoanModel:
    def test_str(self, loan):
        assert 'Кобзар' in str(loan)

    def test_not_overdue_for_fresh_loan(self, loan):
        assert loan.is_overdue is False

    def test_overdue_for_past_due(self, loan):
        loan.due_date = date.today() - timedelta(days=3)
        loan.save()
        assert loan.is_overdue is True

    def test_overdue_days(self, loan):
        loan.due_date = date.today() - timedelta(days=5)
        loan.save()
        assert loan.overdue_days == 5

    def test_calculate_fine(self, loan, settings):
        settings.FINE_PER_DAY = 5
        loan.due_date = date.today() - timedelta(days=4)
        loan.save()
        assert loan.calculate_fine() == 20

    def test_return_book(self, loan, book):
        initial_copies = book.copies_available
        loan.return_book()
        loan.refresh_from_db()
        book.refresh_from_db()
        assert loan.status == Loan.STATUS_RETURNED
        assert loan.return_date == date.today()
        assert book.copies_available == initial_copies + 1

    def test_return_overdue_creates_fine(self, loan, book, settings):
        settings.FINE_PER_DAY = 5
        loan.due_date = date.today() - timedelta(days=3)
        loan.save()
        loan.return_book()
        assert Fine.objects.filter(loan=loan).exists()
        fine = Fine.objects.get(loan=loan)
        assert fine.amount == 15


class TestFineModel:
    def test_pay(self, loan, book, settings):
        settings.FINE_PER_DAY = 5
        loan.due_date = date.today() - timedelta(days=2)
        loan.save()
        loan.return_book()
        fine = Fine.objects.get(loan=loan)
        fine.pay()
        assert fine.is_paid is True
        assert fine.paid_date == date.today()
