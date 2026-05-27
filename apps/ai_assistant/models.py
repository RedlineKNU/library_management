from django.db import models
from django.contrib.auth.models import User


class BookRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    query = models.TextField('Запит')
    response = models.TextField('Відповідь AI')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Рекомендація книг'
        verbose_name_plural = 'Рекомендації книг'
        ordering = ['-created_at']

    def __str__(self):
        return f'Рекомендації для {self.user.username}: {self.query[:50]}'
