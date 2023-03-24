from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    id = models.AutoField(primary_key = True)
    first_name = models.CharField(max_length=200, null= False)
    last_name = models.CharField(max_length=200, null= False)
    email = models.CharField(max_length=250, null= False)
    username = models.CharField(max_length=250, unique= True, null= False)
    password = models.CharField(max_length=250, null= False)
    is_superuser = models.BooleanField(default = True, null= False)
    last_login =  models.DateField(null =False)
    date_joined = models.DateField(null =False)

class Course(models.Model):
    id = models.AutoField(primary_key = True)
    educator_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, default= 1)
    course_name= models.CharField(max_length=250)
    course_subject = models.CharField(max_length=250)
    course_description = models.TextField(null=True)
    start_date = models.DateField(null =False, default=" ")
    end_date = models.DateField(null =False, default=" ")

class Enrollment(models.Model):
    id = models.AutoField(primary_key = True)
    student_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, default= 1)
    course_id = models.ForeignKey(Course, on_delete=models.DO_NOTHING, default= 1)

class Attendance(models.Model):
    id = models.AutoField(primary_key = True)
    student_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, default= 1)
    course_id = models.ForeignKey(Course, on_delete=models.DO_NOTHING, default= 1)
    class_date = models.DateField(null =False, default=" ")
    isPresent = models.BooleanField(null=False, default= True)

class Assignment(models.Model):
    id = models.AutoField(primary_key = True)
    course_id = models.ForeignKey(Course, on_delete=models.DO_NOTHING, default=1)
    assignment_name = models.CharField(max_length=250)
    assignment_description = models.TextField(null=True)
    assignment_file = models.CharField(max_length=250, null= True)
    due_date = models.DateField(null =False, default=" ")

class Submission(models.Model):
    id = models.AutoField(primary_key = True)
    course_id = models.ForeignKey(Course, on_delete=models.DO_NOTHING, default=1)
    assignment_id = models.ForeignKey(Assignment, on_delete=models.DO_NOTHING, default=1)
    student_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, default= 1)
    submission_text = models.TextField(null=True)
    submission_file = models.CharField(max_length=250, null= True)
    submission_date = models.DateField(null =False, default=" ")

class Grade(models.Model):
    id = models.AutoField(primary_key = True)
    course_id = models.ForeignKey(Course, on_delete=models.DO_NOTHING, default=1)
    assignment_id = models.ForeignKey(Assignment, on_delete=models.DO_NOTHING, default= 1)
    student_id = models.ForeignKey(User, on_delete=models.DO_NOTHING,default= 1)
    submission_id  = models.ForeignKey(Submission, on_delete=models.DO_NOTHING,default= 1)
    grade = models.DecimalField(max_digits = 5, decimal_places=2, null=True) 

class Gpa(models.Model):
    id = models.AutoField(primary_key = True)
    course_id = models.ForeignKey(Course, on_delete=models.DO_NOTHING, default=1)
    student_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, default= 1)
    gpa = models.DecimalField(max_digits = 5, decimal_places=1, null=True) 
