from django.db import models
import datetime
from django.utils import timezone
from django.contrib import admin  # Добавляем импорт

# Модель Вопрос (Question) - хранит вопросы для голосования
class Question(models.Model):
    # Поле для текста вопроса, максимум 200 символов
    question_text = models.CharField(max_length=200)
    
    # Поле для даты публикации с понятным названием 'date published'
    pub_date = models.DateTimeField('date published')
    
    # Метод для красивого отображения объекта
    def __str__(self):
        return self.question_text
    
    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Опубликовано недавно?',
    )
    def was_published_recently(self):
        """
        Проверяет, был ли вопрос опубликован недавно (в течение последних суток).
        Возвращает True только если pub_date находится между сейчас и 24 часа назад.
        """
        now = timezone.now()
        # Вопрос считается недавно опубликованным, если:
        # 1) Дата публикации не в будущем (pub_date <= now)
        # 2) Дата публикации не старше 1 дня (now - 1 день <= pub_date)
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
    @property
    def total_votes(self):
        """Возвращает общее количество голосов для этого вопроса."""
        return sum(choice.votes for choice in self.choice_set.all())
    
    # Метаданные модели
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-pub_date']  # Сортировка по умолчанию

# Модель Вариант ответа (Choice) - связана с Question
class Choice(models.Model):
    # Внешний ключ: каждый Choice относится к одному Question
    # on_delete=models.CASCADE - если удалить вопрос, удалятся все варианты ответа
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    # Текст варианта ответа
    choice_text = models.CharField(max_length=200)
    
    # Количество голосов за этот вариант, по умолчанию 0
    votes = models.IntegerField(default=0)
    
    def __str__(self):
        return self.choice_text
    
    # Метаданные модели
    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'