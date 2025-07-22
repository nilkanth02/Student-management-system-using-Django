from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Department(models.Model):
    """
    Department model to organize courses and teachers
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    head_of_department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f"{self.code} - {self.name}"


class Teacher(models.Model):
    """
    Teacher model extending User model for authentication
    """
    QUALIFICATION_CHOICES = [
        ('BSC', 'Bachelor of Science'),
        ('MSC', 'Master of Science'),
        ('PHD', 'Doctor of Philosophy'),
        ('BED', 'Bachelor of Education'),
        ('MED', 'Master of Education'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teachers')
    phone = models.CharField(max_length=15)
    qualification = models.CharField(max_length=3, choices=QUALIFICATION_CHOICES)
    experience_years = models.PositiveIntegerField(default=0)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

    @property
    def full_name(self):
        return self.user.get_full_name()


class Student(models.Model):
    """
    Student model with comprehensive information
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    YEAR_CHOICES = [
        (1, 'First Year'),
        (2, 'Second Year'),
        (3, 'Third Year'),
        (4, 'Fourth Year'),
    ]

    # Personal Information
    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()

    # Academic Information
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    year_of_study = models.PositiveIntegerField(choices=YEAR_CHOICES)
    admission_date = models.DateField()
    graduation_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    emergency_contact_relationship = models.CharField(max_length=50)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class Course(models.Model):
    """
    Course model with detailed information
    """
    SEMESTER_CHOICES = [
        ('FALL', 'Fall'),
        ('SPRING', 'Spring'),
        ('SUMMER', 'Summer'),
    ]

    course_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='courses')
    credits = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    semester = models.CharField(max_length=6, choices=SEMESTER_CHOICES)
    year = models.PositiveIntegerField()
    max_students = models.PositiveIntegerField(default=30)
    schedule = models.CharField(max_length=100, help_text="e.g., 'Mon/Wed/Fri 10:00-11:00'")
    classroom = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['course_code']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        unique_together = ['course_code', 'semester', 'year']

    def __str__(self):
        return f"{self.course_code} - {self.name}"

    @property
    def enrolled_students_count(self):
        return self.enrollments.filter(is_active=True).count()

    @property
    def available_slots(self):
        return self.max_students - self.enrolled_students_count


class Enrollment(models.Model):
    """
    Enrollment model to track student-course relationships
    """
    STATUS_CHOICES = [
        ('ENROLLED', 'Enrolled'),
        ('DROPPED', 'Dropped'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ENROLLED')
    is_active = models.BooleanField(default=True)
    final_grade = models.CharField(max_length=2, blank=True, null=True)
    completion_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-enrollment_date']
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.full_name} - {self.course.course_code}"


class Grade(models.Model):
    """
    Grade model to track student performance in assessments
    """
    ASSESSMENT_CHOICES = [
        ('QUIZ', 'Quiz'),
        ('ASSIGNMENT', 'Assignment'),
        ('MIDTERM', 'Midterm Exam'),
        ('FINAL', 'Final Exam'),
        ('PROJECT', 'Project'),
        ('PRESENTATION', 'Presentation'),
    ]

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='grades')
    assessment_type = models.CharField(max_length=12, choices=ASSESSMENT_CHOICES)
    assessment_name = models.CharField(max_length=100)
    points_earned = models.DecimalField(max_digits=5, decimal_places=2)
    points_possible = models.DecimalField(max_digits=5, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    letter_grade = models.CharField(max_length=2, editable=False)
    assessment_date = models.DateField()
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-assessment_date']
        verbose_name = 'Grade'
        verbose_name_plural = 'Grades'

    def save(self, *args, **kwargs):
        # Calculate percentage and letter grade
        if self.points_possible > 0:
            self.percentage = (self.points_earned / self.points_possible) * 100
            self.letter_grade = self.calculate_letter_grade(self.percentage)
        super().save(*args, **kwargs)

    def calculate_letter_grade(self, percentage):
        """Convert percentage to letter grade"""
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'

    def __str__(self):
        return f"{self.enrollment.student.full_name} - {self.assessment_name}: {self.letter_grade}"


class Attendance(models.Model):
    """
    Attendance model to track student attendance in courses
    """
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('EXCUSED', 'Excused'),
    ]

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=7, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True, help_text="Additional notes about attendance")
    marked_by = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='marked_attendance')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'
        unique_together = ['enrollment', 'date']

    def __str__(self):
        return f"{self.enrollment.student.full_name} - {self.enrollment.course.course_code} - {self.date}: {self.status}"

    @classmethod
    def get_attendance_percentage(cls, enrollment):
        """Calculate attendance percentage for a student in a course"""
        total_records = cls.objects.filter(enrollment=enrollment).count()
        if total_records == 0:
            return 0
        present_records = cls.objects.filter(
            enrollment=enrollment,
            status__in=['PRESENT', 'LATE']
        ).count()
        return (present_records / total_records) * 100
