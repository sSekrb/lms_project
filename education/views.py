from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied 
from .models import Course, Lesson, Progress, Achievement, UserAchievement
from .models import Answer, TestResult, TaskSubmission
from .models import Group, GroupTask, GroupTaskResult
from .forms import LessonForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import StudentTask

# Декоратор для проверки роли пользователя
def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            # Проверяем роль через UserProfile
            if hasattr(request.user, 'profile'):
                if request.user.profile.role not in allowed_roles:
                    raise PermissionDenied("Доступ запрещён. Недостаточно прав.")
            else:
                raise PermissionDenied("Профиль пользователя не найден.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

@login_required
@role_required(['teacher', 'admin'])
def teacher_groups(request):
    groups = Group.objects.filter(teacher=request.user)
    return render(request, 'education/teacher/groups.html', {'groups': groups})

@login_required
@role_required(['teacher', 'admin'])
def create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        student_ids = request.POST.getlist('students')
        
        group = Group.objects.create(
            name=name,
            teacher=request.user
        )
        group.students.set(student_ids)
        return redirect('teacher_groups')
    
    students = User.objects.filter(profile__role='student')
    return render(request, 'education/teacher/create_group.html', {'students': students})

@login_required
@role_required(['teacher', 'admin'])
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id, teacher=request.user)
    return render(request, 'education/teacher/group_detail.html', {'group': group})

@login_required
@role_required(['teacher', 'admin'])
def assign_group_task(request, group_id):
    group = get_object_or_404(Group, id=group_id, teacher=request.user)
    
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        deadline = request.POST.get('deadline')
        
        # Создаём групповое задание (теперь это выдача курса)
        group_task = GroupTask.objects.create(
            group=group,
            course_id=course_id,
            deadline=deadline if deadline else None
        )
        
        # Создаём StudentTask для каждого ученика
        for student in group.students.all():
            StudentTask.objects.get_or_create(
                student=student,
                group_task=group_task,
                defaults={'status': 'pending'}
            )
        
        messages.success(request, f'Курс успешно выдан группе "{group.name}"')
        return redirect('teacher_groups')
    
    courses = Course.objects.all()
    return render(request, 'education/teacher/assign_task.html', {
        'group': group,
        'courses': courses
    })

@login_required
@role_required(['student'])
def my_tasks(request):
    student_tasks = StudentTask.objects.filter(student=request.user).select_related('group_task__course')
    
    tasks_data = []
    for st in student_tasks:
        course = st.group_task.course
        lessons_count = course.lessons.count()
        progress = Progress.objects.filter(user=request.user, lesson__course=course, completed=True).count()
        
        is_overdue = False
        if st.group_task.deadline and st.group_task.deadline < timezone.now():
            is_overdue = True
        
        tasks_data.append({
            'student_task': st,
            'course': course,
            'deadline': st.group_task.deadline,
            'status': st.status,
            'lessons_count': lessons_count,
            'progress': progress,
            'is_overdue': is_overdue
        })
    
    return render(request, 'education/student/my_tasks.html', {'tasks': tasks_data})

@login_required
@role_required(['teacher', 'admin'])
def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id, teacher=request.user)
    
    if request.method == 'POST':
        group.name = request.POST.get('name')
        student_ids = request.POST.getlist('students')
        group.students.set(student_ids)
        group.save()
        return redirect('group_detail', group_id=group.id)
    
    students = User.objects.filter(profile__role='student')
    return render(request, 'education/teacher/edit_group.html', {
        'group': group,
        'students': students
    })

@staff_member_required
def teacher_dashboard(request):
    courses = Course.objects.all()
    return render(request, 'education/teacher/dashboard.html', {'courses': courses})

@staff_member_required
def teacher_add_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = LessonForm()
    
    return render(request, 'education/teacher/add_lesson.html', {
        'form': form,
        'course': course
    })

