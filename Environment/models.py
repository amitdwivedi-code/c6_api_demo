from django.db import models
from .utils import *

# Create your models here.

########################################### Life Cycle ###########################################################
class Life_Cycle_Perspective_Assessments(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Product_Service = models.CharField(max_length=200, blank=True, null=True)
    NIC_Code = models.CharField(max_length=200, blank=True, null=True)
    Year_of_Assessment = models.CharField(max_length=200, blank=True, null=True)
    Boundary_for_Assessment = models.CharField(max_length=500, blank=True, null=True)
    Conducted_by_External_Agency = models.CharField(max_length=100, blank=True, null=True)
    URL_of_Published_Results = models.CharField(max_length=500, blank=True, null=True)
    Percent_of_Turnover_Contributed = models.CharField(max_length=100, blank=True, null=True)
    Description_Assessment = models.CharField(max_length=10000, blank=True, null=True)

    class Meta:
        app_label ="Environment"



class Concerns_and_Action(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Product_Service = models.CharField(max_length=200, blank=True, null=True)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Risk_Concern_in_Assessment = models.CharField(max_length=2000, blank=True, null=True)
    Corrective_Action_Taken = models.CharField(max_length=2000, blank=True, null=True)
    Description_Concern = models.CharField(max_length=10000, blank=True, null=True)    

    class Meta:
        app_label ="Environment"



class Material_Business_Conduct_Issue(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Material_Issue_Identified = models.CharField(max_length=2000, blank=True, null=True)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Risk_or_Opportunity = models.CharField(max_length=100, blank=True, null=True)
    Rationale_for_Identification = models.CharField(max_length=2000, blank=True, null=True)    
    Approach_to_Adapt_or_Mitigate = models.CharField(max_length=2000, blank=True, null=True)
    Positive_and_Negative_Financial_Implications = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        app_label ="Environment"



class Sustainable_Sourcing(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Total_Material_Input = models.CharField(max_length=5000, blank=True, null=True)
    Percent_of_Material_Input_Sustainably_Sourced = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)
    Is_Verified = models.CharField(max_length=200, blank=True, null=True)
    

    class Meta:
        app_label ="Environment"



class Recycled_or_Reused_Input_Material(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Total_Material_Input = models.CharField(max_length=2000, blank=True, null=True)
    Recycled_or_reused_Input_Material = models.DecimalField(decimal_places=2, max_digits=50, blank=True, null=True)

    class Meta:
        app_label ="Environment"



class Production(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Production_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Production_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Production_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Production_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Production_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Production_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Production_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Production_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Production_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Production_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Production_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Production_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Production = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    
    class Meta:
        app_label ="Environment"



class End_of_Life_of_Product(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Plastic_Reused = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Plastic_Recycled = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Plastic_Disposed = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    E_Waste_Reused = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    E_Waste_Recycled = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    E_Waste_Disposed = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Hazardous_Waste_Reused = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Hazardous_Waste_Recycled = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Hazardous_Waste_Disposed = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Other_Waste_Reused = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Other_Waste_Recycled = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Other_Waste_Disposed = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    
    class Meta:
        app_label ="Environment"




class Reclaimed_Products_and_Packaging(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Product_Category = models.CharField(max_length=200, blank=True, null=True)
    Total_no_of_Products_Sold = models.IntegerField(blank=True, null=False)
    Percent_of_Reclaimed = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)


    class Meta:
        app_label ="Environment"



class Reclaim_Process(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Material = models.CharField(max_length=200, blank=True, null=True)
    Reclaim_Type = models.CharField(max_length=200, blank=True, null=True)
    Process = models.CharField(max_length=500, blank=True, null=True)    


    class Meta:
        app_label ="Environment"

# ########################################## Energy #########################################################################

class Energy_Assessment_by_External_Agency(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Agency_Name = models.CharField(max_length=200, blank=True, null=True)
    Agency_Type = models.CharField(max_length=200, blank=True, null=True)
    Description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        app_label = "Environment"



class Electricity_Consumption_mwh(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Source = models.CharField(max_length=200, blank=True, null=True)
    Unit = models.CharField(max_length=15, blank=True, null=True)
    Electricity_Consumption_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Electricity_Consumption = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)


    class Meta:
        app_label = "Environment"



class Electricity_Consumption_GJ(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Source = models.CharField(max_length=200, blank=True, null=True)
    Unit = models.CharField(max_length=15, blank=True, null=True)
    Electricity_Consumption_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Electricity_Consumption_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Electricity_Consumption = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    

    class Meta:
        app_label = "Environment"



class Fuel_Consumption_Onsite_Combustion_General(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Fuel_Type = models.CharField(max_length=200, blank=True, null=True)
    Unit = models.CharField(max_length=200, blank=True, null=True)
    Fuel_Consumption_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Fuel_Consumption = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)


    class Meta:
        app_label = "Environment"



class Fuel_Consumption_Onsite_Combustion_GJ(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Fuel_Type = models.CharField(max_length=200, blank=True, null=True)
    Unit = models.CharField(max_length=200, blank=True, null=True)
    Fuel_Consumption_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Fuel_Consumption = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)


    class Meta:
        app_label = "Environment"




class Fuel_Consumption_Onsite_Vehicles_General(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Fuel_Type = models.CharField(max_length=200, blank=True, null=True)
    Unit = models.CharField(max_length=200, blank=True, null=True)
    Ownership = models.CharField(max_length=200, blank=True, null=True)
    Fuel_Consumption_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Fuel_Consumption = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)


    class Meta:
        app_label = "Environment"



class Fuel_Consumption_Onsite_Vehicles_GJ(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Fuel_Type = models.CharField(max_length=200, blank=True, null=True)
    Unit = models.CharField(max_length=200, blank=True, null=True)
    Ownership = models.CharField(max_length=200, blank=True, null=True)
    Fuel_Consumption_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Fuel_Consumption = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)


    class Meta:
        app_label = "Environment"



class Inbound_Logistics(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Fuel_Type = models.CharField(max_length=200, blank=True, null=True)
    Unit = models.CharField(max_length=15, blank=True, null=True)
    Ownership = models.CharField(max_length=200, blank=True, null=True)
    Fuel_Consumption_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Fuel_Consumption = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)


    class Meta:
        app_label = "Environment"



class Outbound_Logistics(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Fuel_Type = models.CharField(max_length=200, blank=True, null=True)
    Unit = models.CharField(max_length=15, blank=True, null=True)
    Ownership = models.CharField(max_length=200, blank=True, null=True)
    Fuel_Consumption_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Fuel_Consumption = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)


    class Meta:
        app_label = "Environment"


class Business_Travel(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Mode = models.CharField(max_length=200, blank=True, null=True)
    Employee_Code = models.CharField(max_length=200, blank=True, null=True)
    Source = models.CharField(max_length=200, blank=True, null=True)
    Destination = models.CharField(max_length=200, blank=True, null=True)
    Unit = models.CharField(max_length=15, blank=True, null=True)
    Fuel_Consumption_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Fuel_Consumption = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)


    class Meta:
        app_label = "Environment"



class Employee_Commuting(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Employee_Code = models.CharField(max_length=200, blank=True, null=True)
    Employee_Name = models.CharField(max_length=500, blank=True, null=True)
    Commute_to_Work = models.CharField(max_length=200, blank=True, null=True)
    Type_of_Transport = models.CharField(max_length=200, blank=True, null=True)
    Vehicle_Type = models.CharField(max_length=200, blank=True, null=True)
    Fuel_Type = models.CharField(max_length=200, blank=True, null=True)
    Unit = models.CharField(max_length=15, blank=True, null=True)
    Company_Bus_Route = models.CharField(max_length=200, blank=True, null=True)
    Daily_Distance_Covered = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Fuel_Consumption_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Fuel_Consumption = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)


    class Meta:
        app_label = "Environment"



class Energy_Intensity(models.Model):
    #id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Energy_Intensity_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Energy_Intensity = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)



class Energy_Intensity_for_Production(models.Model):
    #id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Energy_Intensity_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Intensity_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Energy_Intensity = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)


    class Meta:
        app_label = "Environment"



class Energy_Consumption_Other_Sources(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    # Source =  models.CharField(max_length=200, blank=True, null=True)
    Energy_Consumption_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Consumption_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Consumption_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Consumption_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Consumption_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Consumption_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Consumption_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Consumption_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Consumption_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Consumption_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Consumption_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Energy_Consumption_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Energy_Consumption = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"



class Process_Emissions(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Gas_Type = models.CharField(max_length=200, blank=True, null=True)
    Unit = models.CharField(max_length=20, blank=True, null=True)
    Process_Emissions_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Process_Emissions_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Process_Emissions_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Process_Emissions_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Process_Emissions_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Process_Emissions_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Process_Emissions_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Process_Emissions_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Process_Emissions_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Process_Emissions_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Process_Emissions_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Process_Emissions_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Process_Emissions = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"



class Refrigerant_Losses(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Month = models.CharField(max_length=200, blank=True, null=True)
    Type = models.CharField(max_length=200, blank=True, null=True)
    Unit = models.CharField(max_length=200, blank=True, null=True)
    Purchased_Quantity = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Stock_at_Start = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Stock_at_End = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    To_Fill_New_Equipment = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)


    class Meta:
        app_label = "Environment"

#################################################################  Water And Air    #######################################################################

class Water_Assessment_By_External_Agency(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Agency_Name= models.CharField(max_length=100,blank=True, null=True)
    Agency_Type = models.CharField(max_length=200,blank=True , null=True)
    Description = models.CharField(max_length=500,blank=True,null=True)

    class Meta:
        app_label = "Environment"


class Water_Intensity(models.Model):
    #id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Water_Intensity_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Intensity_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Intensity_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Intensity_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Intensity_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Intensity_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Intensity_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Intensity_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Intensity_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Intensity_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Intensity_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Intensity_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Water_Intensity = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)


    class Meta:
        app_label = "Environment"

class Water_Stress_Areas(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=100, blank=True, null=True)
    State = models.CharField(max_length=100,blank=True, null=True)
    Operation = models.CharField(max_length=100,blank=True, null=True)
    Reference = models.CharField(max_length=100,blank=True, null=True)

    class Meta:
        app_label = "Environment"



class Water_withdrawal_By_Source(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Source = models.CharField(max_length=200, blank=True, null=True)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Water_withdrawal_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_withdrawal_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_withdrawal_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_withdrawal_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_withdrawal_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_withdrawal_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_withdrawal_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_withdrawal_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_withdrawal_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_withdrawal_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_withdrawal_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_withdrawal_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Water_withdrawal = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    
    
    class Meta:
        app_label = "Environment"




class Water_Consumption(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Water_Consumption_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Consumption_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Consumption_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Consumption_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Consumption_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Consumption_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Consumption_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Consumption_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Consumption_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Consumption_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Consumption_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Consumption_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Consumption = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"



class Water_Discharge_To_Destination_Without_Treatment(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Destination = models.CharField(max_length=200, blank=True, null=True)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Water_Discharge_Without_Treatment_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_Without_Treatment_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_Without_Treatment_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_Without_Treatment_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_Without_Treatment_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_Without_Treatment_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_Without_Treatment_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_Without_Treatment_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_Without_Treatment_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_Without_Treatment_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_Without_Treatment_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_Without_Treatment_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Water_Discharge_Without_Treatment = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"



class Water_Discharge_To_Destination_With_Treatment(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Destination = models.CharField(max_length=200, blank=True, null=True)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Level_Of_Treatment = models.CharField(max_length=20, blank=True, null=True)
    Water_Discharge_With_Treatment_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_With_Treatment_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_With_Treatment_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_With_Treatment_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_With_Treatment_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_With_Treatment_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_With_Treatment_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_With_Treatment_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_With_Treatment_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_With_Treatment_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_With_Treatment_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Water_Discharge_With_Treatment_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Water_Discharge_With_Treatment = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"


class Air_Emissions_Other_Than_GHG_Emissions(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=5000, blank=True, null=True)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Parameter = models.CharField(max_length=5000, blank=True, null=True)
    Unit = models.CharField(max_length=5000, blank=True, null=True)
    Air_Emissions_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Air_Emissions_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Air_Emissions_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Air_Emissions_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Air_Emissions_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Air_Emissions_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Air_Emissions_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Air_Emissions_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Air_Emissions_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Air_Emissions_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Air_Emissions_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Air_Emissions_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Air_Emission = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"

######################################################## GHG Emmission    ########################################################################


class Scope1_Emissions_by_Facilities(models.Model):
    #id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Emission_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Emission = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"



class Scope1_Emissions_by_Fuel(models.Model):
    #id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Fuel_Type = models.CharField(max_length=200, blank=True, null=True)
    Emission_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Emission = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"



class Scope1_Emissions_by_GHG_Type(models.Model):
    #id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    GHG_Type = models.CharField(max_length=200, blank=True, null=True)
    Emission_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Emission = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"



class Scope1_Intensity(models.Model):
    #id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Intensity_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Intensity = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"



class Scope2_Emissions_by_Facilities(models.Model):
    #id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Emission_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Emission = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"



class Scope2_Emissions_by_Fuel(models.Model):
    #id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Type = models.CharField(max_length=200, blank=True, null=True)
    Emission_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Emission = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"



class Scope2_Emissions_by_GHG_Type(models.Model):
    #id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    GHG_Type = models.CharField(max_length=200, blank=True, null=True)
    Emission_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Emission = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"



class Scope3_Emissions_by_Facilities(models.Model):
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Emission_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Emission = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"


class Scope3_Emissions_by_Activity(models.Model):
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Activity = models.CharField(max_length=200, blank=True, null=True)
    Emission_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Emission = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment" 


class Scope3_Emissions_by_GHG_Type(models.Model):
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    GHG_Type = models.CharField(max_length=200, blank=True, null=True)
    Emission_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Emission_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Emission = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"


class Scope3_Intensity(models.Model):
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Intensity_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Intensity = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"



class Scope2_Intensity(models.Model):
    #id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Intensity_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Intensity_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Intensity = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"


class Emission_Assessment_By_External_Agency(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Agency = models.CharField(max_length=200, blank=True, null=True)
    Type = models.CharField(max_length=200, blank=True, null=True)
    Description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        app_label = "Environment"


class EmissionFactors(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Type_of_Emission = models.CharField(max_length=100)
    Reference = models.CharField(max_length=500, blank=True, null=True)

    Fuel = models.CharField(max_length=100,blank=False, null=False)
    Unit = models.CharField(max_length=20,blank=False, null=False)
    CO2E_Emission_Factor = models.DecimalField(decimal_places=8,max_digits=50,null=True,blank=True)
    Biogenic_CO2E_Emission_Factor = models.CharField(max_length=50,blank=False, null=False)

    CO2_Emission_Factor = models.DecimalField(decimal_places=8,max_digits=50,null=True,blank=True)
    CH4_Emission_Factor = models.DecimalField(decimal_places=8,max_digits=50,null=True,blank=True)
    HFC_Emission_Factor = models.DecimalField(decimal_places=8,max_digits=50,null=True,blank=True)
    PFC_Emission_Factor = models.DecimalField(decimal_places=8,max_digits=50,null=True,blank=True)
    SF6_Emission_Factor = models.DecimalField(decimal_places=8,max_digits=50,null=True,blank=True)
    NF3_Emission_Factor = models.DecimalField(decimal_places=8,max_digits=50,null=True,blank=True)
    N2O_Emission_Factor = models.DecimalField(decimal_places=8,max_digits=50,null=True,blank=True)
    Upstream_CO2E_Emission_Factor = models.DecimalField(decimal_places=8,max_digits=50,null=True,blank=True)
    Energy_Use_Emission_Factor = models.DecimalField(decimal_places=8,max_digits=50,null=True,blank=True)

    Greenhouse_Gas = models.CharField(max_length=200, blank=True, null=True)
    Formula = models.CharField(max_length=100, blank=True, null=True)
    Hundred_year_GWP = models.DecimalField(decimal_places=8,max_digits=50,null=True,blank=True)

    Country_or_Region = models.CharField(max_length=200, blank=True, null=True)
    Year = models.IntegerField(blank=True, null=True)
    Type = models.CharField(max_length=200, blank=True, null=True)

    Mode = models.CharField(max_length=100, blank=True, null=True)
    Conversion_Factor = models.DecimalField(decimal_places=8,max_digits=50,null=True,blank=True)

    Mode_of_Commute = models.CharField(max_length=200, blank=True, null=True)
    Type_of_Transport = models.CharField(max_length=200, blank=True, null=True)
    Type_of_Vehicle = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        app_label = "Environment"
        # db_table = "emission_factors"


###############################################################  Waste   ##############################################################################################


class Waste_Assessment_By_External_Agency(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Agency_Name= models.CharField(max_length=100,blank=True, null=True)
    Agency_Type = models.CharField(max_length=200,blank=True , null=True)
    Description = models.CharField(max_length=500,blank=True,null=True)

    class Meta:
        app_label = "Environment"


class Waste_Generated(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Type = models.CharField(max_length=200, blank=True, null=True)
    Waste_Generated_Apr = models.DecimalField(decimal_places=3,max_digits=50,blank=True, null=True)
    Waste_Generated_May = models.DecimalField(decimal_places=3,max_digits=50,blank=True, null=True)
    Waste_Generated_Jun = models.DecimalField(decimal_places=3,max_digits=50,blank=True, null=True)
    Waste_Generated_Jul = models.DecimalField(decimal_places=3,max_digits=50,blank=True, null=True)
    Waste_Generated_Aug = models.DecimalField(decimal_places=3,max_digits=50,blank=True, null=True)
    Waste_Generated_Sep = models.DecimalField(decimal_places=3,max_digits=50,blank=True, null=True)
    Waste_Generated_Oct = models.DecimalField(decimal_places=3,max_digits=50,blank=True, null=True)
    Waste_Generated_Nov = models.DecimalField(decimal_places=3,max_digits=50,blank=True, null=True)
    Waste_Generated_Dec = models.DecimalField(decimal_places=3,max_digits=50,blank=True, null=True)
    Waste_Generated_Jan = models.DecimalField(decimal_places=3,max_digits=50,blank=True, null=True)
    Waste_Generated_Feb = models.DecimalField(decimal_places=3,max_digits=50,blank=True, null=True)
    Waste_Generated_Mar = models.DecimalField(decimal_places=3,max_digits=50,blank=True, null=True)
    Waste_Generated_Total = models.DecimalField(decimal_places=3,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"

class Waste_Recovered(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Facility = models.CharField(max_length=20, blank=True, null=True)
    Waste_Recovered_Category = models.CharField(max_length=200, blank=True, null=True)
    Waste_Recovered_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Recovered_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Recovered_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Recovered_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Recovered_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Recovered_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Recovered_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Recovered_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Recovered_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Recovered_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Recovered_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Recovered_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Recovered_Total = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"


class Waste_Disposed(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Facility = models.CharField(max_length=20, blank=True, null=True)
    Waste_Disposed_Category = models.CharField(max_length=200, blank=True, null=True)
    Waste_Disposed_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Disposed_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Disposed_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Disposed_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Disposed_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Disposed_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Disposed_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Disposed_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Disposed_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Disposed_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Disposed_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Disposed_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Disposed_Total = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)

    class Meta:
        app_label = "Environment"




class Waste_Intensity(models.Model):
    # id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=200, blank=True, null=True)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Waste_Intensity_Apr = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Intensity_May = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Intensity_Jun = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Intensity_Jul = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Intensity_Aug = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Intensity_Sep = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Intensity_Oct = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Intensity_Nov = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Intensity_Dec = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Intensity_Jan = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Intensity_Feb = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Waste_Intensity_Mar = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)
    Total_Waste_Intensity = models.DecimalField(decimal_places=2,max_digits=50,blank=True, null=True)


    class Meta:
        app_label = "Environment"

########################################################    Sustainability    ####################################################################

class Percentage_Of_R_and_D_and_Capex_Investments(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    Percentage_of_R_and_D_investments = models.DecimalField(decimal_places=2, max_digits=100, blank=True, null=True)
    Details_investment = models.CharField(max_length=2000, blank=True, null=True)
    Percent_of_capex= models.DecimalField(decimal_places=2, max_digits=100, blank=True, null=True)
    Details_capex = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        app_label = "Environment"

class Operations_In_Ecologically_Sensitive_Areas(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Facility = models.CharField(max_length=200, blank=True, null=True)
    Operation = models.CharField(max_length = 5000,blank=True,null = True)
    Clearance = models.CharField(max_length=500, blank=True, null=True)
    Reason = models.CharField(max_length=5000, blank=True, null=True)
    # Description_operation = models.CharField(max_length=5000, blank=True, null=True)
    class Meta:
        app_label = "Environment"


class Environmental_Impact_Assessments_Of_Projects_Undertaken(models.Model):
    id = models.IntegerField(primary_key=True,null=False)   
    Name_of_project = models.CharField(max_length=5000, blank=True, null=True)  
    Project_details = models.CharField(max_length=5000, blank=True, null=True)  
    Eia_notification_no = models.CharField(max_length=5000, blank=True, null=True)  
    Date = models.DateField(max_length=5000, blank=True, null=True)  
    Conducted_by_external_agency = models.CharField(max_length=5000, blank=True, null=True)  
    In_public_domain = models.CharField(max_length=5000, blank=True, null=True)  
    Results = models.CharField(max_length=5000, blank=True, null=True,validators=[custom_url_validator])     


    class Meta:
        app_label = "Environment"

class Non_Compliance_With_The_Applicable_Environmental_Law(models.Model):
    id = models.IntegerField(primary_key=True,null=False)   
    The_law_regulations_guidlines_which_was_not_complied_with = models.CharField(max_length=200, blank=True, null=True)
    Details_of_non_compliance = models.CharField(max_length=200, blank=True, null=True)
    Any_fine_penalties_action = models.CharField(max_length=200, blank=True, null=True)
    Corrective_action_taken_if_any = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        app_label = "Environment"

class Initiatives_Towards_Carbon_Zero(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Initiative_undertaken= models.CharField(max_length=200, blank=True, null=True)
    Details_of_the_initiative = models.CharField(max_length=200, blank=True, null=True)
    Outcome_of_the_initiative = models.CharField(max_length=200, blank=True, null=True)
    Web_link = models.CharField(max_length=200, blank=True, null=True,validators=[custom_url_validator])

    class Meta:
        app_label = "Environment"





