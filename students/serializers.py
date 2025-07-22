from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department, Teacher, Student, Course, Enrollment, Grade, Attendance


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model (used in Teacher serializer)
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Department model with student and teacher counts
    """
    students_count = serializers.SerializerMethodField()
    teachers_count = serializers.SerializerMethodField()
    courses_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'description', 'head_of_department',
            'students_count', 'teachers_count', 'courses_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_students_count(self, obj):
        return obj.students.filter(is_active=True).count()

    def get_teachers_count(self, obj):
        return obj.teachers.filter(is_active=True).count()

    def get_courses_count(self, obj):
        return obj.courses.filter(is_active=True).count()


class TeacherSerializer(serializers.ModelSerializer):
    """
    Serializer for Teacher model with nested user information
    """
    user = UserSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    full_name = serializers.CharField(read_only=True)
    courses_count = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            'id', 'user', 'employee_id', 'department', 'department_name',
            'phone', 'qualification', 'experience_years', 'salary',
            'hire_date', 'is_active', 'full_name', 'courses_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_courses_count(self, obj):
        return obj.courses.filter(is_active=True).count()


class StudentSerializer(serializers.ModelSerializer):
    """
    Serializer for Student model with computed fields
    """
    department_name = serializers.CharField(source='department.name', read_only=True)
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    enrollments_count = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'date_of_birth', 'age', 'gender', 'address',
            'department', 'department_name', 'year_of_study', 'admission_date',
            'graduation_date', 'is_active', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship',
            'enrollments_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_enrollments_count(self, obj):
        return obj.enrollments.filter(is_active=True).count()

    def validate_email(self, value):
        """Ensure email is unique"""
        if Student.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("A student with this email already exists.")
        return value

    def validate_student_id(self, value):
        """Ensure student_id is unique"""
        if Student.objects.filter(student_id=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("A student with this ID already exists.")
        return value


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for Course model with related information
    """
    department_name = serializers.CharField(source='department.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    enrolled_students_count = serializers.IntegerField(read_only=True)
    available_slots = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'name', 'description', 'department',
            'department_name', 'teacher', 'teacher_name', 'credits',
            'semester', 'year', 'max_students', 'enrolled_students_count',
            'available_slots', 'schedule', 'classroom', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_course_code(self, value):
        """Ensure course_code is unique for the semester and year"""
        semester = self.initial_data.get('semester')
        year = self.initial_data.get('year')
        
        if semester and year:
            existing = Course.objects.filter(
                course_code=value, 
                semester=semester, 
                year=year
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise serializers.ValidationError(
                    f"A course with code {value} already exists for {semester} {year}."
                )
        return value


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Enrollment model with student and course details
    """
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    grades_count = serializers.SerializerMethodField()
    attendance_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_name', 'student_id', 'course',
            'course_name', 'course_code', 'enrollment_date', 'status',
            'is_active', 'final_grade', 'completion_date', 'grades_count',
            'attendance_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'enrollment_date', 'created_at', 'updated_at']

    def get_grades_count(self, obj):
        return obj.grades.count()

    def get_attendance_percentage(self, obj):
        return Attendance.get_attendance_percentage(obj)

    def validate(self, data):
        """Validate enrollment constraints"""
        student = data.get('student')
        course = data.get('course')
        
        if student and course:
            # Check if student is already enrolled in this course
            if Enrollment.objects.filter(
                student=student, 
                course=course, 
                is_active=True
            ).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise serializers.ValidationError(
                    "Student is already enrolled in this course."
                )
            
            # Check if course has available slots
            if course.available_slots <= 0:
                raise serializers.ValidationError(
                    "This course is full. No available slots."
                )
        
        return data


class GradeSerializer(serializers.ModelSerializer):
    """
    Serializer for Grade model with enrollment details
    """
    student_name = serializers.CharField(source='enrollment.student.full_name', read_only=True)
    course_name = serializers.CharField(source='enrollment.course.name', read_only=True)
    course_code = serializers.CharField(source='enrollment.course.course_code', read_only=True)

    class Meta:
        model = Grade
        fields = [
            'id', 'enrollment', 'student_name', 'course_name', 'course_code',
            'assessment_type', 'assessment_name', 'points_earned',
            'points_possible', 'percentage', 'letter_grade', 'assessment_date',
            'comments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'percentage', 'letter_grade', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate grade constraints"""
        points_earned = data.get('points_earned')
        points_possible = data.get('points_possible')
        
        if points_earned and points_possible:
            if points_earned > points_possible:
                raise serializers.ValidationError(
                    "Points earned cannot be greater than points possible."
                )
            if points_earned < 0 or points_possible <= 0:
                raise serializers.ValidationError(
                    "Points must be positive values."
                )
        
        return data


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for Attendance model with enrollment details
    """
    student_name = serializers.CharField(source='enrollment.student.full_name', read_only=True)
    course_name = serializers.CharField(source='enrollment.course.name', read_only=True)
    course_code = serializers.CharField(source='enrollment.course.course_code', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.full_name', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id', 'enrollment', 'student_name', 'course_name', 'course_code',
            'date', 'status', 'notes', 'marked_by', 'marked_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate attendance constraints"""
        enrollment = data.get('enrollment')
        date = data.get('date')
        
        if enrollment and date:
            # Check if attendance already exists for this enrollment and date
            if Attendance.objects.filter(
                enrollment=enrollment, 
                date=date
            ).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise serializers.ValidationError(
                    "Attendance record already exists for this student on this date."
                )
        
        return data


# Summary serializers for dashboard/overview purposes
class StudentSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for student listings"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'student_id', 'first_name', 'last_name', 'email', 'department_name', 'year_of_study', 'is_active']


class CourseSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for course listings"""
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'course_code', 'name', 'teacher_name', 'credits', 'semester', 'year', 'is_active']
