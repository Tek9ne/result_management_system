from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator  # For score limits, oh so grand!

# Department (Section) Model - Now dynamic, no A-P restriction!
class Department(models.Model):
    name = models.CharField(
        max_length=100,  # Increased to allow descriptive names like "Science", "Arts"
        unique=True,
        help_text="Enter the section name (e.g., Science, Arts), oh man!"
    )
    def __str__(self):
        return self.name  # A single note in our plan!

# Class (Tech) Model, where learning does expand!
class Class(models.Model):
    name = models.CharField(
        max_length=10,
        choices=[('TECH 1', 'TECH 1'), ('TECH 2', 'TECH 2'), ('TECH 3', 'TECH 3')],  # Tech tiers so fine!
        help_text="Select a tech level, align with the line!"
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE, help_text="Link to a section, a destined design!")
    def __str__(self):
        return f"{self.name} - {self.department.name}"  # A duo that does shine!

# Session Model, time’s flowing sand!
class Session(models.Model):
    name = models.CharField(max_length=100, help_text="Name the session, take a stand!")
    year = models.IntegerField(help_text="Year to mark, with a steady hand!")
    def __str__(self):
        return f"{self.name} {self.year}"  # A chorus so grand!

# Academic Session Model, a yearly band! (Replacing Session for clarity)
class AcademicSession(models.Model):
    year = models.CharField(max_length=9, unique=True, help_text="Year range, like 2024/2025, so planned!")
    def __str__(self):
        return self.year  # A single verse, well spanned!

# Term Model, the academic strand!
class Term(models.Model):
    name = models.CharField(
        max_length=10,
        choices=[('First', 'First'), ('Second', 'Second'), ('Third', 'Third')],  # Terms in a row!
        help_text="Pick a term, let the knowledge grow!"
    )
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, help_text="Tie to a session’s flow!")
    def __str__(self):
        return f"{self.name} {self.session.year}"  # A rhythm to know!

# Subject Model, where lessons stand!
class Subject(models.Model):
    name = models.CharField(max_length=100, help_text="Name the subject, a learning brand!")
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, help_text="Link to a class, so grand!")
    def __str__(self):
        return self.name  # A title that’s manned!

# Profile Model (for Users), a role so planned!
class Profile(models.Model):
    ROLE_CHOICES = [('admin', 'Admin'), ('teacher', 'Teacher'), ('student', 'Student')]  # Roles to command!
    user = models.OneToOneField(User, on_delete=models.CASCADE, help_text="User to bind, a steady band!")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, help_text="Choose a role, take a stand!")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, help_text="Department link, if planned!")
    class_assigned = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, help_text="Class to assign, so grand!")
    roll_number = models.CharField(max_length=20, blank=True, null=True, help_text="Roll number, a unique brand!")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, help_text="Upload student avatar, a visual stand!")  # New field
    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="Phone number, e.g., 234XXXXXXXXXX!")  # New field
    home_address = models.TextField(blank=True, null=True, help_text="Home address, a detailed land!")  # New field
    subjects = models.ManyToManyField(Subject, through='StudentSubject', blank=True, help_text="Subjects assigned to student!")  # New field

    def __str__(self):
        return f"{self.user.username} - {self.role}"  # A name to behold!

# StudentSubject Model for many-to-many relationship
class StudentSubject(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('profile', 'subject')

# Score Model, where grades expand!
class Score(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'student'}, related_name='scores', help_text="Student to score, a learning land!")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, help_text="Subject to test, so grand!")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, help_text="Term to mark, with a steady hand!")
    ca_score = models.FloatField(default=0, validators=[MaxValueValidator(40)], help_text="CA score, up to 40, oh so fine!")
    exam_score = models.FloatField(default=0, validators=[MaxValueValidator(60)], help_text="Exam score, up to 60, align with the line!")
    total_score = models.FloatField(default=0, help_text="Total score, the sum to find!")
    grade = models.CharField(max_length=2, blank=True, help_text="Grade to assign, a letter so kind!")
    remarks = models.CharField(max_length=100, blank=True, help_text="Remarks to note, with a mindful mind!")
    subject_position = models.IntegerField(null=True, blank=True, help_text="Position in class, if defined!")

    def save(self, *args, **kwargs):
        self.total_score = self.ca_score + self.exam_score  # Sum the scores with care!
        if self.total_score >= 80:
            self.grade = 'A'; self.remarks = 'EXCELLENT'  # A stellar affair!
        elif self.total_score >= 70:
            self.grade = 'B'; self.remarks = 'VERY GOOD'  # A strong declare!
        elif self.total_score >= 60:
            self.grade = 'C'; self.remarks = 'GOOD'  # A solid square!
        elif self.total_score >= 50:
            self.grade = 'D'; self.remarks = 'FAIR'  # A pass to share!
        else:
            self.grade = 'E'; self.remarks = 'FAIL'  # A need for repair!
        super().save(*args, **kwargs)  # Save with a flair!

    def __str__(self):
        return f"{self.student.username} - {self.subject.name} - {self.term}"  # A record so rare!

# Result Model, the final stand!
class Result(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'student'}, related_name='results', help_text="Student to review, a learning band!")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, help_text="Term to sum, with a steady hand!")
    total_score = models.FloatField(default=0, help_text="Total score to show, oh so grand!")
    average_score = models.FloatField(default=0, help_text="Average to compute, a planned demand!")
    class_position = models.IntegerField(null=True, blank=True, help_text="Position in class, if it can!")
    pass_status = models.BooleanField(default=False, help_text="Pass or fail, a final stand!")
    principal_comment = models.TextField(blank=True, help_text="Comment from the top, a guiding hand!")
    conduct = models.CharField(max_length=100, blank=True, help_text="Conduct to note, a moral brand!")

    def save(self, *args, **kwargs):
        scores = Score.objects.filter(student=self.student, term=self.term)  # Gather the scores!
        self.total_score = sum(score.total_score for score in scores if scores.exists())  # Total to explore!
        self.average_score = self.total_score / len(scores) if scores.exists() else 0  # Average to restore!
        self.pass_status = self.average_score >= 50  # Pass if fifty or more!
        super().save(*args, **kwargs)  # Save with a roar!

    def __str__(self):
        return f"{self.student.username} - {self.term}"  # A result to adore!