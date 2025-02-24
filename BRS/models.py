from django.db import models

# Create your models here.
# from djongo import models

# class BRS_Policy_1(models.Model):
#     id = models.IntegerField(primary_key=True,null=False)
#     Principle_Core_Elements_NGRBC = models.JSONField(default=list)
#     Policy_into_Procedures = models.JSONField(default=list)
#     Performance_of_Entity_with_reasons = models.CharField(max_length=5000, blank=True, null=True)
#     Name_of_National_International_Codes = models.CharField(max_length=5000, blank=True, null=True)
#     Policy_Approved_by_Board = models.JSONField(default=list)
#     Policies_Extend_Value_Chain_Partners = models.JSONField(default=list)
#     Specific_Commitments_Goals_Targets = models.CharField(max_length=5000, blank=True, null=True)
#     Web_Link_Policies = models.JSONField(default=list)
#     Principles_Material_Business = models.JSONField(default=list)
#     Financial_Human_Technical_Resources = models.JSONField(default=list)
#     Other_Reason = models.CharField(max_length=5000, blank=True, null=True)
#     Planned_Next_Financial_Year = models.JSONField(default=list)
#     Position_Formulate_Policies = models.JSONField(default=list)

#     class Meta:
#         app_label = "BRS_Policy_1"

class BRS_Policy_1(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Model_Name = models.CharField(max_length=5000, blank=True, null=True)
    Heading = models.CharField(max_length=100, blank=True, null=True)
    Description = models.CharField(max_length=5000, blank=True, null=True)
    Select_All = models.CharField(max_length=50, blank=True, null=True)
    P1 = models.CharField(max_length=50, blank=True, null=True)
    P2 = models.CharField(max_length=50, blank=True, null=True)
    P3 = models.CharField(max_length=50, blank=True, null=True)
    P4 = models.CharField(max_length=50, blank=True, null=True)
    P5 = models.CharField(max_length=50, blank=True, null=True)
    P6 = models.CharField(max_length=50, blank=True, null=True)
    P7 = models.CharField(max_length=50, blank=True, null=True)
    P8 = models.CharField(max_length=50, blank=True, null=True)
    P9 = models.CharField(max_length=50, blank=True, null=True)
    
    
    
    class Meta:
        app_label = "BRS"


class BRS_Policy_1a(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Model_Name = models.CharField(max_length=5000, blank=True, null=True)
    Heading = models.CharField(max_length=100, blank=True, null=True)
    Description = models.CharField(max_length=5000, blank=True, null=True)
    Select_All = models.CharField(max_length=50, blank=True, null=True)
    P1 = models.CharField(max_length=50, blank=True, null=True)
    P2 = models.CharField(max_length=50, blank=True, null=True)
    P3 = models.CharField(max_length=50, blank=True, null=True)
    P4 = models.CharField(max_length=50, blank=True, null=True)
    P5 = models.CharField(max_length=50, blank=True, null=True)
    P6 = models.CharField(max_length=50, blank=True, null=True)
    P7 = models.CharField(max_length=50, blank=True, null=True)
    P8 = models.CharField(max_length=50, blank=True, null=True)
    P9 = models.CharField(max_length=50, blank=True, null=True)
    
    
    
    
    class Meta:
        app_label = "BRS"
        
        

class BRS_Policy_2(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Model_Name = models.CharField(max_length=5000, blank=True, null=True)
    Heading = models.CharField(max_length=100, blank=True, null=True)
    Description = models.CharField(max_length=5000, blank=True, null=True)
    Frequency = models.CharField(max_length=50, blank=True, null=True)
    Select_All = models.CharField(max_length=50, blank=True, null=True)
    P1 = models.CharField(max_length=50, blank=True, null=True)
    P2 = models.CharField(max_length=50, blank=True, null=True)
    P3 = models.CharField(max_length=50, blank=True, null=True)
    P4 = models.CharField(max_length=50, blank=True, null=True)
    P5 = models.CharField(max_length=50, blank=True, null=True)
    P6 = models.CharField(max_length=50, blank=True, null=True)
    P7 = models.CharField(max_length=50, blank=True, null=True)
    P8 = models.CharField(max_length=50, blank=True, null=True)
    P9 = models.CharField(max_length=50, blank=True, null=True)
    
    
    
    
    class Meta:
        app_label = "BRS"        