from django.db import models
from polls.models import Question

class PollStatistic(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='statistic')
    total_votes = models.IntegerField(default=0)
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Статистика опроса'
        verbose_name_plural = 'Статистики опросов'