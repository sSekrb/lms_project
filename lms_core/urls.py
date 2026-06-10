from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from education import views
from education.forms import RussianUserCreationForm
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('profile/', views.profile, name='profile'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/add-lesson/<int:course_id>/', views.teacher_add_lesson, name='teacher_add_lesson'),
    path('submit-test/<int:lesson_id>/', views.submit_test, name='submit_test'),
    path('submit-task/<int:lesson_id>/', views.submit_task, name='submit_task'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),

    # Учитель — группы
    path('teacher/groups/', views.teacher_groups, name='teacher_groups'),
    path('teacher/groups/create/', views.create_group, name='create_group'),
    path('teacher/groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('teacher/groups/<int:group_id>/assign/', views.assign_group_task, name='assign_group_task'),
    path('teacher/groups/<int:group_id>/edit/', views.edit_group, name='edit_group'),

    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='education/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', CreateView.as_view(
    template_name='education/register.html',
    form_class=RussianUserCreationForm,
    success_url=reverse_lazy('home')
), name='register'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

