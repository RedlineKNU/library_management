from django.db import models
from django.contrib.auth.models import User


class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сесія чату'
        verbose_name_plural = 'Сесії чату'
        ordering = ['-updated_at']

    def __str__(self):
        return f'Сесія {self.user.username} від {self.created_at:%d.%m.%Y %H:%M}'


class ChatMessage(models.Model):
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'

    ROLE_CHOICES = [
        (ROLE_USER, 'Користувач'),
        (ROLE_ASSISTANT, 'Асистент'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES)
    content = models.TextField('Зміст')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Повідомлення'
        verbose_name_plural = 'Повідомлення'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.get_role_display()}: {self.content[:50]}'


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
