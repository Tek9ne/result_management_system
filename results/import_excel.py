from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from results.models import Profile, Department, Level, Subject, AcademicSession, Term, Score, Result
import pandas as pd
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Import Excel data into database'

    def handle(self, *args, **kwargs):
        session, _ = AcademicSession.objects.get_or_create(year='2024/2025')
        terms = {
            1: Term.objects.get_or_create(name='1ST TERM', session=session)[0],
            2: Term.objects.get_or_create(name='2ND TERM', session=session)[0],
            3: Term.objects.get_or_create(name='3RD TERM', session=session)[0],
        }

        dept1, _ = Department.objects.get_or_create(name='Instrument Mechanics Works')
        dept2, _ = Department.objects.get_or_create(name='Electrical Installation & Maintenance')
        levels = ['100', '200', '300', '400']
        level_objects = {}
        for level_name in levels:
            level_objects[level_name] = Level.objects.get_or_create(name=level_name, department=dept1)[0]
            Level.objects.get_or_create(name=level_name, department=dept2)[0]

        subjects = [
            'CRAFT PRACTICE', 'BUILDING/ENG. DRAWING', 'ENGLISH LANGUAGE', 'MATHEMATICS',
            # Add more subjects from Excel
        ]
        for subject_name in subjects:
            for level in level_objects.values():
                Subject.objects.get_or_create(name=subject_name, level_assigned=level)

        files = [
            ('Instrument Mechnics works TECH 1.xlsx', dept1, level_objects['100']),
            ('ELECTRICAL TECH 1 new.xlsx', dept2, level_objects['100']),
        ]
        for file_name, dept, level_assigned in files:
            file_path = os.path.join(settings.BASE_DIR, 'results', 'data', file_name)
            try:
                df = pd.read_excel(file_path, sheet_name='TECH 1', header=7)
                for _, row in df.iterrows():
                    student_id = row['S/N']
                    username = f"student_{student_id}"
                    user, _ = User.objects.get_or_create(username=username, defaults={'password': 'default_password'})
                    Profile.objects.get_or_create(
                        user=user,
                        defaults={
                            'role': 'student',
                            'department': dept,
                            'level_assigned': level_assigned
                        }
                    )
                    for term_id, term in terms.items():
                        term_prefix = {1: '1ST TERM', 2: '2ND TERM', 3: '3RD TERM'}[term_id]
                        for subject_name in subjects:
                            subject = Subject.objects.get(name=subject_name, level_assigned=level_assigned)
                            ca_col = f"{subject_name}.{term_prefix}.CA (40)"
                            exam_col = f"{subject_name}.{term_prefix}.EXAM (60)"
                            if ca_col in df.columns and exam_col in df.columns:
                                Score.objects.get_or_create(
                                    student=user,
                                    subject=subject,
                                    term=term,
                                    defaults={
                                        'ca_score': row[ca_col] if not pd.isna(row[ca_col]) else 0,
                                        'exam_score': row[exam_col] if not pd.isna(row[exam_col]) else 0,
                                    }
                                )
                        scores = Score.objects.filter(student=user, term=term)
                        if scores:
                            Result.objects.get_or_create(
                                student=user,
                                term=term,
                                defaults={
                                    'total_score': sum(score.total_score for score in scores),
                                    'average_score': sum(score.total_score for score in scores) / len(scores),
                                    'pass_status': (sum(score.total_score for score in scores) / len(scores)) >= 50
                                }
                            )
                self.stdout.write(self.style.SUCCESS(f'Imported data from {file_name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error importing {file_name}: {str(e)}'))