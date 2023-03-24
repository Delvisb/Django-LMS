from django.urls import path, include
from . import views

urlpatterns = [
    #Universal Urls 
    path('', views.login),
    path('register/', views.register, name = "register"),
    path('login/', views.login, name = "login"),
    path('logout/', views.log_out, name = "logout"),
    path('serveFile/<str:file_url>', views.serveFile, name = "serveFile"), 
    
    # Educator Urlss
    path('educator/', include(([
        path('home/', views.educatorHome, name = "educatorHome"),
        path('profile/', views.educatorProfile, name = "educatorProfile"),
        path('courses/', include(([
            path('<str:course_name>/', views.educatorCourses, name = "educatorCourses"),
            path('<str:course_name>/students/', views.educatorStudents, name = "educatorStudents"),
            path('<str:course_name>/assigments/', views.educatorAssignments, name = "educatorAssignments"),
            path('<str:course_name>/viewAssignment/<int:assignment_id>', views.educatorViewAssignment, name = "educatorViewAssignment"),
            path('<str:course_name>/attendance/<str:date>', views.educatorAttendance, name = "educatorAttendance"),
            path('<str:course_name>/grades/', views.educatorGrades, name = "educatorGrades"),
            path('<str:course_name>/viewSubmission/<int:submission_id>', views.educatorViewSubmission, name = "educatorViewSubmission"),
        ])))
    ]))),
    
    # Student Urls
    path('student/', include(([
        path('home/', views.studentHome, name = "studentHome"),
        path('profile/', views.studentProfile, name = "studentProfile"),
        path('courses/', include(([
            path('<str:course_name>/', views.studentCourses, name = "studentCourses"),
            path('<str:course_name>/assigments/', views.studentAssignments, name = "studentAssignments"),
            path('<str:course_name>/viewAssignment/<int:assignment_id>', views.studentViewAssignment, name = "studentViewAssignment"),
            path('<str:course_name>/attendance/', views.studentAttendance, name = "studentAttendance"),
            path('<str:course_name>/grades/', views.studentGrades, name = "studentGrades")
        ]))),
    ])))
]
