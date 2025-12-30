# polls/forms.py
from django import forms
from .models import Question, Choice

class PollCreationForm(forms.Form):
    """
    Форма для создания нового опроса.
    Вопрос и варианты ответов в одной текстовой области.
    """
    question_text = forms.CharField(
        label="Текст вопроса",
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите вопрос для опроса'
        })
    )
    
    choices_text = forms.CharField(
        label="Варианты ответов",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Введите каждый вариант ответа с новой строки'
        }),
        help_text="Каждый вариант ответа вводите с новой строки"
    )