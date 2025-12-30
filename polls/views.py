from django.utils import timezone
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from .models import Choice, Question
from django.contrib.auth.decorators import login_required
from .forms import PollCreationForm 
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .auth_forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView

# Общее представление для главной страницы (список вопросов)
class IndexView(generic.ListView):
    template_name = 'polls/index.html'  # Используем наш шаблон
    context_object_name = 'latest_question_list'  # Имя переменной в шаблоне
    
    def get_queryset(self):
        """
        Возвращает последние 5 опубликованных вопросов (исключая будущие).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()  # lte = less than or equal (меньше или равно)
        ).order_by('-pub_date')[:5]

# Общее представление для деталей вопроса
class DetailView(generic.DetailView):
    model = Question  # Указываем модель
    template_name = 'polls/detail.html'  # Используем наш шаблон
    pk_url_kwarg = 'question_id'

    def get_queryset(self):
        """
        Исключает вопросы, которые еще не опубликованы (будущие даты).
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

# Общее представление для результатов
class ResultsView(generic.DetailView):
    model = Question  # Та же модель
    template_name = 'polls/results.html'  # Другой шаблон
    pk_url_kwarg = 'question_id'

    def get_queryset(self):
        """
        Исключает вопросы, которые еще не опубликованы (будущие даты).
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

# Функция для обработки голосования
def vote(request, question_id):
    """
    Обрабатывает голосование за конкретный вариант ответа.
    Увеличивает счетчик голосов и перенаправляет на страницу результатов.
    """
    # Получаем вопрос или 404
    question = get_object_or_404(Question, pk=question_id)
    
    try:
        # Получаем выбранный вариант из POST-данных
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Если вариант не выбран или не существует, показываем форму с ошибкой
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "Вы не выбрали вариант ответа.",
        })
    else:
        # Используем F() для атомарного увеличения счетчика в базе данных
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        # Обновляем объект из базы, чтобы получить актуальное значение
        selected_choice.refresh_from_db()
        
        # Всегда возвращаем HttpResponseRedirect после успешной обработки POST
        # Это предотвращает повторную отправку формы при нажатии кнопки "Назад"
        return HttpResponseRedirect(
            reverse('polls:results', args=(question.id,))
        )
    
@login_required
def create_poll(request):
    """
    Представление для создания нового опроса через форму
    """
    if request.method == 'POST':
        form = PollCreationForm(request.POST)
        if form.is_valid():
            # 1. Создаем вопрос
            question_text = form.cleaned_data['question_text']
            question = Question.objects.create(
                question_text=question_text,
                pub_date=timezone.now()
            )
            
            # 2. Создаем варианты ответов из текстовой области
            choices_text = form.cleaned_data['choices_text']
            choices_list = [choice.strip() for choice in choices_text.split('\n') if choice.strip()]
            
            for choice_text in choices_list:
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    votes=0
                )
            
            # 3. Перенаправляем на страницу с деталями созданного опроса
            return redirect('polls:detail', question_id=question.id)
    else:
        form = PollCreationForm()
    
    return render(request, 'polls/create_poll.html', {'form': form})

# Представление для регистрации
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('polls:index')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

# Классы для входа и выхода (альтернатива функциям)
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = AuthenticationForm
    
    def form_valid(self, form):
        # Дополнительная логика при успешном входе
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    next_page = 'polls:index'

class PollAnalyticsView(TemplateView):
    """Страница поиска и анализа голосований"""
    template_name = 'polls/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем последние опросы для начального отображения
        context['recent_polls'] = Question.objects.order_by('-pub_date')[:10]
        return context