from django.db import models


"""
Workforce App models
"""
class Employees(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Type = models.CharField(max_length=200, blank=True, null=True)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Gender =  models.CharField(max_length=20, blank=True, null=True)
    Employees_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employees_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employees_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employees_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employees_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employees_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employees_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employees_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employees_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employees_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employees_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employees_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Employees = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    class Meta:
        app_label = "Workplace"


class Differently_Abled_Employees(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Type = models.CharField(max_length=200, blank=True, null=True)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Gender =  models.CharField(max_length=20, blank=True, null=True)
    Differently_Abled_Employees_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Employees_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Employees_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Employees_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Employees_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Employees_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Employees_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Employees_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Employees_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Employees_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Employees_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Employees_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Differently_Abled_Employees = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    
    class Meta:
        app_label = "Workplace"

class Employees_Membership_In_Association_Or_Unions(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Permanent_Males =  models.IntegerField(blank=True, null=True)
    Male_Percentage_Covered =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Permanent_Females =  models.IntegerField(blank=True, null=True)
    Female_Percentage_Covered =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    class Meta:
        app_label = "Workplace"

class Workers(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Type = models.CharField(max_length=200, blank=True, null=True)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Gender =  models.CharField(max_length=20, blank=True, null=True)
    Differently_Abled_Workers_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Differently_Abled_Workers = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    
    class Meta:
        app_label = "Workplace"

class Differently_Abled_Workers(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Type = models.CharField(max_length=200, blank=True, null=True)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Gender =  models.CharField(max_length=20, blank=True, null=True)
    Differently_Abled_Workers_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Differently_Abled_Workers_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Differently_Abled_Workers = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    
    class Meta:
        app_label = "Workplace"



class Workers_Membership_In_Association_Or_Unions(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Permanent_Males = models.IntegerField(blank=True, null=True)
    Male_Percentage_Covered =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Permanent_Females = models.IntegerField(blank=True, null=True)
    Female_Percentage_Covered =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    class Meta:
        app_label = "Workplace"

class Management_Board_of_Directors(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Gender =  models.CharField(max_length=20, blank=True, null=True)
    Board_of_Directors_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Board_of_Directors_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Board_of_Directors_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Board_of_Directors_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Board_of_Directors_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Board_of_Directors_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Board_of_Directors_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Board_of_Directors_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Board_of_Directors_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Board_of_Directors_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Board_of_Directors_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Board_of_Directors_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Board_of_Directors = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    
    class Meta:
        app_label = "Workplace"

class Key_Management_Personnel(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Gender =  models.CharField(max_length=20, blank=True, null=True)
    Key_Management_Personnel_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Key_Management_Personnel_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Key_Management_Personnel_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Key_Management_Personnel_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Key_Management_Personnel_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Key_Management_Personnel_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Key_Management_Personnel_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Key_Management_Personnel_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Key_Management_Personnel_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Key_Management_Personnel_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Key_Management_Personnel_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Key_Management_Personnel_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Key_Management_Personnel = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    
    class Meta:
        app_label = "Workplace"

class Wages_Paid(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Type = models.CharField(max_length=200, blank=True, null=True)
    Segment =  models.CharField(max_length=200, blank=True, null=True)
    Males_With_Equal_To_Minimum_Wages =  models.IntegerField(blank=True, null=True)
    Females_With_Equal_To_Minimum_Wages =  models.IntegerField(blank=True, null=True)
    Males_With_More_Than_Minimum_Wages = models.IntegerField(blank=True, null=True)
    Females_With_More_Than_Minimum_Wages = models.IntegerField(blank=True, null=True)
    Percent_Males_With_Equal_To_Minimum_Wages =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Percent_Females_With_Equal_To_Minimum_Wages =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Percent_Males_With_More_Than_Minimum_Wages = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Percent_Females_With_More_Than_Minimum_Wages = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Workplace"



class Median_Remuneration_Salary_Wages(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Males_Board_Of_Directors =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Females_Board_Of_Directors =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Males_Key_Management_Personnel = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Females_Key_Management_Personnel = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Males_Employees = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Females_Employees = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Males_Workers = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Females_Workers  = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    class Meta:
        app_label = "Workplace"



class EmployeeSummary(models.Model):
    Financial_Year = models.CharField(max_length=200)  
    Facility = models.CharField(max_length=255)  

    Male_Permanent = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    Male_Non_Permanent = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    Female_Permanent = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    Female_Non_Permanent = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)

    Total_Male = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    Total_Female = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)

    Percentage_Male = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    Percentage_Female = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    
    class Meta:
        app_label = "Workplace"



class WorkerSummary(models.Model):
    Financial_Year = models.CharField(max_length=200)  
    Facility = models.CharField(max_length=255)  

    Male_Permanent = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    Male_Non_Permanent = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    Female_Permanent = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    Female_Non_Permanent = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)

    Total_Male = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    Total_Female = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)

    Percentage_Male = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    Percentage_Female = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    
    class Meta:
        app_label = "Workplace"



"""
Model for Employee Turnover Rate
"""
class Employee_Turnover_Rate(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Financial_Year = models.CharField(max_length=200)  
    Type = models.CharField(max_length=200, blank=True, null=True)
    Gender =  models.CharField(max_length=20, blank=True, null=True)
    Employee_Turnover_Rate_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employee_Turnover_Rate_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employee_Turnover_Rate_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employee_Turnover_Rate_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employee_Turnover_Rate_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employee_Turnover_Rate_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employee_Turnover_Rate_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employee_Turnover_Rate_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employee_Turnover_Rate_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employee_Turnover_Rate_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employee_Turnover_Rate_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Employee_Turnover_Rate_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Employee_Turnover_Rate = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    # Total_Employee_Turnover_Rate = models.FloatField(blank=True, null=True)
    
    
    class Meta:
        app_label = "Workplace"


"""
Model for Workers Turnover Rate
"""
class Workers_Turnover_Rate(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Type = models.CharField(max_length=200, blank=True, null=True)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Gender =  models.CharField(max_length=20, blank=True, null=True)
    Workers_Turnover_Rate_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Workers_Turnover_Rate_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Workers_Turnover_Rate_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Workers_Turnover_Rate_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Workers_Turnover_Rate_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Workers_Turnover_Rate_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Workers_Turnover_Rate_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Workers_Turnover_Rate_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Workers_Turnover_Rate_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Workers_Turnover_Rate_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Workers_Turnover_Rate_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Workers_Turnover_Rate_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Workers_Turnover_Rate = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    # Total_Workers_Turnover_Rate = models.FloatField(blank=True, null=True)
    
    
    class Meta:
        app_label = "Workplace"



class Gross_Wages_Paid(models.Model):

    id = models.IntegerField(primary_key=True,null=False) 
    Financial_Year = models.CharField(max_length=50, blank=True, null=True)
    Rural =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Semi_Urban =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Urban =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Metropolitan =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    
    class Meta:
        app_label = "Workplace"





class Job_Creation_In_Smaller_Town(models.Model):
    id = models.IntegerField(primary_key=True,null=False) 
    Financial_Year = models.CharField(max_length=50, blank=True, null=True)
    Gross_Wages_Paid_To_Females_As_Divided_Of_Total_Wages = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    
    class Meta:
        app_label = "Workplace"














"""
Models for Training app
"""


class Ingeneral(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Segment =  models.CharField(max_length=200, blank=True, null=True)
    Ingeneral_Consumption_Apr = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Ingeneral_Consumption_May = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Ingeneral_Consumption_Jun = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Ingeneral_Consumption_Jul = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Ingeneral_Consumption_Aug = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Ingeneral_Consumption_Sep = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Ingeneral_Consumption_Oct = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Ingeneral_Consumption_Nov = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Ingeneral_Consumption_Dec = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Ingeneral_Consumption_Jan = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Ingeneral_Consumption_Feb = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Ingeneral_Consumption_Mar = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Total_Ingeneral_Consumption = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)

    class Meta:
        app_label = "Workplace"


class On_Skill_Upgradation(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Segment =  models.CharField(max_length=200, blank=True, null=True)
    No_Of_Male = models.IntegerField(blank=True, null=True)
    No_Of_Female = models.IntegerField(blank=True, null=True)
    Total_Male_And_Female = models.IntegerField(blank=True, null=True)
    Percentage_Of_Male = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True)
    Percentage_Of_Female = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True)

    class Meta:
        app_label = "Workplace"


class Performance_And_Career_Reviews(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Segment =  models.CharField(max_length=200, blank=True, null=True)
    No_Of_Male = models.IntegerField(blank=True, null=True)
    No_Of_Female = models.IntegerField(blank=True, null=True)
    Total_Male_And_Female = models.IntegerField(blank=True, null=True)
    Percentage_Of_Male = models.DecimalField(decimal_places=2, max_digits=100, blank=True, null=True)
    Percentage_Of_Female = models.DecimalField(decimal_places=2, max_digits=100, blank=True, null=True)

    class Meta:
        app_label = "Workplace"


class  Awareness_Programmes_On_ESG(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Segment =  models.CharField(max_length=2000, blank=True, null=True)
    Total_No_Of_Programmes_Held = models.IntegerField(blank=True, null=True)
    Topics_Covered = models.CharField(max_length=2000, blank=True, null=True)
    Percentage_Of_Persons = models.DecimalField(decimal_places=2, max_digits=100, blank=True, null=True)

    class Meta:
        app_label = "Workplace"


class On_Health_And_Safety_Measures(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Segment =  models.CharField(max_length=200, blank=True, null=True)
    No_Of_Male = models.IntegerField(blank=True, null=True)
    No_Of_Female = models.IntegerField(blank=True, null=True)
    Total_Male_And_Female = models.IntegerField(blank=True, null=True)
    Percentage_Of_Male = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True)
    Percentage_Of_Female = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True)

    class Meta:
        app_label = "Workplace"


class On_Human_Rights_Issues_And_Policies(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Segment =  models.CharField(max_length=200, blank=True, null=True)
    Total_Permanent_Covered = models.IntegerField(blank=True, null=True)
    Total_Non_Permanent_Covered = models.IntegerField(blank=True, null=True)
    Permanent_Covered_Percentage = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True)
    Non_Permanent_Covered_Percentage = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True)

    class Meta:
        app_label = "Workplace"

    



























"""
Models for Health and sefty
"""


class Percentage_Covered_In_Wellbeing_Measures(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Type = models.CharField(max_length=100, blank=True, null=True)
    Segment =  models.CharField(max_length=200, blank=True, null=True)

    Health_Insurance_No_Of_Male = models.IntegerField(blank=True, null=True)
    Health_Insurance_No_Of_Female = models.IntegerField(blank=True, null=True)

    Accident_Insurance_No_Of_Male = models.IntegerField(blank=True, null=True)
    Accident_Insurance_No_Of_Female = models.IntegerField(blank=True, null=True)

    Maternity_Benefits_No_Of_Male = models.IntegerField(blank=True, null=True)
    Maternity_Benefits_No_Of_Female = models.IntegerField(blank=True, null=True)

    Paternity_Benefits_No_Of_Male = models.IntegerField(blank=True, null=True)
    Paternity_Benefits_No_Of_Female = models.IntegerField(blank=True, null=True)

    Day_Care_Facilities_No_Of_Male = models.IntegerField(blank=True, null=True)
    Day_Care_Facilities_No_Of_Female = models.IntegerField(blank=True, null=True)

    class Meta:
        app_label = "Workplace"




class Retirement_Benefits(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Segment =  models.CharField(max_length=200, blank=True, null=True)
    Total_Covered_PF =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Covered_Gratuity = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Covered_ESI =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Covered_Other = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Covered_Superannuation = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
   
    Deducted_And_Deposited_PF =  models.CharField(max_length=20, blank=True, null=True)
    Deducted_And_Deposited_Gratuity = models.CharField(max_length=20, blank=True, null=True)
    Deducted_And_Deposited_ESI = models.CharField(max_length=20, blank=True, null=True)
    Deducted_And_Deposited_Other = models.CharField(max_length=20, blank=True, null=True)
    Deducted_And_Deposited_Superannuation = models.CharField(max_length=20, blank=True, null=True)
   

    class Meta:
        app_label = "Workplace"


class Post_Paternal_Leave_For_Permanent_Employee_And_Worker(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)

    Return_To_Work_Rate_For_Male_Employee =  models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Return_To_Work_Rate_For_Female_Employee =  models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Total_Return_To_Work_Rate_Employee = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)

    Retention_Rate_For_Male_Employee =  models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Retention_Rate_For_Female_Employee = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Total_Retention_Rate_Employee = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)

    Return_To_Work_Rate_Male_Workers =models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Return_To_Work_Rate_Female_Workers = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Total_Return_To_Work_Rate_Of_Workers = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)

    Retention_Rate_For_Male_Workers =  models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Retention_Rate_For_Female_Workers =  models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Total_Retention_Rate_Workers = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)

    class Meta:
        app_label = "Workplace"




class Lost_Time_Injury_Frequency_Rate(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Segment =  models.CharField(max_length=200, blank=True, null=True)
    Frequency_Rate_Apr = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Frequency_Rate_May = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Frequency_Rate_Jun = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Frequency_Rate_Jul = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Frequency_Rate_Aug = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Frequency_Rate_Sep = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Frequency_Rate_Oct = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Frequency_Rate_Nov = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Frequency_Rate_Dec = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Frequency_Rate_Jan = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Frequency_Rate_Feb = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Frequency_Rate_Mar = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Total_Frequency_Rate = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)

    class Meta:
        app_label = "Workplace"




class Total_Work_Related_Injuries(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Segment =  models.CharField(max_length=200, blank=True, null=True)
    Injuries_Rate_Apr = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injuries_Rate_May = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injuries_Rate_Jun = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injuries_Rate_Jul = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injuries_Rate_Aug = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injuries_Rate_Sep = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injuries_Rate_Oct = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injuries_Rate_Nov = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injuries_Rate_Dec = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injuries_Rate_Jan = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injuries_Rate_Feb = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injuries_Rate_Mar = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Total_Injuries_Rate = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)

    class Meta:
        app_label = "Workplace"





class No_Of_Fatalities(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Segment =  models.CharField(max_length=200, blank=True, null=True)
    No_Of_Fatalities_Apr = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    No_Of_Fatalities_May = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    No_Of_Fatalities_Jun = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    No_Of_Fatalities_Jul = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    No_Of_Fatalities_Aug = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    No_Of_Fatalities_Sep = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    No_Of_Fatalities_Oct = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    No_Of_Fatalities_Nov = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    No_Of_Fatalities_Dec = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    No_Of_Fatalities_Jan = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    No_Of_Fatalities_Feb = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    No_Of_Fatalities_Mar = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Total_No_Of_Fatalities = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)

    class Meta:
        app_label = "Workplace"

class Injury_Or_Ill_Health(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Segment =  models.CharField(max_length=200, blank=True, null=True)
    Injury_Or_Ill_Health_Rate_Apr = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injury_Or_Ill_Health_Rate_May = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injury_Or_Ill_Health_Rate_Jun = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injury_Or_Ill_Health_Rate_Jul = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injury_Or_Ill_Health_Rate_Aug = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injury_Or_Ill_Health_Rate_Sep = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injury_Or_Ill_Health_Rate_Oct = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injury_Or_Ill_Health_Rate_Nov = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injury_Or_Ill_Health_Rate_Dec = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injury_Or_Ill_Health_Rate_Jan = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injury_Or_Ill_Health_Rate_Feb = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Injury_Or_Ill_Health_Rate_Mar = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Total_Injury_Or_Ill_Health_Rate = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)

    class Meta:
        app_label = "Workplace"

class Suffered_High_Consequence_Work_Related_Injury(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Total_No_Of_Affected_Employees =  models.IntegerField(blank=True, null=True)
    Total_No_Of_Affected_Workers =  models.IntegerField(blank=True, null=True)

    Rehabilitated_And_Placed_In_Suitable_Employee = models.IntegerField(blank=True, null=True)
    Rehabilitated_And_Placed_In_Suitable_Workers = models.IntegerField(blank=True, null=True)

    class Meta:
        app_label = "Workplace"




class Assessment_Of_Plants_And_Offices_Health_And_Safety(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Percentage_Assessed_For_Working_Conditions = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Percentage_Assessed_For_Health_And_Safety =  models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)

    class Meta:
        app_label = "Workplace"



class Assessment_Of_Value_Chain_Partners_Health_And_Safety(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Percentage_Assessed_For_Working_Conditions = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Percentage_Assessed_For_Health_And_Safety =  models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Number_of_Supplier = models.IntegerField(null=False)
    class Meta:
        app_label = "Workplace"

class CostIncurredOnWellbeingMeasures(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    Financial_Year = models.CharField(max_length=20)
    percentage_cost_incurred = models.DecimalField(decimal_places=2, max_digits=50)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        app_label = "Workplace"


    


class Receive_And_Redress_Grievance_Mechanism(models.Model):

    id = models.IntegerField(primary_key=True,null=False) 
    Financial_Year = models.CharField(max_length=50, blank=True, null=True)
    Facility =  models.CharField(max_length=200, blank=True, null=True)
    Segment = models.CharField(max_length=200, blank=True, null=True)
    Male =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Female =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Percent_Of_Female_Employee_Divided_By_Worker = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Upheld = models.CharField(max_length=5000,blank=True,null=True) 

    class Meta:
        app_label = "Workplace"












"""
Gravience app models
"""

class Health_and_safety_related_complaints(models.Model):
    id = models.IntegerField(primary_key=True,null = False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Complaint_Type = models.CharField(max_length=200, blank=True, null=True)
    Filed_During_The_Year = models.IntegerField( blank=True, null=True)
    Pending_Resolution_At_The_EOY = models.IntegerField(blank=True, null=True)
    Remark = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        app_label = "Workplace"



class Human_Rights_related_complaints(models.Model):
    id = models.IntegerField(primary_key=True,null = False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Complaint_Type = models.CharField(max_length=200, blank=True, null=True)
    Filed_During_The_Year = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Pending_Resolution_At_The_EOY = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Remark = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        app_label = "Workplace"


class Conflict_of_interest_complaints(models.Model):
    id = models.IntegerField(primary_key=True,null = False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Segment = models.CharField(max_length=200, blank=True, null=True)
    No_of_complaints = models.IntegerField(blank=True, null=True)
    Remark = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        app_label = "Workplace"        

class Receive_and_redress_grievances_mechanism(models.Model):
    id = models.IntegerField(primary_key=True,null = False)
    Segment = models.CharField(max_length=200, blank=True, null=True)
    Type = models.CharField(max_length=20, blank=True, null=True)
    Yes_No = models.CharField(max_length=20, blank=True, null=True)
    Description = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        app_label = "Workplace"   



"""
Models for policy and penelty
"""
class Policy_Details_Health_safety(models.Model):
    id = models.IntegerField(primary_key=True,null = False)
    Model_Name_Health_safety = models.CharField(max_length=100, blank=True, null=True)
    Heading = models.CharField(max_length=100, blank=True, null=True)
    Descriptions_Health_safety = models.CharField(max_length=5000, blank=True, null=True)
    Is_Verified =  models.CharField(max_length=100,blank=True, null=True)

    class Meta:
       app_label = "Workplace"



class Policy_Details_Human_Rights(models.Model):
    id = models.IntegerField(primary_key=True,null = False)
    Model_Name_Human_Rights = models.CharField(max_length=100, blank=True, null=True)
    Heading = models.CharField(max_length=100, blank=True, null=True)
    Descriptions_Human_Rights = models.CharField(max_length=5000, blank=True, null=True)
    Is_Verified =  models.CharField(max_length=100,blank=True, null=True)

    class Meta:
       app_label = "Workplace"


class Policy_Details_Penalty(models.Model):
    id = models.IntegerField(primary_key=True,null = False)
    Model_Name_Penalty = models.CharField(max_length=100, blank=True, null=True)
    Heading = models.CharField(max_length=100, blank=True, null=True)
    Descriptions_Penalty = models.CharField(max_length=5000, blank=True, null=True)
    Is_Verified =  models.CharField(max_length=100,blank=True, null=True)

    
    class Meta:
       app_label = "Workplace"





class Assessment_of_plants_and_offices_Policies_and_Penalties(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=100, blank=True, null=True)
    Child_Labour = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Forced_Involuntary_Labour = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Sexual_Harasement = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Discrimination_at_workplace = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Wages = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Others = models.CharField(max_length=5000, blank=True, null=True)
    Percentage_for_Others = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Corrective_Action = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
       app_label = "Workplace"


class Assessment_of_value_chain_partners_Policies_and_Penalties(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=5000, blank=True, null=True)
    Child_Labour = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Forced_Involuntary_Labour = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Sexual_Harasement = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Discrimination_at_workplace = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Wages = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Others = models.CharField(max_length=5000, blank=True, null=True)
    Corrective_Action = models.CharField(max_length=5000, blank=True, null=True)
    Percentage_for_Others =  models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Number_of_Suppliers = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
       app_label = "Workplace"       


class Penalty_Monetary(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=5000, blank=True, null=True)
    Monetary_Type = models.CharField(max_length=5000, blank=True, null=True)
    NGRBC_Principle = models.CharField(max_length=5000, blank=True, null=True)
    Name_of_agency = models.CharField(max_length=5000, blank=True, null=True)
    Amount = models.IntegerField(blank=True, null=True)
    Brief_case = models.CharField(max_length=5000, blank=True, null=True)
    Has_an_appeal_been_prefered = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
       app_label = "Workplace" 


class Penalty_Non_Monetary(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=5000, blank=True, null=True)
    Non_Monetary_Type = models.CharField(max_length=5000, blank=True, null=True)
    NGRBC_Principle = models.CharField(max_length=5000, blank=True, null=True)
    Name_of_agency = models.CharField(max_length=5000, blank=True, null=True)
    Brief_case = models.CharField(max_length=5000, blank=True, null=True)
    Has_an_appeal_been_prefered = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
       app_label = "Workplace"      

class Details_of_the_appeal(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=100, blank=True, null=True)
    Case_details = models.CharField(max_length=5000, blank=True, null=True)
    Name_of_agency = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
       app_label = "Workplace"         

class Disciplinary_Action_Against_For_curruption(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=5000, blank=True, null=True) 
    BOD = models.IntegerField(blank=True, null=True)
    KMPs = models.IntegerField( blank=True, null=True)
    WORKERS = models.IntegerField(blank=True, null=True)
    EMPLOYEES = models.IntegerField(blank=True, null=True)

    class Meta:
       app_label = "Workplace"    



class Attachment(models.Model):
    id = models.IntegerField(primary_key=True)
    
    parent_type = models.CharField(
        max_length=100,
        choices=[("Employees", "Employees"), ("Workers", "Workers")]
    )
    parent_id = models.IntegerField()

    file = models.FileField(upload_to="attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "Workplace"
