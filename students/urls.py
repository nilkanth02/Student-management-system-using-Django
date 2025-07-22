from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # ============================================================================
    # WEB INTERFACE ROUTES
    # ============================================================================
    path('', views.dashboard_view, name='dashboard'),
    path('web/students/', views.student_list_view, name='student_list'),
    path('web/students/<int:pk>/', views.student_detail_view, name='student_detail'),
    path('web/courses/', views.course_list_view, name='course_list'),
    path('web/teachers/', views.teacher_list_view, name='teacher_list'),
    path('web/enrollments/', views.enrollment_list_view, name='enrollment_list'),

    # ============================================================================
    # API ENDPOINT 1: Student Management (CRUD Operations)
    # ============================================================================
    path('api/students/', views.StudentListCreateView.as_view(), name='student-list-create'),
    path('api/students/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    
    # ============================================================================
    # API ENDPOINT 2: Course Management (CRUD Operations)
    # ============================================================================
    path('api/courses/', views.CourseListCreateView.as_view(), name='course-list-create'),
    path('api/courses/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),

    # ============================================================================
    # API ENDPOINT 3: Enrollment Management
    # ============================================================================
    path('api/enrollments/', views.EnrollmentListCreateView.as_view(), name='enrollment-list-create'),
    path('api/enrollments/<int:pk>/', views.EnrollmentDetailView.as_view(), name='enrollment-detail'),

    # ============================================================================
    # API ENDPOINT 4: Grade Management
    # ============================================================================
    path('api/grades/', views.GradeListCreateView.as_view(), name='grade-list-create'),
    path('api/grades/<int:pk>/', views.GradeDetailView.as_view(), name='grade-detail'),

    # ============================================================================
    # API ENDPOINT 5: Attendance Management
    # ============================================================================
    path('api/attendance/', views.AttendanceListCreateView.as_view(), name='attendance-list-create'),
    path('api/attendance/<int:pk>/', views.AttendanceDetailView.as_view(), name='attendance-detail'),

    # ============================================================================
    # API ENDPOINT 6: Department Management
    # ============================================================================
    path('api/departments/', views.DepartmentListCreateView.as_view(), name='department-list-create'),
    path('api/departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department-detail'),

    # ============================================================================
    # API ENDPOINT 7: Teacher Management
    # ============================================================================
    path('api/teachers/', views.TeacherListCreateView.as_view(), name='teacher-list-create'),
    path('api/teachers/<int:pk>/', views.TeacherDetailView.as_view(), name='teacher-detail'),

    # ============================================================================
    # API ENDPOINT 8: Analytics & Dashboard Data
    # ============================================================================
    path('api/analytics/dashboard/', views.dashboard_analytics, name='dashboard-analytics'),

    # ============================================================================
    # API ENDPOINT 9: Bulk Operations & Advanced Queries
    # ============================================================================
    path('api/attendance/bulk-mark/', views.bulk_attendance_mark, name='bulk-attendance-mark'),
    path('api/students/<int:student_id>/performance-report/', views.student_performance_report, name='student-performance-report'),
]

# API Documentation URLs (for easy reference)
"""
API Endpoints Summary:

1. Student Management:
   - GET/POST /api/students/ - List all students / Create new student
   - GET/PUT/PATCH/DELETE /api/students/{id}/ - Student details and operations

2. Course Management:
   - GET/POST /api/courses/ - List all courses / Create new course
   - GET/PUT/PATCH/DELETE /api/courses/{id}/ - Course details and operations

3. Enrollment Management:
   - GET/POST /api/enrollments/ - List enrollments / Enroll student in course
   - GET/PUT/PATCH/DELETE /api/enrollments/{id}/ - Enrollment details and operations

4. Grade Management:
   - GET/POST /api/grades/ - List grades / Add new grade
   - GET/PUT/PATCH/DELETE /api/grades/{id}/ - Grade details and operations

5. Attendance Management:
   - GET/POST /api/attendance/ - List attendance / Mark attendance
   - GET/PUT/PATCH/DELETE /api/attendance/{id}/ - Attendance details and operations

6. Department Management:
   - GET/POST /api/departments/ - List departments / Create department
   - GET/PUT/PATCH/DELETE /api/departments/{id}/ - Department details and operations

7. Teacher Management:
   - GET/POST /api/teachers/ - List teachers / Create teacher
   - GET/PUT/PATCH/DELETE /api/teachers/{id}/ - Teacher details and operations

8. Analytics & Dashboard:
   - GET /api/analytics/dashboard/ - Get comprehensive dashboard analytics

9. Bulk Operations & Reports:
   - POST /api/attendance/bulk-mark/ - Mark attendance for multiple students
   - GET /api/students/{id}/performance-report/ - Get detailed student performance report

Features:
- All endpoints support filtering, searching, and pagination
- Token-based authentication required
- Comprehensive error handling and validation
- Optimized database queries with select_related and prefetch_related
- Soft delete for students, teachers, and courses
- Automatic calculation of grades, attendance percentages, and statistics
"""
