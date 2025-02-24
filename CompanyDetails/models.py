#Create your models here.
#from django.db import models
from djongo import models


class Company_Profile(models.Model):
    Company_Name = models.CharField(max_length=255, unique=True,primary_key=True)
    CIN = models.CharField(max_length=200, blank=True, null=True)
    Year_of_Incorporation = models.IntegerField(blank=True, null=True)
    Registered_Office_Address_Line1 = models.CharField(max_length=500, blank=True, null=True)
    Registered_Office_Address_Line2 = models.CharField(max_length=500, blank=True, null=True)
    Registered_Office_Country = models.CharField(max_length=200, blank=True, null=True) 
    Registered_Office_State = models.CharField      (max_length=200, blank=True, null=True)
    Registered_Office_City = models.CharField(max_length=200, blank=True, null=True)
    Registered_Office_Pincode = models.CharField(max_length=200, blank=True, null=True)
    Corporate_Office_Address_Line1 = models.CharField(max_length=500, blank=True, null=True)
    Corporate_Office_Address_Line2 = models.CharField(max_length=500, blank=True, null=True)
    Corporate_Office_Country = models.CharField(max_length=200, blank=True, null=True) 
    Corporate_Office_State = models.CharField(max_length=200, blank=True, null=True)
    Corporate_Office_City = models.CharField(max_length=200, blank=True, null=True)
    Corporate_Office_Pincode = models.CharField(max_length=200, blank=True, null=True)
    Email = models.CharField(max_length=200, blank=True, null=True)
    Website = models.CharField(max_length=500, blank=True, null=True)
    Phone_Ext = models.CharField(max_length=10, blank=True, null=True)
    Phone_Number = models.BigIntegerField(blank=True, null=True)
    Shares_Listed_On = models.CharField(max_length=500, blank=True, null=True)
    CSR_Applicable = models.CharField(max_length=100, blank=True, null=True)
    Company_logo =  models.ImageField(upload_to='images/', null=True, blank=True)
    Name_of_Assurance_Provider = models.TextField(blank=True, null=True)
    Reporting_Boundary = models.CharField(max_length=500, blank=True, null=True)
    Type_Of_Assurance = models.CharField(max_length=500, blank=True, null=True)



    class Meta:
        app_label = "CompanyDetails"



class Turnover(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Turnover_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Turnover_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Turnover_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Turnover_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Turnover_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Turnover_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Turnover_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Turnover_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Turnover_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Turnover_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Turnover_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Turnover_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Turnover = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    
    class Meta:
        app_label = "CompanyDetails"



class Networth(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Networth_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Networth_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Networth_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Networth_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Networth_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Networth_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Networth_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Networth_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Networth_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Networth_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Networth_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Networth_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Networth = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "CompanyDetails"



class Business_Activity_Details(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Name_of_Business_Activity = models.CharField(max_length=200, blank=True, null=True)
    Description = models.CharField(max_length=1000, blank=True, null=True)
    
    class Meta:
        app_label = "CompanyDetails"



class Products_Services_Details(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Name_of_Product_Service = models.CharField(max_length=200, blank=True, null=True)
    NIC_Code = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        app_label = "CompanyDetails"



class Exports(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Contribution_of_Turnover = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    class Meta:
        app_label = "CompanyDetails"



class Business_Activity(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Business_Activity_and_Turnover = models.JSONField(default=list, unique=True, blank=True, null=True)
    Total_Percent_Turnover = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    class Meta:
        app_label = "CompanyDetails"



class Products_Services(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Products_Services_and_Turnover = models.JSONField(default=list, unique=True, blank=True, null=True)
    Total_Percent_Turnover = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    class Meta:
        app_label = "CompanyDetails"


class Offices_and_Plants(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    No_of_National_Offices = models.IntegerField(blank=True, null=True)
    No_of_National_Plants = models.IntegerField(blank=True, null=True)
    No_of_International_Offices = models.IntegerField(blank=True, null=True)
    No_of_International_Plants = models.IntegerField(blank=True, null=True)
    Total = models.IntegerField(blank=True, null=True)
    
    class Meta:
        app_label = "CompanyDetails"


class Markets_Served(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    National_No_of_States = models.IntegerField(blank=True, null=True)
    International_No_of_Countries = models.IntegerField(blank=True, null=True)
    
    class Meta:
        app_label = "CompanyDetails"



class Paid_up_Capital(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Paid_up_Capital = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Paid_Up_Capital_Unit =  models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        app_label = "CompanyDetails"



class Holdings(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    Name_of_Holding = models.CharField(max_length=200, blank=True, null=True)
    Type_of_Holding = models.CharField(max_length=200, blank=True, null=True)
    Percent_of_Share_Held = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Participates_in_Business_Responsibility = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        app_label = "CompanyDetails"



class Facilities(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Name_of_Facility = models.CharField(max_length=200, blank=True, null=True)
    Type_of_Facility = models.CharField(max_length=200, blank=True, null=True)
    Location = models.CharField(max_length=500, blank=True, null=True)
    State = models.CharField(max_length=200, blank=True, null=True)
    Description_of_Operations = models.CharField(max_length=500, blank=True, null=True)
    
    class Meta:
        app_label = "CompanyDetails"


"""
Model for Number of days of accounts payables (Accounts payable *365)
"""
class NumberOfDaysOfAccountsPayablesModel(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Days_Of_Accounts_Payables = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        app_label = "CompanyDetails"


"""
Model for Concentration Of Sales
"""
class Concentration_Of_Sales(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Sales_To_Dealers_Divided_BY_Distributors_As_Percent_Of_Total_Sales = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Number_Of_Dealers_Divided_BY_Distributors_To_Whom_Sales_Are_Made = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Sales_To_Top_Ten_Dealers_Divided_BY_Distributors_As_Percent_Of_Total_Sales_To_Dealers_Divided_BY_Distributors = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    class Meta:
        app_label = "CompanyDetails"


"""
Model for Concentration of Purchases
"""
class Concentration_Of_Purchases(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Purchases_From_Trading_Houses_As_Percent_Of_Total_Purchases = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Number_Of_Trading_Houses_Where_Purchases_Are_Made = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Purchases_From_Top_Ten_Trading_Houses_As_Percent_Of_Total_Purchases_From_Trading_Houses = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    class Meta:
        app_label = "CompanyDetails"



"""
Model for Share of RPTs in
"""
class ShareOfRPTs(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Purchases_With_Related_Parties_As_Percent_Of_Total_Purchases = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Sales_To_Related_Parties_As_Percent_Of_Total_Sales = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Loans_And_Advances_To_Related_Parties_As_Percent_Of_Total_Loans_And_Advances = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Investments_In_Related_Parties_As_Percent_Of_Total_Investments = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    class Meta:
        app_label = "CompanyDetails"



class Indian_States_Cities(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    state_name = models.CharField(max_length=100, unique=True)
    cities = models.JSONField()

    class Meta:
        app_label = "CompanyDetails"
