#from django.db import models
from djongo import models
from user.custom_manager import CustomUserManager
from django.contrib.auth.base_user import AbstractBaseUser

# class User(models.Model):
#     employee_code = models.CharField(max_length=20)
#     firstname = models.CharField(max_length=20,blank=False, null=False)
#     lastname = models.CharField(max_length=20,blank=False, null=False)
#     email = models.EmailField(blank=False, primary_key=True, unique=True)
#     phone_extension = models.CharField(max_length=5,blank=False, null=False)
#     phone_number = models.CharField(max_length=20,blank=False, null=False)
#     location = models.CharField(max_length=100, blank=False, null=False)
#     sub_location = models.JSONField(max_length=100)
#     division = models.CharField(max_length=100, blank=False, null=False)
#     password = models.CharField(max_length=255, blank=False, null=False)

#     class Meta:
#         app_label = 'User'


class User(AbstractBaseUser):
    id = models.IntegerField(primary_key=True,null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    firstname = models.CharField(max_length=20,blank=False, null=False)
    lastname = models.CharField(max_length=20,blank=False, null=False)
    email = models.EmailField(blank=False,unique=True)
    phone_extension = models.CharField(max_length=5,blank=False, null=False)
    phone_number = models.CharField(max_length=20,blank=False, null=False)
    designation = models.CharField(max_length=100, blank=False, null=False)
    role = models.CharField(max_length=100, blank=False, null=False)
    status = models.CharField(max_length=100, blank=False, null=False)
    password = models.CharField(max_length=255, blank=False, null=False)
    location =  models.JSONField() 
    employee_code =  models.CharField(max_length=255, blank=True, null=True)
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        app_label = 'user'


class Access_Control(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Role = models.CharField(max_length=255) 
    location = models.CharField(max_length=255, blank=False, null=False)
    employee_code =  models.IntegerField(blank=True, null=True)
    Section = models.CharField(max_length=255)  
    Page_Name = models.CharField(max_length=255) 
    Sub_Page_Name = models.CharField(max_length=255, blank=True, null=True)  
    Menu_Access = models.BooleanField(default=False) 

    View = models.BooleanField(default=True)  # Always True
    Add = models.BooleanField(default=False)  
    Edit = models.BooleanField(default=False)  
    Delete = models.BooleanField(default=False)  

    class Meta:
        app_label = "user"

class Human_Resoursce_Access_Control(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Section = models.CharField(max_length=255)  
    Page_Name = models.CharField(max_length=255) 
    Sub_Page_Name = models.CharField(max_length=255, blank=True, null=True)  
    Menu_Access = models.BooleanField(default=False) 

    View = models.BooleanField(default=True)  # Always True
    Add = models.BooleanField(default=False)  
    Edit = models.BooleanField(default=False)  
    Delete = models.BooleanField(default=False)  

    class Meta:
        app_label = "user"


class Finance_Access_Control(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Section = models.CharField(max_length=255)  
    Page_Name = models.CharField(max_length=255) 
    Sub_Page_Name = models.CharField(max_length=255, blank=True, null=True)  
    Menu_Access = models.BooleanField(default=False) 

    View = models.BooleanField(default=True)  # Always True
    Add = models.BooleanField(default=False)  
    Edit = models.BooleanField(default=False)  
    Delete = models.BooleanField(default=False)  
    class Meta:
        app_label = "user"


class Company_Secretary_Access_Control(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Section = models.CharField(max_length=255)  
    Page_Name = models.CharField(max_length=255) 
    Sub_Page_Name = models.CharField(max_length=255, blank=True, null=True)  
    Menu_Access = models.BooleanField(default=False) 

    View = models.BooleanField(default=True)  # Always True
    Add = models.BooleanField(default=False)  
    Edit = models.BooleanField(default=False)  
    Delete = models.BooleanField(default=False)  

    class Meta:
        app_label = "user"


class EmployeesAccessControl(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    employee_code =  models.CharField(max_length=255)
    employee_name =  models.CharField(max_length=255)
    role =  models.JSONField() 
    section = models.CharField(max_length=255)
    page = models.CharField(max_length=255)
    sub_page = models.CharField(max_length=255)
    permissions = models.JSONField()