from django.urls import path
from . import views


urlpatterns = [
    path('companydetails_dashboard/', views.Companydetails_Dashboard.as_view(), name='get_turnover_networth_summery'),
    path('energy_consumption_breakdown_dashboard/', views.EnergyConsumptionBreakdown_Dashboard.as_view(), name='get_energy_consumption_breakdown_summery'),
    path('electricity_distribution_dashboard/', views.Electricity_Distribution_Dashboard.as_view(), name='get_electricity_distribution_summery'),
    path('water_consumption_dashboard/', views.Water_Consumption_Dashboard.as_view() , name='get_Water_Consumption_summery'),
    path('scope1_emission_dashboard/',views.Scope1_Emission_Dashboard.as_view(), name='scope1_emission_dashboard')


    






]