import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_core.settings')
django.setup()

from django.contrib.auth.models import User
from education.models import (
    Course, Lesson, Progress, Achievement, UserAchievement,
    Test, Question, Answer, TestResult, Group, GroupTask, StudentTask,
    UserProfile
)

print("Заполнение базы данных...")

# 1. Создаём пользователей
users = {}
for name in ['admin', 'teacher', 'student1', 'student2', 'student3']:
    if name == 'admin':
        user, _ = User.objects.get_or_create(username=name, defaults={'email': f'{name}@example.com'})
        user.set_password('admin123')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'admin'})
    elif name == 'teacher':
        user, _ = User.objects.get_or_create(username=name, defaults={'email': f'{name}@example.com'})
        user.set_password('teacher123')
        user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'teacher'})
    else:
        user, _ = User.objects.get_or_create(username=name, defaults={'email': f'{name}@example.com'})
        user.set_password('student123')
        user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'student'})
    users[name] = user
    print(f"  Создан пользователь: {name}")

# 2. Создаём курсы
courses = {}
course_data = [
    ('Математика 5 класс', 'Основы математики: дроби, проценты, уравнения'),
    ('Русский язык 5 класс', 'Орфография, пунктуация, развитие речи'),
    ('Основы программирования', 'Введение в Python: переменные, условия, циклы'),
]

for title, desc in course_data:
    course, _ = Course.objects.get_or_create(title=title, defaults={'description': desc})
    courses[title] = course
    print(f"  Создан курс: {title}")

# 3. Создаём уроки
lessons_data = [
    ('Математика 5 класс', 'Что такое дроби?', 'text', 'Дробь — это часть целого. 1/2 — половина.'),
    ('Математика 5 класс', 'Сложение дробей', 'quiz', 'Правила сложения дробей с одинаковыми знаменателями.'),
    ('Математика 5 класс', 'Решение задач', 'task', 'Решите 3 задачи на дроби и пришлите решение.'),
    ('Русский язык 5 класс', 'Имя существительное', 'text', 'Часть речи, которая обозначает предмет.'),
    ('Русский язык 5 класс', 'Падежи', 'quiz', 'Тест на знание падежей русского языка.'),
    ('Основы программирования', 'Переменные', 'video', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
    ('Основы программирования', 'Условный оператор if', 'task', 'Напишите программу с if-else'),
]

for course_title, title, ltype, content in lessons_data:
    course = courses[course_title]
    lesson, _ = Lesson.objects.get_or_create(
        course=course, title=title,
        defaults={'content': content, 'lesson_type': ltype}
    )
    print(f"  Создан урок: {title}")

# 4. Создаём тесты (для уроков с типом quiz)
math_quiz = Lesson.objects.filter(course=courses['Математика 5 класс'], lesson_type='quiz').first()
if math_quiz:
    test, _ = Test.objects.get_or_create(lesson=math_quiz, defaults={'title': 'Тест по дробям'})
    questions_data = [
        ('Что такое дробь 3/5?', [('3 части из 5', True), ('5 частей из 3', False)]),
        ('Сколько будет 1/4 + 2/4?', [('3/4', True), ('3/8', False), ('1/2', False)]),
    ]
    for q_text, answers in questions_data:
        q, _ = Question.objects.get_or_create(test=test, defaults={'text': q_text})
        for a_text, is_correct in answers:
            Answer.objects.get_or_create(question=q, defaults={'text': a_text, 'is_correct': is_correct})
    print(f"  Создан тест: {test.title}")

# 5. Создаём достижения
achievements_data = [
    ('Первый шаг', 'Пройден первый урок', '🚀'),
    ('Усердный ученик', 'Пройдено 5 уроков', '⭐'),
    ('Знаток дробей', 'Пройден курс математики', '🧮'),
]
for name, desc, icon in achievements_data:
    Achievement.objects.get_or_create(name=name, defaults={'description': desc, 'icon': icon})
    print(f"  Создано достижение: {name}")

# 6. Создаём группу и выдаём курс
teacher = users['teacher']
group, _ = Group.objects.get_or_create(
    name='5А класс',
    defaults={'teacher': teacher}
)
for name in ['student1', 'student2', 'student3']:
    group.students.add(users[name])

# Выдаём курс группе
course_to_assign = courses['Математика 5 класс']
group_task, _ = GroupTask.objects.get_or_create(
    group=group,
    course=course_to_assign,
    defaults={'deadline': datetime.now() + timedelta(days=7)}
)
for student in group.students.all():
    StudentTask.objects.get_or_create(
        student=student,
        group_task=group_task,
        defaults={'status': 'pending'}
    )
print(f"  Курс '{course_to_assign.title}' выдан группе '{group.name}'")

print("\n✅ База данных успешно заполнена!")
print("\nЛогины и пароли:")
print("  Админ: admin / admin123")
print("  Учитель: teacher / teacher123")
print("  Ученики: student1, student2, student3 / student123")