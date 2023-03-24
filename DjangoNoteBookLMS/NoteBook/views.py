from django.shortcuts import render, redirect
from django.http import request, HttpResponseRedirect, FileResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login as loginUser, logout
from django.core.files.storage import FileSystemStorage
from .models import User, Course, Enrollment, Attendance, Assignment, Submission, Grade, Gpa
from datetime import datetime, timedelta
# python3 manage.py runserver 0.0.0.0:8000
# python3 manage.py migrate --fake NoteBook 
# python3 manage.py makemigrations 
# python3 manage.py migrate
# python3 manage.py inspectdb

# Universal Views
def register(request):
    if request.method == "GET":
        return render(request, 'register.html')     
    else:
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmedPassword = request.POST['password']
        userType = request.POST['userType']
        current_day = datetime.today()
        current_day = datetime.strftime(current_day, "%Y-%m-%d")
        if confirmedPassword != password:
            context= {'message': "Passwords don't match"}
            return render(request, 'register.html', {'context': context})

        if User.objects.filter(username=username).exists():
            context= {'message': 'Username is already in use' }
            return render(request, 'register.html', {'context': context})
        else: 
            if userType == "Educator":
                newUser = User(first_name = firstname, last_name = lastname, email = email, username = username, is_superuser = True, date_joined = current_day, last_login = current_day)
                newUser.set_password(password)
                user = newUser.save()
                loginUser(request, user)
                return redirect('educatorHome')
            else:
                newUser = User(first_name = firstname, last_name = lastname, email = email, username = username, is_superuser = False, date_joined = current_day, last_login = current_day)
                newUser.set_password(password)
                user = newUser.save()
                loginUser(request, user)
                return redirect('studentHome')

