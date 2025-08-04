from django.contrib import admin
from .models import Department, Class, AcademicSession, Term, Subject, Profile, Score, Result

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'department']
    list_filter = ['department']

@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ['year']

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['name', 'session']
    list_filter = ['session']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'class_assigned']
    list_filter = ['class_assigned']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'class_assigned']
    list_filter = ['role', 'department', 'class_assigned']
    search_fields = ['user__username']

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'term', 'ca_score', 'exam_score', 'total_score', 'grade']
    list_filter = ['term', 'subject']
    search_fields = ['student__username', 'subject__name']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'term', 'total_score', 'average_score', 'class_position']
    list_filter = ['term']
    search_fields = ['student__username']