from django import template

register = template.Library()

@register.filter
def filter_student(scores, student_id):
    return [s for s in scores if s.student_id == int(student_id)]