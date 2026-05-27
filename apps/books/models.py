from django.db import models
from django.utils.text import slugify


class Author(models.Model):
    first_name = models.CharField('Ім\'я', max_length=100)
    last_name = models.CharField('Прізвище', max_length=100)
    bio = models.TextField('Біографія', blank=True)
    photo = models.ImageField('Фото', upload_to='authors/', blank=True, null=True)

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Автори'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class Genre(models.Model):
    name = models.CharField('Назва', max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанри'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Book(models.Model):
    title = models.CharField('Назва', max_length=300)
    authors = models.ManyToManyField(Author, verbose_name='Автори', related_name='books')
    genres = models.ManyToManyField(Genre, verbose_name='Жанри', related_name='books', blank=True)
    isbn = models.CharField('ISBN', max_length=20, unique=True, blank=True, null=True, default=None)
    publisher = models.CharField('Видавництво', max_length=200, blank=True)
    year_published = models.PositiveIntegerField('Рік видання', null=True, blank=True)
    description = models.TextField('Опис', blank=True)
    cover = models.ImageField('Обкладинка', upload_to='covers/', blank=True, null=True)
    copies_total = models.PositiveIntegerField('Загальна кількість примірників', default=1)
    copies_available = models.PositiveIntegerField('Доступно примірників', default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        return self.copies_available > 0

    @property
    def authors_display(self):
        return ', '.join(str(a) for a in self.authors.all())
