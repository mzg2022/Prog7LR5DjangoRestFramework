from django.contrib import admin
from django.utils import timezone
import datetime
from .models import Choice, Question
from .admin_filters import TodayFilter, HasChoicesFilter

# Встроенное отображение Choice внутри Question
class ChoiceInline(admin.TabularInline):
    """
    TabularInline отображает варианты ответов в табличном формате.
    Более компактно, чем StackedInline.
    """
    model = Choice
    extra = 3  # Количество пустых форм для новых вариантов
    fields = ['choice_text', 'votes']  # Поля, которые отображаются
    classes = ['collapse']  # Возможность свернуть/развернуть


# Класс для настройки отображения Question в админке
class QuestionAdmin(admin.ModelAdmin):
    """
    Настройки админ-панели для модели Question.
    """
    # Поля, отображаемые в форме редактирования
    fieldsets = [
        (None, {
            'fields': ['question_text'],
            'description': 'Введите текст вопроса'
        }),
        ('Информация о дате', {
            'fields': ['pub_date'],
            'classes': ['collapse'],  # Можно свернуть
            'description': 'Дата публикации вопроса'
        }),
    ]
    
    # Встроенные объекты (Choice отображаются внутри Question)
    inlines = [ChoiceInline]
    
    # Поля, отображаемые в списке вопросов
    list_display = ['question_text', 'pub_date', 'was_published_recently']
    
    # Фильтры в правой панели
    list_filter = [TodayFilter, HasChoicesFilter,'pub_date']
    
    # Поля для поиска
    search_fields = ['question_text']
    
    # Количество объектов на странице
    list_per_page = 20
    
    # Порядок сортировки по умолчанию
    ordering = ['-pub_date']
    
    # Поля только для чтения (при редактировании)
    readonly_fields = ['was_published_recently']
    
    # Дата-иерархия (навигация по датам)
    date_hierarchy = 'pub_date'


# Регистрируем модели с кастомными настройками
admin.site.register(Question, QuestionAdmin)
# Модель Choice не регистрируем отдельно, она встроена в Question