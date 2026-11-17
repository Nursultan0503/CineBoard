from django.contrib.auth.models import User
from django.db import models


# МНОГИЕ КО МНОГИМ: у фильма много жанров, у жанра много фильмов
class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Жанр")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ['name']


class Movie(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    poster = models.ImageField(upload_to='posters/', blank=True, null=True, verbose_name="Постер")
    director = models.CharField(max_length=100, verbose_name="Режиссёр")
    year = models.PositiveIntegerField(verbose_name="Год выпуска")
    duration = models.PositiveIntegerField(verbose_name="Длительность (мин.)")
    country = models.CharField(max_length=100, verbose_name="Страна")
    genres = models.ManyToManyField(Genre, related_name='movies', verbose_name="Жанры")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")

    def __str__(self):
        return f"{self.title} ({self.year})"

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"
        ordering = ['-created_at']


# ОДИН КО МНОГИМ: у фильма много комментариев
class Comment(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='comments', verbose_name="Фильм")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name="Автор")
    text = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    def __str__(self):
        return f"{self.author.username}: {self.movie.title}"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-created_at']


# ОДИН К ОДНОМУ: один человек может забронировать только одно VIP-место
class VipBooking(models.Model):
    SEATS = [(f'VIP-{i}', f'VIP-{i}') for i in range(1, 11)]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vip_booking', verbose_name="Пользователь")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='vip_bookings', verbose_name="Фильм")
    seat = models.CharField(max_length=10, choices=SEATS, verbose_name="VIP-место")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата брони")

    def __str__(self):
        return f"{self.user.username} — {self.movie.title}, {self.seat}"

    class Meta:
        verbose_name = "VIP-бронь"
        verbose_name_plural = "VIP-брони"
        # одно место на один фильм может занять только один человек
        constraints = [
            models.UniqueConstraint(fields=['movie', 'seat'], name='unique_seat_per_movie'),
        ]
