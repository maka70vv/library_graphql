from django.db import models
from django.db.models import Avg

from library_api import settings


class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    biography = models.TextField(verbose_name="Биография")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"


class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    authors = models.ManyToManyField(Author, verbose_name="Авторы")
    publication_year = models.IntegerField(verbose_name="Год издания")
    isbn = models.CharField(max_length=13, verbose_name="ISBN")

    @property
    def average_rating(self):
        return self.ratings.aggregate(Avg('score'))['score__avg'] or 0.0

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"


class Rating(models.Model):
    book = models.ForeignKey(
        Book,
        related_name='ratings',
        on_delete=models.CASCADE,
        verbose_name="Книга"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='ratings',
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    score = models.PositiveIntegerField()
    review = models.TextField()

    class Meta:
        unique_together = ('book', 'user')

    def __str__(self):
        return f"{self.user.email} - {self.book.title} - {self.score}"
