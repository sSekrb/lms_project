from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Lesson

class RussianUserCreationForm(UserCreationForm):
    username = forms.CharField(label='Имя пользователя', max_length=150)
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем английские подсказки
        self.fields['username'].help_text = 'Обязательное поле. Не более 150 символов.'
        self.fields['password1'].help_text = 'Ваш пароль должен быть не менее 8 символов.'
        self.fields['password2'].help_text = 'Введите тот же пароль для подтверждения.'

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'lesson_type', 'video_url', 'task_description']
        labels = {
            'title': 'Название урока',
            'content': 'Содержание',
            'lesson_type': 'Тип урока',
            'video_url': 'Ссылка на видео',
            'task_description': 'Описание задания',
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }