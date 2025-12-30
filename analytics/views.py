from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
import matplotlib.pyplot as plt
import io
import base64
import json

from polls.models import Question, Choice
from .serializers import PollStatSerializer, PollSearchSerializer

class PollStatsAPIView(APIView):
    """
    Микросервис 1: Статистика по конкретному голосованию
    GET /analytics/api/polls/<question_id>/stats/
    """
    def get(self, request, question_id):
        question = get_object_or_404(Question, id=question_id)
        choices = question.choice_set.all()
        
        # Рассчитываем общее количество голосов
        total_votes = choices.aggregate(total=Sum('votes'))['total'] or 0
        
        # Подготавливаем данные по вариантам ответов
        choices_data = []
        for choice in choices:
            percentage = 0
            if total_votes > 0:
                percentage = round((choice.votes / total_votes) * 100, 2)
            
            choices_data.append({
                'choice_text': choice.choice_text,
                'votes': choice.votes,
                'percentage': percentage
            })
        
        # Сортируем по количеству голосов (по убыванию)
        choices_data.sort(key=lambda x: x['votes'], reverse=True)
        
        data = {
            'question_id': question.id,
            'question_text': question.question_text,
            'total_votes': total_votes,
            'choices': choices_data,
            'pub_date': question.pub_date
        }
        
        serializer = PollStatSerializer(data)
        return Response(serializer.data)

class PollChartAPIView(APIView):
    """
    Микросервис 2: Диаграмма результатов голосования
    GET /analytics/api/polls/<question_id>/chart/
    Возвращает base64 encoded PNG изображение
    """
    def get(self, request, question_id):
        question = get_object_or_404(Question, id=question_id)
        choices = question.choice_set.all().order_by('-votes')
        
        # Данные для диаграммы
        labels = [choice.choice_text for choice in choices]
        votes = [choice.votes for choice in choices]
        
        # Создаем диаграмму
        plt.figure(figsize=(10, 6))
        bars = plt.bar(labels, votes, color=['#4CAF50', '#2196F3', '#FF9800', '#F44336'])
        
        # Добавляем значения на столбцы
        for bar, vote in zip(bars, votes):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    str(vote), ha='center', va='bottom')
        
        plt.xlabel('Варианты ответов')
        plt.ylabel('Количество голосов')
        plt.title(f'Результаты опроса: {question.question_text[:50]}...')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Сохраняем в буфер
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        plt.close()
        
        # Кодируем в base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        
        return Response({
            'question_id': question.id,
            'question_text': question.question_text,
            'chart': f'data:image/png;base64,{image_base64}',
            'chart_type': 'bar'
        })

class PollSearchAPIView(APIView):
    """
    API для поиска и фильтрации голосований
    GET /analytics/api/polls/search/?date_from=...&date_to=...&sort_by=...
    """
    def get(self, request):
        queryset = Question.objects.all()
        
        # Фильтрация по дате
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(pub_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(pub_date__lte=date_to)
        
        # Сортировка
        sort_by = request.query_params.get('sort_by', 'recent')
        
        # Добавляем аннотацию для total_votes всегда
        queryset = queryset.annotate(
            total_votes_sum=Sum('choice__votes')
        )
        
        if sort_by == 'popularity':
            queryset = queryset.order_by('-total_votes_sum')
        elif sort_by == 'recent':
            queryset = queryset.order_by('-pub_date')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('pub_date')
        
        # Используем кастомный сериализатор
        data = []
        for question in queryset:
            votes = question.total_votes_sum or 0
            data.append({
                'id': question.id,
                'question_text': question.question_text,
                'pub_date': question.pub_date,
                'total_votes': votes
            })
        
        return Response(data)

class OverallStatsAPIView(APIView):
    """
    Общая статистика по всем голосованиям
    GET /analytics/api/stats/overall/
    """
    def get(self, request):
        total_polls = Question.objects.count()
        total_votes = Choice.objects.aggregate(total=Sum('votes'))['total'] or 0
        
        # Самые популярные опросы
        popular_polls = Question.objects.annotate(
            total_votes=Sum('choice__votes')
        ).order_by('-total_votes')[:5]
        
        # Активные опросы (за последние 7 дней)
        week_ago = timezone.now() - timedelta(days=7)
        recent_polls = Question.objects.filter(pub_date__gte=week_ago).count()
        
        return Response({
            'total_polls': total_polls,
            'total_votes': total_votes,
            'recent_polls': recent_polls,
            'popular_polls': [
                {
                    'id': poll.id,
                    'question_text': poll.question_text,
                    'total_votes': poll.total_votes
                } for poll in popular_polls
            ]
        })