def login(request): 
    if request.method == "GET":
        return render(request, 'login.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_superuser:
                loginUser(request, user)
                return redirect('educatorHome')
            else: 
                loginUser(request, user)
                return redirect('studentHome')
        else: 
            context= {'message': 'Credentials are not correct'}
            return render(request, 'login.html', {'context': context})

def log_out(request):
    if request.method == "GET":
        logout(request)
        return redirect('login')
    else:
        pass


def updateGrade(student_id, newGrade, course):
    if Gpa.objects.filter(student_id = student_id, course_id = course).exists():
        studentGpa = Gpa.objects.get(student_id = student_id, course_id = course)
        currentGPa = float(studentGpa.gpa)
        studentGpa =  currentGPa + float(newGrade) / Grade.objects.filter(student_id = student_id).count()
    else:
        studentGpa = Gpa(student_id = student_id, gpa = newGrade, course_id = course)
        studentGpa.save()

def savefile(assignment_file, assignment_file_name):               
    folder = 'NoteBook/static' 
    fs = FileSystemStorage(location = folder)
    filename = fs.save(assignment_file_name, assignment_file)
    return assignment_file_name

def serveFile(request, file_url):
    filename = f"./NoteBook/static/{file_url}"
    response = FileResponse(open(filename, 'rb'))
    return response

@login_required(login_url='login')
def educatorHome(request): 
    if request.method == "GET":
        if Course.objects.filter(educator_id = request.user.id).count() > 0 : 
            context = {'courses': Course.objects.all().filter(educator_id = request.user.id)}
            return render(request, 'educatorHome.html', {'context': context})
        else:
            return render(request, 'educatorHome.html')
    else:
        course_name = request.POST['course_name']
        course_subject = request.POST['course_subject']
        course_description = request.POST['course_description']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        newCourse = Course(educator_id = request.user, course_name = course_name, course_subject = course_subject, course_description = course_description, start_date = start_date, end_date = end_date)
        newCourse.save()
        return redirect('educatorHome')

@login_required(login_url='login')
def educatorProfile(request):
    if request.method == "GET":
        user = User.objects.filter(username = request.user).values('first_name', 'last_name', 'email', 'username', 'date_joined')
        context = {
            'user_details': user,
            'course_count': Course.objects.filter(educator_id = request.user).count()
        }
        return render(request, 'educatorProfile.html', {'context': context})
    else:
        pass

@login_required(login_url='login')
def educatorCourses(request, course_name): 
    if request.method == "GET":
        current_day = datetime.today()
        current_day = datetime.strftime(current_day, "%Y-%m-%d")
        context = { 'course_name': course_name, 'course': Course.objects.get(course_name = course_name), 'date': current_day}
        return render(request, 'educatorCourses.html', {'context': context})
    else:
        course_to_update =  Course.objects.get(educator_id = request.user.id, course_name = request.POST['course_name'],  course_subject = request.POST['course_subject'])
        course_to_update.course_name = request.post['new_course_name']
        course_to_update.course_subject = request.post['new_course_subject']
        course_to_update.start_date = request.post['new_start_date']
        course_to_update.end_date = request.post['new_end_date']
        course_to_update.course_description = request.post['new_course_description']
        course_to_update.save()
        return redirect('educatorCourses', course_name = course_name)

@login_required(login_url='login')
def educatorStudents(request, course_name): 
    if request.method == "GET":
        id = Course.objects.filter(course_name = course_name).values('id')
        current_day = datetime.today()
        current_day = datetime.strftime(current_day, "%Y-%m-%d")
        context = {
            'course_name': course_name,
            'students_list':  User.objects.all().filter(is_superuser = 0).values('first_name', 'last_name'),
            'student_enrolled': Enrollment.objects.all().filter(course_id = id[0]['id']), 
            'date': current_day
        }
        return render(request, 'educatorStudents.html', {'context': context})
    else:
        if request.POST.get('student_to_add'):
            student_to_add = request.POST['student_to_add']
            student = student_to_add.split()
            student_to_add = User.objects.get(first_name = student[0],last_name = student[1])
            course_to_add = Course.objects.get(course_name = course_name)
            exists = Enrollment.objects.filter(student_id = student_to_add, course_id = course_to_add).exists()
            if exists:
                pass
            else:
                student_added = Enrollment(student_id = student_to_add, course_id = course_to_add)
                student_added.save()
                
            return redirect('educatorStudents',course_name=course_name)   
        elif request.POST.get('student_to_delete'):      
            student_to_delete = request.POST['student_to_delete']
            student = student_to_delete.split()
            student_to_delete = User.objects.get(first_name = student[0],last_name = student[1])
            deleted_student = Enrollment.objects.get(student_id= student_to_delete.id)
            deleted_student.delete()
            return redirect('educatorStudents',course_name=course_name)   

@login_required(login_url='login')
def educatorAssignments(request, course_name): 
    if request.method == "GET":
        current_day = datetime.today()
        current_day = datetime.strftime(current_day, "%Y-%m-%d")
        course_id = Course.objects.get(course_name = course_name)
        context = {
            'course_name': course_name, 
            'date': current_day, 
            'assignments': Assignment.objects.filter(course_id = course_id).order_by('-due_date').values()
        }
        return render(request, 'educatorAssignment.html', {'context': context})
    else: 
        course = Course.objects.get(course_name = course_name)
        assignment_name = request.POST['assignment_name']
        assignment_description = request.POST['assignment_description']
        due_date = request.POST['due_date']
    
        if len(request.POST['assignment_file']) > 0:
            assignment_file = request.POST['assignment_file']
            assignment_file_name = request.POST['assignment_file'].name
            file_url = savefile(assignment_file, assignment_file_name)
            newAssignment = Assignment(course_id = course, assignment_name = assignment_name, assignment_description = assignment_description, assignment_file = file_url, due_date = due_date)
            newAssignment.save() 
        else:
            newAssignment = Assignment(course_id = course, assignment_name = assignment_name, assignment_description = assignment_description, due_date = due_date)
            newAssignment.save() 

        return redirect('educatorAssignments', course_name = course_name)

@login_required(login_url='login')
def educatorViewAssignment(request, course_name, assignment_id):
    if request.method == "GET":
        id = Course.objects.filter(course_name = course_name).values('id')
        context = {
            'course_name': course_name,
            'assignment':  Assignment.objects.get(id = assignment_id, course_id = id[0]['id']),
        }
        return render(request, 'educatorViewAssignment.html', {'context': context})
    else:
        if request.POST.get('delete_form'): 
            if request.POST.get('delete_form') == 'Delete': 
                id = Course.objects.filter(course_name = course_name).values('id')
                assignment_id = request.POST['assignment_id']
                deletedAssignment = Assignment.objects.get(id = assignment_id, course_id = id[0]['id']).delete()
                if deletedAssignment:
                    return redirect('educatorAssignments', course_name = course_name)
                else:
                    return redirect('educatorViewAssignment', course_name = course_name, assignment_id = assignment_id)
        else:
            id = Course.objects.filter(course_name = course_name).values('id')
            updateAssignment = Assignment.objects.get(id = assignment_id, course_id = id[0]['id'])
            updateAssignment.assignment_name = request.POST['new_assignment_name']
            updateAssignment.assignment_description = request.POST['new_assignment_description']
            if len(request.POST['new_assignment_file'])>0:
                file_url = savefile(request.POST['new_assignment_file'], request.POST['new_assignment_file'].name)
                updateAssignment.assignment_file = file_url
            updateAssignment.due_date = request.POST['new_due_date']
            updateAssignment.save()
            return redirect('educatorViewAssignment', course_name = course_name, assignment_id = assignment_id)

@login_required(login_url='login')
def educatorAttendance(request, course_name, date): 
    if request.method == "GET":
        id = Course.objects.filter(course_name = course_name).values('id')
        date =  datetime.strptime(date, "%Y-%m-%d")
        previous_day = date - timedelta(1)
        previous_day = datetime.strftime(previous_day, "%Y-%m-%d")
        following_day = date + timedelta(1)
        following_day = datetime.strftime(following_day, "%Y-%m-%d")
        date = datetime.strftime(date, "%Y-%m-%d")
        context = {
            'course_name': course_name,
            'students_enrolled':  Enrollment.objects.all().filter(course_id = id[0]['id']),
            'attendance': Attendance.objects.all().filter(course_id = id[0]['id'], class_date = date),
            'date': date,
            'previous_day': previous_day,
            'following_day': following_day
        }      
        return render(request, 'educatorAttendance.html', {'context': context})
    else:
        course = Course.objects.get(course_name = course_name)
        date = request.POST.get('attendance_date')
        student_id = request.POST.get('student_id') 
        student = User.objects.get(id = student_id)
        if Attendance.objects.filter(student_id = student.id, course_id = course.id, class_date = date).exists():
            if request.POST.get('present'):
                updateAttendance = Attendance.objects.get(student_id = student, course_id = course, class_date = date)
                updateAttendance.isPresent = True
                updateAttendance.save()
            else:
                updateAttendance = Attendance.objects.get(student_id = student, course_id = course, class_date = date)
                updateAttendance.isPresent = False
                updateAttendance.save()
            
            return redirect('educatorAttendance',course_name=course_name, date = date)  
        else:
            if request.POST.get('present'):
                newAttendance = Attendance(student_id = student, course_id = course, class_date = date, isPresent = True )
                newAttendance.save()
            else:
                newAttendance = Attendance(student_id = student, course_id = course, class_date = date, isPresent = False)
                newAttendance.save()

            return redirect('educatorAttendance',course_name=course_name, date = date)  

@login_required(login_url='login')
def educatorGrades(request, course_name): 
    if request.method == "GET":
        id = Course.objects.filter(course_name = course_name).values('id')
        current_day = datetime.today()
        current_day = datetime.strftime(current_day, "%Y-%m-%d")
        context = {
            'course_name': course_name,
            'date': current_day, 
            'submissions': Submission.objects.all().filter(course_id = id[0]['id']),
            'grades': Grade.objects.all().filter(course_id = id[0]['id']),
            'enrolled': Enrollment.objects.all().filter(course_id = id[0]['id']),
            'assignments': Assignment.objects.filter(course_id = id[0]['id']).order_by('-due_date'),
            '100Percentage': Grade.objects.filter(course_id= id[0]['id'], grade__lte = 100, grade__gte = 90).count(),
            '90Percentage': Grade.objects.filter(course_id= id[0]['id'], grade__lte = 90, grade__gte = 80).count(),
            '80Percentage': Grade.objects.filter(course_id= id[0]['id'], grade__lte = 80, grade__gte = 70).count(),
            '70Percentage': Grade.objects.filter(course_id= id[0]['id'], grade__lte = 70, grade__gte = 65).count(),
            '65Percentage': Grade.objects.filter(course_id= id[0]['id'], grade__lte = 65).count(),
        }
        
        return render(request, 'educatorGrades.html', {'context': context})
    else:
       pass
    
@login_required(login_url='login')
def educatorViewSubmission(request, course_name, submission_id): 
    if request.method == "GET":
        course = Course.objects.get(course_name = course_name)
        submission = Submission.objects.get(id = submission_id)
        assignment = Assignment.objects.get(id = submission.assignment_id.id)
        grade = Grade.objects.filter(course_id = course.id, assignment_id = assignment.id, submission_id = submission.id, student_id = submission.student_id.id).exists()
        if grade:
            grade =  Grade.objects.get(course_id = course.id, assignment_id = assignment.id, submission_id = submission.id, student_id = submission.student_id.id)
            context = {
                'course_name': course_name,
                'submission': submission,
                'assignment': assignment,
                'grade': grade
            }
        else: 
            context = { 
                'course_name': course_name,
                'submission': submission,
                'assignment': assignment
            }
        return render(request, 'educatorViewSubmission.html', {'context': context})
    else:
        course = Course.objects.get(course_name = course_name)
        assignment = Assignment.objects.get(id = request.POST['assignment_id'])
        student = User.objects.get(id = request.POST['student_id'])
        submission = Submission.objects.get(id = request.POST['submission_id'])
        grade = request.POST['grade']
        newGrade = Grade(course_id = course, assignment_id = assignment, student_id = student, submission_id = submission, grade = grade )
        updateGrade(student, grade, course)
        newGrade = newGrade.save()
        return redirect('educatorViewSubmission', course_name = course_name , submission_id = submission_id)


#Student Views
@login_required(login_url='login')
def studentHome(request):
    if request.method == "GET":
        if Enrollment.objects.filter(student_id = request.user).count() > 0 : 
            context = {'courses': Enrollment.objects.all().filter(student_id = request.user.id)}
            return render(request, 'studentHome.html', {'context': context})
        else:
            return render(request, 'studentHome.html')
    else:
        return render(request, 'studentHome.html')

@login_required(login_url='login')
def studentProfile(request):
    if request.method == "GET":
        studentGpa = Gpa.objects.filter(student_id = request.user.id)
        userGpa = 0
        for i in studentGpa:
            userGpa = userGpa + i.gpa 
        userGpa = ((userGpa / Gpa.objects.filter(student_id = request.user.id).count()) / 20) - 1
        context = {
            'user_details': User.objects.filter(username = request.user).values('first_name', 'last_name', 'email', 'username', 'date_joined'),
            'userGpa': userGpa
        }
        return render(request, 'studentProfile.html', {'context': context})
    else:
        pass

@login_required(login_url='login')
def studentCourses(request, course_name): 
    if request.method == "GET":
        context = { 'course_name': course_name, 'course': Course.objects.all().filter(course_name = course_name)}
        return render(request, 'studentCourses.html', {'context': context})
    else:
        pass

@login_required(login_url='login')
def studentAssignments(request, course_name): 
    if request.method == "GET":
        id = Course.objects.filter(course_name = course_name).values('id')
        current_day = datetime.today()
        current_day = datetime.strftime(current_day, "%Y-%m-%d")
        context = {
            'course_name': course_name,
            'assignments':  Assignment.objects.all().filter(course_id = id[0]['id']),
            'past_assignments':  Assignment.objects.all().filter(course_id = id[0]['id'], due_date__lte = current_day),
            'current_assignments':  Assignment.objects.all().filter(course_id = id[0]['id'], due_date__gte = current_day).order_by('-due_date')
        }
        return render(request, 'studentAssignments.html', {'context': context})
    else:
        pass

@login_required(login_url='login')
def studentViewAssignment(request, course_name, assignment_id): 
    if request.method == "GET":
        id = Course.objects.filter(course_name = course_name).values('id')
        if Submission.objects.filter(assignment_id = assignment_id, student_id = request.user.id, course_id = id[0]['id']).exists():
            context = {
                'course_name': course_name, 
                'assignment':  Assignment.objects.get(id = assignment_id),
                'submission':  Submission.objects.get(assignment_id = assignment_id, student_id = request.user.id, course_id = id[0]['id'])
            }
            return render(request, 'studentViewAssignment.html', {'context': context})
        else:
            context = {
                'course_name': course_name, 
                'assignment':  Assignment.objects.get(id = assignment_id)
            }
            return render(request, 'studentViewAssignment.html', {'context': context})
    else:
        course = Course.objects.get(course_name = course_name)
        assignment = Assignment.objects.get(id = assignment_id)
        student = User.objects.get(id = request.user.id)
        current_day = datetime.today()
        current_day = datetime.strftime(current_day, "%Y-%m-%d")
        submission_text = request.POST['submission_text']
        if len(request.POST['submission_file'])>0:
            submission_file = request.POST['submission_file']
            file_url = savefile(submission_file, submission_file)
            newSubmission = Submission(course_id = course, assignment_id = assignment, student_id = student, submission_text = submission_text, submission_file = file_url, submission_date = current_day)
            newSubmission.save()
            return redirect('studentViewAssignment',course_name = course_name, assignment_id = assignment_id)
        else: 
            newSubmission = Submission(course_id = course, assignment_id = assignment, student_id = student, submission_text = submission_text, submission_date = current_day)
            newSubmission.save()
            return redirect('studentViewAssignment',course_name = course_name, assignment_id = assignment_id)
            
@login_required(login_url='login')
def studentAttendance(request, course_name): 
    if request.method == "GET":
        current_day = datetime.today()
        current_day = datetime.strftime(current_day, "%m-%d-%Y")
        id = Course.objects.filter(course_name = course_name).values('id')
        context = {
            'course_name': course_name,
            'attendance': Attendance.objects.filter(student_id = request.user.id, course_id = id[0]['id']).order_by('class_date'), 
            'daysPresent': len(Attendance.objects.filter(student_id = request.user.id, course_id = id[0]['id'], isPresent = True)),
            'daysAbsent': len(Attendance.objects.filter(student_id = request.user.id, course_id = id[0]['id'],  isPresent = False))
        }
        return render(request, 'studentAttendance.html', {'context': context})
    else:
        pass

@login_required(login_url='login')
def studentGrades(request, course_name): 
    if request.method == "GET":
        current_day = datetime.today()
        current_day = datetime.strftime(current_day, "%m-%d-%Y")
        id = Course.objects.filter(course_name = course_name).values('id')
        context = {
        'course_name': course_name,
        'attendance': Attendance.objects.filter(student_id = request.user.id, course_id= id[0]['id']).order_by('class_date'), 
        'daysPresent': len(Attendance.objects.filter(student_id = request.user.id, course_id= id[0]['id'], isPresent = True)),
        'daysAbsent': len(Attendance.objects.filter(student_id = request.user.id, course_id= id[0]['id'],  isPresent = False)),
        'submissions': Submission.objects.filter(student_id = request.user.id, course_id= id[0]['id']),
        'grades': Grade.objects.filter(student_id = request.user.id, course_id= id[0]['id']),
        '100Percentage': Grade.objects.filter(student_id = request.user.id, course_id= id[0]['id'], grade__lte = 100, grade__gte = 90).count(),
        '90Percentage': Grade.objects.filter(student_id = request.user.id, course_id= id[0]['id'], grade__lte = 90, grade__gte = 80).count(),
        '80Percentage': Grade.objects.filter(student_id = request.user.id, course_id= id[0]['id'], grade__lte = 80, grade__gte = 70).count(),
        '70Percentage': Grade.objects.filter(student_id = request.user.id, course_id= id[0]['id'], grade__lte = 70, grade__gte = 65).count(),
        '65Percentage': Grade.objects.filter(student_id = request.user.id, course_id= id[0]['id'], grade__lte = 65).count(),
        }
        return render(request, 'studentGrades.html', {'context': context})
    else:
        pass