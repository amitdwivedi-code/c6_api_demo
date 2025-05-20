from django.urls import path
from . import views


urlpatterns = [
    ############################################# company details #############################################
    path('companydetails_dashboard/', views.Companydetails_Dashboard.as_view(), name='get_turnover_networth_summery'),

    ############################################# quick action  #############################################
    path('energy_consumption_breakdown_dashboard/', views.EnergyConsumptionBreakdown_Dashboard.as_view(), name='energy and quick action'),
    path('electricity_distribution_dashboard/', views.Electricity_Distribution_Dashboard.as_view(), name='quick action'),
    path('water_consumption_dashboard/', views.Water_Consumption_Dashboard.as_view() , name='quick action'),
    path('fuel_distribution_dashboard/', views.Fuel_Distribution_Dashboard.as_view(), name='quick action'),
    path('scope2_emission_dashboard/',views.Scope2_Emission_Dashboard.as_view(), name='quick action page'),
    path('scope1_emission_dashboard/',views.Scope1_Emission_Dashboard.as_view(), name='quick action page'),

    ############################################# energy #############################################
    path('combined_fuel_consumption_dashboard/', views.Combined_Fuel_Consumption_Dashboard.as_view(), name='energy dashboard'),
    path('combined_electricity_consumption_dashboard/', views.Combined_Electricity_Consumption_Dashboard.as_view(), name='energy dashboard'),

    ############################################# waste #############################################
    path('waste_generated_dashboard/',views.Waste_Generated_Dashboard.as_view(),name="waste generated summery"),
    path('waste_recovered_dashboard/',views.Waste_Recovered_Dashboard.as_view(),name="waste recovered summery"),
    path('waste_disposed_dashboard/',views.Waste_Disposed_Dashboard.as_view(),name="waste disposed summery"),
    path('total_waste_generated_dashboard/',views.Total_Waste_Generated_Dashboard.as_view(),name="total waste generated summery"),


    ############################################# GHG Emission #############################################
    path('combined_scope1_emission_dashboard/',views.Combined_Scope1_Emission_Dashboard.as_view(),name="scope1 emission summery"),
    path('combined_scope2_emission_dashboard/',views.Combined_Scope2_Emission_Dashboard.as_view(),name="scope2 emission summery"),

    ############################################# Workforce ################################################
    path('employee_summary_dashboard/',views.CombinedEmployeeWorkerDashboard.as_view(),name="workforce Emp, permant vs non-permants, workforce workers"),
    path('plant_wise_distribution/',views.PlantWiseDistributionDashboard.as_view(),name="plant wise distribution and total workers month"),
    path('female_distribution/', views.FemaleDistributionDashboard.as_view(), name='female_distribution'),
    
    ############################################# Traning ################################################
    path('skill_upgradtion_and_total_programmes_held_by_facility/',views.SkillAndProgrammeDashboard.as_view(), name='skill upgradtion traning and total programmes held by facility'), 
    path('health_and_safety_by_gender_and_human_rights_training/',views.CombinedTrainingDashboard.as_view(), name='health and safety traning by gender, human rights training'),
    path('training_ingeneral_by_segment_and_month/',views.TrainingIngeneralDashboard.as_view(), name='training ingeneral by segment and month'),
 


    

    




    






]