import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question

def create_question(question_text, days, **kwargs):
    """
    Создает вопрос с заданным текстом и смещением времени.
    Положительные значения days - будущие даты, отрицательные - прошлые.
    Дополнительные параметры: hours, minutes, seconds.
    """
    time = timezone.now() + datetime.timedelta(days=days, **kwargs)
    return Question.objects.create(question_text=question_text, pub_date=time)


# Тесты для модели Question
class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() возвращает False для вопросов с будущей датой публикации.
        """
        future_question = create_question("Будущий вопрос", days=30)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() возвращает False для вопросов старше 1 дня.
        """
        old_question = create_question("Старый вопрос", days=-1, seconds=-1)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() возвращает True для вопросов, опубликованных в течение последних 24 часов.
        """
        recent_question = create_question("Недавний вопрос", days=0, hours=-23, minutes=-59)
        self.assertIs(recent_question.was_published_recently(), True)


# Тесты для представления IndexView
class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        Если нет вопросов, отображается соответствующее сообщение.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Нет доступных опросов")
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Вопросы с прошлой датой публикации отображаются на странице индекса.
        """
        question = create_question("Прошлый вопрос", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Вопросы с будущей датой публикации не отображаются на странице индекса.
        """
        create_question("Будущий вопрос", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "Нет доступных опросов")
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Даже если есть и прошлые, и будущие вопросы, отображаются только прошлые.
        """
        past_question = create_question("Прошлый вопрос", days=-30)
        create_question("Будущий вопрос", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.context['latest_question_list'],
            [past_question],
        )

    def test_two_past_questions(self):
        """
        На странице индекса могут отображаться несколько вопросов.
        """
        question1 = create_question("Прошлый вопрос 1", days=-30)
        question2 = create_question("Прошлый вопрос 2", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.context['latest_question_list'],
            [question2, question1],  # Более новые первыми
        )


# Тесты для представления DetailView
class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        Детальное представление вопроса с будущей датой публикации возвращает 404.
        """
        future_question = create_question("Будущий вопрос", days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        Детальное представление вопроса с прошлой датой публикации отображает текст вопроса.
        """
        past_question = create_question("Прошлый вопрос", days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)