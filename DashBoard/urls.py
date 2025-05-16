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
    path('total_programmes_held_by_facility/', views.TotalProgrammesHeldByFacilityDashboard.as_view(), name='total programmes held by facility'),
    path('skill_upgradtion_traning/',views.SkillUpgradtionTraningDashborad.as_view(), name='skill upgradtion traning'),
    path('traning_ingeneral_by_month/',views.TraningIngeneralByMonthDashborad.as_view(), name='traning ingeneral by month'),
    path('human_rights_training/',views.HumanRightsTrainingDashboard.as_view(), name='human rights training'),
    path('health_and_safety_traning_by_gender/',views.HealthSafetyTrainingByGender.as_view(), name='health and safety traning by gender'),
    path('training_ingeneral_by_segment/',views.TrainingIngeneralBySegment.as_view(), name='training ingeneral by segment'),


    

    




    






]