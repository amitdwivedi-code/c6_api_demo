from django.db import models
from djongo import models

# Create your models here.

class List_Stakeholder_Groups(models.Model):
    id = models.IntegerField(primary_key=True,null=False) 
    Stack_Holder_Group = models.CharField(max_length=5000, blank=True, null=True)
    Vulnerable_And_Marginalized =  models.CharField(max_length=5000, blank=True, null=True)
    Channels_Of_Communication = models.CharField(max_length=5000, blank=True, null=True)
    Frequency_Of_Engagement = models.CharField(max_length=5000, blank=True, null=True)
    Purpose_And_Scope_Of_Engagement = models.CharField(max_length=5000, blank=True, null=True)
    class Meta:
        app_label = "Community"



class Number_Of_Affiliations(models.Model):
    id = models.IntegerField(primary_key=True,null=False) 
    Financial_Year = models.CharField(max_length=50, blank=True, null=True)
    Number_Of_Affiliations_With_Trade_And_Industry_Chambers = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        app_label = "Community"


  
class  Top_10_Trade_And_Industry_Chambers(models.Model):
    id = models.IntegerField(primary_key=True,null=False) 
    Sr_No =  models.IntegerField(blank=True, null=True)
    Name_Of_The_Trade_And_Industry_Chambers = models.CharField(max_length=200, blank=True, null=True)
    Reach_Of_Trade_And_Industry_Chambers = models.CharField(max_length=200, blank=True, null=True)
    class Meta:
        app_label = "Community"



class Details_Of_Any_Issues_Related_To_Anti_Competitive_Conduct_By_The_Entity(models.Model):
    id = models.IntegerField(primary_key=True,null=False) 
    Financial_Year = models.CharField(max_length=50, blank=True, null=True)
    Name_OF_Authority = models.CharField(max_length=200, blank=True, null=True)
    Brief_Of_The_Case = models.CharField(max_length=200, blank=True, null=True)
    Corrective_Action_Taken = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        app_label = "Community"



class Information_on_CSR_Projects(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    State = models.CharField(max_length=100,blank=True,null=True)
    Aspirational_District = models.CharField(max_length=100,blank=True,null=True)
    Amount_Spent = models.IntegerField(blank=True,null=True)  
    Description_CSR = models.CharField(max_length=30000,blank=True,null=True)
    
    class Meta:
        app_label = "Community"




class Details_Of_Public_Policy_Positions_Advocated_By_The_Entity(models.Model):
    id = models.IntegerField(primary_key=True,null=False) 
    Financial_Year = models.CharField(max_length=50, blank=True, null=True)
    Sr_No =  models.IntegerField(blank=True, null=True)
    Public_Policy_Advocated = models.CharField(max_length=2000, blank=True, null=True)
    Method_Resorted_For_Such_Advocacy = models.CharField(max_length=2000, blank=True, null=True)
    Information_Available_In_Public_Domain =  models.CharField(max_length=2000, blank=True, null=True)
    Frequency_Of_Engagement =  models.CharField(max_length=2000, blank=True, null=True)
    Web_Link = models.CharField(max_length=2000, blank=True, null=True)
    Description_Details = models.CharField(max_length=2000, blank=True, null=True)
    class Meta:
        app_label = "Community"



class Benefits_Derived_And_Shared_From_Intellectual_Property(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=100,blank=True,null=True)
    IP = models.CharField(max_length=100,blank=True,null=True)
    Owned = models.CharField(max_length=100,blank=True,null=True)  
    Benefit_Shared = models.CharField(max_length=100,blank=True,null=True) 
    Basis_of_Calculating_Benefit_Share = models.CharField(max_length=100,blank=True,null=True) 

    class Meta:
        app_label = "Community"



class Awareness_Programmes_For_Value_Chain_Partners(models.Model):
    id = models.IntegerField(primary_key=True,null=False) 
    Financial_Year = models.CharField(max_length=50, blank=True, null=True)
    # Facility =  models.CharField(max_length=200, blank=True, null=True)
    Total_No_Of_Programmes_Held = models.IntegerField(blank=True, null=True)
    Topics_Covered = models.CharField(max_length=5000, blank=True, null=True)
    Percentage_Of_Persons_Covered = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True)

    class Meta:
        app_label = "Community"



class Details_Of_Intellectual_Property_Related_Disputes(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=100,blank=True,null=True)
    Name_of_Authority = models.CharField(max_length=100,blank=True,null=True)
    Brief_of_The_case = models.CharField(max_length=100,blank=True,null=True)
    Corrective_Actions_Taken = models.CharField(max_length=100,blank=True,null=True)

    class Meta:
        app_label = "Community"

