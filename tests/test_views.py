import pytest
from datetime import date, timedelta
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from apps.books.models import Author, Genre, Book
from apps.readers.models import Reader
from apps.loans.models import Loan


@pytest.fixture
def user(db):
    return User.objects.create_user(username='viewer', password='pass123')


@pytest.fixture
def reader(db, user):
    return Reader.objects.create(user=user)


@pytest.fixture
def librarian(db):
    u = User.objects.create_user(username='librarian', password='pass123')
    perms = Permission.objects.filter(codename__in=['can_manage_readers', 'can_view_all_loans'])
    u.user_permissions.set(perms)
    return u


@pytest.fixture
def book(db):
    author = Author.objects.create(first_name='Іван', last_name='Франко')
    b = Book.objects.create(title='Захар Беркут', copies_total=2, copies_available=2)
    b.authors.add(author)
    return b


class TestBookViews:
    def test_book_list_accessible_without_login(self, client, book):
        response = client.get(reverse('books:list'))
        assert response.status_code == 200
        assert 'Захар Беркут' in response.content.decode()

    def test_book_list_search(self, client, book):
        response = client.get(reverse('books:list'), {'query': 'Захар'})
        assert response.status_code == 200
        assert 'Захар Беркут' in response.content.decode()

    def test_book_list_search_no_result(self, client, book):
        response = client.get(reverse('books:list'), {'query': 'Ромео і Джульєтта'})
        assert response.status_code == 200
        assert 'Захар Беркут' not in response.content.decode()

    def test_book_detail_requires_login(self, client, book):
        response = client.get(reverse('books:detail', args=[book.pk]))
        assert response.status_code == 302

    def test_book_detail_accessible_when_logged_in(self, client, user, reader, book):
        client.login(username='viewer', password='pass123')
        response = client.get(reverse('books:detail', args=[book.pk]))
        assert response.status_code == 200


class TestReaderViews:
    def test_registration(self, client, db):
        data = {
            'username': 'newuser',
            'first_name': 'Олена',
            'last_name': 'Іваненко',
            'email': 'olena@test.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = client.post(reverse('readers:register'), data)
        assert response.status_code == 302
        assert User.objects.filter(username='newuser').exists()
        assert Reader.objects.filter(user__username='newuser').exists()

    def test_login(self, client, user):
        response = client.post(reverse('readers:login'), {
            'username': 'viewer', 'password': 'pass123'
        })
        assert response.status_code == 302

    def test_profile_requires_login(self, client):
        response = client.get(reverse('readers:profile'))
        assert response.status_code == 302

    def test_profile_accessible(self, client, user, reader):
        client.login(username='viewer', password='pass123')
        response = client.get(reverse('readers:profile'))
        assert response.status_code == 200

    def test_reader_list_requires_permission(self, client, user, reader):
        client.login(username='viewer', password='pass123')
        response = client.get(reverse('readers:list'))
        assert response.status_code == 403

    def test_reader_list_accessible_for_librarian(self, client, librarian):
        client.login(username='librarian', password='pass123')
        response = client.get(reverse('readers:list'))
        assert response.status_code == 200


class TestLoanViews:
    def test_my_loans_requires_login(self, client):
        response = client.get(reverse('loans:my_loans'))
        assert response.status_code == 302

    def test_my_loans_accessible(self, client, user, reader):
        client.login(username='viewer', password='pass123')
        response = client.get(reverse('loans:my_loans'))
        assert response.status_code == 200

    def test_issue_book_requires_permission(self, client, user, reader, book):
        client.login(username='viewer', password='pass123')
        response = client.get(reverse('loans:issue_book', args=[book.pk]))
        assert response.status_code == 403

    def test_issue_book_by_librarian(self, client, librarian, book, db):
        reader_user = User.objects.create_user(username='rdr', password='pass123')
        reader = Reader.objects.create(user=reader_user)
        client.login(username='librarian', password='pass123')
        response = client.post(reverse('loans:issue_book', args=[book.pk]), {
            'reader': reader.pk,
            'due_date': (date.today() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'notes': '',
        })
        assert response.status_code == 302
        assert Loan.objects.filter(book=book, reader=reader).exists()
        book.refresh_from_db()
        assert book.copies_available == 1
