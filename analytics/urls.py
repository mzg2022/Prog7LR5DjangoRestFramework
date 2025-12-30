from django.urls import path
from . import views

urlpatterns = [
    # Статистика по конкретному опросу
    path('api/polls/<int:question_id>/stats/', 
         views.PollStatsAPIView.as_view(), 
         name='poll_stats'),
    
    # Диаграмма по конкретному опросу
    path('api/polls/<int:question_id>/chart/', 
         views.PollChartAPIView.as_view(), 
         name='poll_chart'),
    
    # Поиск и фильтрация опросов
    path('api/polls/search/', 
         views.PollSearchAPIView.as_view(), 
         name='poll_search'),
    
    # Общая статистика
    path('api/stats/overall/', 
         views.OverallStatsAPIView.as_view(), 
         name='overall_stats'),
]