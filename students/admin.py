from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Department, Teacher, Student, Course, Enrollment, Grade, Attendance


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'head_of_department', 'students_count', 'teachers_count', 'courses_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code', 'head_of_department']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'head_of_department')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def students_count(self, obj):
        count = obj.students.filter(is_active=True).count()
        url = reverse('admin:students_student_changelist') + f'?department__id__exact={obj.id}'
        return format_html('<a href="{}">{} students</a>', url, count)
    students_count.short_description = 'Active Students'

    def teachers_count(self, obj):
        count = obj.teachers.filter(is_active=True).count()
        url = reverse('admin:students_teacher_changelist') + f'?department__id__exact={obj.id}'
        return format_html('<a href="{}">{} teachers</a>', url, count)
    teachers_count.short_description = 'Active Teachers'

    def courses_count(self, obj):
        count = obj.courses.filter(is_active=True).count()
        url = reverse('admin:students_course_changelist') + f'?department__id__exact={obj.id}'
        return format_html('<a href="{}">{} courses</a>', url, count)
    courses_count.short_description = 'Active Courses'


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'department', 'qualification', 'experience_years', 'is_active', 'hire_date']
    list_filter = ['department', 'qualification', 'is_active', 'hire_date']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'user__email']
    ordering = ['user__last_name', 'user__first_name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Teacher Details', {
            'fields': ('employee_id', 'department', 'phone', 'qualification', 'experience_years', 'salary')
        }),
        ('Employment', {
            'fields': ('hire_date', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    full_name.short_description = 'Full Name'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'full_name', 'email', 'department', 'year_of_study', 'is_active', 'admission_date']
    list_filter = ['department', 'year_of_study', 'gender', 'is_active', 'admission_date']
    search_fields = ['student_id', 'first_name', 'last_name', 'email']
    ordering = ['last_name', 'first_name']
    readonly_fields = ['age', 'created_at', 'updated_at']

    fieldsets = (
        ('Personal Information', {
            'fields': ('student_id', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'age', 'gender', 'address')
        }),
        ('Academic Information', {
            'fields': ('department', 'year_of_study', 'admission_date', 'graduation_date', 'is_active')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['activate_students', 'deactivate_students']

    def activate_students(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} students were successfully activated.')
    activate_students.short_description = "Activate selected students"

    def deactivate_students(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} students were successfully deactivated.')
    deactivate_students.short_description = "Deactivate selected students"


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_code', 'name', 'department', 'teacher', 'credits', 'semester', 'year', 'enrollment_info', 'is_active']
    list_filter = ['department', 'teacher', 'semester', 'year', 'credits', 'is_active']
    search_fields = ['course_code', 'name', 'description']
    ordering = ['course_code']
    readonly_fields = ['enrolled_students_count', 'available_slots', 'created_at', 'updated_at']

    fieldsets = (
        ('Course Information', {
            'fields': ('course_code', 'name', 'description', 'department', 'teacher', 'credits')
        }),
        ('Schedule & Capacity', {
            'fields': ('semester', 'year', 'max_students', 'enrolled_students_count', 'available_slots', 'schedule', 'classroom')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def enrollment_info(self, obj):
        enrolled = obj.enrolled_students_count
        total = obj.max_students
        percentage = (enrolled / total * 100) if total > 0 else 0

        color = 'green' if percentage < 80 else 'orange' if percentage < 100 else 'red'
        return format_html(
            '<span style="color: {};">{}/{} ({:.1f}%)</span>',
            color, enrolled, total, percentage
        )
    enrollment_info.short_description = 'Enrollment'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'enrollment_date', 'final_grade', 'is_active']
    list_filter = ['status', 'is_active', 'enrollment_date', 'course__department', 'course__semester', 'course__year']
    search_fields = ['student__first_name', 'student__last_name', 'student__student_id', 'course__course_code', 'course__name']
    ordering = ['-enrollment_date']
    readonly_fields = ['enrollment_date', 'created_at', 'updated_at']

    fieldsets = (
        ('Enrollment Information', {
            'fields': ('student', 'course', 'enrollment_date', 'status', 'is_active')
        }),
        ('Completion', {
            'fields': ('final_grade', 'completion_date'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_completed', 'mark_dropped']

    def mark_completed(self, request, queryset):
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f'{updated} enrollments were marked as completed.')
    mark_completed.short_description = "Mark selected enrollments as completed"

    def mark_dropped(self, request, queryset):
        updated = queryset.update(status='DROPPED', is_active=False)
        self.message_user(request, f'{updated} enrollments were marked as dropped.')
    mark_dropped.short_description = "Mark selected enrollments as dropped"


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'course_code', 'assessment_type', 'assessment_name', 'points_display', 'letter_grade', 'assessment_date']
    list_filter = ['assessment_type', 'letter_grade', 'assessment_date', 'enrollment__course__department']
    search_fields = ['enrollment__student__first_name', 'enrollment__student__last_name', 'enrollment__course__course_code', 'assessment_name']
    ordering = ['-assessment_date']
    readonly_fields = ['percentage', 'letter_grade', 'created_at', 'updated_at']

    fieldsets = (
        ('Assessment Information', {
            'fields': ('enrollment', 'assessment_type', 'assessment_name', 'assessment_date')
        }),
        ('Grading', {
            'fields': ('points_earned', 'points_possible', 'percentage', 'letter_grade', 'comments')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def student_name(self, obj):
        return obj.enrollment.student.full_name
    student_name.short_description = 'Student'

    def course_code(self, obj):
        return obj.enrollment.course.course_code
    course_code.short_description = 'Course'

    def points_display(self, obj):
        return f"{obj.points_earned}/{obj.points_possible} ({obj.percentage:.1f}%)"
    points_display.short_description = 'Points (Percentage)'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'course_code', 'date', 'status', 'marked_by', 'created_at']
    list_filter = ['status', 'date', 'enrollment__course__department', 'marked_by']
    search_fields = ['enrollment__student__first_name', 'enrollment__student__last_name', 'enrollment__course__course_code']
    ordering = ['-date']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Attendance Information', {
            'fields': ('enrollment', 'date', 'status', 'marked_by')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_present', 'mark_absent']

    def student_name(self, obj):
        return obj.enrollment.student.full_name
    student_name.short_description = 'Student'

    def course_code(self, obj):
        return obj.enrollment.course.course_code
    course_code.short_description = 'Course'

    def mark_present(self, request, queryset):
        updated = queryset.update(status='PRESENT')
        self.message_user(request, f'{updated} attendance records were marked as present.')
    mark_present.short_description = "Mark selected records as present"

    def mark_absent(self, request, queryset):
        updated = queryset.update(status='ABSENT')
        self.message_user(request, f'{updated} attendance records were marked as absent.')
    mark_absent.short_description = "Mark selected records as absent"


# Customize admin site headers
admin.site.site_header = "Student Management System"
admin.site.site_title = "SMS Admin"
admin.site.index_title = "Welcome to Student Management System Administration"
