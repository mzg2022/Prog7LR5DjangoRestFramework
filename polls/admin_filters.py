from django.contrib import admin
from django.utils import timezone
import datetime

# Кастомный фильтр для вопросов, опубликованных сегодня
class TodayFilter(admin.SimpleListFilter):
    title = 'публикация'
    parameter_name = 'pub_date'
    
    def lookups(self, request, model_admin):
        return (
            ('today', 'Сегодня'),
            ('week', 'За неделю'),
            ('month', 'За месяц'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'today':
            today = timezone.now().date()
            return queryset.filter(pub_date__date=today)
        elif self.value() == 'week':
            week_ago = timezone.now() - datetime.timedelta(days=7)
            return queryset.filter(pub_date__gte=week_ago)
        elif self.value() == 'month':
            month_ago = timezone.now() - datetime.timedelta(days=30)
            return queryset.filter(pub_date__gte=month_ago)
        return queryset


# Кастомный фильтр для вопросов с вариантами ответов
class HasChoicesFilter(admin.SimpleListFilter):
    title = 'имеет варианты'
    parameter_name = 'has_choices'
    
    def lookups(self, request, model_admin):
        return (
            ('yes', 'Есть варианты'),
            ('no', 'Нет вариантов'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(choice__isnull=False).distinct()
        elif self.value() == 'no':
            return queryset.filter(choice__isnull=True)
        return queryset