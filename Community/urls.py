from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [

    path('stakeholder_group/', views.StakeHolderGroupView.as_view(), name='stakeholder-group'),
    path('frequency_of_engagement/',views.FrequencyOfEngagementView.as_view(), name='frequency-of-engagement'),
    ################################## StackHolder ###########################################################################################
    path('list_stakeholder_groups/', views.List_Stakeholder_Groups_View.as_view(), name='add_get_list_stakeholder_groups'),
    
    path('list_stakeholder_groups/<int:id>/', views.List_Stakeholder_Groups_View.as_view(), name='update_delete_list_stakeholder_groups'),

    path('number_of_affiliations/', views.Number_Of_Affiliations_View.as_view(), name='add_get_Number_Of_Affiliations'),
    path('number_of_affiliations/<int:id>/', views.Number_Of_Affiliations_View.as_view(), name='update_delete_Number_Of_Affiliations'),

    path('Top_10_Trade_And_Industry_Chambers/', views.Top_10_Trade_And_Industry_Chambers_View.as_view(), name='add_get_Top_10_Trade_And_Industry_Chambers'),
    path('Top_10_Trade_And_Industry_Chambers/<int:id>/', views.Top_10_Trade_And_Industry_Chambers_View.as_view(), name='update_delete_Top_10_Trade_And_Industry_Chambers'),

    path('Details_Anti_Competitive_Conduct_By_The_Entity/', views.Details_Anti_Competitive_Conduct_By_The_Entity_View.as_view(), name='add_get_Top_10_Trade_And_Industry_Chambers'),
    path('Details_Anti_Competitive_Conduct_By_The_Entity/<int:id>/', views.Details_Anti_Competitive_Conduct_By_The_Entity_View.as_view(), name='update_delete_Top_10_Trade_And_Industry_Chambers'),


    path('details_of_public_policy_positions_advocated_by_the_entity/', views.Details_Of_Public_Policy_Positions_Advocated_By_The_Entity_View.as_view(), name='add_get_Top_10_Trade_And_Industry_Chambers'),
    path('details_of_public_policy_positions_advocated_by_the_entity/<int:id>/', views.Details_Of_Public_Policy_Positions_Advocated_By_The_Entity_View.as_view(), name='update_delete_Top_10_Trade_And_Industry_Chambers'),

    path('awareness_programmes_for_value_chain_partners/', views.Awareness_Programmes_For_Value_Chain_Partners_View.as_view(), name='add_get_Awareness_Programmes_For_Value_Chain_Partners_View'),
    path('awareness_programmes_for_value_chain_partners/<int:id>/', views.Awareness_Programmes_For_Value_Chain_Partners_View.as_view(), name='update_delete_Awareness_Programmes_For_Value_Chain_Partners_View'),
    path('awareness_programmes_for_value_chain_partners/filter/', views.Awareness_Programmes_For_Value_Chain_Partners_Filter_View.as_view(), name='update_delete_Awareness_Programmes_For_Value_Chain_Partners_View'),

    path('stakeholder_Details/',views.Stakeholders_DetailsAPIView.as_view(),name='get_stakeholder_Details'),
    path('stakeholder_Details/<str:ids>/',views.Stakeholders_DetailsAPIView.as_view(),name='create_update_stakeholder_Details'),

    ################################################# Coporate Social Responcibility #################################################################
    path('information_on_CSR_Projects/', views.Information_on_CSR_Projects_View.as_view(), name='add_get_information_on_CSR_Projects'),
    path('information_on_CSR_Projects/<int:id>/', views.Information_on_CSR_Projects_View.as_view(), name='update_delete_information_on_CSR_Projects'),

    path('benefits_Derived_And_Shared_From_Intellectual_Property/', views.Benefits_Derived_And_Shared_From_Intellectual_Property_View.as_view(), name='add_get_benefits_Derived_And_Shared_From_Intellectual_Property'),
    path('benefits_Derived_And_Shared_From_Intellectual_Property/<int:id>/', views.Benefits_Derived_And_Shared_From_Intellectual_Property_View.as_view(), name='update_delete_benefits_Derived_And_Shared_From_Intellectual_Property'),

    path('details_Of_Intellectual_Property_Related_Disputes/', views.Details_Of_Intellectual_Property_Related_Disputes_View.as_view(), name='add_get_details_Of_Intellectual_Property_Related_Disputes'),
    path('details_Of_Intellectual_Property_Related_Disputes/<int:id>/', views.Details_Of_Intellectual_Property_Related_Disputes_View.as_view(), name='update_delete_details_Of_Intellectual_Property_Related_Disputes'),
 
    path('details_Of_Beneficiaries_Of_CSR_Projects/', views.Details_Of_Beneficiaries_Of_CSR_Projects_View.as_view(), name='add_get_details_Of_Beneficiaries_Of_CSR_Projects'),
    path('details_Of_Beneficiaries_Of_CSR_Projects/<int:id>/', views.Details_Of_Beneficiaries_Of_CSR_Projects_View.as_view(), name='update_delete_details_Of_Beneficiaries_Of_CSR_Projects'),


    ######################################################### Consumer #######################################################################
    path('turnover_Of_Products_As_A_Percentage_Of_Turnover/', views.Turnover_Of_Products_As_A_Percentage_Of_Turnover_View.as_view(), name='add_get_turnover_Of_Products_As_A_Percentage_Of_Turnover'),
    path('turnover_Of_Products_As_A_Percentage_Of_Turnover/<int:id>/', views.Turnover_Of_Products_As_A_Percentage_Of_Turnover_View.as_view(), name='update_delete_turnover_Of_Products_As_A_Percentage_Of_Turnover'),
    
    path('type_Consumer_Complaints_List/',views.Type_Consumer_Complaints_List_View.as_view(),name='list'),
    path('number_of_Consumer_Complaints/', views.Number_of_Consumer_Complaints_View.as_view(), name='add_get_number_of_Consumer_Complaints'),
    path('number_of_Consumer_Complaints/<int:id>/', views.Number_of_Consumer_Complaints_View.as_view(), name='update_delete_number_of_Consumer_Complaints'),

    path('recall_List/',views.Recall_List_View.as_view(),name='list'),
    path('details_Of_Instances_Of_Product_Recalls/', views.Details_Of_Instances_Of_Product_Recalls_View.as_view(), name='add_get_details_Of_Instances_Of_Product_Recalls'),
    path('details_Of_Instances_Of_Product_Recalls/<int:id>/', views.Details_Of_Instances_Of_Product_Recalls_View.as_view(), name='update_delete_details_Of_Instances_Of_Product_Recalls'),

    path('corporate_Social_Responsibility_Details/',views.Corporate_Social_Responsibility_Details_View.as_view(),name='get_corporate_Social_Responsibility_Details'),
    path('corporate_Social_Responsibility_Details/<str:ids>/',views.Corporate_Social_Responsibility_Details_View.as_view(),name='create_update_corporate_Social_Responsibility_Details'),

    path('consumer_Details/',views.Consumer_Details_View.as_view(),name='get_corporate_Social_Responsibility_Details'),
    path('consumer_Details/<str:ids>/',views.Consumer_Details_View.as_view(),name='create_update_corporate_Social_Responsibility_Details'),

   
    ############################################################ Society ######################################################################
    path('details_of_social_impact_assessments/',views.Details_Of_Social_Impact_Assessments_View.as_view(),name='list'),
    path('details_of_social_impact_assessments/<int:id>/',views.Details_Of_Social_Impact_Assessments_View.as_view(),name='list'),

    path('ongoing_rehabilitation_and_resettlement/',views.Ongoing_Rehabilitation_And_Resettlement_View.as_view(),name='list'),
    path('ongoing_rehabilitation_and_resettlement/<int:id>/',views.Ongoing_Rehabilitation_And_Resettlement_View.as_view(),name='list'),

    path('percentage_of_input_material/',views.Percentage_Of_Input_Material_View.as_view(),name='list'),
    path('percentage_of_input_material/<int:id>/',views.Percentage_Of_Input_Material_View.as_view(),name='list'),

    path('details_of_actions_taken_to_mitigate/',views.Details_Of_Actions_Taken_To_Mitigate_View.as_view(),name='list'),
    path('details_of_actions_taken_to_mitigate/<int:id>/',views.Details_Of_Actions_Taken_To_Mitigate_View.as_view(),name='list'),

    path('society_Details/',views.Society_Details_View.as_view(),name='get_Society_Details'),
    path('society_Details/<str:ids>/',views.Society_Details_View.as_view(),name='create_update_Society_Details'),


    path('transparency_and_disclosure_compliances/', views.TransparencyAndDisclosureCompliancesView.as_view(), name='add_get_transparency_and_disclosure_compliances'),
    path('transparency_and_disclosure_compliances/<int:id>/', views.TransparencyAndDisclosureCompliancesView.as_view(), name='update_delete_transparency_and_disclosure_compliances'),

    path('number_of_instance_of_data_breache/', views.Number_Of_Instance_Of_Data_BreacheView.as_view(), name='add_get_number_of_instance_of_data_breache'),  
    path('number_of_instance_of_data_breache/<int:id>/', views.Number_Of_Instance_Of_Data_BreacheView.as_view(), name='update_delete_number_of_instance_of_data_breache'),
]

