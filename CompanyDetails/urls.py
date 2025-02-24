from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('company_profile/', views.CompanyProfile.as_view(), name='Company_Profile'),
    path('company_profile/<str:Company_Name>/', views.CompanyProfile.as_view(), name='company_logo_detail'),
    path('reporting_boundary_list/', views.ReportingBoundaryListView.as_view(), name='reporting_boundary_list'),
    path('type_of_assurance_list/', views.TypeOfAssuranceListView.as_view(), name='type_of_assurance_list'),
    path('financials/turnover/', views.Turn_over.as_view(), name='Turnover'),
    path('financials/turnover/<int:id>/', views.Turn_over.as_view(), name='update_delete_turnover'),
    path('financial_year_list/', views.FinancialYearList.as_view(), name='Financial_Year_List'),
    path('financials/networth/', views.Networth_View.as_view(), name='Networth'),
    path('financials/networth/<int:id>/', views.Networth_View.as_view(), name='update_delete_networth'),
    path('business_activity/business_activity_details/', views.BusinessActivityDetails.as_view(), name='add_business_activity_details'),
    path('business_activity/business_activity_details/<int:id>/', views.BusinessActivityDetails.as_view(), name='update_delete_business_activity'),
    path('business_activity/products_services_details/', views.ProductsServicesDetails.as_view(), name='add_products_services_details'),
    path('business_activity/products_services_details/<int:id>/', views.ProductsServicesDetails.as_view(), name='update_delete_products_services_details'),
    path('business_activity/exports/', views.Exports_View.as_view(), name='add_get_exports'),
    path('business_activity/exports/<int:id>/', views.Exports_View.as_view(), name='update_delete_exports'),
    path('business_activity/business_activity_list/', views.BusinessActivityList_View.as_view(), name='businessActivityList'),
    path('business_activity/products_services_list/', views.ProductsServicesList_View.as_view(), name='productsServicesList'),
    path('business_activity/business_activity/', views.Business_Activity_View.as_view(), name='add_get_business_activity'),  
    path('business_activity/business_activity/<int:id>/', views.Business_Activity_View.as_view(), name='update_delete_business_activity'),  
    path('business_activity/products_services/', views.Products_Services_View.as_view(), name='add_get_products_services'),  
    path('business_activity/products_services/<int:id>/', views.Products_Services_View.as_view(), name='update_delete_products_services'),
    path('operations/offices_and_plants/', views.OfficesandPlants_View.as_view(), name='add_get_offices_and_plants'),  
    path('operations/offices_and_plants/<int:id>/', views.OfficesandPlants_View.as_view(), name='update_delete_offices_and_plants'),
    path('operations/markets_served/', views.MarketsServed_View.as_view(), name='add_get_markets_served'),  
    path('operations/markets_served/<int:id>/', views.MarketsServed_View.as_view(), name='update_delete_markets_served'),
    path('operations/paid_up_capital/', views.PaidupCapital_View.as_view(), name='add_get_paidup_capital'),  
    path('operations/paid_up_capital/<int:id>/', views.PaidupCapital_View.as_view(), name='update_delete_paidup_capital'),

    path('operations/paid_up_capital_unit/', views.PaidupCapital_Unit_View.as_view(), name='get_paidup_capital_unit'),  


    path('operations/type_of_holding_list/', views.TypeofHoldingList_View.as_view(), name='typeofholdingList'),
    path('operations/holdings/', views.Holdings_View.as_view(), name='add_get_holdings'),  
    path('operations/holdings/<int:id>/', views.Holdings_View.as_view(), name='update_delete_holdings'),
    path('operations/type_of_facility_list/', views.TypeofFacilityList_View.as_view(), name='typeoffacilityList'),
    path('operations/indian_states_list/', views.IndianStatesList_View.as_view(), name='indianstatesList'),
    path('operations/facilities/', views.Facilities_View.as_view(), name='add_get_facilities'),  
    path('operations/facilities/<int:id>/', views.Facilities_View.as_view(), name='update_delete_facilities'),
    path('company_profile/countries_list/countries/', views.Countries_View.as_view(), name='CountriesList'),
    path('company_profile/states_list/states/', views.States_View.as_view(),name='add get state_cities'),
    path('company_profile/cities_list/cities/', views.Cities_View.as_view(), name='CitiesList'),
    path('shares_listed_on/', views.SharesListedOn_View.as_view(), name='shareslistedonList'),
    path('operations/facility_list/', views.FacilityList_View.as_view(), name='facilityList'),
    path('financials/number_of_days_of_accounts_payables/', views.NumberOfDaysOfAccountsPayablesView.as_view(), name='add_get_number_of_days_of_accounts_payables'),  
    path('financials/number_of_days_of_accounts_payables/<int:id>/', views.NumberOfDaysOfAccountsPayablesView.as_view(), name='update_delete_number_of_days_of_accounts_payables'),

    path('financials/concentration_of_sales/', views.ConcentrationOfSalesView.as_view(), name='add_get_concentration_of_sales'),  
    path('financials/concentration_of_sales/<int:id>/', views.ConcentrationOfSalesView.as_view(), name='update_delete_concentration_of_sales'),

    path('financials/concentration_of_purchases/', views.ConcentrationOfPurchasesView.as_view(), name='add_get_concentration_of_purchases'),  
    path('financials/concentration_of_purchases/<int:id>/', views.ConcentrationOfPurchasesView.as_view(), name='update_delete_concentration_of_purchases'),

    path('financials/share_of_rpt/', views.ShareOfRPTsView.as_view(), name='add_get_share_of_rpt'),  
    path('financials/share_of_rpt/<int:id>/', views.ShareOfRPTsView.as_view(), name='update_delete_share_of_rpt'),

    path('facility_list_for_admin/', views.FacilityListAdmin_View.as_view(), name='facilityList'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)