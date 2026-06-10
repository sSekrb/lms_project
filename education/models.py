from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField('Название курса', max_length=200)
    description = models.TextField('Описание')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
    
    def __str__(self):
        return self.title

class Lesson(models.Model):
    LESSON_TYPES = (
        ('text', 'Текстовый урок'),
        ('video', 'Видеоурок'),
        ('quiz', 'Тест'),
        ('task', 'Практическое задание'),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField('Название урока', max_length=200)
    content = models.TextField('Содержание урока', blank=True)
    lesson_type = models.CharField('Тип урока', max_length=20, choices=LESSON_TYPES, default='text')
    video_url = models.URLField('Ссылка на видео', blank=True, null=True)
    task_description = models.TextField('Описание задания', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class TaskSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_submissions')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='submissions')
    text_answer = models.TextField('Текстовый ответ', blank=True, null=True)
    file_upload = models.FileField('Загруженный файл', upload_to='submissions/', blank=True, null=True)
    grade = models.IntegerField('Оценка', null=True, blank=True)
    feedback = models.TextField('Комментарий учителя', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Отправка задания'
        verbose_name_plural = 'Отправки заданий'
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField('Пройдено', default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Прогресс'
        verbose_name_plural = 'Прогресс'
        unique_together = ['user', 'lesson']
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"
    
class Achievement(models.Model):
    name = models.CharField('Название достижения', max_length=100)
    description = models.TextField('Описание')
    icon = models.CharField('Иконка', max_length=10, default='🏆')
    
    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'
    
    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField('Получено', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Достижение пользователя'
        verbose_name_plural = 'Достижения пользователей'
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"
    
class UserProfile(models.Model):
    USER_ROLES = (
        ('student', 'Ученик'),
        ('teacher', 'Учитель'),
        ('admin', 'Администратор'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField('Роль', max_length=20, choices=USER_ROLES, default='student')
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Test(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='test')
    title = models.CharField('Название теста', max_length=200)
    
    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'
    
    def __str__(self):
        return self.title

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField('Вопрос')
    
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
    
    def __str__(self):
        return self.text[:50]

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Ответ', max_length=200)
    is_correct = models.BooleanField('Правильный', default=False)
    
    def __str__(self):
        return self.text
    
class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.IntegerField('Результат', default=0)
    max_score = models.IntegerField('Максимум', default=0)
    passed = models.BooleanField('Тест пройден', default=False)
    completed_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField('Попытки', default=3)
    
    def __str__(self):
        return f"{self.user.username} - {self.test.title} - {self.score}/{self.max_score}"
    
class Group(models.Model):
    name = models.CharField('Название группы', max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher_groups')
    students = models.ManyToManyField(User, related_name='student_groups', limit_choices_to={'userprofile__role': 'student'})
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
    
    def __str__(self):
        return self.name
    
class GroupTask(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='tasks')
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    deadline = models.DateTimeField('Срок сдачи', null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Групповое задание'
        verbose_name_plural = 'Групповые задания'

    def __str__(self):
        if self.course_id:
            return f"{self.group.name} - {self.course.title}"
        return f"{self.group.name} - Задание {self.id}"
    
class GroupTaskResult(models.Model):
    group_task = models.ForeignKey(GroupTask, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'userprofile__role': 'student'})
    score = models.IntegerField('Баллы', null=True, blank=True)
    max_score = models.IntegerField('Максимум', null=True, blank=True)
    status = models.CharField('Статус', max_length=20, default='pending')
    submitted_at = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField('Комментарий учителя', blank=True)
    
    class Meta:
        verbose_name = 'Результат группового задания'
        verbose_name_plural = 'Результаты групповых заданий'
        unique_together = ['group_task', 'student']
    
    def __str__(self):
        return f"{self.student.username} - {self.group_task.lesson.title}"
    
class StudentTask(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'student'})
    group_task = models.ForeignKey(GroupTask, on_delete=models.CASCADE)
    status = models.CharField('Статус', max_length=20, default='pending')  # pending, completed, overdue
    score = models.IntegerField('Оценка', null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Задание ученика'
        verbose_name_plural = 'Задания учеников'
        unique_together = ['student', 'group_task']

    def __str__(self):
        return f"{self.student.username} - {self.group_task.lesson.title}"