def home(request):
    if request.user.is_authenticated and request.user.profile.role == 'student':
        # Ученик: показываем задания из его групп
        student_groups = request.user.student_groups.all()
        group_tasks = GroupTask.objects.filter(group__in=student_groups).order_by('deadline')
        
        tasks_with_status = []
        for gt in group_tasks:
            if not gt.course:continue 
            # Статус задания для ученика
            student_task = StudentTask.objects.filter(student=request.user, group_task=gt).first()
            status = 'pending'
            if student_task:
                status = student_task.status
            
            # Проверка дедлайна
            is_overdue = gt.deadline and gt.deadline < timezone.now() and status == 'pending'
            
            tasks_with_status.append({
                'group_task': gt,
                'status': status,
                'is_overdue': is_overdue,
                'deadline': gt.deadline,
                'course': gt.course
            })
        
        return render(request, 'education/student/home.html', {
            'tasks': tasks_with_status
        })
    else:
        # Для учителя и гостя: показываем все курсы
        courses = Course.objects.all()
        return render(request, 'education/home.html', {'courses': courses})

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()
    
    # Создаем список уроков с информацией о прогрессе
    lessons_with_progress = []
    for lesson in lessons:
        lesson_data = {
            'lesson': lesson,
            'completed': False
        }
        if request.user.is_authenticated:
            progress = Progress.objects.filter(user=request.user, lesson=lesson).first()
            lesson_data['completed'] = progress.completed if progress else False
        lessons_with_progress.append(lesson_data)
    
    return render(request, 'education/course_detail.html', {
        'course': course,
        'lessons_with_progress': lessons_with_progress
    })
    
    return render(request, 'education/course_detail.html', {
        'course': course,
        'lessons_with_progress': lessons_with_progress
    })

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Получаем последний результат теста ТОЛЬКО если у урока есть тест
    last_result = None
    try:
        if hasattr(lesson, 'test') and lesson.test:
            last_result = TestResult.objects.filter(
                user=request.user, 
                test=lesson.test
            ).order_by('-completed_at').first()
    except:
        last_result = None
    
    # Отмечаем урок как пройденный
    progress, created = Progress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'completed': True}
    )
    
    if not progress.completed:
        progress.completed = True
        progress.save()
        #check_achievements(request.user)
    
    return render(request, 'education/lesson_detail.html', {
        'lesson': lesson,
        'last_result': last_result,
    })

@login_required
def profile(request):
    user = request.user
    
    # Статистика
    completed_lessons = Progress.objects.filter(user=user, completed=True).count()
    total_lessons = Lesson.objects.count()
    
    # Уровень (простая формула: 1 уровень за каждые 3 урока)
    level = (completed_lessons // 3) + 1
    
    # Достижения пользователя
    user_achievements = UserAchievement.objects.filter(user=user).select_related('achievement')
    
    # Все доступные достижения
    all_achievements = Achievement.objects.all()
    
    return render(request, 'education/profile.html', {
        'user': user,
        'level': level,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'user_achievements': user_achievements,
        'all_achievements': all_achievements
    })

#def check_achievements(user):
    """Проверка условий для выдачи достижений"""
    completed_count = Progress.objects.filter(user=user, completed=True).count()
    
    # Достижение "Первый шаг" (1 урок)
    if completed_count >= 1:
        achievement = Achievement.objects.filter(name='Первый шаг').first()
        if achievement:
            UserAchievement.objects.get_or_create(user=user, achievement=achievement)
    
    # Достижение "Усердный ученик" (5 уроков)
    if completed_count >= 5:
        achievement = Achievement.objects.filter(name='Усердный ученик').first()
        if achievement:
            UserAchievement.objects.get_or_create(user=user, achievement=achievement)
    
    # Достижение "Математик" (за курс математики)
    math_course = Course.objects.filter(title__icontains='математик').first()
    if math_course:
        math_lessons = Lesson.objects.filter(course=math_course)
        math_completed = all(
            Progress.objects.filter(user=user, lesson=lesson, completed=True).exists()
            for lesson in math_lessons
        )
        if math_completed and math_lessons.exists():
            achievement = Achievement.objects.filter(name='Математик').first()
            if achievement:
                UserAchievement.objects.get_or_create(user=user, achievement=achievement)

@login_required
def submit_test(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    test = lesson.test
    
    # Получаем или создаём результат
    result, created = TestResult.objects.get_or_create(
        user=request.user,
        test=test,
        defaults={'score': 0, 'max_score': test.questions.count(), 'attempts': 0}
    )
    
    # Проверка на количество попыток (например, максимум 3)
    MAX_ATTEMPTS = 3
    if result.attempts >= MAX_ATTEMPTS:
        messages.error(request, f'Вы исчерпали лимит попыток ({MAX_ATTEMPTS}).')
        return redirect('lesson_detail', lesson_id=lesson.id)
    
    if request.method == 'POST':
        score = 0
        total = test.questions.count()
        
        for question in test.questions.all():
            answer_id = request.POST.get(f'q{question.id}')
            if answer_id:
                try:
                    answer = Answer.objects.get(id=answer_id)
                    if answer.is_correct:
                        score += 1
                except:
                    pass
        
        # Обновляем результат
        result.score = score
        result.max_score = total
        result.passed = score >= (total * 0.7)
        result.attempts += 1
        result.save()
        
        messages.success(request, f'Результат: {score}/{total}. Попытка {result.attempts} из {MAX_ATTEMPTS}')
        
    return redirect('lesson_detail', lesson_id=lesson.id)

def submit_task(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        submission = TaskSubmission.objects.create(
            user=request.user,
            lesson=lesson,
            text_answer=request.POST.get('text_answer', ''),
            file_upload=request.FILES.get('file_upload')
        )
        messages.success(request, 'Задание отправлено на проверку!')
    return redirect('lesson_detail', lesson_id=lesson.id)

