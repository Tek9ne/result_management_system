from django.urls import path
from . import views
from django.conf.urls import handler404

app_name = 'results'

def custom_404(request, exception):
    """Custom 404 error handler."""
    return render(request, 'results/404.html', {
        'timestamp': 'August 02, 2025 05:14 PM CEST'
    }, status=404)

handler404 = custom_404

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change_password/', views.change_password, name='change_password'),
    path('change_password_student/', views.change_password_student, name='change_password_student'),
    path('two_factor_auth/', views.two_factor_auth, name='two_factor_auth'),

    # Home and Dashboard URLs
    path('home/', views.home, name='home'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher_home/', views.teacher_home, name='teacher_home'),
    path('teacher_settings/', views.teacher_settings, name='teacher_settings'),

    # Score Management URLs
    path('upload_scores/', views.upload_scores, name='upload_scores'),
    path('edit_score/<int:score_id>/', views.edit_score, name='edit_score'),
    path('delete_score/<int:score_id>/', views.delete_score, name='delete_score'),
    path('assign_subject/<int:student_id>/<int:subject_id>/', views.assign_subject, name='assign_subject'),

    # Reporting URLs
    path('generate_broadsheet/', views.generate_broadsheet, name='generate_broadsheet'),
    path('view_result/', views.view_result, name='view_result'),

    # Admin Management URLs
    path('add_department/', views.add_department, name='add_department'),
    path('add_teacher/', views.add_teacher, name='add_teacher'),
    path('add_student/', views.add_student, name='add_student'),
    path('remove_subject/<int:subject_id>/', views.remove_subject, name='remove_subject'),
    path('add_class/', views.add_class, name='add_class'),
    path('add_subject/', views.add_subject, name='add_subject'),
    path('add_term/', views.add_term, name='add_term'),
    path('lock_result/', views.lock_result, name='lock_result'),
    path('update_database/', views.update_database, name='update_database'),
    path('add_session/', views.add_session, name='add_session'),
]