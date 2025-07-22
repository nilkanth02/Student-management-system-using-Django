from rest_framework import permissions
from .models import Teacher


class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow teachers to edit data.
    Students and other users can only read.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for teachers or superusers
        if request.user and request.user.is_authenticated:
            return (
                request.user.is_superuser or 
                hasattr(request.user, 'teacher')
            )
        
        return False


class IsOwnerOrTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow:
    - Students to view/edit their own data
    - Teachers to view/edit any student data
    - Superusers to do anything
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Superuser can do anything
        if request.user.is_superuser:
            return True
        
        # Teachers can edit any student data
        if hasattr(request.user, 'teacher'):
            return True
        
        # Students can only edit their own data
        if hasattr(obj, 'student_id'):  # For Student model
            # This would require linking User to Student model
            # For now, we'll allow teachers only for write operations
            return False
        
        return False


class IsTeacherOfCourse(permissions.BasePermission):
    """
    Permission to allow only the teacher of a course to manage
    grades and attendance for that course.
    """
    
    def has_object_permission(self, request, view, obj):
        # Superuser can do anything
        if request.user.is_superuser:
            return True
        
        # Check if user is a teacher
        if not hasattr(request.user, 'teacher'):
            return False
        
        teacher = request.user.teacher
        
        # For Grade and Attendance objects
        if hasattr(obj, 'enrollment'):
            return obj.enrollment.course.teacher == teacher
        
        # For Enrollment objects
        if hasattr(obj, 'course'):
            return obj.course.teacher == teacher
        
        return False


class IsDepartmentMemberOrReadOnly(permissions.BasePermission):
    """
    Permission to allow department members to manage
    department-related data.
    """
    
    def has_permission(self, request, view):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions for teachers or superusers
        return (
            request.user and request.user.is_authenticated and
            (request.user.is_superuser or hasattr(request.user, 'teacher'))
        )
    
    def has_object_permission(self, request, view, obj):
        # Superuser can do anything
        if request.user.is_superuser:
            return True
        
        # Teachers can manage their department's data
        if hasattr(request.user, 'teacher'):
            teacher = request.user.teacher
            
            # For Department objects
            if hasattr(obj, 'name'):  # Department model
                return obj == teacher.department
            
            # For objects with department relationship
            if hasattr(obj, 'department'):
                return obj.department == teacher.department
        
        return False
