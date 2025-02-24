from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [

    ######################################################### life_cycle  #######################################################################
    path('life_cycle/life_cycle_assessment/production/', views.Production_View.as_view(), name='add_get_production'),
    path('life_cycle/life_cycle_assessment/production/<int:id>/', views.Production_View.as_view(), name='update_delete_production'),
    
    path('life_cycle/life_cycle_assessment/life_cycle_perspective_assessments/', views.Life_Cycle_Perspective_Assessments_View.as_view(), name='add_get_lifecycle_perspective_assessments'),
    path('life_cycle/life_cycle_assessment/life_cycle_perspective_assessments/<int:id>/', views.Life_Cycle_Perspective_Assessments_View.as_view(), name='update_delete_lifecycle_perspective_assessments'),
    
    path('life_cycle/life_cycle_assessment/concerns_and_action/', views.Concerns_and_Action_View.as_view(), name='add_get_concerns_and_action'),
    path('life_cycle/life_cycle_assessment/concerns_and_action/<int:id>/', views.Concerns_and_Action_View.as_view(), name='update_delete_concerns_and_action'),
    
    path('life_cycle/material/material_business_conduct_issue/', views.Material_Business_Conduct_Issue_View.as_view(), name='add_get_material_business_conduct_issue'),
    path('life_cycle/material/material_business_conduct_issue/<int:id>/', views.Material_Business_Conduct_Issue_View.as_view(), name='update_delete_material_business_conduct_issue'),
    
    path('life_cycle/material/sustainable_sourcing/', views.Sustainable_Sourcing_View.as_view(), name='add_get_sustainable_sourcing'),
    path('life_cycle/material/sustainable_sourcing/<int:id>/', views.Sustainable_Sourcing_View.as_view(), name='update_delete_sustainable_sourcing'),
    
    path('life_cycle/material/input_material_list/', views.Input_MaterialList_View.as_view(), name='list'),
    path('life_cycle/material/recycled_or_reused_input_material/', views.Recycled_or_Reused_Input_Material_View.as_view(), name='add_get_recycled_ip_material'),
    path('life_cycle/material/recycled_or_reused_input_material/<int:id>/', views.Recycled_or_Reused_Input_Material_View.as_view(), name='update_delete_recycled_ip_material'),
    
    path('life_cycle/reclaim/end_of_life_of_product/', views.End_of_Life_of_Product_View.as_view(), name='add_get_end_of_life_of_product'),
    path('life_cycle/reclaim/end_of_life_of_product/<int:id>/', views.End_of_Life_of_Product_View.as_view(), name='update_delete_life_of_product'),
    
    path('life_cycle/reclaim/reclaimed_products_and_packaging/', views.Reclaimed_Products_and_Packaging_View.as_view(), name='add_get_reclaimed_products_and_packaging'),
    path('life_cycle/reclaim/reclaimed_products_and_packaging/<int:id>/', views.Reclaimed_Products_and_Packaging_View.as_view(), name='update_delete_reclaimed_products_and_packaging'),
    
    path('life_cycle/reclaim/material/', views.MaterialList_View.as_view(), name='materialList'),
    path('life_cycle/reclaim/reclaim_type/', views.ReclaimTypeList_View.as_view(), name='reclaimtypeList'),
    path('life_cycle/reclaim/reclaim_process/', views.Reclaim_Process_View.as_view(), name='add_get_reclaim_process'),
    path('life_cycle/reclaim/reclaim_process/<int:id>/', views.Reclaim_Process_View.as_view(), name='update_delete_reclaim_process'),
    
    path('life_cycle/life_cycle_assessment/production/filter_by_facility/', views.Production_Filter.as_view(), name='filter_by_facility'),

    ################################################################    Energy    ################################################################

    path('energy/overall/agency_type/', views.AgencyTypeList_View.as_view(), name='agency_type_list'),
    path('energy/overall/assessment_by_external_agency/', views.Energy_Assessment_by_External_Agency_View.as_view(), name='add_get_assessment_by_external_agency'),
    path('energy/overall/assessment_by_external_agency/<int:id>/', views.Energy_Assessment_by_External_Agency_View.as_view(), name='update_delete_assessment_by_external_agency'),
    
    path('energy/electricity/source/', views.Elecricity_SourceList_View.as_view(), name='electricity_source_list'),
    
    path('energy/electricity/electricity_consumption_mwh/', views.Electricity_Consumption_mwh_View.as_view(), name='add_get_electricity_consumption_mwh'),
    path('energy/electricity/electricity_consumption_mwh/<int:id>/', views.Electricity_Consumption_mwh_View.as_view(), name='update_delete_electricity_consumption_mwh'),
    path('energy/electricity/electricity_consumption_mwh/filter', views.Electricity_Consumption_mwh_Filter_View.as_view(), name='filter_by_facility_electricity_consumption_GJ'),

    path('energy/electricity/electricity_consumption_GJ/', views.Electricity_Consumption_GJ_View.as_view(), name='get_electricity_consumption_GJ'),
    path('energy/electricity/electricity_consumption_GJ/filter', views.Electricity_Consumption_GJ_Filter_View.as_view(), name='filter_by_facility_electricity_consumption_GJ'),
    
    path('energy/fuel_combustion/onsite_combustion/fuel_type_list/', views.FuelTypeList_View.as_view(), name='fuel_type_list'),
    path('energy/fuel_combustion/onsite_combustion/fuel_unit_list/', views.FuelUnitList_View.as_view(), name='fuel_unit_list'),
    
    path('energy/fuel_combustion/onsite_combustion_general/', views.Fuel_Consumption_Onsite_Combustion_General_View.as_view(), name='add_get_fuel_consumption_by_onsite_combustion'),
    path('energy/fuel_combustion/onsite_combustion_general/<int:id>/', views.Fuel_Consumption_Onsite_Combustion_General_View.as_view(), name='update_delete_fuel_consumption_by_onsite_combustion'),

    path('energy/fuel_combustion/onsite_combustion_general/filter', views.Fuel_Consumption_Onsite_Combustion_General_Filter_View.as_view(), name='filter_fuel_consumption_by_onsite_combustion'),

    path('energy/fuel_combustion/onsite_combustion_GJ/', views.Fuel_Consumption_Onsite_Combustion_GJ_View.as_view(), name='get_fuel_consumption_GJ'),
    path('energy/fuel_combustion/onsite_combustion_GJ/filter', views.Fuel_Consumption_Onsite_Combustion_GJ_Filter_View.as_view(), name='get_filter_by_facility_fuel_consumption_GJ'),
    
    path('energy/fuel_combustion/onsite_vehicles_general/', views.Fuel_Consumption_Onsite_Vehicles_View.as_view(), name='add_get_fuel_consumption_by_onsite_vehicles'),

    path('energy/fuel_combustion/onsite_vehicles_general/filter', views.Fuel_Consumption_Onsite_Vehicles_Filter_View.as_view(), name='add_get_fuel_consumption_by_onsite_vehicles'),

    path('energy/fuel_combustion/onsite_vehicles_general/<int:id>/', views.Fuel_Consumption_Onsite_Vehicles_View.as_view(), name='update_delete_fuel_consumption_by_onsite_combustion'),
    path('energy/fuel_combustion/onsite_vehicles_GJ/', views.Fuel_Consumption_Onsite_Vehicles_GJ_View.as_view(), name='get_fuel_consumption_onsite_vehicles_GJ'),
    path('energy/fuel_combustion/onsite_vehicles_GJ/filter', views.Fuel_Consumption_Onsite_Vehicles_GJ_filter_View.as_view(), name='get_filter_by_facility_fuel_consumption_onsite_vehicles_GJ'),
    
    path('energy/fuel_combustion/onsite_vehicles/ownership/', views.Onsite_Vehicles_OwnershipList_View.as_view(), name='onsite_vehicles_ownership_list'),
    path('energy/fuel_combustion/onsite_vehicles/fuel_type/', views.OnsiteVehiclesFuelTypeList_View.as_view(), name='onsite_vehicles_fuel_type_list'),
    path('energy/logistics/fuel_type/', views.Logistics_Fuel_Type_List_View.as_view(), name='logistics_fuel_type_list'),
    
    path('energy/logistics/inbound_logistics/', views.Inbound_Logistics_View.as_view(), name='add_get_fuel_consumption_by_inbound_logistics'),
    path('energy/logistics/inbound_logistics/filter', views.Inbound_Logistics_Filter_View.as_view(), name='get_filter_by_facility'),
    path('energy/logistics/inbound_logistics/<int:id>/', views.Inbound_Logistics_View.as_view(), name='update_delete_fuel_consumption_by_inbound_logistics'),
    
    path('energy/logistics/outbound_logistics/', views.Outbound_Logistics_View.as_view(), name='add_get_fuel_consumption_by_outbound_logistics'),
    path('energy/logistics/outbound_logistics/filter', views.Outbound_Logistics_Filter_View.as_view(), name='get_filter_by_facility'),
    path('energy/logistics/outbound_logistics/<int:id>/', views.Outbound_Logistics_View.as_view(), name='update_delete_fuel_consumption_by_outbound_logistics'),

    path('energy/travel/business_travel/mode/', views.Business_Travel_Mode_List_View.as_view(), name='business_travel_mode_list'),
    path('energy/travel/business_travel/', views.Business_Travel_View.as_view(), name='add_get_business_travel'),
    path('energy/travel/business_travel/filter', views.Business_Travel_Filter_View.as_view(), name='get_filter_by_facility_business_travel'),
    path('energy/travel/business_travel/<int:id>/', views.Business_Travel_View.as_view(), name='update_delete_business_travel'),
    
    path('energy/travel/employee_commuting/', views.Employee_Commuting_View.as_view(), name='add_get_employee_commuting'),
    path('energy/travel/employee_commuting/filter', views.Employee_Commuting_Filter_View.as_view(), name='get_filter_by_facility_employee_commuting'),
    path('energy/travel/employee_commuting/<int:id>/', views.Employee_Commuting_View.as_view(), name='update_delete_employee_commuting'),
    path('energy/travel/employee_commuting/way_to_commute/', views.Employee_Commuting_Way_to_Commute_View.as_view(), name='get_way_to_commute'),
    path('energy/travel/employee_commuting/type_of_transport/', views.Employee_Commuting_Type_of_Transport_View.as_view(), name='get_type_of_transport'),
    path('energy/travel/employee_commuting/vehicle_type/', views.Employee_Commuting_Vehicle_Type_View.as_view(), name='get_vehicle_type'),
    path('energy/travel/employee_commuting/vehicle_fuel_type/', views.Employee_Commuting_Vehicle_Fuel_Type_View.as_view(), name='get_vehicle_fuel_type'),
    path('energy/travel/employee_commuting/company_bus_route/', views.Employee_Commuting_Company_Bus_Route_View.as_view(), name='get_'),

    path('energy/energy_intensity/energy_intensity_for_turnover/', views.Energy_Intensity_View.as_view(), name='get_energy_intensity'),
    path('energy/energy_intensity/energy_intensity_for_production/', views.Energy_Intensity_for_Production_View.as_view(), name='get_energy_intensity_for_Production'),
    
    path('energy/others/energy_consumption_other_sources/', views.Energy_Consumption_Other_Sources_View.as_view(), name='add_get_energy_consumption_other_sources'),
    path('energy/others/energy_consumption_other_sources/filter', views.Energy_Consumption_Other_Sources_Filter_View.as_view(), name='get_filter_by_facility_energy_consumption_other_sources'),
    path('energy/others/energy_consumption_other_sources/<int:id>/', views.Energy_Consumption_Other_Sources_View.as_view(), name='update_delete_energy_consumption_other_sources'),
    
    path('energy/others/process_emissions/gas_type/', views.GasTypeList_View.as_view(), name='get_gas_type'),

    path('energy/others/process_emissions/', views.Process_Emissions_View.as_view(), name='add_get_process_emissions'),
    path('energy/others/process_emissions/filter', views.Process_Emissions_Filter_View.as_view(), name='get_filter_by_facility_process_emissions'),
    path('energy/others/process_emissions/<int:id>/', views.Process_Emissions_View.as_view(), name='update_delete_process_emissions'),

    path('energy/others/refrigerant_losses/months/', views.Refrigerant_Losses_Months_View.as_view(), name='get_months'),
    path('energy/others/refrigerant_losses/type/', views.Refrigerant_Losses_TypesList_View.as_view(), name='get_refrigerant_losses_type'),
    path('energy/others/refrigerant_losses/', views.Refrigerant_Losses_View.as_view(), name='add_get_refrigerant_losses'),
    path('energy/others/refrigerant_losses/filter', views.Refrigerant_Losses_Filter_View.as_view(), name='get_filter_by_facility_refrigerant_losses'),
    path('energy/others/refrigerant_losses/<int:id>/', views.Refrigerant_Losses_View.as_view(), name='update_delete_refrigerant_losses'),

    # #####################################################################  Water And Air  ###########################################################
    path('water/overall/agency_type/',views.Water_AgencyTypeList_View.as_view(),name='agency_type_list'),
    path('water/overall/assessment_by_external_agency/',views.Assessment_By_External_Agency_View.as_view(),name='add_agency'),
    path('water/overall/assessment_by_external_agency/<int:id>/',views.Assessment_By_External_Agency_View.as_view(),name = 'update_delete_agency'),
    path('water/overall/water_stress_areas/',views.Water_Stress_Areas_View.as_view(),name='list_create'),
    path('water/overall/water_stress_areas/<int:id>/',views.Water_Stress_Areas_View.as_view(),name = 'post_update_delete_'),
    path('water/overall/water_intensity/',views.Water_Intensity_View.as_view(),name='list_create'),
    path('water/overall/water_intensity/<int:id>/',views.Water_Intensity_View.as_view(),name='update_delete'),
    path('water/source_list/',views.SourceList_View.as_view(),name='source_list'),
    path('water/water_withdrawal_by_source/',views.Water_Withdrawal_By_Source_View.as_view(),name='list_create'),
    path('water/water_withdrawal_by_source/<int:id>/',views.Water_Withdrawal_By_Source_View.as_view(),name = 'post_update_delete_'),
    path('water/water_consumption/',views.Water_Consumption_View.as_view(),name ='list_create'),

    path('water/water_consumption/filter/',views.Water_Consumption_Filter_View.as_view(),name ='list_create'),
    path('water/water_withdrawal_by_source/filter/',views.Water_Withdrawal_Filter_View.as_view(),name='Filter by facility'),
    path('water/water_discharge_to_destination_without_treatment/filter/',views.Water_Discharge_To_Destination_Without_Treatment_Filter_View.as_view(),name='without_treatment_Filter by facility'),
    path('water/water_discharge_to_destination_with_treatment/filter/',views.Water_Discharge_To_Destination_With_Treatment_Filter_View.as_view(),name='with_treatment_Filter by facility'),
    path('water/air_emissions/filter/',views.Air_Emissions_Other_Than_GHG_Emissions_Filter_View.as_view(),name = 'filter_by_facility_air_emissions_'),

    path('water/water_consumption/<int:id>/',views.Water_Consumption_View.as_view(),name='post_update_delete'),
    path('water/destination_list_without_treatment/',views.DestinationList_View.as_view(),name='destination_list'),
    path('water/water_discharge_to_destination_without_treatment/',views.Water_Discharge_To_Destination_Without_Treatment_View.as_view(),name = 'create'),
    path('water/water_discharge_to_destination_without_treatment/<int:id>/',views.Water_Discharge_To_Destination_Without_Treatment_View.as_view(),name = 'update_delete'),
    path('water/destination_list_with_treatment/',views.DestinationListWithTreatment_View.as_view(),name='destination_list'),
    path('water/water_discharge_to_destination_with_treatment/',views.Water_Discharge_To_Destination_With_Treatment_View.as_view(),name = 'create'),
    path('water/water_discharge_to_destination_with_treatment/<int:id>/',views.Water_Discharge_To_Destination_With_Treatment_View.as_view(),name = 'update_delete'),
    path('water/parameter_list/',views.ParameterList_View.as_view(),name='parameter_list'),
    path('water/unit_list/',views.UnitList_View.as_view(),name='unit_list'),
    path('water/air_emissions/',views.Air_Emissions_Other_Than_GHG_Emissions_View.as_view(),name = 'air_emissions_list'),
    path('water/air_emissions/<int:id>/',views.Air_Emissions_Other_Than_GHG_Emissions_View.as_view(),name = 'air_emissions_list'),

    
    # #############################################################  GHG Emmission  ###################################################################
    
    path('emissions/scope1/scope1_emissions_by_facilities/', views.Scope1_Emissions_by_Facilities_View.as_view(), name='get_scope1_emissions_by_facilities'),
    path('emissions/scope1/scope1_emissions_by_fuel/', views.Scope1_Emissions_by_Fuel_View.as_view(), name='get_scope1_emissions_by_fuel'),
    path('emissions/scope1/scope1_emissions_by_ghg_type/', views.Scope1_Emissions_by_GHG_Type_View.as_view(), name='get_scope1_emissions_by_ghg_type'),
    path('emissions/scope1/scope1_intensity/', views.Scope1_Intensity_View.as_view(), name='get_scope1_intensity'),

    path('emissions/scope2/scope2_emissions_by_facilities/', views.Scope2_Emissions_by_Facilities_View.as_view(), name='get_scope2_emissions_by_facilities'),
    path('emissions/scope2/scope2_emissions_by_fuel/', views.Scope2_Emissions_by_Fuel_View.as_view(), name='get_scope2_emissions_by_fuel'),
    path('emissions/scope2/scope2_emissions_by_ghg_type/', views.Scope2_Emissions_by_GHG_Type_View.as_view(), name='get_scope2_emissions_by_ghg_type'),
    path('emissions/scope2/scope2_intensity/', views.Scope2_Intensity_View.as_view(), name='get_scope2_intensity'),

    path('emissions/scope3/scope3_emissions_by_facilities/',views.Scope3_Emissions_by_Facilities_View.as_view(),name= 'get_scope3_emissions_by_facilities'),
    path('emissions/scope3/scope3_emissions_by_activity/',views.Scope3_Emissions_by_Activity_View.as_view(),name= 'get_scope3_emissions_by_activity'),
    path('emissions/scope3/scope3_emissions_by_ghg_type/', views.Scope3_Emissions_by_GHG_Type_View.as_view(), name='get_scope3_emissions_by_ghg_type'),
    path('emissions/scope3/scope3_intensity/', views.Scope3_Intensity_View.as_view(), name='get_scope3_intensity'),

    path('emissions/Overall/Assessment_By_External_Agency/', views.Emission_Assessment_By_External_Agency_view.as_view(), name='add_get_Assessment_By_External_Agency'),
    path('emissions/Overall/Assessment_By_External_Agency/<int:id>/', views.Emission_Assessment_By_External_Agency_view.as_view(), name='update_delete_Assessment_By_External_Agency'),

    ###################################################################     Waste      #############################################################
    
    path('waste/overall/agency_type/',views.Waste_AgencyTypeList_View.as_view(),name='agency_type_list'),
    path('waste/overall/assessment_by_external_agency/',views.Waste_Assessment_By_External_Agency_View.as_view(),name='add_agency'),
    path('waste/overall/assessment_by_external_agency/<int:id>/',views.Waste_Assessment_By_External_Agency_View.as_view(),name = 'update_delete_agency'),

    path('waste/waste_generated/filter/',views.Waste_Generated_Filter_View.as_view(),name='waste_generated_filter'),
    path('waste/waste_generated/',views.Waste_Generated_View.as_view(),name='create'),
    path('waste/waste_generated/<int:id>/',views.Waste_Generated_View.as_view(),name='update_delete'),
    path('waste/generated_type/', views.GeneratedTypeList_View.as_view(), name='waste_type_choices'),
    
    path('waste/waste_recovered/filter/',views.Waste_Recovered_Filter_View.as_view(),name='waste_recovered_filter'),
    path('waste/waste_recovered/',views.Waste_Recovered_View.as_view(),name='create'),
    path('waste/waste_recovered/<int:id>/',views.Waste_Recovered_View.as_view(),name='update_delete'),
    path('waste/recovered_category/',views.RecoveredCategoryList_View.as_view(),name='waste_recovered_category'),
    
    path('waste/waste_disposed/filter/',views.Waste_Disposed_Filter_View.as_view(),name='waste_disposed_filter'),
    path('waste/waste_disposed/',views.Waste_Disposed_View.as_view(),name='create'),
    path('waste/waste_disposed/<int:id>/',views.Waste_Disposed_View.as_view(),name='update_delete'),
    path('waste/disposed_category/',views.DisposedCategoryList_View.as_view(),name='waste_disposed_category'),
    
    path('waste/overall/waste_intensity/',views.Waste_Intensity_View.as_view(),name='list_create'),
    path('waste/overall/waste_intensity/<int:id>/',views.Waste_Intensity_View.as_view(),name='update_delete'),
    
    ################################################################  Sustainability       ################################################################
    
    path('sustainability/environmental_impact/percentage_of_R_and_D_and_capex_investments/',views.Percentage_Of_R_and_D_and_Capex_Investments_View.as_view(),name='list'),
    path('sustainability/environmental_impact/percentage_of_R_and_D_and_capex_investments/<int:id>/',views.Percentage_Of_R_and_D_and_Capex_Investments_View.as_view(),name='create_update_delete'),

    path('sustainability/environmental_impact/operations_in_ecologically_sensitive_areas/',views.Operations_In_Ecologically_Sensitive_Areas_View.as_view(),name='list'),
    path('sustainability/environmental_impact/operations_in_ecologically_sensitive_areas/<int:id>/',views.Operations_In_Ecologically_Sensitive_Areas_View.as_view(),name='create_update_delete'),

    path('sustainability/environmental_impact/environmental_impact_assessments_of_projects_undertaken/',views.Environmental_Impact_Assessments_Of_Projects_Undertaken_View.as_view(),name='list'),
    path('sustainability/environmental_impact/environmental_impact_assessments_of_projects_undertaken/<int:id>/',views.Environmental_Impact_Assessments_Of_Projects_Undertaken_View.as_view(),name='create_update_delete'),

    path('sustainability/environmental_impact/non_compliance_with_the_applicable_environmental_law/',views.Non_Compliance_With_The_Applicable_Environmental_Law_View.as_view(),name='list'),
    path('sustainability/environmental_impact/non_compliance_with_the_applicable_environmental_law/<int:id>/',views.Non_Compliance_With_The_Applicable_Environmental_Law_View.as_view(),name='create_update_delete'),
    
    path('sustainability/environmental_impact/initiatives_towards_carbon_zero/',views.Initiatives_Towards_Carbon_Zero_View.as_view(),name='list'),
    path('sustainability/environmental_impact/initiatives_towards_carbon_zero/<int:id>/',views.Initiatives_Towards_Carbon_Zero_View.as_view(),name='create_update_delete'),
    
    
    # for trial 
    path('emission_factors/',views.EmissionFactorsView.as_view(), name='emission_factors_add_get'),
    path('emission_factors/<str:id>/',views.EmissionFactorsView.as_view(), name='emission_factors_update_delete'),


]