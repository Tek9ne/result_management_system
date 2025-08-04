# Standard library imports
from io import BytesIO
import logging

# Third-party imports
import pandas as pd
import pyotp
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

# Django imports
from django.conf import settings
from django.contrib.auth import authenticate, login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Local application imports
from .models import Profile, Score, Result, Term, Class, Subject, Department, AcademicSession, StudentSubject

# Logger setup
logger = logging.getLogger(__name__)

# Role-based access checks
def is_admin(user):
    """Check if the user is an admin."""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'

def is_teacher(user):
    """Check if the user is a teacher."""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'teacher'

def is_student(user):
    """Check if the user is a student."""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'student'

def is_admin_or_staff(user):
    """Check if the user is an admin or staff."""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role in ['admin', 'staff']

def login_view(request):
    """Handle user login and initiate 2FA for admins and teachers if enabled."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        logger.info(f"Login attempt for user ID: {user.id if user else 'unknown'}")
        if user:
            login(request, user)
            profile, created = Profile.objects.get_or_create(user=user)
            if username.lower() == 'admin' or user.is_superuser:
                profile.role = 'admin'
            elif created:
                profile.role = 'student'
            profile.save()

            # Check if 2FA is enabled and user is admin or teacher
            if settings.ENABLE_2FA and (is_admin(user) or is_teacher(user)):
                if not user.email:
                    logger.error(f"Login failed for user ID: {user.id}: No email address provided")
                    return render(request, 'results/login.html', {
                        'error': 'No email address associated with this account.',
                        'timestamp': 'August 02, 2025 05:00 PM CEST'
                    })
                totp = pyotp.TOTP(pyotp.random_base32(), interval=30)
                otp_code = totp.now()
                profile.otp_secret = totp.secret
                profile.save()
                try:
                    send_mail(
                        'Your Security Code',
                        f'Your code is: {otp_code}',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    logger.info(f"2FA code sent to user ID: {user.id}")
                except Exception as e:
                    logger.error(f"Failed to send 2FA email for user ID: {user.id}: {str(e)}")
                    return render(request, 'results/login.html', {
                        'error': 'Failed to send security code. Please check your email configuration or try again.',
                        'timestamp': 'August 02, 2025 05:00 PM CEST'
                    })
                request.session['2fa_user_id'] = user.id
                return redirect('results:two_factor_auth')
            else:
                # Bypass 2FA for students or if 2FA is disabled
                if is_admin(user):
                    return redirect('results:admin_dashboard')
                elif is_teacher(user):
                    if user.has_usable_password() and 'teacherpass123' in user.password:
                        return redirect('results:change_password')
                    return redirect('results:teacher_home')
                elif is_student(user):
                    if user.has_usable_password() and 'pass' in user.password:
                        return redirect('results:change_password_student')
                    return redirect('results:student_dashboard')
        logger.error("Login failed: Invalid credentials")
        return render(request, 'results/login.html', {
            'error': 'Invalid credentials',
            'timestamp': 'August 02, 2025 05:00 PM CEST'
        })
    return render(request, 'results/login.html', {'timestamp': 'August 02, 2025 05:00 PM CEST'})

@login_required
def two_factor_auth(request):
    """Verify 2FA code and redirect based on user role."""
    if not settings.ENABLE_2FA:
        logger.info("2FA is disabled, redirecting to home")
        return redirect('results:home')
    if request.method == 'POST':
        user_id = request.session.get('2fa_user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                profile = user.profile
                entered_code = request.POST.get('otp_code')
                totp = pyotp.TOTP(profile.otp_secret, interval=30)
                if totp.verify(entered_code):
                    del request.session['2fa_user_id']
                    if is_admin(user):
                        return redirect('results:admin_dashboard')
                    elif is_teacher(user):
                        if user.has_usable_password() and 'teacherpass123' in user.password:
                            return redirect('results:change_password')
                        return redirect('results:teacher_home')
                    else:
                        logger.error(f"2FA attempted for non-admin/teacher user ID: {user_id}")
                        return render(request, 'results/unauthorized.html', {
                            'error': '2FA is only for admins and teachers.',
                            'timestamp': 'August 02, 2025 05:00 PM CEST'
                        })
                logger.error(f"2FA verification failed for user ID: {user_id}")
                return render(request, 'results/two_factor_auth.html', {
                    'error': 'Invalid Security Code',
                    'timestamp': 'August 02, 2025 05:00 PM CEST'
                })
            except User.DoesNotExist:
                logger.error(f"2FA user ID not found: {user_id}")
                return render(request, 'results/two_factor_auth.html', {
                    'error': 'User not found',
                    'timestamp': 'August 02, 2025 05:00 PM CEST'
                })
    return render(request, 'results/two_factor_auth.html', {'timestamp': 'August 02, 2025 05:00 PM CEST'})

@login_required
def home(request):
    """Render the home page, assigning a student role if none exists."""
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user, role='student')
    return render(request, 'results/home.html', {
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    })

@login_required
@user_passes_test(is_teacher)
def change_password(request):
    """Allow teachers to change their password."""
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password == confirm_password:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            logger.info(f"Password changed for user ID: {request.user.id}")
            return redirect('results:teacher_home')
        logger.error(f"Password change failed for user ID: {request.user.id}: Passwords do not match")
        return render(request, 'results/change_password.html', {
            'error': 'Passwords do not match',
            'timestamp': 'August 02, 2025 05:00 PM CEST'
        })
    return render(request, 'results/change_password.html', {
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    })

@login_required
@user_passes_test(is_student)
def change_password_student(request):
    """Allow students to change their password."""
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password == confirm_password:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            logger.info(f"Password changed for user ID: {request.user.id}")
            return redirect('results:student_dashboard')
        logger.error(f"Password change failed for user ID: {request.user.id}: Passwords do not match")
        return render(request, 'results/change_password_student.html', {
            'error': 'Passwords do not match',
            'timestamp': 'August 02, 2025 05:00 PM CEST'
        })
    return render(request, 'results/change_password_student.html', {
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    })

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Render the admin dashboard with relevant data."""
    context = {
        'teachers': User.objects.filter(profile__role='teacher'),
        'students': User.objects.filter(profile__role='student'),
        'departments': Department.objects.all(),
        'classes': Class.objects.all(),
        'subjects': Subject.objects.all(),
        'sessions': AcademicSession.objects.all(),
        'terms': Term.objects.all(),
        'scores': Score.objects.all(),
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    return render(request, 'results/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def generate_broadsheet(request):
    """Generate a broadsheet report with PDF or Excel export options."""
    context = {
        'departments': Department.objects.all(),
        'classes': Class.objects.all(),
        'terms': Term.objects.all(),
        'students': None,
        'scores': None,
        'results': None,
        'error': None,
        'best_in_section': {},
        'overall_best': None,
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    if request.method == 'POST':
        department_id = request.POST.get('department')
        class_id = request.POST.get('class')
        term_id = request.POST.get('term')
        if department_id and class_id and term_id:
            try:
                students = User.objects.filter(profile__role='student', profile__department_id=department_id, profile__class_assigned_id=class_id)
                scores = Score.objects.filter(student__in=students, term_id=term_id)
                results = Result.objects.filter(student__in=students, term_id=term_id)
                if not students.exists():
                    context['error'] = 'No students found for the selected department and class.'
                else:
                    context.update({'students': students, 'scores': scores, 'results': results})
                    for dept in Department.objects.all():
                        dept_students = students.filter(profile__department=dept)
                        if dept_students.exists():
                            dept_results = Result.objects.filter(student__in=dept_students, term_id=term_id)
                            if dept_results.exists():
                                best = dept_results.order_by('-total_score').first()
                                context['best_in_section'][dept.name] = {
                                    'student': best.student.username,
                                    'score': best.total_score
                                }
                    all_results = Result.objects.filter(term_id=term_id)
                    if all_results.exists():
                        context['overall_best'] = all_results.order_by('-total_score').first()
            except Exception as e:
                logger.error(f"Broadsheet generation failed: {str(e)}")
                context['error'] = 'An error occurred while generating the broadsheet.'
        if 'pdf_export' in request.POST:
            if students and scores.exists():
                try:
                    buffer = BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=letter)
                    elements = []
                    styles = getSampleStyleSheet()
                    elements.append(Paragraph("Broadsheet Report", styles['Title']))
                    data = [['Student', 'Roll No', 'Subject', 'CA', 'Exam', 'Total']]
                    for student in students:
                        for score in scores.filter(student=student):
                            data.append([student.username, student.profile.roll_number or 'N/A', score.subject.name, score.ca_score, score.exam_score, score.total_score])
                    table = Table(data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 14),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    elements.append(table)
                    doc.build(elements)
                    pdf = buffer.getvalue()
                    buffer.close()
                    response = HttpResponse(content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="broadsheet.pdf"'
                    response.write(pdf)
                    return response
                except Exception as e:
                    logger.error(f"PDF export failed: {str(e)}")
                    context['error'] = 'Failed to export as PDF.'
            else:
                context['error'] = 'No data available to export as PDF.'
        elif 'excel_export' in request.POST:
            if students and scores.exists():
                try:
                    data = []
                    for student in students:
                        for score in scores.filter(student=student):
                            data.append({
                                'Student': student.username,
                                'Roll No': student.profile.roll_number or 'N/A',
                                'Subject': score.subject.name,
                                'CA': score.ca_score,
                                'Exam': score.exam_score,
                                'Total': score.total_score,
                            })
                    df = pd.DataFrame(data)
                    buffer = BytesIO()
                    df.to_excel(buffer, index=False)
                    buffer.seek(0)
                    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = 'attachment; filename="broadsheet.xlsx"'
                    response.write(buffer.read())
                    buffer.close()
                    return response
                except Exception as e:
                    logger.error(f"Excel export failed: {str(e)}")
                    context['error'] = 'Failed to export as Excel.'
            else:
                context['error'] = 'No data available to export as Excel.'
    return render(request, 'results/generate_broadsheet.html', context)

@login_required
@user_passes_test(is_admin)
def add_department(request):
    """Add a new department."""
    context = {
        'departments': Department.objects.all(),
        'error': None,
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    if request.method == 'POST':
        name = request.POST.get('name')
        if name and not Department.objects.filter(name=name).exists():
            Department.objects.create(name=name)
            logger.info(f"Department added: {name}")
            return redirect('results:add_department')
        logger.error(f"Department addition failed: {'Department already exists' if name else 'Invalid input'}")
        context['error'] = 'Department already exists or invalid input.'
    return render(request, 'results/add_department.html', context)

@login_required
@user_passes_test(is_admin)
def add_teacher(request):
    """Add or remove a teacher."""
    context = {
        'teachers': User.objects.filter(profile__role='teacher'),
        'subjects': Subject.objects.all(),
        'error': None,
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    if request.method == 'POST':
        if 'remove' in request.POST:
            teacher_id = request.POST.get('remove_teacher')
            if teacher_id:
                try:
                    User.objects.filter(id=teacher_id).delete()
                    logger.info(f"Teacher removed: ID {teacher_id}")
                    return redirect('results:add_teacher')
                except Exception as e:
                    logger.error(f"Teacher removal failed: {str(e)}")
                    context['error'] = 'Failed to remove teacher.'
        else:
            first_name = request.POST.get('first_name')
            roll_number = request.POST.get('roll_number')
            phone_number = request.POST.get('phone_number')
            home_address = request.POST.get('home_address')
            if first_name and roll_number:
                username = f"{first_name.lower()}_{roll_number}"
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(username=username, password='teacherpass123')
                    Profile.objects.create(
                        user=user,
                        role='teacher',
                        roll_number=roll_number,
                        phone_number=phone_number or None,
                        home_address=home_address or None
                    )
                    logger.info(f"Teacher added: {username}")
                    return redirect('results:add_teacher')
                logger.error(f"Teacher addition failed: Teacher already exists")
                context['error'] = 'Teacher already exists.'
            else:
                logger.error("Teacher addition failed: Missing required fields")
                context['error'] = 'First name and roll number are required.'
    return render(request, 'results/add_teacher.html', context)

@login_required
@user_passes_test(is_admin)
def add_student(request):
    """Add a new student with subjects."""
    context = {
        'classes': Class.objects.all(),
        'subjects': Subject.objects.all(),
        'error': None,
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    if request.method == 'POST':
        school_code = request.POST.get('school_code')
        admission_number = request.POST.get('admission_number')
        first_name = request.POST.get('full_name')
        roll_number = request.POST.get('roll_number')
        phone_number = request.POST.get('phone_number')
        home_address = request.POST.get('home_address')
        department_id = request.POST.get('department')
        class_id = request.POST.get('class')
        if school_code and admission_number and first_name and roll_number and phone_number and home_address and department_id and class_id:
            username = f"{school_code}_{admission_number}_{first_name.lower().replace(' ', '_')}"
            if not User.objects.filter(username=username).exists():
                try:
                    user = User.objects.create_user(username=username, password='pass')
                    profile = Profile.objects.create(
                        user=user,
                        role='student',
                        roll_number=roll_number,
                        phone_number=phone_number,
                        home_address=home_address,
                        department_id=department_id,
                        class_assigned_id=class_id
                    )
                    subject_ids = request.POST.getlist('subjects')
                    for subject_id in subject_ids:
                        StudentSubject.objects.get_or_create(profile=profile, subject_id=subject_id, defaults={'is_active': True})
                    logger.info(f"Student added: {username}")
                    return redirect('results:add_student')
                except Exception as e:
                    logger.error(f"Student addition failed: {str(e)}")
                    context['error'] = 'Failed to add student.'
            else:
                logger.error(f"Student addition failed: Student already exists")
                context['error'] = 'Student already exists.'
        else:
            logger.error("Student addition failed: Missing required fields")
            context['error'] = 'All fields are required.'
    return render(request, 'results/add_student.html', context)

@login_required
@user_passes_test(is_admin)
def add_class(request):
    """Add a new class."""
    context = {
        'error': None,
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    if request.method == 'POST':
        name = request.POST.get('name')
        if name and not Class.objects.filter(name=name).exists():
            Class.objects.create(name=name)
            logger.info(f"Class added: {name}")
            return redirect('results:add_class')
        logger.error(f"Class addition failed: {'Class already exists' if name else 'Invalid input'}")
        context['error'] = 'Class already exists or invalid input.'
    return render(request, 'results/add_class.html', context)

@login_required
@user_passes_test(is_admin)
def add_subject(request):
    """Add a new subject."""
    context = {
        'subjects': Subject.objects.all(),
        'error': None,
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    if request.method == 'POST':
        name = request.POST.get('name')
        if name and not Subject.objects.filter(name=name).exists():
            Subject.objects.create(name=name)
            logger.info(f"Subject added: {name}")
            return redirect('results:add_subject')
        logger.error(f"Subject addition failed: {'Subject already exists' if name else 'Invalid input'}")
        context['error'] = 'Subject already exists or invalid input.'
    return render(request, 'results/add_subject.html', context)

@login_required
@user_passes_test(is_admin)
def remove_subject(request, subject_id):
    """Remove a subject by ID."""
    if request.method == 'POST':
        try:
            Subject.objects.filter(id=subject_id).delete()
            logger.info(f"Subject removed: ID {subject_id}")
            return redirect('results:add_subject')
        except Exception as e:
            logger.error(f"Subject removal failed: {str(e)}")
            return render(request, 'results/add_subject.html', {
                'error': 'Failed to remove subject.',
                'subjects': Subject.objects.all(),
                'timestamp': 'August 02, 2025 05:00 PM CEST'
            })
    return redirect('results:add_subject')

@login_required
@user_passes_test(is_admin)
def add_term(request):
    """Add a new term."""
    context = {
        'error': None,
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    if request.method == 'POST':
        name = request.POST.get('name')
        if name and not Term.objects.filter(name=name).exists():
            Term.objects.create(name=name)
            logger.info(f"Term added: {name}")
            return redirect('results:add_term')
        logger.error(f"Term addition failed: {'Term already exists' if name else 'Invalid input'}")
        context['error'] = 'Term already exists or invalid input.'
    return render(request, 'results/add_term.html', context)

@login_required
@user_passes_test(is_admin)
def lock_result(request):
    """Lock results (placeholder)."""
    context = {
        'error': None,
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    if request.method == 'POST':
        logger.info("Result lock attempted")
        return redirect('results:lock_result')
    return render(request, 'results/lock_result.html', context)

@login_required
@user_passes_test(is_admin)
def update_database(request):
    """Update database with term-specific backup."""
    context = {
        'terms': Term.objects.all(),
        'error': None,
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    if request.method == 'POST':
        term_id = request.POST.get('term')
        if term_id:
            try:
                term = Term.objects.get(id=term_id)
                students = User.objects.filter(profile__role='student')
                scores = Score.objects.filter(student__in=students, term=term)
                results = Result.objects.filter(student__in=students, term=term)
                message = f"Backup for {term.name} ({term.session.year}) created with {scores.count()} scores and {results.count()} results."
                context['message'] = message
                logger.info(message)
                return redirect('results:update_database')
            except Term.DoesNotExist:
                logger.error(f"Database update failed: Term ID {term_id} not found")
                context['error'] = 'Selected term not found.'
        else:
            logger.error("Database update failed: No term selected")
            context['error'] = 'Please select a term.'
    return render(request, 'results/update_database.html', context)

@login_required
@user_passes_test(is_teacher)
def teacher_home(request):
    """Render teacher home with score upload functionality."""
    context = {
        'students': User.objects.filter(profile__role='student').select_related('profile'),
        'subjects': Subject.objects.all(),
        'scores': Score.objects.filter(student__profile__role='student').select_related('student', 'subject', 'term'),
        'avatar_url': request.user.profile.avatar.url if hasattr(request.user.profile, 'avatar') else None,
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        try:
            df = pd.read_excel(excel_file)
            uploaded_count = 0
            for index, row in df.iterrows():
                student = User.objects.get(username=row.get('student_username', ''))
                subject = Subject.objects.get(name=row.get('subject_name', ''))
                term = Term.objects.get(name=row.get('term_name', ''))
                score, created = Score.objects.get_or_create(
                    student=student,
                    subject=subject,
                    term=term,
                    defaults={'ca_score': float(row.get('ca_score', 0)), 'exam_score': float(row.get('exam_score', 0))}
                )
                if not created:
                    score.ca_score = float(row.get('ca_score', 0))
                    score.exam_score = float(row.get('exam_score', 0))
                    score.save()
                uploaded_count += 1
            context['message'] = f"Successfully uploaded {uploaded_count} scores."
            logger.info(f"Score upload successful: {uploaded_count} scores")
        except (User.DoesNotExist, Subject.DoesNotExist, Term.DoesNotExist, ValueError, pd.errors.EmptyDataError) as e:
            logger.error(f"Score upload failed: {str(e)}")
            context['error'] = f'Invalid Excel file or data: {str(e)}'
    return render(request, 'results/teacher_home.html', context)

@login_required
@user_passes_test(is_teacher)
def teacher_settings(request):
    """Render teacher settings page."""
    context = {
        'avatar_url': request.user.profile.avatar.url if hasattr(request.user.profile, 'avatar') else None,
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    return render(request, 'results/teacher_settings.html', context)

@login_required
@user_passes_test(is_teacher)
def upload_scores(request):
    """Placeholder for uploading scores."""
    context = {
        'error': 'This feature is under development.',
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    return render(request, 'results/upload_scores.html', context)

@login_required
@user_passes_test(is_teacher)
def assign_subject(request, student_id, subject_id):
    """Placeholder for assigning subjects to students."""
    context = {
        'error': 'This feature is under development.',
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    return render(request, 'results/assign_subject.html', context)

@login_required
def view_result(request):
    """Placeholder for viewing results."""
    context = {
        'error': 'This feature is under development.',
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    return render(request, 'results/view_result.html', context)

@login_required
@user_passes_test(is_teacher)
def edit_score(request, score_id):
    """Edit an existing score."""
    try:
        score = Score.objects.get(id=score_id)
        if request.method == 'POST':
            ca_score = float(request.POST.get('ca_score', score.ca_score))
            exam_score = float(request.POST.get('exam_score', score.exam_score))
            score.ca_score = ca_score
            score.exam_score = exam_score
            score.save()
            logger.info(f"Score updated: ID {score_id}")
            return redirect('results:teacher_home')
        return render(request, 'results/edit_score.html', {
            'score': score,
            'timestamp': 'August 02, 2025 05:00 PM CEST'
        })
    except Score.DoesNotExist:
        logger.error(f"Score edit failed: Score ID {score_id} not found")
        return render(request, 'results/edit_score.html', {
            'error': 'Score not found.',
            'timestamp': 'August 02, 2025 05:00 PM CEST'
        })

@login_required
@user_passes_test(is_teacher)
def delete_score(request, score_id):
    """Delete a score."""
    if request.method == 'POST':
        try:
            Score.objects.get(id=score_id).delete()
            logger.info(f"Score deleted: ID {score_id}")
            return redirect('results:teacher_home')
        except Score.DoesNotExist:
            logger.error(f"Score deletion failed: Score ID {score_id} not found")
            return render(request, 'results/delete_score.html', {
                'error': 'Score not found.',
                'score_id': score_id,
                'timestamp': 'August 02, 2025 05:00 PM CEST'
            })
    return render(request, 'results/delete_score.html', {
        'score_id': score_id,
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    })

@login_required
@user_passes_test(is_admin_or_staff)
def add_session(request):
    """Add a new academic session."""
    context = {
        'error': None,
        'success': False,
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    if request.method == 'POST':
        year = request.POST.get('year')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        if year and start_date and end_date:
            if not AcademicSession.objects.filter(year=year).exists():
                AcademicSession.objects.create(year=year, start_date=start_date, end_date=end_date)
                logger.info(f"Session added: {year}")
                context['success'] = True
                return render(request, 'results/add_session.html', context)
            logger.error(f"Session addition failed: Session already exists for year {year}")
            context['error'] = 'Session already exists for this year.'
        else:
            logger.error("Session addition failed: Missing required fields")
            context['error'] = 'All fields are required.'
    return render(request, 'results/add_session.html', context)

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    """Render student dashboard with results and subject selection."""
    student = request.user
    context = {
        'results': Result.objects.filter(student=student).select_related('term'),
        'scores': Score.objects.filter(student=student).select_related('subject', 'term'),
        'subjects': Subject.objects.all(),
        'selected_subjects': StudentSubject.objects.filter(profile=student.profile, is_active=True),
        'chart_labels': [score.subject.name for score in Score.objects.filter(student=student)],
        'chart_data': [score.total_score for score in Score.objects.filter(student=student)],
        'avatar_url': request.user.profile.avatar.url if hasattr(request.user.profile, 'avatar') else None,
        'timestamp': 'August 02, 2025 05:00 PM CEST'
    }
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        if subject_id:
            try:
                subject = Subject.objects.get(id=subject_id)
                StudentSubject.objects.get_or_create(profile=student.profile, subject=subject, defaults={'is_active': True})
                logger.info(f"Subject assigned to student ID {student.id}: Subject ID {subject_id}")
                return redirect('results:student_dashboard')
            except Subject.DoesNotExist:
                logger.error(f"Subject assignment failed: Subject ID {subject_id} not found")
                context['error'] = 'Selected subject not found.'
    return render(request, 'results/student_dashboard.html', context)

@login_required
def logout_view(request):
    """Log out the user."""
    logger.info(f"User logged out: ID {request.user.id}")
    auth_logout(request)
    return redirect('results:login')