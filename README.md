# Django Polls с микросервисами аналитики

Приложение для голосований с системой аналитики на Django REST Framework.

## Микросервисы:
1. **Статистика** - GET /analytics/api/polls/{id}/stats/
2. **Диаграммы** - GET /analytics/api/polls/{id}/chart/
3. **Поиск** - GET /analytics/api/polls/search/

## Веб-интерфейс:
- Аналитика: /polls/analytics/
- Динамическая загрузка данных
- Визуализация результатов

## Технологии:
- Django 6.0
- Django REST Framework
- Matplotlib для графиков
- JavaScript/AJAX для интерфейса
