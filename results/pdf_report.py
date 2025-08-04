from django.http import HttpResponse
from django.contrib.auth.models import User
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from results.models import Profile, Score, Result, Term, AcademicSession

def generate_result_pdf(request, student_id, term_id, section):
    try:
        user = User.objects.get(id=student_id)
        profile = Profile.objects.get(user=user)
        term = Term.objects.get(id=term_id)
        if profile.role != 'student' or profile.department.name != section:
            return HttpResponse('Unauthorized', status=403)
    except (User.DoesNotExist, Profile.DoesNotExist, Term.DoesNotExist):
        return HttpResponse('Invalid student or term', status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="result_student_{student_id}_term_{term_id}.pdf"'
    p = canvas.Canvas(response, pagesize=A4)

    p.setFont("Helvetica-Bold", 14)
    width, height = A4
    x_margin, y_margin = 50, 800
    y = y_margin

    p.drawString(x_margin, y, "LAGOS STATE GOVERNMENT")
    y -= 20
    p.drawString(x_margin, y, "GOVERNMENT TECHNICAL COLLEGE, ODOMOLA, EPE")
    y -= 20
    p.drawString(x_margin, y, "STUDENT'S RESULT PRINT OUT")
    y -= 30

    p.setFont("Helvetica", 12)
    p.drawString(x_margin, y, f"Name: {user.get_full_name() or user.username}")
    y -= 20
    p.drawString(x_margin, y, f"Roll Number: {profile.roll_number or student_id}")
    y -= 20
    p.drawString(x_margin, y, f"Department: {profile.department.name if profile.department else 'N/A'}")
    y -= 20
    p.drawString(x_margin, y, f"Level: {profile.level_assigned.name if profile.level_assigned else 'N/A'}")
    y -= 20
    p.drawString(x_margin, y, f"Term: {term.name}")
    y -= 20
    p.drawString(x_margin, y, f"Session: {term.session.year}")
    y -= 30

    p.setFont("Helvetica-Bold", 10)
    p.drawString(x_margin, y, "SUBJECT")
    p.drawString(x_margin + 150, y, "CA (40)")
    p.drawString(x_margin + 200, y, "EXAM (60)")
    p.drawString(x_margin + 250, y, "TOTAL (100)")
    p.drawString(x_margin + 300, y, "GRADE")
    p.drawString(x_margin + 350, y, "REMARKS")
    p.drawString(x_margin + 400, y, "POSITION")
    y -= 15
    p.line(x_margin, y, x_margin + 500, y)
    y -= 10

    p.setFont("Helvetica", 10)
    scores = Score.objects.filter(student=user, term=term).select_related('subject')
    for score in scores:
        p.drawString(x_margin, y, score.subject.name)
        p.drawString(x_margin + 150, y, str(score.ca_score))
        p.drawString(x_margin + 200, y, str(score.exam_score))
        p.drawString(x_margin + 250, y, str(score.total_score))
        p.drawString(x_margin + 300, y, score.grade)
        p.drawString(x_margin + 350, y, score.remarks)
        p.drawString(x_margin + 400, y, str(score.subject_position or 'N/A'))
        y -= 20

    y -= 20
    p.setFont("Helvetica-Bold", 10)
    p.drawString(x_margin, y, "RESULT SUMMARY")
    y -= 15
    p.line(x_margin, y, x_margin + 500, y)
    y -= 10
    p.setFont("Helvetica", 10)

    result = Result.objects.filter(student=user, term=term).first()
    if result:
        p.drawString(x_margin, y, f"Total Score: {result.total_score}")
        y -= 20
        p.drawString(x_margin, y, f"Average Score: {result.average_score:.2f}")
        y -= 20
        p.drawString(x_margin, y, f"Pass Status: {'Pass' if result.pass_status else 'Fail'}")
        y -= 20
        p.drawString(x_margin, y, f"Class Position: {result.class_position or 'N/A'}")
    else:
        p.drawString(x_margin, y, "No result summary available")
    y -= 20

    y -= 20
    p.setFont("Helvetica-Bold", 10)
    p.drawString(x_margin, y, "COMMENTS")
    y -= 15
    p.line(x_margin, y, x_margin + 500, y)
    y -= 10
    p.setFont("Helvetica", 10)
    p.drawString(x_margin, y, f"Principal's Comment: {result.principal_comment if result else 'N/A'}")
    y -= 20
    p.drawString(x_margin, y, "Teacher's Comment: ____________________")

    p.showPage()
    p.save()
    return response