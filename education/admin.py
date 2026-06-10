from django.contrib import admin
from .models import Course, Lesson, Progress
from .models import UserProfile
from .models import Test, Question, Answer
from .models import TaskSubmission
from .models import Achievement, UserAchievement
from .models import Group, GroupTask, GroupTaskResult

# Настройка заголовков админки
admin.site.site_header = "Умный школьник - Администрирование"
admin.site.site_title = "Умный школьник"
admin.site.index_title = "Панель управления"

@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'grade', 'submitted_at']
    list_filter = ['lesson', 'grade']
    
    class Meta:
        verbose_name = 'Отправка задания'
        verbose_name_plural = 'Отправки заданий'

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course']
    list_filter = ['course']
    
    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

admin.site.register(Progress)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']
    
    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'

admin.site.register(UserAchievement)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2
    verbose_name = 'Ответ'
    verbose_name_plural = 'Ответы'

class QuestionInline(admin.TabularInline):
    model = Question
    inlines = [AnswerInline]
    extra = 1
    verbose_name = 'Вопрос'
    verbose_name_plural = 'Вопросы'

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson']
    
    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'
    
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'created_at']
    filter_horizontal = ['students']
    list_filter = ['teacher']

@admin.register(GroupTask)
class GroupTaskAdmin(admin.ModelAdmin):
    list_display = ['group', 'course', 'deadline', 'assigned_at']
    list_filter = ['group']
    
@admin.register(GroupTaskResult)
class GroupTaskResultAdmin(admin.ModelAdmin):
    list_display = ['group_task', 'student', 'score', 'status']
    list_filter = ['status']
