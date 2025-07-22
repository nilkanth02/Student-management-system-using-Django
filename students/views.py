from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import Department, Teacher, Student, Course, Enrollment, Grade, Attendance
from .serializers import (
    DepartmentSerializer, TeacherSerializer, StudentSerializer, CourseSerializer,
    EnrollmentSerializer, GradeSerializer, AttendanceSerializer,
    StudentSummarySerializer, CourseSummarySerializer
)
from .permissions import (
    IsTeacherOrReadOnly, IsOwnerOrTeacherOrReadOnly,
    IsTeacherOfCourse, IsDepartmentMemberOrReadOnly
)


# ============================================================================
# ENDPOINT 1: Student Management (CRUD Operations)
# ============================================================================

class StudentListCreateView(generics.ListCreateAPIView):
    """
    GET: List all students with filtering and search capabilities
    POST: Create a new student

    Features:
    - Search by name, email, student_id
    - Filter by department, year_of_study, is_active
    - Pagination support
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'year_of_study', 'is_active', 'gender']
    search_fields = ['first_name', 'last_name', 'email', 'student_id']
    ordering_fields = ['last_name', 'first_name', 'admission_date', 'student_id']
    ordering = ['last_name', 'first_name']

    def get_queryset(self):
        queryset = Student.objects.select_related('department')

        # Additional custom filters
        department_code = self.request.query_params.get('department_code')
        if department_code:
            queryset = queryset.filter(department__code=department_code)

        return queryset


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific student
    PUT/PATCH: Update student information
    DELETE: Soft delete (set is_active=False)
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        """Soft delete - set is_active to False instead of actual deletion"""
        student = self.get_object()
        student.is_active = False
        student.save()
        return Response(
            {"message": "Student deactivated successfully"},
            status=status.HTTP_200_OK
        )


# ============================================================================
# ENDPOINT 2: Course Management (CRUD Operations)
# ============================================================================

class CourseListCreateView(generics.ListCreateAPIView):
    """
    GET: List all courses with filtering capabilities
    POST: Create a new course

    Features:
    - Search by course name, code
    - Filter by department, semester, year, teacher
    - Shows enrollment statistics
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'teacher', 'semester', 'year', 'is_active']
    search_fields = ['name', 'course_code', 'description']
    ordering_fields = ['course_code', 'name', 'credits', 'year']
    ordering = ['course_code']

    def get_queryset(self):
        return Course.objects.select_related('department', 'teacher__user')


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific course with enrollment details
    PUT/PATCH: Update course information
    DELETE: Soft delete course
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        """Soft delete - set is_active to False"""
        course = self.get_object()
        course.is_active = False
        course.save()
        return Response(
            {"message": "Course deactivated successfully"},
            status=status.HTTP_200_OK
        )


# ============================================================================
# ENDPOINT 3: Enrollment Management
# ============================================================================

class EnrollmentListCreateView(generics.ListCreateAPIView):
    """
    GET: List all enrollments with filtering
    POST: Enroll a student in a course

    Features:
    - Filter by student, course, status
    - Automatic validation for enrollment constraints
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'course', 'status', 'is_active']
    search_fields = ['student__first_name', 'student__last_name', 'course__name', 'course__course_code']
    ordering_fields = ['enrollment_date', 'completion_date']
    ordering = ['-enrollment_date']

    def get_queryset(self):
        return Enrollment.objects.select_related(
            'student', 'course', 'course__department', 'course__teacher'
        )


class EnrollmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve enrollment details with grades and attendance
    PUT/PATCH: Update enrollment status
    DELETE: Remove enrollment
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.select_related(
            'student', 'course'
        ).prefetch_related('grades', 'attendance_records')


# ============================================================================
# ENDPOINT 4: Grade Management
# ============================================================================

class GradeListCreateView(generics.ListCreateAPIView):
    """
    GET: List all grades with filtering
    POST: Add a new grade for a student

    Features:
    - Filter by enrollment, assessment type, date range
    - Automatic percentage and letter grade calculation
    """
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['enrollment', 'assessment_type', 'letter_grade']
    search_fields = ['assessment_name', 'enrollment__student__first_name', 'enrollment__student__last_name']
    ordering_fields = ['assessment_date', 'percentage', 'points_earned']
    ordering = ['-assessment_date']

    def get_queryset(self):
        queryset = Grade.objects.select_related(
            'enrollment__student', 'enrollment__course'
        )

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(assessment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(assessment_date__lte=end_date)

        return queryset


class GradeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve specific grade details
    PUT/PATCH: Update grade information
    DELETE: Remove grade record
    """
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]


