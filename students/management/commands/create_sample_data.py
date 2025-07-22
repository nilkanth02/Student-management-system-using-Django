from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
import random

from students.models import Department, Teacher, Student, Course, Enrollment, Grade, Attendance


class Command(BaseCommand):
    help = 'Create sample data for the student management system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Attendance.objects.all().delete()
            Grade.objects.all().delete()
            Enrollment.objects.all().delete()
            Course.objects.all().delete()
            Student.objects.all().delete()
            Teacher.objects.all().delete()
            Department.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Creating sample data...')

        # Create departments
        departments_data = [
            {'name': 'Computer Science', 'code': 'CS', 'head_of_department': 'Dr. John Smith'},
            {'name': 'Mathematics', 'code': 'MATH', 'head_of_department': 'Dr. Jane Doe'},
            {'name': 'Physics', 'code': 'PHYS', 'head_of_department': 'Dr. Bob Johnson'},
            {'name': 'Chemistry', 'code': 'CHEM', 'head_of_department': 'Dr. Alice Brown'},
        ]

        departments = []
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults=dept_data
            )
            departments.append(dept)
            if created:
                self.stdout.write(f'Created department: {dept.name}')

        # Create teacher users and teachers
        teachers_data = [
            {'username': 'prof_wilson', 'first_name': 'Robert', 'last_name': 'Wilson', 'email': 'r.wilson@university.edu', 'dept_idx': 0, 'qualification': 'PHD'},
            {'username': 'prof_davis', 'first_name': 'Sarah', 'last_name': 'Davis', 'email': 's.davis@university.edu', 'dept_idx': 1, 'qualification': 'PHD'},
            {'username': 'prof_miller', 'first_name': 'Michael', 'last_name': 'Miller', 'email': 'm.miller@university.edu', 'dept_idx': 2, 'qualification': 'PHD'},
            {'username': 'prof_garcia', 'first_name': 'Maria', 'last_name': 'Garcia', 'email': 'm.garcia@university.edu', 'dept_idx': 3, 'qualification': 'PHD'},
        ]

        teachers = []
        for teacher_data in teachers_data:
            user, created = User.objects.get_or_create(
                username=teacher_data['username'],
                defaults={
                    'first_name': teacher_data['first_name'],
                    'last_name': teacher_data['last_name'],
                    'email': teacher_data['email'],
                    'is_staff': True,
                }
            )
            if created:
                user.set_password('teacher123')
                user.save()

            teacher, created = Teacher.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': f'T{1000 + len(teachers)}',
                    'department': departments[teacher_data['dept_idx']],
                    'phone': f'+1-555-{random.randint(1000, 9999)}',
                    'qualification': teacher_data['qualification'],
                    'experience_years': random.randint(5, 20),
                    'salary': random.randint(50000, 100000),
                    'hire_date': date.today() - timedelta(days=random.randint(365, 3650)),
                }
            )
            teachers.append(teacher)
            if created:
                self.stdout.write(f'Created teacher: {teacher.full_name}')

        # Create students
        student_names = [
            ('John', 'Doe'), ('Jane', 'Smith'), ('Mike', 'Johnson'), ('Sarah', 'Williams'),
            ('David', 'Brown'), ('Lisa', 'Jones'), ('Chris', 'Garcia'), ('Amy', 'Miller'),
            ('Tom', 'Davis'), ('Emma', 'Wilson'), ('Alex', 'Moore'), ('Olivia', 'Taylor'),
        ]

        students = []
        for i, (first_name, last_name) in enumerate(student_names):
            student, created = Student.objects.get_or_create(
                student_id=f'S{2024}{i+1:03d}',
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f'{first_name.lower()}.{last_name.lower()}@student.university.edu',
                    'phone': f'+1-555-{random.randint(1000, 9999)}',
                    'date_of_birth': date(2000 + random.randint(0, 4), random.randint(1, 12), random.randint(1, 28)),
                    'gender': random.choice(['M', 'F']),
                    'address': f'{random.randint(100, 999)} Main St, City, State',
                    'department': random.choice(departments),
                    'year_of_study': random.randint(1, 4),
                    'admission_date': date(2024, 9, 1),
                    'emergency_contact_name': f'{first_name} Parent',
                    'emergency_contact_phone': f'+1-555-{random.randint(1000, 9999)}',
                    'emergency_contact_relationship': 'Parent',
                }
            )
            students.append(student)
            if created:
                self.stdout.write(f'Created student: {student.full_name}')

        # Create courses
        courses_data = [
            {'code': 'CS101', 'name': 'Introduction to Programming', 'dept_idx': 0, 'teacher_idx': 0, 'credits': 3},
            {'code': 'CS201', 'name': 'Data Structures', 'dept_idx': 0, 'teacher_idx': 0, 'credits': 4},
            {'code': 'MATH101', 'name': 'Calculus I', 'dept_idx': 1, 'teacher_idx': 1, 'credits': 4},
            {'code': 'MATH201', 'name': 'Linear Algebra', 'dept_idx': 1, 'teacher_idx': 1, 'credits': 3},
            {'code': 'PHYS101', 'name': 'General Physics I', 'dept_idx': 2, 'teacher_idx': 2, 'credits': 4},
            {'code': 'CHEM101', 'name': 'General Chemistry', 'dept_idx': 3, 'teacher_idx': 3, 'credits': 4},
        ]

        courses = []
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                course_code=course_data['code'],
                semester='FALL',
                year=2024,
                defaults={
                    'name': course_data['name'],
                    'description': f'This is the {course_data["name"]} course.',
                    'department': departments[course_data['dept_idx']],
                    'teacher': teachers[course_data['teacher_idx']],
                    'credits': course_data['credits'],
                    'max_students': 30,
                    'schedule': 'Mon/Wed/Fri 10:00-11:00',
                    'classroom': f'Room {random.randint(100, 999)}',
                }
            )
            courses.append(course)
            if created:
                self.stdout.write(f'Created course: {course.course_code} - {course.name}')

        # Create enrollments
        for student in students[:8]:  # Enroll first 8 students
            for course in random.sample(courses, random.randint(2, 4)):
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={
                        'status': 'ENROLLED',
                    }
                )
                if created:
                    self.stdout.write(f'Enrolled {student.full_name} in {course.course_code}')

                    # Create some grades
                    for i in range(random.randint(2, 5)):
                        Grade.objects.create(
                            enrollment=enrollment,
                            assessment_type=random.choice(['QUIZ', 'ASSIGNMENT', 'MIDTERM', 'FINAL']),
                            assessment_name=f'Assessment {i+1}',
                            points_earned=random.randint(70, 100),
                            points_possible=100,
                            assessment_date=date.today() - timedelta(days=random.randint(1, 60)),
                        )

                    # Create attendance records
                    for i in range(random.randint(10, 20)):
                        Attendance.objects.create(
                            enrollment=enrollment,
                            date=date.today() - timedelta(days=i),
                            status=random.choice(['PRESENT', 'ABSENT', 'LATE']),
                            marked_by=course.teacher,
                        )

        self.stdout.write(self.style.SUCCESS('Successfully created sample data!'))
        self.stdout.write(f'Created:')
        self.stdout.write(f'  - {Department.objects.count()} departments')
        self.stdout.write(f'  - {Teacher.objects.count()} teachers')
        self.stdout.write(f'  - {Student.objects.count()} students')
        self.stdout.write(f'  - {Course.objects.count()} courses')
        self.stdout.write(f'  - {Enrollment.objects.count()} enrollments')
        self.stdout.write(f'  - {Grade.objects.count()} grades')
        self.stdout.write(f'  - {Attendance.objects.count()} attendance records')
