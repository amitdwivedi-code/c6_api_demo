from django.urls import path
from . import views

urlpatterns = [
    # --------- Workforce url --------- #
    path("attachments/", views.AttachmentView.as_view(), name="attachment-list-create"),
    path("attachments/<int:id>/", views.AttachmentView.as_view(), name="attachment-delete"),
    path('workforce/employees/genderlist/', views.GenderList_View.as_view(), name='Gender_List'),
    path('workforce/employees/typelist/', views.TypeList_View.as_view(), name='Gender_List'),

    path('workforce/employees/total_employees/', views.TotalEmployees_View.as_view(), name='employee-summary'),
    path('workforce/employees/total_employees/filter/', views.TotalEmployees_Filter_View.as_view(), name='employee-summary'),

    path('workforce/employees/employees/', views.Employees_View.as_view(), name='add_get_employees'),
    path('workforce/employees/employees/<int:id>/', views.Employees_View.as_view(), name='update_delete_employees'),
    path('workforce/employees/employees/filter/', views.Employees_Filter_View.as_view(), name='filter_by_employees'),

    path('workforce/employees/differently_abled_employees/', views.Differently_Abled_Employees_View.as_view(), name='add_get_Differently_Abled_Employees'),
    path('workforce/employees/differently_abled_employees/<int:id>/', views.Differently_Abled_Employees_View.as_view(), name='update_delete_Differently_Abled_Employees'),
    path('workforce/employees/differently_abled_employees/filter/', views.Differently_Abled_Employees_Filter_View.as_view(), name='filter_by_differently_abled_employees'),
    
    path('workforce/employees/employees_membership_in_association/', views.Employees_Membership_In_Association_View.as_view(), name='add_get_employees_membership_in_Association'),
    path('workforce/employees/employees_membership_in_association/<int:id>/', views.Employees_Membership_In_Association_View.as_view(), name='update_delete_employees_membership_in_Association'),
    path('workforce/employees/employees_membership_in_association/filter/', views.Employees_Membership_In_Association_Filter_View.as_view(), name='filter_by_employees_membership_in_association'),
    
    path('workforce/workers/total_workers/', views.TotalWorkers_View.as_view(), name='workers-summary'),
    path('workforce/workers/total_workers/filter/', views.TotalWorkers_Filter_View.as_view(), name='workers-summary_filter'),

    path('workforce/workers/workers/', views.Workers_View.as_view(), name='add_get_workers'),
    path('workforce/workers/workers/<int:id>/', views.Workers_View.as_view(), name='update_delete_Differently_Abled_Employees'),
    path('workforce/workers/workers/filter/', views.Workers_Filter_View.as_view(), name='filter_by_workers'),

    path('workforce/workers/differently_abled_workers/', views.DifferentlyAbledWorkersView.as_view(), name='add_get_differently_abled_workers'),
    path('workforce/workers/differently_abled_workers/<int:id>/', views.DifferentlyAbledWorkersView.as_view(), name='update_delete_differently_abled_workers'),
    path('workforce/workers/differently_abled_workers/filter/', views.Differently_Abled_Workers_Filter_View.as_view(), name='differently_abled_workers_filter'),

    path('workforce/workers/workers_membership_in_association/', views.Workers_Membership_In_Association_View.as_view(), name='add_get_workers_membership_in_Association'),
    path('workforce/workers/workers_membership_in_association/<int:id>/', views.Workers_Membership_In_Association_View.as_view(), name='update_delete_workers_membership_in_Association'),
    path('workforce/workers/workers_membership_in_association/filter', views.Workers_Membership_In_Association_Filter_View.as_view(), name='filter_by_workers_membership_in_association'),    

    path('workforce/management/board_of_director/', views.BoardOfDirectorsView.as_view(), name='add_get_board_of_director'),
    path('workforce/management/board_of_director/<int:id>/', views.BoardOfDirectorsView.as_view(), name='update_delete_board_of_director'),
    path('workforce/management/Key_Management_Personnel/', views.KeyManagementPersonnelView.as_view(), name='add_get_Key_Management_Personnel'),
    path('workforce/management/Key_Management_Personnel/<int:id>/', views.KeyManagementPersonnelView.as_view(), name='update_delete_Key_Management_Personnel'),

    path('workforce/wages/segmentlist/', views.Wages_View.as_view(), name='segment_List'),
    path('workforce/wages/wages_paid/', views.WagesPaidView.as_view(), name='add_get_wages_paid'),
    path('workforce/wages/wages_paid/<int:id>/', views.WagesPaidView.as_view(), name='update_delete_wages_paid'),
    path('workforce/wages/median_remuneration_salary_wages/', views.Median_Remuneration_Salary_WagesView.as_view(), name='add_get_median_remuneration_salary_wages'),
    path('workforce/wages/median_remuneration_salary_wages/<int:id>/', views.Median_Remuneration_Salary_WagesView.as_view(), name='update_delete_median_remuneration_salary_wages'),


    path('workforce/employees/employee_turnover_rate/', views.EmployeeTurnoverRateView.as_view(), name='add_get_employee_turnover_rate'),
    path('workforce/employees/employee_turnover_rate/<int:id>/', views.EmployeeTurnoverRateView.as_view(), name='update_delete_employee_turnover_rate'),

    path('workforce/workers/workers_turnover_rate/', views.WorkersTurnoverRateView.as_view(), name='add_get_workers_turnover_rate'),
    path('workforce/workers/workers_turnover_rate/<int:id>/', views.WorkersTurnoverRateView.as_view(), name='update_delete_workers_turnover_rate'),
       

    path('workforce/wages/gross_wages_paid/', views.Gross_Wages_Paid_View.as_view(), name='add_get_gross_wages_paid'),
    path('workforce/wages/gross_wages_paid/<int:id>/', views.Gross_Wages_Paid_View.as_view(), name='update_delete_gross_wages_paid'),

    path('workforce/wages/job_creation_in_smaller_town/', views.Job_Creation_In_Smaller_Town_View.as_view(), name='add_get_job_creation_in_smaller_town'),
    path('workforce/wages/job_creation_in_smaller_town/<int:id>/', views.Job_Creation_In_Smaller_Town_View.as_view(), name='update_delete_job_creation_in_smaller_town'),




    # --------- training url --------- #

    path('training/ingeneral/segmentlist/', views.Segment_View.as_view(), name='segment_List'),
    path('training/ingeneral/', views.Ingeneral_View.as_view(), name='get_add_agency_type_list'),
    path('training/ingeneral/<int:id>/', views.Ingeneral_View.as_view(), name='update_delete_agency_type_list'),
    path('training/ingeneral/filter/', views.Ingeneral_Filter_View.as_view(), name='filter_by_facility_ingeneral'),

    path('training/career_development/on_skill_upgradation/', views.On_Skill_Upgradation_View.as_view(), name='get_add_on_skill_upgradation'),
    path('training/career_development/on_skill_upgradation/<int:id>/', views.On_Skill_Upgradation_View.as_view(), name='update_delete_on_skill_upgradation'),
    path('training/career_development/on_skill_upgradation/filter/', views.On_Skill_Upgradation_Filter_View.as_view(), name='filter_by_facility_on_skill_upgradation'),

    path('training/career_development/performance_and_career_reviews/', views.Performance_And_Career_Reviews_View.as_view(), name='get_add_on_skill_upgradation'),
    path('training/career_development/performance_and_career_reviews/<int:id>/', views.Performance_And_Career_Reviews_View.as_view(), name='update_delete_on_skill_upgradation'),
    path('training/career_development/performance_and_career_reviews/filter/', views.Performance_And_Career_Reviews_Filter_View.as_view(), name='filter_by_facility_on_skill_upgradation'),

    path('training/awareness_programmes/awareness_programmes_on_esg/', views.Awareness_Programmes_On_ESG_View.as_view(), name='get_add_on_skill_upgradation'),
    path('training/awareness_programmes/awareness_programmes_on_esg/<int:id>/', views.Awareness_Programmes_On_ESG_View.as_view(), name='update_delete_on_skill_upgradation'),
    path('training/awareness_programmes/awareness_programmes_on_esg/filter/', views.Awareness_Programmes_On_ESG_Filter_View.as_view(), name='filter_by_facility_on_skill_upgradation'),

    path('training/health_and_safety/on_health_and_safety_measures/', views.On_Health_And_Safety_Measures_View.as_view(), name='get_add_on_skill_upgradation'),
    path('training/health_and_safety/on_health_and_safety_measures/<int:id>/', views.On_Health_And_Safety_Measures_View.as_view(), name='update_delete_on_skill_upgradation'),
    path('training/health_and_safety/on_health_and_safety_measures/filter/', views.On_Health_And_Safety_Measures_Filter_View.as_view(), name='filter_by_facility_on_skill_upgradation'),

    path('training/health_and_safety/on_human_rights_issues_and_policies/', views.On_Human_Rights_Issues_And_Policies_View.as_view(), name='get_add_on_skill_upgradation'),
    path('training/health_and_safety/on_human_rights_issues_and_policies/<int:id>/', views.On_Human_Rights_Issues_And_Policies_View.as_view(), name='update_delete_on_skill_upgradation'),
    path('training/health_and_safety/on_human_rights_issues_and_policies/filter/', views.On_Human_Rights_Issues_And_Policies_Filter.as_view(), name='filter_by_facility_on_skill_upgradation'),



    # -------------- urls for health and sefty ------------ #

    path('health_and_safety/segmentlist/', views.Segment_View.as_view(), name='segment_List'),
    path('health_and_safety/typelist/', views.TypeList_View.as_view(), name='type_List'),
    path('health_and_safety/deposited_deducted/', views.Deposited_Deducted_View.as_view(), name='deposited_deducted_List'),
    
    path('health_and_safety/well_being_measures/percentage_covered_in_wellbeing_measures/', views.Percentage_Covered_In_Wellbeing_Measures_View.as_view(), name='get_add_percentage_covered_in_wellbeing_measures'),
    path('health_and_safety/well_being_measures/percentage_covered_in_wellbeing_measures/<int:id>/', views.Percentage_Covered_In_Wellbeing_Measures_View.as_view(), name='update_delete_percentage_covered_in_wellbeing_measures'),
    path('health_and_safety/well_being_measures/percentage_covered_in_wellbeing_measures/filter/', views.Percentage_Covered_In_Wellbeing_Measures_Filter_View.as_view(), name='filter_by_facility_percentage_covered_in_wellbeing_measures'),

    path('health_and_safety/well_being_measures/retirement_benefits/', views.Retirement_Benefits_View.as_view(), name='get_add_retirement_benefits'),
    path('health_and_safety/well_being_measures/retirement_benefits/<int:id>/', views.Retirement_Benefits_View.as_view(), name='update_delete_retirement_benefits'),
    path('health_and_safety/well_being_measures/retirement_benefits/filter/', views.Retirement_Benefits_Filter_View.as_view(), name='filter_by_facility_retirement_benefits'),

    path('health_and_safety/well_being_measures/paternal_leave_for_permanent_employee_and_worker/', views.Post_Paternal_Leave_For_Permanent_Employee_And_Worker_view.as_view(), name='get_add_paternal_leave_for_permanent_employee_and_worker'),
    path('health_and_safety/well_being_measures/paternal_leave_for_permanent_employee_and_worker/<int:id>/', views.Post_Paternal_Leave_For_Permanent_Employee_And_Worker_view.as_view(), name='update_delete_paternal_leave_for_permanent_employee_and_worker'),
    path('health_and_safety/well_being_measures/paternal_leave_for_permanent_employee_and_worker/filter/', views.Post_Paternal_Leave_For_Permanent_Employee_And_Worker_Filter_View.as_view(), name='filter_by_facility_paternal_leave_for_permanent_employee_and_worker'),

    path('health_and_safety/workplace_safety/lost_time_injury_frequency_rate/', views.Lost_Time_Injury_Frequency_Rate_View.as_view(), name='get_add_lost_time_injury_frequency_rate'),
    path('health_and_safety/workplace_safety/lost_time_injury_frequency_rate/<int:id>/', views.Lost_Time_Injury_Frequency_Rate_View.as_view(), name='update_delete_lost_time_injury_frequency_rate'),
    path('health_and_safety/workplace_safety/lost_time_injury_frequency_rate/filter/', views.Lost_Time_Injury_Frequency_Rate_Filter_View.as_view(), name='filter_by_facility_lost_time_injury_frequency_rate'),


    path('health_and_safety/workplace_safety/total_work_related_injuries/', views.Total_Work_Related_Injuries_View.as_view(), name='get_add_Total_Work_Related_Injuries'),
    path('health_and_safety/workplace_safety/total_work_related_injuries/<int:id>/', views.Total_Work_Related_Injuries_View.as_view(), name='update_delete_Total_Work_Related_Injuries'),
    path('health_and_safety/workplace_safety/total_work_related_injuries/filter/', views.Total_Work_Related_Injuries_Filter_View.as_view(), name='filter_by_facility_Total_Work_Related_Injuries'),


    path('health_and_safety/workplace_safety/no_of_fatalities/', views.No_Of_Fatalities_View.as_view(), name='get_add_No_Of_Fatalities'),
    path('health_and_safety/workplace_safety/no_of_fatalities/<int:id>/', views.No_Of_Fatalities_View.as_view(), name='update_delete_No_Of_Fatalities'),
    path('health_and_safety/workplace_safety/no_of_fatalities/filter/', views.No_Of_Fatalities_Filter_View.as_view(), name='filter_by_facility_No_Of_Fatalities'),

    path('health_and_safety/workplace_safety/injury_or_ill_health/', views.Injury_Or_Ill_Health_View.as_view(), name='get_add_injury_or_ill_health'),
    path('health_and_safety/workplace_safety/injury_or_ill_health/<int:id>/', views.Injury_Or_Ill_Health_View.as_view(), name='update_delete_injury_or_ill_health'),
    path('health_and_safety/workplace_safety/injury_or_ill_health/filter/', views.Injury_Or_Ill_Health_Filter_View.as_view(), name='filter_by_facility_injury_or_ill_health'),


    path('health_and_safety/workplace_safety/suffered_high_consequence_work_related_injury/', views.Suffered_High_Consequence_Work_Related_Injury_View.as_view(), name='get_add_Suffered_High_Consequence_Work_Related_Injury'),
    path('health_and_safety/workplace_safety/suffered_high_consequence_work_related_injury/<int:id>/', views.Suffered_High_Consequence_Work_Related_Injury_View.as_view(), name='update_delete_Suffered_High_Consequence_Work_Related_Injury'),
    path('health_and_safety/workplace_safety/suffered_high_consequence_work_related_injury/filter/', views.Suffered_High_Consequence_Work_Related_Injury_Filter_View.as_view(), name='filter_by_facility_Suffered_High_Consequence_Work_Related_Injury'),

    path('health_and_safety/workplace_safety/assessment_of_plants_and_offices/', views.Assessment_Of_Plants_And_Offices_Health_And_Safety_View.as_view(), name='get_add_assessment_of_plants_and_offices'),
    path('health_and_safety/workplace_safety/assessment_of_plants_and_offices/<int:id>/', views.Assessment_Of_Plants_And_Offices_Health_And_Safety_View.as_view(), name='update_delete_assessment_of_plants_and_offices'),
    
    path('health_and_safety/workplace_safety/assessment_of_value_chain_partners/', views.Assessment_Of_Value_Chain_Partners_Health_And_Safety_View.as_view(), name='get_add_assessment_of_value_chain_partners'),
    path('health_and_safety/workplace_safety/assessment_of_value_chain_partners/<int:id>/', views.Assessment_Of_Value_Chain_Partners_Health_And_Safety_View.as_view(), name='update_delete_assessment_of_value_chain_partners'),
    

    path('health_and_safety/posh/receive_and_redress_grievance_mechanism/', views.Receive_And_Redress_Grievance_Mechanism_View.as_view(), name='get_add_receive_and_redress_grievance_mechanism'),
    path('health_and_safety/posh/receive_and_redress_grievance_mechanism/<int:id>/', views.Receive_And_Redress_Grievance_Mechanism_View.as_view(), name='update_delete_receive_and_redress_grievance_mechanism'),

    path('health_and_safety/well_being_measures/cost_incurred_on_wellbeing_measures/', views.CostIncurredOnWellbeingMeasuresView.as_view(), name='cost_incurred_on_wellbeing_measures'),
    path('health_and_safety/well_being_measures/cost_incurred_on_wellbeing_measures/<int:id>/', views.CostIncurredOnWellbeingMeasuresView.as_view(), name='cost_incurred_on_wellbeing_measures_with_id'),


    #--------- gravience urls ----------#
    path('grievances/grievances/complaintHS_type/',views.ComplaintHSTypeList_View.as_view(),name='complaint_HS_type_list'),
    path('grievances/grievances/health_and_safety_related_complaints/',views. Health_and_safety_related_complaints_View.as_view(),name = 'create'),
    path('grievances/grievances/health_and_safety_related_complaints/<int:id>/',views. Health_and_safety_related_complaints_View.as_view(),name = 'create'),
  
    path('grievances/grievances/complaintHR_type/',views.ComplaintHRTypeList_View.as_view(),name='ComplaintHRTypeList'),
    path('grievances/grievances/human_rights_related_complaints/',views.Human_Rights_related_complaints_View.as_view(),name = 'create'),
    path('grievances/grievances/human_rights_related_complaints/<int:id>/',views.Human_Rights_related_complaints_View.as_view(),name = 'create'),
    
    path('grievances/grievances/segmentconflictList/',views.SegmentConflictsList_View.as_view(),name='SegmentConflictsList'),
    path('grievances/grievances/conflict_of_interest_complaints/',views.Conflict_of_interest_complaints_View.as_view(),name = 'create'),
    path('grievances/grievances/conflict_of_interest_complaints/<int:id>/',views.Conflict_of_interest_complaints_View.as_view(),name = 'create'),
    

    path('grievances/grievances/SegmentReceiveRedressList/',views.SegmentReceiveRedressList_View.as_view(),name='SegmentReceiveRedressList'),
    path('grievances/grievances/TypeList/',views.TypeList_View.as_view(),name='TypeList'),
    path('grievances/grievances/receive_and_redress_grievances_mechanism/',views.Receive_and_redress_grievances_mechanism_View.as_view(),name = 'create'),
    path('grievances/grievances/receive_and_redress_grievances_mechanism/<int:id>/',views.Receive_and_redress_grievances_mechanism_View.as_view(),name = 'create'),



    #------- urls for policy and penelty ----------#

    path('policies_and_penalties/policies_human_safety/',views.Policy_Details_Health_Safety_View.as_view(),name='get_policies_human_safety'),
    path('policies_and_penalties/policies_human_safety/<str:model_name>/',views.Policy_Details_Health_Safety_View.as_view(),name='create_update_policies_human_safety'),


    path('policies_and_penalties/policies_human_rights/',views.Policy_Details_Human_Rights_View.as_view(),name='get_policies_human_rights'),
    path('policies_and_penalties/policies_human_rights/<str:model_name>/',views.Policy_Details_Human_Rights_View.as_view(),name='create_update_policies_human_rights'),


    path('policies_and_penalties/policies_penalty/',views.Policy_Details_Penalty_View.as_view(),name='policies_penalty'),
    path('policies_and_penalties/policies_penalty/<str:model_name>/',views.Policy_Details_Penalty_View.as_view(),name='create_update_policies_penalty'),

    path('policies_and_penalties/assessment_of_plants_and_offices/',views.Assessment_of_plants_and_offices_Policies_and_Penalties_View.as_view(),name='get_list'),
    path('policies_and_penalties/assessment_of_plants_and_offices/<int:id>/',views.Assessment_of_plants_and_offices_Policies_and_Penalties_View.as_view(),name='add_update_delete'),
    
    path('policies_and_penalties/assessment_of_value_chain_partners/',views.Assessment_of_value_chain_partners_Policies_and_Penalties_View.as_view(),name='get_list'),
    path('policies_and_penalties/assessment_of_value_chain_partners/<int:id>/',views.Assessment_of_value_chain_partners_Policies_and_Penalties_View.as_view(),name='add_update_delete'),
    
    path('policies_and_penalties/OptionsList/',views.OptionsList_View.as_view(),name = 'list'),   
    path('policies_and_penalties/monetarytypelist/',views.MonetaryTypeList_View.as_view(),name = 'type_list'),
    path('policies_and_penalties/penalty_Monetary/',views.Penalty_Monetary_View.as_view(),name='get_list'),
    path('policies_and_penalties/penalty_Monetary/<int:id>/',views.Penalty_Monetary_View.as_view(),name='add_update_delete'),
    
    path('policies_and_penalties/nonmonetarytypelist/',views.Non_MonetaryTypeList_View.as_view(),name = 'type_list'),
    path('policies_and_penalties/penalty_non_monetary/',views.Penalty_Non_Monetary_View.as_view(),name='get_list'),
    path('policies_and_penalties/penalty_non_monetary/<int:id>/',views.Penalty_Non_Monetary_View.as_view(),name='add_update_delete'),
   


    path('policies_and_penalties/details_of_appeal/',views.Details_of_the_appeal_View.as_view(),name='get_list'),
    path('policies_and_penalties/details_of_appeal/<int:id>/',views.Details_of_the_appeal_View.as_view(),name='add_update_delete'),
    
    path('policies_and_penalties/disciplinary_Action_Against_For_curruption/',views.Disciplinary_Action_Against_For_curruption_View.as_view(),name='get_list'),
    path('policies_and_penalties/disciplinary_Action_Against_For_curruption/<int:id>/',views.Disciplinary_Action_Against_For_curruption_View.as_view(),name='add_update_delete'),
       

]