# ============================================================================
# ENDPOINT 5: Attendance Management
# ============================================================================

class AttendanceListCreateView(generics.ListCreateAPIView):
    """
    GET: List attendance records with filtering
    POST: Mark attendance for a student

    Features:
    - Filter by enrollment, date range, status
    - Bulk attendance marking support
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['enrollment', 'status', 'marked_by']
    search_fields = ['enrollment__student__first_name', 'enrollment__student__last_name', 'notes']
    ordering_fields = ['date', 'status']
    ordering = ['-date']

    def get_queryset(self):
        queryset = Attendance.objects.select_related(
            'enrollment__student', 'enrollment__course', 'marked_by'
        )

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset


class AttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve specific attendance record
    PUT/PATCH: Update attendance status
    DELETE: Remove attendance record
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]


# ============================================================================
# ENDPOINT 6: Department Management
# ============================================================================

class DepartmentListCreateView(generics.ListCreateAPIView):
    """
    GET: List all departments with statistics
    POST: Create a new department

    Features:
    - Shows student, teacher, and course counts
    - Search by name and code
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve department details with related data
    PUT/PATCH: Update department information
    DELETE: Remove department (if no related data)
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        """Check for related data before deletion"""
        department = self.get_object()

        if department.students.exists() or department.teachers.exists() or department.courses.exists():
            return Response(
                {"error": "Cannot delete department with existing students, teachers, or courses"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().delete(request, *args, **kwargs)


# ============================================================================
# ENDPOINT 7: Teacher Management
# ============================================================================

class TeacherListCreateView(generics.ListCreateAPIView):
    """
    GET: List all teachers with filtering
    POST: Create a new teacher

    Features:
    - Filter by department, qualification, active status
    - Search by name and employee ID
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'qualification', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']
    ordering_fields = ['user__last_name', 'hire_date', 'experience_years']
    ordering = ['user__last_name', 'user__first_name']

    def get_queryset(self):
        return Teacher.objects.select_related('user', 'department')


class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve teacher details with courses
    PUT/PATCH: Update teacher information
    DELETE: Soft delete teacher
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        """Soft delete - set is_active to False"""
        teacher = self.get_object()
        teacher.is_active = False
        teacher.save()
        return Response(
            {"message": "Teacher deactivated successfully"},
            status=status.HTTP_200_OK
        )


# ============================================================================
# ENDPOINT 8: Analytics & Dashboard Data
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_analytics(request):
    """
    GET: Comprehensive dashboard analytics

    Returns:
    - Student statistics (total, by department, by year)
    - Course statistics (total, by semester, enrollment rates)
    - Attendance statistics
    - Grade distribution
    - Recent activities
    """
    from django.db.models import Count, Avg

    # Basic counts
    total_students = Student.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_teachers = Teacher.objects.filter(is_active=True).count()
    total_departments = Department.objects.count()

    # Students by department
    students_by_dept = list(
        Department.objects.annotate(
            student_count=Count('students', filter=Q(students__is_active=True))
        ).values('name', 'student_count')
    )

    # Students by year
    students_by_year = list(
        Student.objects.filter(is_active=True)
        .values('year_of_study')
        .annotate(count=Count('id'))
        .order_by('year_of_study')
    )

    # Course enrollment statistics
    course_enrollment_stats = list(
        Course.objects.filter(is_active=True)
        .annotate(
            enrolled_count=Count('enrollments', filter=Q(enrollments__is_active=True))
        )
        .values('course_code', 'name', 'max_students', 'enrolled_count')[:10]
    )

    # Recent enrollments (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_enrollments = Enrollment.objects.filter(
        enrollment_date__gte=thirty_days_ago
    ).count()

    # Grade distribution
    grade_distribution = list(
        Grade.objects.values('letter_grade')
        .annotate(count=Count('id'))
        .order_by('letter_grade')
    )

    # Average attendance percentage
    total_attendance_records = Attendance.objects.count()
    present_records = Attendance.objects.filter(status__in=['PRESENT', 'LATE']).count()
    avg_attendance = (present_records / total_attendance_records * 100) if total_attendance_records > 0 else 0

    return Response({
        'overview': {
            'total_students': total_students,
            'total_courses': total_courses,
            'total_teachers': total_teachers,
            'total_departments': total_departments,
            'recent_enrollments': recent_enrollments,
            'average_attendance_percentage': round(avg_attendance, 2)
        },
        'students_by_department': students_by_dept,
        'students_by_year': students_by_year,
        'course_enrollment_stats': course_enrollment_stats,
        'grade_distribution': grade_distribution,
        'generated_at': timezone.now()
    })


# ============================================================================
# ENDPOINT 9: Bulk Operations & Advanced Queries
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_attendance_mark(request):
    """
    POST: Mark attendance for multiple students at once

    Expected payload:
    {
        "course_id": 1,
        "date": "2024-01-15",
        "attendance_records": [
            {"student_id": 1, "status": "PRESENT"},
            {"student_id": 2, "status": "ABSENT"},
            ...
        ],
        "marked_by": 1
    }
    """
    course_id = request.data.get('course_id')
    date = request.data.get('date')
    attendance_records = request.data.get('attendance_records', [])
    marked_by_id = request.data.get('marked_by')

    if not all([course_id, date, attendance_records, marked_by_id]):
        return Response(
            {"error": "Missing required fields: course_id, date, attendance_records, marked_by"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        course = Course.objects.get(id=course_id)
        marked_by = Teacher.objects.get(id=marked_by_id)

        created_records = []
        errors = []

        for record in attendance_records:
            student_id = record.get('student_id')
            attendance_status = record.get('status')

            try:
                # Get enrollment
                enrollment = Enrollment.objects.get(
                    student_id=student_id,
                    course=course,
                    is_active=True
                )

                # Create or update attendance
                attendance, created = Attendance.objects.get_or_create(
                    enrollment=enrollment,
                    date=date,
                    defaults={
                        'status': attendance_status,
                        'marked_by': marked_by
                    }
                )

                if not created:
                    attendance.status = attendance_status
                    attendance.marked_by = marked_by
                    attendance.save()

                created_records.append({
                    'student_id': student_id,
                    'status': attendance_status,
                    'created': created
                })

            except Enrollment.DoesNotExist:
                errors.append(f"Student {student_id} is not enrolled in this course")
            except Exception as e:
                errors.append(f"Error processing student {student_id}: {str(e)}")

        return Response({
            'message': f'Processed {len(created_records)} attendance records',
            'created_records': created_records,
            'errors': errors
        }, status=status.HTTP_201_CREATED)

    except Course.DoesNotExist:
        return Response(
            {"error": "Course not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Teacher.DoesNotExist:
        return Response(
            {"error": "Teacher not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_performance_report(request, student_id):
    """
    GET: Comprehensive performance report for a specific student

    Returns:
    - Student basic info
    - All enrollments with grades and attendance
    - Overall GPA and attendance percentage
    - Performance trends
    """
    try:
        student = Student.objects.get(id=student_id)

        # Get all enrollments with related data
        enrollments = Enrollment.objects.filter(
            student=student
        ).select_related('course').prefetch_related('grades', 'attendance_records')

        enrollment_data = []
        total_grade_points = 0
        total_credits = 0
        total_attendance_records = 0
        present_records = 0

        for enrollment in enrollments:
            # Calculate course GPA
            grades = enrollment.grades.all()
            course_avg = grades.aggregate(avg_percentage=Avg('percentage'))['avg_percentage'] or 0

            # Calculate attendance percentage
            attendance_records = enrollment.attendance_records.all()
            course_attendance_count = attendance_records.count()
            course_present_count = attendance_records.filter(status__in=['PRESENT', 'LATE']).count()
            course_attendance_percentage = (course_present_count / course_attendance_count * 100) if course_attendance_count > 0 else 0

            # Add to totals for overall calculations
            if course_avg > 0:
                total_grade_points += course_avg * enrollment.course.credits
                total_credits += enrollment.course.credits

            total_attendance_records += course_attendance_count
            present_records += course_present_count

            enrollment_data.append({
                'course_code': enrollment.course.course_code,
                'course_name': enrollment.course.name,
                'credits': enrollment.course.credits,
                'status': enrollment.status,
                'final_grade': enrollment.final_grade,
                'average_percentage': round(course_avg, 2),
                'attendance_percentage': round(course_attendance_percentage, 2),
                'total_grades': grades.count(),
                'enrollment_date': enrollment.enrollment_date
            })

        # Calculate overall statistics
        overall_gpa = (total_grade_points / total_credits) if total_credits > 0 else 0
        overall_attendance = (present_records / total_attendance_records * 100) if total_attendance_records > 0 else 0

        return Response({
            'student': StudentSerializer(student).data,
            'enrollments': enrollment_data,
            'overall_statistics': {
                'gpa': round(overall_gpa, 2),
                'attendance_percentage': round(overall_attendance, 2),
                'total_courses': enrollments.count(),
                'completed_courses': enrollments.filter(status='COMPLETED').count(),
                'active_enrollments': enrollments.filter(is_active=True).count(),
                'total_credits': total_credits
            },
            'generated_at': timezone.now()
        })

    except Student.DoesNotExist:
        return Response(
            {"error": "Student not found"},
            status=status.HTTP_404_NOT_FOUND
        )


# ============================================================================
# WEB INTERFACE VIEWS (For Frontend Dashboard)
# ============================================================================

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Avg


def dashboard_view(request):
    """
    Main dashboard view with statistics and charts
    """
    # Get basic statistics
    total_students = Student.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_teachers = Teacher.objects.filter(is_active=True).count()
    total_departments = Department.objects.count()

    # Students by department
    students_by_department = list(
        Department.objects.annotate(
            student_count=Count('students', filter=Q(students__is_active=True))
        ).values('name', 'student_count')
    )

    # Students by year
    students_by_year = list(
        Student.objects.filter(is_active=True)
        .values('year_of_study')
        .annotate(count=Count('id'))
        .order_by('year_of_study')
    )

    # Recent enrollments
    recent_enrollments = Enrollment.objects.select_related(
        'student', 'course'
    ).order_by('-enrollment_date')[:10]

    # Calculate average attendance
    total_attendance_records = Attendance.objects.count()
    present_records = Attendance.objects.filter(status__in=['PRESENT', 'LATE']).count()
    avg_attendance = (present_records / total_attendance_records * 100) if total_attendance_records > 0 else 0

    # Recent enrollments count (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_enrollments_count = Enrollment.objects.filter(
        enrollment_date__gte=thirty_days_ago
    ).count()

    context = {
        'stats': {
            'total_students': total_students,
            'total_courses': total_courses,
            'total_teachers': total_teachers,
            'total_departments': total_departments,
            'average_attendance_percentage': avg_attendance,
            'recent_enrollments': recent_enrollments_count,
            'generated_at': timezone.now(),
        },
        'students_by_department': students_by_department,
        'students_by_year': students_by_year,
        'recent_enrollments': recent_enrollments,
    }

    return render(request, 'dashboard.html', context)


def student_list_view(request):
    """
    Student list view with search and filtering
    """
    students = Student.objects.select_related('department').all()

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Filter by active status
    is_active = request.GET.get('is_active')
    if is_active is not None:
        students = students.filter(is_active=is_active.lower() == 'true')

    # Filter by year
    year_of_study = request.GET.get('year_of_study')
    if year_of_study:
        students = students.filter(year_of_study=year_of_study)

    # Filter by department
    department = request.GET.get('department')
    if department:
        students = students.filter(department_id=department)

    # Pagination
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Additional statistics
    active_count = students.filter(is_active=True).count()
    departments_count = students.values('department').distinct().count()
    avg_year = students.aggregate(avg_year=Avg('year_of_study'))['avg_year'] or 0

    context = {
        'students': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'active_count': active_count,
        'departments_count': departments_count,
        'avg_year': avg_year,
    }

    return render(request, 'student_list.html', context)


def student_detail_view(request, pk):
    """
    Student detail view with performance information
    """
    student = get_object_or_404(Student, pk=pk)

    # Get enrollments with related data
    enrollments = Enrollment.objects.filter(
        student=student
    ).select_related('course').prefetch_related('grades', 'attendance_records')

    # Calculate performance metrics
    total_courses = enrollments.count()
    active_enrollments = enrollments.filter(is_active=True).count()
    completed_courses = enrollments.filter(status='COMPLETED').count()

    # Calculate GPA
    total_grade_points = 0
    total_credits = 0

    for enrollment in enrollments:
        grades = enrollment.grades.all()
        if grades:
            course_avg = grades.aggregate(avg_percentage=Avg('percentage'))['avg_percentage'] or 0
            if course_avg > 0:
                total_grade_points += course_avg * enrollment.course.credits
                total_credits += enrollment.course.credits

    gpa = (total_grade_points / total_credits) if total_credits > 0 else 0

    # Calculate overall attendance
    total_attendance = 0
    present_attendance = 0

    for enrollment in enrollments:
        attendance_records = enrollment.attendance_records.all()
        total_attendance += attendance_records.count()
        present_attendance += attendance_records.filter(status__in=['PRESENT', 'LATE']).count()

    attendance_percentage = (present_attendance / total_attendance * 100) if total_attendance > 0 else 0

    context = {
        'student': student,
        'enrollments': enrollments,
        'total_courses': total_courses,
        'active_enrollments': active_enrollments,
        'completed_courses': completed_courses,
        'gpa': gpa,
        'attendance_percentage': attendance_percentage,
    }

    return render(request, 'student_detail.html', context)


def course_list_view(request):
    """
    Course list view with search and filtering
    """
    courses = Course.objects.select_related('department', 'teacher__user').all()

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        courses = courses.filter(
            Q(name__icontains=search_query) |
            Q(course_code__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Filter by department
    department = request.GET.get('department')
    if department:
        courses = courses.filter(department_id=department)

    # Filter by semester
    semester = request.GET.get('semester')
    if semester:
        courses = courses.filter(semester=semester)

    # Filter by active status
    is_active = request.GET.get('is_active')
    if is_active is not None:
        courses = courses.filter(is_active=is_active.lower() == 'true')

    # Pagination
    paginator = Paginator(courses, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'courses': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'departments': Department.objects.all(),
    }

    return render(request, 'course_list.html', context)


def teacher_list_view(request):
    """
    Teacher list view
    """
    teachers = Teacher.objects.select_related('user', 'department').all()

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        teachers = teachers.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(employee_id__icontains=search_query)
        )

    # Filter by department
    department = request.GET.get('department')
    if department:
        teachers = teachers.filter(department_id=department)

    # Pagination
    paginator = Paginator(teachers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'teachers': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'departments': Department.objects.all(),
    }

    return render(request, 'teacher_list.html', context)


def enrollment_list_view(request):
    """
    Enrollment list view
    """
    enrollments = Enrollment.objects.select_related(
        'student', 'course', 'course__department'
    ).all()

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        enrollments = enrollments.filter(status=status_filter)

    # Filter by course
    course = request.GET.get('course')
    if course:
        enrollments = enrollments.filter(course_id=course)

    # Pagination
    paginator = Paginator(enrollments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'enrollments': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'courses': Course.objects.filter(is_active=True),
    }

    return render(request, 'enrollment_list.html', context)