class Details_Of_Beneficiaries_Of_CSR_Projects(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    CSR_Project = models.CharField(max_length=5000,blank=True,null=True) 
    NO_Of_Persons_Benefitted_From_CSR_Projects = models.IntegerField(blank=True,null=True) 
    Percent_of_Beneficiaries_From_Vulnerable_And_Merginalized_Groups = models.IntegerField(blank=True,null=True) 

    class Meta:
        app_label = "Community" 


class Turnover_Of_Products_As_A_Percentage_Of_Turnover(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=100,blank=True,null=True) 
    Environment_Parameters = models.CharField(max_length=100,blank=True,null=True) 
    Safe_Usage = models.CharField(max_length=100,blank=True,null=True) 
    Recycling_Disposal = models.CharField(max_length=100,blank=True,null=True) 

    class Meta:
        app_label = "Community" 

class Number_of_Consumer_Complaints(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=100,blank=True,null=True) 
    Type = models.CharField(max_length=5000,blank=True,null=True)
    Received_During_The_Year = models.IntegerField(blank=True,null=True) 
    Pending_Resolution_At_End_Of_The_Year = models.IntegerField(blank=True,null=True) 
    Remarks = models.CharField(max_length=1000,blank=True,null=True) 

    class Meta:
        app_label = "Community" 


class Details_Of_Instances_Of_Product_Recalls(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=100,blank=True,null=True) 
    Recall_Type = models.CharField(max_length=5000,blank=True,null=True)
    Number = models.IntegerField(blank=True,null=True) 
    Reasons_For_Recall = models.CharField(max_length=100,blank=True,null=True)

    class Meta:
        app_label = "Community" 


class Corporate_Social_Responsibility_Details(models.Model):
    id = models.IntegerField(primary_key=True)
    Model_Name_Corporate = models.CharField(max_length=100,blank=True,null=True) 
    Heading = models.CharField(max_length=100,blank=True,null=True)
    Description = models.CharField(max_length=5000,blank=True,null=True) 
    Is_Verified =  models.CharField(max_length=100,blank=True, null=True)

    class Meta:
        app_label = "Community"


class Consumer_Details(models.Model):
    id = models.IntegerField(primary_key=True)
    Model_Name_Consumer = models.CharField(max_length=100,blank=True,null=True) 
    Heading = models.CharField(max_length=100,blank=True,null=True)
    Description_consumer = models.CharField(max_length=50000,blank=True,null=True) 
    Is_Verified =  models.CharField(max_length=100,blank=True, null=True)

    class Meta:
        app_label = "Community"


class Stakeholders_Details(models.Model):
    id = models.IntegerField(primary_key=True)
    Model_Name_Stakeholder = models.CharField(max_length=5000,blank=True,null=True) 
    Heading = models.CharField(max_length=100,blank=True,null=True)
    Description = models.CharField(max_length=50000,blank=True,null=True) 


    class Meta:
        app_label = "Community"



class Society_Details(models.Model):
    id = models.IntegerField(primary_key=True)
    Model_Name_Society = models.CharField(max_length=5000,blank=True,null=True) 
    Heading = models.CharField(max_length=100,blank=True,null=True)
    Description = models.CharField(max_length=50000,blank=True,null=True) 


    class Meta:
        app_label = "Community"
        app_label = "Community" 

class Details_Of_Social_Impact_Assessments(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Name_And_Brief_Details_Of_Project = models.CharField(max_length=5000,blank=True,null=True)
    SIA_Notification_No =  models.IntegerField(blank=True,null=True) 
    Date_Of_Notification = models.DateField(blank=True, null=True)
    Relevant_Web_Link = models.CharField(max_length=5000, blank=True, null=True)
    Conducted_By_Independent_External_Agency = models.CharField(max_length=5000,blank=True,null=True)
    Frequency_of_Review_by_Board = models.CharField(max_length=5000,blank=True,null=True)
    Results_Communicated_In_Public_Domain = models.CharField(max_length=5000,blank=True,null=True)
    Description_Details = models.CharField(max_length=5000,blank=True,null=True) 
    Whether_available_public_domain = models.CharField(max_length=5000,blank=True,null=True) 
    class Meta:
        app_label = "Community" 

class Ongoing_Rehabilitation_And_Resettlement(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=100,blank=True,null=True) 
    Name_Of_Project = models.CharField(max_length=5000,blank=True,null=True)
    State =  models.CharField(max_length=5000,blank=True,null=True) 
    District =  models.CharField(max_length=5000,blank=True,null=True) 
    No_Of_PAFs =  models.IntegerField(blank=True,null=True) 
    Percentage_Of_PAFs_Covered_By_R_R =  models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True)
    Amounts_Paid_To_PAFs  =  models.IntegerField(blank=True,null=True) 
    Description_Ongoing = models.CharField(max_length=5000,blank=True,null=True) 

    class Meta:
        app_label = "Community" 


class Percentage_Of_Input_Material(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=100,blank=True,null=True) 
    Directly_Sourced_From_MSMEs_Small_Producers =  models.DecimalField(decimal_places=2,max_digits=500,blank=True, null=True)
    Sourced_Directly_Within_The_District_And_Neighbouring_Districts =  models.DecimalField(decimal_places=2,max_digits=500,blank=True, null=True)

    class Meta:
        app_label = "Community" 

class Details_Of_Actions_Taken_To_Mitigate(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=100,blank=True,null=True) 
    Detail_of_Negative_Impact_Identified = models.CharField(max_length=5000,blank=True,null=True) 
    Corrective_Action_Taken =  models.CharField(max_length=5000,blank=True,null=True) 
    class Meta:
        app_label = "Community" 





"""
Models for Transparency and Disclosure Compliances
"""

class TransparencyAndDisclosureCompliancesModel(models.Model):
    id = models.IntegerField(primary_key=True,null=False) 
    Financial_Year=  models.CharField(max_length=50, blank=True, null=True)
    Stack_Holder_Group = models.CharField(max_length=50, blank=True, null=True)
    Field_Complaint = models.CharField(max_length=200, blank=True, null=True)
    Pending_Complaint = models.CharField(max_length=200, blank=True, null=True)
    Weblink = models.CharField(max_length=5000, blank=True, null=True)
    Remarks = models.TextField(blank=True, null=True)

    YES_NO_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    grievance_redressal_mechanism_in_place = models.CharField(
        max_length=255,
        choices=YES_NO_CHOICES,
        
        blank=True,
        null=True
    )
    class Meta:
        app_label = "Community"




"""
Model for Number Of Instances Of Data Breaches
"""
class Number_Of_Instance_Of_Data_Breache(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Number_Of_Instances_Of_Data_Breaches = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Percent_Of_Customers_Affected_By_Data_Breaches = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Description = models.CharField(max_length=200, blank=True, null=True)
    Impact = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        app_label = "Community"