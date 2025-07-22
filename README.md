# Student Management System

A comprehensive web-based Student Management System built with Django and Django REST Framework. This system provides both a user-friendly web interface and a powerful REST API for managing students, courses, teachers, enrollments, grades, and attendance.

## 🚀 Features

### Core Functionality
- **Student Management**: Complete CRUD operations for student records
- **Course Management**: Manage courses with enrollment tracking
- **Teacher Management**: Handle teacher profiles and assignments
- **Enrollment System**: Track student course enrollments
- **Grade Management**: Record and calculate student grades
- **Attendance Tracking**: Mark and monitor student attendance
- **Department Organization**: Organize courses and staff by departments
- **Analytics Dashboard**: Comprehensive statistics and visualizations

### Technical Features
- **REST API**: 9 comprehensive API endpoints with full CRUD operations
- **Web Interface**: Clean, responsive Bootstrap-based UI
- **Authentication**: Token-based API authentication
- **Admin Panel**: Full Django admin interface for data management
- **Data Validation**: Comprehensive validation and error handling
- **Search & Filtering**: Advanced search and filtering capabilities
- **Pagination**: Efficient data pagination
- **Sample Data**: Management command to generate test data

## 🛠️ Technology Stack

- **Backend**: Django 5.2.4, Django REST Framework 3.16.0
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Frontend**: Bootstrap 5, Chart.js for visualizations
- **Authentication**: Django Token Authentication
- **API Documentation**: Built-in browsable API

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone <https://github.com/nilkanth02/Student-management-system-using-Django.git>
cd student_management_system/Home
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install django djangorestframework django-filter
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Load Sample Data (Optional)
```bash
python manage.py create_sample_data
```

### 8. Run Development Server
```bash
python manage.py runserver
```

## 🌐 Access Points

- **Web Dashboard**: http://127.0.0.1:8000/api/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Root**: http://127.0.0.1:8000/api/
- **API Documentation**: http://127.0.0.1:8000/api/ (browsable API)

### Default Login Credentials
- **Username**: admin
- **Password**: admin123

## 📊 API Endpoints

### 1. Students
- `GET/POST /api/api/students/` - List/Create students
- `GET/PUT/DELETE /api/api/students/{id}/` - Student details

### 2. Courses
- `GET/POST /api/api/courses/` - List/Create courses
- `GET/PUT/DELETE /api/api/courses/{id}/` - Course details

### 3. Teachers
- `GET/POST /api/api/teachers/` - List/Create teachers
- `GET/PUT/DELETE /api/api/teachers/{id}/` - Teacher details

### 4. Enrollments
- `GET/POST /api/api/enrollments/` - List/Create enrollments
- `GET/PUT/DELETE /api/api/enrollments/{id}/` - Enrollment details

### 5. Grades
- `GET/POST /api/api/grades/` - List/Create grades
- `GET/PUT/DELETE /api/api/grades/{id}/` - Grade details

### 6. Attendance
- `GET/POST /api/api/attendance/` - List/Create attendance
- `GET/PUT/DELETE /api/api/attendance/{id}/` - Attendance details

### 7. Departments
- `GET/POST /api/api/departments/` - List/Create departments
- `GET/PUT/DELETE /api/api/departments/{id}/` - Department details

### 8. Analytics
- `GET /api/api/analytics/dashboard/` - Dashboard analytics

### 9. Bulk Operations
- `POST /api/api/attendance/bulk-mark/` - Bulk attendance marking
- `GET /api/api/students/{id}/performance-report/` - Student performance report

## 🔐 Authentication

### API Token Authentication
1. Obtain token: `POST /api-token-auth/` with username/password
2. Include in headers: `Authorization: Token your_token_here`

### Example API Usage
```bash
# Get token
curl -X POST http://127.0.0.1:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use token to access API
curl -H "Authorization: Token your_token_here" \
  http://127.0.0.1:8000/api/api/students/
```

## 📱 Web Interface Features

### Dashboard
- Overview statistics (students, courses, teachers, departments)
- Interactive charts showing student distribution
- Recent enrollments list
- Quick action buttons

### Student Management
- Searchable student list with filtering
- Detailed student profiles
- Performance tracking
- Contact information management

### Course Management
- Course catalog with enrollment tracking
- Teacher assignments
- Schedule management
- Capacity monitoring

## 🚀 Deployment

### For Production Deployment:

1. **Environment Variables**
```bash
export DEBUG=False
export SECRET_KEY='your-secret-key'
export DATABASE_URL='your-database-url'
```

2. **Database Setup** (PostgreSQL recommended)
```bash
pip install psycopg2-binary
```

3. **Static Files**
```bash
python manage.py collectstatic
```

4. **WSGI Server** (Gunicorn recommended)
```bash
pip install gunicorn
gunicorn student_management.wsgi:application
```



## 📝 Project Structure

```
student_management_system/
├── Home/
│   ├── manage.py
│   ├── student_management/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── students/
│       ├── models.py          # Database models
│       ├── views.py           # API and web views
│       ├── serializers.py     # API serializers
│       ├── urls.py            # URL routing
│       ├── admin.py           # Admin interface
│       ├── permissions.py     # Custom permissions
│       ├── templates/         # Web templates
│       └── management/        # Custom commands
└── README.md                  # This file
```

## 🎯 Key Features for Recruiters

### Technical Skills Demonstrated
- **Django Framework**: Full-stack web development
- **REST API Development**: Professional API design
- **Database Design**: Normalized database schema
- **Authentication & Security**: Token-based auth, permissions
- **Frontend Development**: Responsive web interface
- **Code Organization**: Clean, maintainable code structure

### Business Logic
- **Educational Domain**: Real-world application
- **Data Relationships**: Complex model relationships
- **Performance Optimization**: Efficient database queries
- **User Experience**: Intuitive interface design
- **Scalability**: Designed for growth

## 🧪 Testing

Run the development server and test:
```bash
python manage.py runserver
```

Visit the web interface and admin panel to explore all features.

