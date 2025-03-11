from django.shortcuts import render
from django.shortcuts import render
from django.forms.models import model_to_dict
import json
from decimal import InvalidOperation
from bson.decimal128 import Decimal128
from datetime import datetime
from decimal import Decimal, InvalidOperation
from bson import Decimal128
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import APIException
from django.db.models import Max, Sum

from bson.decimal128 import Decimal128
from Activity_Log.serializers import BRS_Report_LogSerializer
import logging
import traceback


from BRS.models import *
from CompanyDetails.serializers import HoldingsSerializer
from Environment.models import *
from Community.models import *
from CompanyDetails.models import *
from Descriptions.models import *
from user.models import *
from Workplace.models import *


logger = logging.getLogger(__name__)

from .utils import *

# Create your views here.


class BRS_Report_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:

            financial_year = request.query_params.get("financial_year", None)

            if financial_year is None:
                return Response(
                    {"error": "financial_year parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract the start year from the financial year string (assumes format is 'FYYYYY-YYYY')
            start_year = int(financial_year[2:6])
            previous_financial_year = f"FY{start_year-1}-{start_year}"

            response_data = {}

            company_profile_object = Company_Profile.objects.first()

            response_data["Section_A_1"] = company_profile_object.CIN
            response_data["Section_A_2"] = company_profile_object.Company_Name
            response_data["Section_A_3"] = company_profile_object.Year_of_Incorporation
            response_data["Section_A_4"] = (
                company_profile_object.Registered_Office_Address_Line1
                + ", "
                + company_profile_object.Registered_Office_Address_Line2
            )
            response_data["Section_A_5"] = (
                company_profile_object.Corporate_Office_Address_Line1
                + ", "
                + company_profile_object.Corporate_Office_Address_Line2
            )
            response_data["Section_A_6"] = company_profile_object.Email
            response_data["Section_A_7"] = (
                company_profile_object.Phone_Ext
                + "-"
                + str(company_profile_object.Phone_Number)
            )
            response_data["Section_A_8"] = company_profile_object.Website
            response_data["Section_A_9"] = financial_year
            response_data["Section_A_10"] = company_profile_object.Shares_Listed_On

            obj = Paid_up_Capital.objects.filter(Financial_Year=financial_year).first()
            if obj:
                response_data["Section_A_11"] = float(obj.Paid_up_Capital.to_decimal())
            else:
                response_data["Section_A_11"] = 0

            business_activity_details_obj = Business_Activity_Details.objects.all()
            if business_activity_details_obj:
                business_activity_details_list = list(
                    business_activity_details_obj.values()
                )

                for elem in business_activity_details_list:
                    business_activity_obj = Business_Activity.objects.filter(
                        Financial_Year=financial_year
                    ).first()

                    if business_activity_obj:
                        activities = (
                            business_activity_obj.Business_Activity_and_Turnover
                        )
                        found = False  # To track if a matching activity is found

                        for activity in activities:
                            if activity.get("Business_Activity") == elem.get(
                                "Name_of_Business_Activity"
                            ):
                                elem["Percent_Turnover"] = activity.get(
                                    "Percent_Turnover", 0
                                )
                                found = True
                                break  # Exit the loop as we found the matching activity
                        if not found:
                            elem["Percent_Turnover"] = 0
                    else:
                        elem["Percent_Turnover"] = 0
            else:
                business_activity_details_list = []
            response_data["Section_A_16"] = business_activity_details_list

            products_services_details_obj = Products_Services_Details.objects.all()
            if products_services_details_obj:
                products_services_details_list = list(
                    products_services_details_obj.values()
                )

                for elem in products_services_details_list:
                    product_service_obj = Products_Services.objects.filter(
                        Financial_Year=financial_year
                    ).first()

                    if product_service_obj:
                        activities = product_service_obj.Products_Services_and_Turnover
                        found = False  # To track if a matching activity is found

                        for activity in activities:
                            if activity.get("Product_Service") == elem.get(
                                "Name_of_Product_Service"
                            ):
                                elem["Percent_Turnover"] = activity.get(
                                    "Percent_Turnover", 0
                                )
                                found = True
                                break  # Exit the loop as we found the matching activity
                        if not found:
                            elem["Percent_Turnover"] = 0
                    else:
                        elem["Percent_Turnover"] = 0
            else:
                products_services_details_list = []
            response_data["Section_A_17"] = products_services_details_list

            offices_and_plants_obj = Offices_and_Plants.objects.all()
            response_data["Section_A_18"] = list(offices_and_plants_obj.values())

            markets_served_obj = Markets_Served.objects.all()
            response_data["Section_A_19_a"] = list(markets_served_obj.values())

            exports_obj = Exports.objects.filter(Financial_Year=financial_year).first()
            if exports_obj:
                response_data["Section_A_19_b"] = float(
                    exports_obj.Contribution_of_Turnover.to_decimal()
                )
            else:
                response_data["Section_A_19_b"] = 0

            description_obj = Descriptions.objects.filter(
                Heading="type_of_customer"
            ).first()
            if description_obj:
                response_data["Section_A_19_c"] = description_obj.Description
            else:
                response_data["Section_A_19_c"] = ""

            employee_summary_json = calculate_section_A_20_a_employees_data(
                financial_year
            )
            response_data["Section_A_20_a_Employees"] = [employee_summary_json]

            worker_summary_json = calculate_section_A_20_a_workers_data(financial_year)
            response_data["Section_A_20_a_Workers"] = [worker_summary_json]

            diff_abled_emp_json = (
                calculate_section_A_20_b_differently_abled_employees_data(
                    financial_year
                )
            )
            response_data["Section_A_20_b_Diff_Abled_Employees"] = [diff_abled_emp_json]

            diff_abled_workers_json = (
                calculate_section_A_20_b_differently_abled_workers_data(financial_year)
            )
            response_data["Section_A_20_b_Diff_Abled_Workers"] = [
                diff_abled_workers_json
            ]

            management_json = calculate_section_A_21_Management(financial_year)
            response_data["Section_A_21_Management"] = [management_json]

            holdings_obj = Holdings.objects.all()
            serializer = HoldingsSerializer(holdings_obj, many=True)
            response_data["Section_A_23"] = serializer.data

            response_data["Section_A_24_1"] = company_profile_object.CSR_Applicable

            turnover_obj = Turnover.objects.filter(
                Financial_Year=financial_year
            ).first()
            if turnover_obj:
                response_data["Section_A_24_2"] = float(
                    turnover_obj.Total_Turnover.to_decimal()
                )
            else:
                response_data["Section_A_24_2"] = 0.00

            networth_obj = Networth.objects.filter(
                Financial_Year=financial_year
            ).first()
            if networth_obj:
                response_data["Section_A_24_3"] = float(
                    networth_obj.Total_Networth.to_decimal()
                )
            else:
                response_data["Section_A_24_3"] = 0.00

            # material_obj = Material_Business_Conduct_Issue.objects.filter(Financial_Year=financial_year).first()
            # if material_obj:
            #     # Convert the model instance to a dictionary
            #     response_data["Section_A_26"] = [model_to_dict(material_obj)]
            # else:
            #     response_data["Section_A_26"] = []

            brs_policy_1_obj = BRS_Policy_1.objects.all()
            response_data["Section_B_1"] = list(brs_policy_1_obj.values())

            brs_policy_2_obj = BRS_Policy_2.objects.all()
            response_data["Section_B_2"] = list(brs_policy_2_obj.values())

            details_of_appeal = calculate_section_C_EI_3(financial_year)
            response_data["Section_C_Principle_1_E1_3"] = [details_of_appeal]

            description_obj = Policy_Details_Penalty.objects.filter(
                Model_Name_Penalty="AntiCorruption"
            ).first()
            if description_obj:
                response_data["Section_C_Principle_1_E1_4"] = (
                    description_obj.Descriptions_Penalty
                )
            else:
                response_data["Section_C_Principle_1_E1_4"] = ""

            disciplinary_action = calculate_section_C_EI_5(
                financial_year, previous_financial_year
            )
            response_data["Section_C_Principle_1_E1_5"] = [disciplinary_action]

            conflict_of_interest_complaints = calculate_section_C_EI_6(
                financial_year, previous_financial_year
            )
            response_data["Section_C_Principle_1_E1_6"] = [
                conflict_of_interest_complaints
            ]

            description_obj = Policy_Details_Penalty.objects.filter(
                Model_Name_Penalty="Cases of Corruption"
            ).first()
            if description_obj:
                response_data["Section_C_Principle_1_E1_7"] = (
                    description_obj.Descriptions_Penalty
                )
            else:
                response_data["Section_C_Principle_1_E1_7"] = ""

            awareness_programmes_on_esg = calculate_section_C_Principle_1_LI_1(
                financial_year
            )
            response_data["Section_C_Principle_1_L1_1"] = [awareness_programmes_on_esg]

            description_obj = Policy_Details_Penalty.objects.filter(
                Model_Name_Penalty="Involving Members of the board"
            ).first()
            if description_obj:
                response_data["Section_C_Principle_1_L1_2"] = (
                    description_obj.Descriptions_Penalty
                )
            else:
                response_data["Section_C_Principle_1_L1_2"] = ""

            percent_of_investments = calculate_principle_2_EI_1(
                financial_year, previous_financial_year
            )
            response_data["Principle_2_EI_1"] = [percent_of_investments]

            description_obj = DescriptionsProjectandPolicies.objects.filter(
                Module_Name="Reclaim of Product"
            ).first()
            if description_obj:
                response_data["Principle_2_EI_3"] = description_obj.Description
            else:
                response_data["Principle_2_EI_3"] = ""

            description_obj = DescriptionsProjectandPolicies.objects.filter(
                Module_Name="Extended Producer Responsibility"
            ).first()
            if description_obj:
                response_data["Principle_2_EI_4"] = description_obj.Description
            else:
                response_data["Principle_2_EI_4"] = ""

            lifecycle_assessment = calculate_principle_2_LI_1(financial_year)
            response_data["Principle_2_LI_1"] = [lifecycle_assessment]

            concerns_and_action = calculate_principle_2_LI_2(financial_year)
            response_data["Principle_2_LI_2"] = [concerns_and_action]

            end_of_life_of_product = calculate_principle_2_LI_4(
                financial_year, previous_financial_year
            )
            response_data["Principle_2_LI_4"] = [end_of_life_of_product]

            reclaimed_products_and_packaging = calculate_principle_2_LI_5(
                financial_year
            )
            response_data["Principle_2_LI_5"] = [reclaimed_products_and_packaging]

            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except APIException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BRS_Report1_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            financial_year = request.query_params.get("financial_year", None)
            start_year = int(financial_year[2:6])
            previous_financial_year = f"FY{start_year-1}-{start_year}"

            response_data = {
                "Section_EI_1": [{}],
                "Section_EI_2": [{}],
                "Section_EI_4": [{}],
                "P3_1_1a": [{}],
                "P3_2": [{}],
                "P3_3": [{}],
                "P3_4": [{}],
                "P3_5": [{}],
                "P3_6": [{}],
                "P3_10_a": [{}],
                "P3_10_b": [{}],
                "P3_10_c": [{}],
                "P3_10_d": [{}],
                "P3_12": [{}],
                "P3_13": [{}],
                "P3_14": [{}],
                "P3_15": [{}],
                "LI_1a": [{}],
                "LI_1b": [{}],
                "LI_2": [{}],
                "LI_3": [{}],
                "LI_4": [{}],
                "LI_5": [{}],
                "LI_6": [{}],
                "P3_EI_8": {},
            }

            segments = [
                "Employees",
                "Workers",
                "Board Of Directors",
                "Key Managerial Personnel",
            ]
            for segment in segments:
                awareness_programmes_obj = Awareness_Programmes_On_ESG.objects.filter(
                    Financial_Year=financial_year, Segment=segment
                ).first()

                if awareness_programmes_obj:
                    segment_data = [
                        awareness_programmes_obj.Total_No_Of_Programmes_Held or 0,
                        awareness_programmes_obj.Topics_Covered or "",
                        awareness_programmes_obj.Percentage_Of_Persons.to_decimal(),
                    ]
                else:
                    segment_data = [0, "", 0.0]

                # Adjust segment names to match the requested format
                segment_key = segment.replace(" ", "_")
                response_data["Section_EI_1"][0][segment_key] = segment_data

            monetory_type = ["Penalty/Fine", "Settelment", "Compounding Fee"]
            for type in monetory_type:
                monetory_obj = Penalty_Monetary.objects.filter(
                    Financial_Year=financial_year, Monetary_Type=type
                ).first()

                if monetory_obj:
                    monetory_data = [
                        monetory_obj.NGRBC_Principle or "",
                        monetory_obj.Name_of_agency or "",
                        monetory_obj.Amount or 0,
                        monetory_obj.Brief_case or "",
                        monetory_obj.Has_an_appeal_been_prefered or "",
                    ]
                else:
                    monetory_data = ["", "", 0, "", ""]

                # Adjust segment names to match the requested format
                monetory_key = type.replace("/", "_").replace(" ", "_")
                response_data["Section_EI_2"][0][monetory_key] = monetory_data

            non_monetory = ["Imprisonment", "Punishment"]
            for type in non_monetory:
                non_monetory_obj = Penalty_Non_Monetary.objects.filter(
                    Financial_Year=financial_year, Non_Monetary_Type=non_monetory
                ).first()

                if non_monetory_obj:
                    non_monetory_data = [
                        non_monetory_obj.NGRBC_Principle or "",
                        non_monetory_obj.Name_of_agency or "",
                        non_monetory_obj.Brief_case or "",
                        non_monetory_obj.Has_an_appeal_been_prefered or "",
                    ]
                else:
                    non_monetory_data = ["", "", "", ""]

                non_monetory_key = type.replace("/", "_").replace(" ", "_")
                response_data["Section_EI_2"][0][non_monetory_key] = non_monetory_data

                policy_details_penalty = Policy_Details_Penalty.objects.get(
                    Model_Name_Penalty="Sites Facilities"
                )
                EI_4 = policy_details_penalty.Descriptions_Penalty
                response_data["Section_EI_4"] = EI_4

            response_data["P3_1_1a"] = {
                "Permanent": get_totals(financial_year, "Employees", "Permanent"),
                "Non_Permanent": get_totals(
                    financial_year, "Employees", "Non-Permanent"
                ),
            }

            response_data["P3_1_1b"] = {
                "Permanent": get_totals(financial_year, "Workers", "Permanent"),
                "Non_Permanent": get_totals(financial_year, "Workers", "Non-Permanent"),
            }

            description_obj = Policy_Details_Health_safety.objects.filter(
                Model_Name_Health_safety="Rights of Persons"
            ).first()
            if description_obj:
                response_data["P3_3"] = description_obj.Descriptions_Health_safety
            else:
                response_data["P3_3"] = ""
            description_obj = Policy_Details_Health_safety.objects.filter(
                Model_Name_Health_safety="Equal opportunity"
            ).first()
            if description_obj:
                response_data["P3_4"] = description_obj.Descriptions_Health_safety
            else:
                response_data["P3_4"] = ""

            # Initialize the rate variables
            return_to_work_rate_for_male_employee = 0
            return_to_work_rate_for_female_employee = 0
            retention_rate_for_male_employee = 0
            retention_rate_for_female_employee = 0
            return_to_work_rate_male_worker = 0
            return_to_work_rate_female_worker = 0
            retention_rate_for_male_worker = 0
            retention_rate_for_female_worker = 0
            total_return_to_work_rate_employee = 0
            total_retention_rate_employee = 0
            total_return_to_work_rate_of_workers = 0
            total_retention_rate_workers = 0

            # Get the records for both the current and previous financial years
            filtered_records = (
                Post_Paternal_Leave_For_Permanent_Employee_And_Worker.objects.filter(
                    Financial_Year__in=[financial_year, previous_financial_year]
                )
            )

            # Accumulate the rates from the filtered records
            for record in filtered_records:
                return_to_work_rate_for_male_employee += (
                    record.Return_To_Work_Rate_For_Male_Employee or 0
                )
                return_to_work_rate_for_female_employee += (
                    record.Return_To_Work_Rate_For_Female_Employee or 0
                )
                retention_rate_for_male_employee += (
                    record.Retention_Rate_For_Male_Employee or 0
                )
                retention_rate_for_female_employee += (
                    record.Retention_Rate_For_Female_Employee or 0
                )
                return_to_work_rate_male_worker += (
                    record.Return_To_Work_Rate_Male_Workers or 0
                )
                return_to_work_rate_female_worker += (
                    record.Return_To_Work_Rate_Female_Workers or 0
                )
                retention_rate_for_male_worker += (
                    record.Retention_Rate_For_Male_Workers or 0
                )
                retention_rate_for_female_worker += (
                    record.Retention_Rate_For_Female_Workers or 0
                )
                total_return_to_work_rate_employee += (
                    record.Total_Return_To_Work_Rate_Employee or 0
                )
                total_return_to_work_rate_of_workers += (
                    record.Total_Return_To_Work_Rate_Of_Workers or 0
                )
                total_retention_rate_employee += (
                    record.Total_Retention_Rate_Employee or 0
                )
                total_retention_rate_workers += record.Total_Retention_Rate_Workers or 0

            # Fetch the post paternal leave object for the current financial year
            # Fetch all post paternal leave objects for the current financial year
            post_paternal_leave_objs = (
                Post_Paternal_Leave_For_Permanent_Employee_And_Worker.objects.filter(
                    Financial_Year=financial_year
                )
            )

            # Accumulate the rates from the current year's specific object data
            for post_paternal_leave_obj in post_paternal_leave_objs:
                return_to_work_rate_for_male_employee += (
                    post_paternal_leave_obj.Return_To_Work_Rate_For_Male_Employee or 0
                )
                return_to_work_rate_for_female_employee += (
                    post_paternal_leave_obj.Return_To_Work_Rate_For_Female_Employee or 0
                )
                retention_rate_for_male_employee += (
                    post_paternal_leave_obj.Retention_Rate_For_Male_Employee or 0
                )
                retention_rate_for_female_employee += (
                    post_paternal_leave_obj.Retention_Rate_For_Female_Employee or 0
                )

                return_to_work_rate_male_worker += (
                    post_paternal_leave_obj.Return_To_Work_Rate_Male_Workers or 0
                )
                return_to_work_rate_female_worker += (
                    post_paternal_leave_obj.Return_To_Work_Rate_Female_Workers or 0
                )
                retention_rate_for_male_worker += (
                    post_paternal_leave_obj.Retention_Rate_For_Male_Workers or 0
                )
                retention_rate_for_female_worker += (
                    post_paternal_leave_obj.Retention_Rate_For_Female_Workers or 0
                )

                total_return_to_work_rate_employee += (
                    post_paternal_leave_obj.Total_Return_To_Work_Rate_Employee or 0
                )
                total_return_to_work_rate_of_workers += (
                    post_paternal_leave_obj.Total_Return_To_Work_Rate_Of_Workers or 0
                )
                total_retention_rate_employee += (
                    post_paternal_leave_obj.Total_Retention_Rate_Employee or 0
                )
                total_retention_rate_workers += (
                    post_paternal_leave_obj.Total_Retention_Rate_Workers or 0
                )

            # Prepare the response data
            response_data["P3_5"] = {
                "Return_To_Work_Rate_For_Male_Employee": return_to_work_rate_for_male_employee,
                "Return_To_Work_Rate_For_Female_Employee": return_to_work_rate_for_female_employee,
                "Retention_Rate_For_Male_Employee": retention_rate_for_male_employee,
                "Retention_Rate_For_Female_Employee": retention_rate_for_female_employee,
                "Return_To_Work_Rate_Male_Worker": return_to_work_rate_male_worker,
                "Return_To_Work_Rate_Female_Worker": return_to_work_rate_female_worker,
                "Retention_Rate_For_Male_Worker": retention_rate_for_male_worker,
                "Retention_Rate_For_Female_Worker": retention_rate_for_female_worker,
                "Total_Return_To_Work_Rate_Employee": total_return_to_work_rate_employee,
                "Total_Return_To_Work_Rate_Of_Workers": total_return_to_work_rate_of_workers,
                "Total_Retention_Rate_Employee": total_retention_rate_employee,
                "Total_Retention_Rate_Workers": total_retention_rate_workers,
            }

            grievances_redress_obj1 = (
                Receive_and_redress_grievances_mechanism.objects.filter(
                    Segment="Employee", Type="Permanent"
                ).values("Yes_No", "Description")
            )

            grievances_redress_obj2 = (
                Receive_and_redress_grievances_mechanism.objects.filter(
                    Segment="Employee", Type="Non Permanent"
                ).values("Yes_No", "Description")
            )

            grievances_redress_obj3 = (
                Receive_and_redress_grievances_mechanism.objects.filter(
                    Segment="Worker", Type="Permanent"
                ).values("Yes_No", "Description")
            )

            grievances_redress_obj4 = (
                Receive_and_redress_grievances_mechanism.objects.filter(
                    Segment="Worker", Type="Non Permanent"
                ).values("Yes_No", "Description")
            )

            response_data["P3_6"] = {
                "Permanent_Employee": list(grievances_redress_obj1),
                "Non Permanent_Employee": list(grievances_redress_obj2),
                "Permanent_Workers": list(grievances_redress_obj3),
                "Non Permanent_Workers": list(grievances_redress_obj4),
            }

            description_obj = Policy_Details_Health_safety.objects.filter(
                Model_Name_Health_safety="Occupational Health"
            ).first()
            if description_obj:
                response_data["P3_10_a"] = description_obj.Descriptions_Health_safety
            else:
                response_data["P3_10_a"] = ""
            description_obj = Policy_Details_Health_safety.objects.filter(
                Model_Name_Health_safety="Work Related Hazards"
            ).first()
            if description_obj:
                response_data["P3_10_b"] = description_obj.Descriptions_Health_safety
            else:
                response_data["P3_10_b"] = ""
            description_obj = Policy_Details_Health_safety.objects.filter(
                Model_Name_Health_safety="Workers to Report"
            ).first()
            if description_obj:
                response_data["P3_10_c"] = description_obj.Is_Verified
            else:
                response_data["P3_10_c"] = ""
            description_obj = Policy_Details_Health_safety.objects.filter(
                Model_Name_Health_safety="Workers of Entity"
            ).first()
            if description_obj:
                response_data["P3_10_d"] = description_obj.Is_Verified
            else:
                response_data["P3_10_d"] = ""
            description_obj = Policy_Details_Health_safety.objects.filter(
                Model_Name_Health_safety="Healthy Workplace"
            ).first()
            if description_obj:
                response_data["P3_12"] = description_obj.Descriptions_Health_safety
            else:
                response_data["P3_12"] = ""

            current_working_condition = (
                Health_and_safety_related_complaints.objects.filter(
                    Financial_Year=financial_year, Complaint_Type="Working Conditions"
                ).first()
            )

            current_health_safety = Health_and_safety_related_complaints.objects.filter(
                Financial_Year=financial_year, Complaint_Type="Health & Safety"
            ).first()

            # Fetch data for the previous financial year
            previous_working_condition = (
                Health_and_safety_related_complaints.objects.filter(
                    Financial_Year=previous_financial_year,
                    Complaint_Type="Working Conditions",
                ).first()
            )

            previous_health_safety = (
                Health_and_safety_related_complaints.objects.filter(
                    Financial_Year=previous_financial_year,
                    Complaint_Type="Health & Safety",
                ).first()
            )

            response_data["P3_13"] = {
                "current": {
                    "Working Conditions": {
                        "Filed_During_The_Year": (
                            current_working_condition.Filed_During_The_Year
                            if current_working_condition
                            else None
                        ),
                        "Pending_Resolution_At_The_EOY": (
                            current_working_condition.Pending_Resolution_At_The_EOY
                            if current_working_condition
                            else None
                        ),
                        "Remark": (
                            current_working_condition.Remark
                            if current_working_condition
                            else None
                        ),
                    },
                    "Health & Safety": {
                        "Filed_During_The_Year": (
                            current_health_safety.Filed_During_The_Year
                            if current_health_safety
                            else None
                        ),
                        "Pending_Resolution_At_The_EOY": (
                            current_health_safety.Pending_Resolution_At_The_EOY
                            if current_health_safety
                            else None
                        ),
                        "Remark": (
                            current_health_safety.Remark
                            if current_health_safety
                            else None
                        ),
                    },
                },
                "previous": {
                    "Working Conditions": {
                        "Filed_During_The_Year": (
                            previous_working_condition.Filed_During_The_Year
                            if previous_working_condition
                            else None
                        ),
                        "Pending_Resolution_At_The_EOY": (
                            previous_working_condition.Pending_Resolution_At_The_EOY
                            if previous_working_condition
                            else None
                        ),
                        "Remark": (
                            previous_working_condition.Remark
                            if previous_working_condition
                            else None
                        ),
                    },
                    "Health & Safety": {
                        "Filed_During_The_Year": (
                            previous_health_safety.Filed_During_The_Year
                            if previous_health_safety
                            else None
                        ),
                        "Pending_Resolution_At_The_EOY": (
                            previous_health_safety.Pending_Resolution_At_The_EOY
                            if previous_health_safety
                            else None
                        ),
                        "Remark": (
                            previous_health_safety.Remark
                            if previous_health_safety
                            else None
                        ),
                    },
                },
            }

            assessment_of_the_year = Assessment_Of_Plants_And_Offices.objects.get(
                Financial_Year=financial_year
            )
            Percentage_Assessed_For_Working_Conditions = (
                assessment_of_the_year.Percentage_Assessed_For_Working_Conditions.to_decimal()
            )
            Percentage_Assessed_For_Health_And_Safety = (
                assessment_of_the_year.Percentage_Assessed_For_Health_And_Safety.to_decimal()
            )

            response_data["P3_14"] = {
                "Percentage_Assessed_For_Working_Conditions": Percentage_Assessed_For_Working_Conditions,
                "Percentage_Assessed_For_Health_And_Safety": Percentage_Assessed_For_Health_And_Safety,
            }

            description_obj = Policy_Details_Health_safety.objects.filter(
                Model_Name_Health_safety="Safety Related Incidence"
            ).first()
            if description_obj:
                response_data["P3_15"] = description_obj.Descriptions_Health_safety
            else:
                response_data["P3_15"] = ""

            description_obj = Policy_Details_Health_safety.objects.filter(
                Model_Name_Health_safety="Event of Death employees"
            ).first()
            if description_obj:
                response_data["LI_1a"] = description_obj.Is_Verified
            else:
                response_data["LI_1a"] = ""
            description_obj = Policy_Details_Health_safety.objects.filter(
                Model_Name_Health_safety="Event of death workers"
            ).first()
            if description_obj:
                response_data["LI_1b"] = description_obj.Is_Verified
            else:
                response_data["LI_1b"] = ""
            description_obj = Policy_Details_Health_safety.objects.filter(
                Model_Name_Health_safety="Value Chain Partners"
            ).first()
            if description_obj:
                response_data["LI_2"] = description_obj.Descriptions_Health_safety
            else:
                response_data["LI_2"] = ""

            # Initialize totals
            total_no_of_affected_employees = 0
            total_no_of_affected_workers = 0
            rehabilitated_and_placed_in_suitable_employee = 0
            rehabilitated_and_placed_in_suitable_workers = 0

            # Get filtered records for the given financial year
            filtered_records = (
                Suffered_High_Consequence_Work_Related_Injury.objects.filter(
                    Financial_Year=financial_year,
                )
            )

            # Accumulate the values from the filtered records
            for record in filtered_records:
                total_no_of_affected_employees += (
                    record.Total_No_Of_Affected_Employees or 0
                )
                total_no_of_affected_workers += record.Total_No_Of_Affected_Workers or 0
                rehabilitated_and_placed_in_suitable_employee += (
                    record.Rehabilitated_And_Placed_In_Suitable_Employee or 0
                )
                rehabilitated_and_placed_in_suitable_workers += (
                    record.Rehabilitated_And_Placed_In_Suitable_Workers or 0
                )

            # Get the records for the current financial year
            current_year_records = (
                Suffered_High_Consequence_Work_Related_Injury.objects.filter(
                    Financial_Year=financial_year,
                )
            )

            # Get the records for the previous financial year
            previous_year_records = (
                Suffered_High_Consequence_Work_Related_Injury.objects.filter(
                    Financial_Year=previous_financial_year,
                )
            )

            # Add the values from the current year records
            for record in current_year_records:
                total_no_of_affected_employees += (
                    record.Total_No_Of_Affected_Employees or 0
                )
                total_no_of_affected_workers += record.Total_No_Of_Affected_Workers or 0
                rehabilitated_and_placed_in_suitable_employee += (
                    record.Rehabilitated_And_Placed_In_Suitable_Employee or 0
                )
                rehabilitated_and_placed_in_suitable_workers += (
                    record.Rehabilitated_And_Placed_In_Suitable_Workers or 0
                )

            # Add the values from the previous year records
            for record in previous_year_records:
                total_no_of_affected_employees += (
                    record.Total_No_Of_Affected_Employees or 0
                )
                total_no_of_affected_workers += record.Total_No_Of_Affected_Workers or 0
                rehabilitated_and_placed_in_suitable_employee += (
                    record.Rehabilitated_And_Placed_In_Suitable_Employee or 0
                )
                rehabilitated_and_placed_in_suitable_workers += (
                    record.Rehabilitated_And_Placed_In_Suitable_Workers or 0
                )

            # Prepare the response data
            response_data["LI_3"] = {
                "Total_No_Of_Affected_Employees": total_no_of_affected_employees,
                "Total_No_Of_Affected_Workers": total_no_of_affected_workers,
                "Rehabilitated_And_Placed_In_Suitable_Employee": rehabilitated_and_placed_in_suitable_employee,
                "Rehabilitated_And_Placed_In_Suitable_Workers": rehabilitated_and_placed_in_suitable_workers,
            }

            description_obj = Policy_Details_Health_safety.objects.filter(
                Model_Name_Health_safety="Transition Assistance PGM"
            ).first()
            if description_obj:
                response_data["LI_4"] = description_obj.Is_Verified
            else:
                response_data["LI_4"] = ""

            assessment_of_the_year = (
                Assessment_Of_Value_Chain_Partners_Health_And_Safety.objects.get(
                    Financial_Year=financial_year
                )
            )
            Percentage_Assessed_For_Working_Conditions = (
                assessment_of_the_year.Percentage_Assessed_For_Working_Conditions.to_decimal()
            )
            Percentage_Assessed_For_Health_And_Safety = (
                assessment_of_the_year.Percentage_Assessed_For_Health_And_Safety.to_decimal()
            )

            response_data["LI_5"] = {
                "Percentage_Assessed_For_Working_Conditions": Percentage_Assessed_For_Working_Conditions,
                "Percentage_Assessed_For_Health_And_Safety": Percentage_Assessed_For_Health_And_Safety,
            }

            description_obj = Policy_Details_Health_safety.objects.filter(
                Model_Name_Health_safety="Working of Partners"
            ).first()
            if description_obj:
                response_data["LI_6"] = description_obj.Descriptions_Health_safety
            else:
                response_data["LI_6"] = ""

            # Get the records for the current financial year
            current_year_records = On_Skill_Upgradation.objects.filter(
                Financial_Year=financial_year, Segment="Employees"
            )

            # Get the records for the previous financial year
            previous_year_records = On_Skill_Upgradation.objects.filter(
                Financial_Year=previous_financial_year, Segment="Employees"
            )

            # Calculate totals for males and females separately
            current_total_male = sum(
                float(record.No_Of_Male or 0) for record in current_year_records
            )
            current_total_female = sum(
                float(record.No_Of_Female or 0) for record in current_year_records
            )
            current_total_male_female = sum(
                float(record.Total_Male_And_Female or 0)
                for record in current_year_records
            )

            previous_total_male = sum(
                float(record.No_Of_Male or 0) for record in previous_year_records
            )
            previous_total_female = sum(
                float(record.No_Of_Female or 0) for record in previous_year_records
            )
            previous_total_male_female = sum(
                float(record.Total_Male_And_Female or 0)
                for record in previous_year_records
            )

            response_data["LI_8"] = {
                "current_total_male": current_total_male,
                "current_total_female": current_total_female,
                "current_total_male_female": current_total_male_female,
                "previous_total_male": previous_total_male,
                "previous_total_female": previous_total_female,
                "previous_total_male_female": previous_total_male_female,
            }

            current_year_records_B = (
                Employees_Membership_In_Association_Or_Unions.objects.filter(
                    Financial_Year=financial_year
                )
            )

            # Get the records for the previous financial year
            previous_year_records_B = (
                Employees_Membership_In_Association_Or_Unions.objects.filter(
                    Financial_Year=previous_financial_year
                )
            )

            current_total_male_B = sum(
                float(record.Permanent_Males or 0) for record in current_year_records_B
            )
            current_total_female_B = sum(
                float(record.Permanent_Females or 0)
                for record in current_year_records_B
            )

            previous_total_male_B = sum(
                float(record.Permanent_Males or 0) for record in previous_year_records_B
            )
            previous_total_female_B = sum(
                float(record.Permanent_Females or 0)
                for record in previous_year_records_B
            )

            current_year_records_total_emp = EmployeeSummary.objects.filter(
                Financial_Year=financial_year
            )

            # Get the records for the previous financial year
            previous_year_records_total_emp = EmployeeSummary.objects.filter(
                Financial_Year=previous_financial_year
            )

            current_total_male_total_emp = sum(
                float(record.Male_Permanent.to_decimal() or 0)
                for record in current_year_records_total_emp
            )
            current_total_female_total_emp = sum(
                float(record.Female_Permanent.to_decimal() or 0)
                for record in current_year_records_total_emp
            )

            previous_total_male_total_emp = sum(
                float(record.Male_Permanent.to_decimal() or 0)
                for record in previous_year_records_total_emp
            )
            previous_total_female_total_emp = sum(
                float(record.Female_Permanent.to_decimal() or 0)
                for record in previous_year_records_total_emp
            )

            # Get the records for the current financial year
            current_year_records_W = (
                Workers_Membership_In_Association_Or_Unions.objects.filter(
                    Financial_Year=financial_year
                )
            )

            # Get the records for the previous financial year
            previous_year_records_W = (
                Workers_Membership_In_Association_Or_Unions.objects.filter(
                    Financial_Year=previous_financial_year
                )
            )

            current_total_male_W = sum(
                float(record.Permanent_Males or 0) for record in current_year_records_W
            )
            current_total_female_W = sum(
                float(record.Permanent_Females or 0)
                for record in current_year_records_W
            )

            previous_total_male_W = sum(
                float(record.Permanent_Males or 0) for record in previous_year_records_W
            )
            previous_total_female_W = sum(
                float(record.Permanent_Females or 0)
                for record in previous_year_records_W
            )

            # Get the records for the current and previous financial years for workers
            current_year_records_total_workers = WorkerSummary.objects.filter(
                Financial_Year=financial_year
            )

            previous_year_records_total_workers = WorkerSummary.objects.filter(
                Financial_Year=previous_financial_year
            )

            # Calculate the total male and female workers for the current and previous financial years
            current_total_male_workers = sum(
                float(record.Male_Permanent.to_decimal() or 0)
                for record in current_year_records_total_workers
            )
            current_total_female_workers = sum(
                float(record.Female_Permanent.to_decimal() or 0)
                for record in current_year_records_total_workers
            )

            previous_total_male_workers = sum(
                float(record.Male_Permanent.to_decimal() or 0)
                for record in previous_year_records_total_workers
            )
            previous_total_female_workers = sum(
                float(record.Female_Permanent.to_decimal() or 0)
                for record in previous_year_records_total_workers
            )

            response_data["P3_EI_7"] = {
                "current_total_male_B": current_total_male_B,
                "current_total_female_B": current_total_female_B,
                "Current_year_total_male_emp": (
                    round((current_total_male_B / current_total_male_total_emp), 2)
                    if current_total_male_total_emp != 0
                    else 0
                ),
                "Current_year_total_female_emp": (
                    round((current_total_female_B / current_total_female_total_emp), 2)
                    if current_total_female_total_emp != 0
                    else 0
                ),
                "previous_total_male_B": previous_total_male_B,
                "previous_total_female_B": previous_total_female_B,
                "pervious_total_male_emp": (
                    round((previous_total_male_B / previous_total_male_total_emp), 2)
                    if previous_total_male_total_emp != 0
                    else 0
                ),
                "pervious_total_female_emp": (
                    round(
                        (previous_total_female_B / previous_total_female_total_emp), 2
                    )
                    if previous_total_female_total_emp != 0
                    else 0
                ),
                "current_total_male_total_emp": current_total_male_total_emp,
                "current_total_female_total_emp": current_total_female_total_emp,
                "previous_total_male_total_emp": previous_total_male_total_emp,
                "previous_total_female_total_emp": previous_total_female_total_emp,
                "current_total_male_W": current_total_male_W,
                "current_total_female_W": current_total_female_W,
                "Current_year_total_male_workers": (
                    round((current_total_male_W / current_total_male_workers), 2)
                    if current_total_male_workers != 0
                    else 0
                ),
                "Current_year_total_female_workers": (
                    round((current_total_female_W / current_total_female_workers), 2)
                    if current_total_female_workers != 0
                    else 0
                ),
                "previous_total_male_W": previous_total_male_W,
                "previous_total_female_W": previous_total_female_W,
                "previous_total_male_workers": (
                    round((previous_total_male_W / previous_total_male_workers), 2)
                    if previous_total_male_workers != 0
                    else 0
                ),
                "previous_total_female_workers": (
                    round((previous_total_female_W / previous_total_female_workers), 2)
                    if previous_total_female_workers != 0
                    else 0
                ),
                "current_total_male_workers": current_total_male_workers,
                "current_total_female_workers": current_total_female_workers,
                "previous_total_male_workers": previous_total_male_workers,
                "previous_total_female_workers": previous_total_female_workers,
            }

            # Get the records for the current financial year

            # Fetch records for the current financial year for the "Employees" segment
            current_year_employee_records = On_Skill_Upgradation.objects.filter(
                Financial_Year=financial_year, Segment="Employees"
            )

            # Fetch records for the previous financial year for the "Employees" segment
            previous_year_employee_records = On_Skill_Upgradation.objects.filter(
                Financial_Year=previous_financial_year, Segment="Employees"
            )

            # Calculate total number of male employees in the current financial year
            current_total_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in current_year_employee_records
            )
            current_total_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in current_year_employee_records
            )

            # Calculate total number of male employees in the previous financial year
            previous_total_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in previous_year_employee_records
            )
            previous_total_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in previous_year_employee_records
            )

            ############################### P3 -  EI_8 #############################################
            total_emp_current_year = EmployeeSummary.objects.filter(
                Financial_Year=financial_year,
            )
            total_emp_previous_year = EmployeeSummary.objects.filter(
                Financial_Year=previous_financial_year,
            )
            # Calculate total number of male employees in the current financial year
            current_year_total_male_employees = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_emp_current_year
            )
            current_year_total_female_employees = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_emp_current_year
            )
            previous_year_total_male_employees = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_emp_previous_year
            )
            previous_year_total_female_employees = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_emp_previous_year
            )

            # Fetch health and safety measures for the current and previous financial years
            health_and_safety_measures_current_year = (
                On_Health_And_Safety_Measures.objects.filter(
                    Financial_Year=financial_year, Segment="Employees"
                )
            )
            health_and_safety_measures_previous_year = (
                On_Health_And_Safety_Measures.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Employees"
                )
            )
            # Calculate total number of male and female employees in health and safety measures for the current financial year
            current_year_health_and_safety_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in health_and_safety_measures_current_year
            )
            current_year_health_and_safety_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in health_and_safety_measures_current_year
            )

            # Calculate total number of male and female employees in health and safety measures for the previous financial year
            previous_year_health_and_safety_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in health_and_safety_measures_previous_year
            )
            previous_year_health_and_safety_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in health_and_safety_measures_previous_year
            )

            # Fetch skill upgradation records for the current and previous financial years
            skill_upgradation_current_year = On_Skill_Upgradation.objects.filter(
                Financial_Year=financial_year, Segment="Employees"
            )
            skill_upgradation_previous_year = On_Skill_Upgradation.objects.filter(
                Financial_Year=previous_financial_year, Segment="Employees"
            )

            # Calculate total number of male and female employees in skill upgradation for the current financial year
            current_year_skill_upgradation_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in skill_upgradation_current_year
            )
            current_year_skill_upgradation_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in skill_upgradation_current_year
            )

            # Calculate total number of male and female employees in skill upgradation for the previous financial year
            previous_year_skill_upgradation_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in skill_upgradation_previous_year
            )
            previous_year_skill_upgradation_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in skill_upgradation_previous_year
            )

            ############################### P3 - EI_8 for WorkSummary #############################################
            # WorkSummary calculations
            total_work_current_year = WorkerSummary.objects.filter(
                Financial_Year=financial_year
            )
            total_work_previous_year = WorkerSummary.objects.filter(
                Financial_Year=previous_financial_year
            )

            current_year_total_male_workers = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_work_current_year
            )
            current_year_total_female_workers = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_work_current_year
            )
            previous_year_total_male_workers = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_work_previous_year
            )
            previous_year_total_female_workers = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_work_previous_year
            )

            health_and_safety_measures_work_current_year = (
                On_Health_And_Safety_Measures.objects.filter(
                    Financial_Year=financial_year, Segment="Workers"
                )
            )
            health_and_safety_measures_work_previous_year = (
                On_Health_And_Safety_Measures.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Workers"
                )
            )

            current_year_health_and_safety_male_workers = sum(
                float(record.No_Of_Male or 0)
                for record in health_and_safety_measures_work_current_year
            )
            current_year_health_and_safety_female_workers = sum(
                float(record.No_Of_Female or 0)
                for record in health_and_safety_measures_work_current_year
            )
            previous_year_health_and_safety_male_workers = sum(
                float(record.No_Of_Male or 0)
                for record in health_and_safety_measures_work_previous_year
            )
            previous_year_health_and_safety_female_workers = sum(
                float(record.No_Of_Female or 0)
                for record in health_and_safety_measures_work_previous_year
            )

            skill_upgradation_work_current_year = On_Skill_Upgradation.objects.filter(
                Financial_Year=financial_year, Segment="Workers"
            )
            skill_upgradation_work_previous_year = On_Skill_Upgradation.objects.filter(
                Financial_Year=previous_financial_year, Segment="Workers"
            )

            current_year_skill_upgradation_male_workers = sum(
                float(record.No_Of_Male or 0)
                for record in skill_upgradation_work_current_year
            )
            current_year_skill_upgradation_female_workers = sum(
                float(record.No_Of_Female or 0)
                for record in skill_upgradation_work_current_year
            )
            previous_year_skill_upgradation_male_workers = sum(
                float(record.No_Of_Male or 0)
                for record in skill_upgradation_work_previous_year
            )
            previous_year_skill_upgradation_female_workers = sum(
                float(record.No_Of_Female or 0)
                for record in skill_upgradation_work_previous_year
            )

            # current_total_male_female_workers = round((current_year_total_male_workers+current_year_total_female_workers),2)
            # current_year_total_health_and_safety_male_female_workers = round((current_year_health_and_safety_male_workers+current_year_health_and_safety_female_workers),2)
            # previous_total_male_female = round((previous_year_total_male_workers+previous_year_total_female_workers),2)
            # previous_year_health_and_safety_male_female_workers = round((previous_year_health_and_safety_male_workers+previous_year_health_and_safety_female_workers),2)

            current_year_male_workers_ratio = (
                round(
                    current_year_total_male_workers
                    / current_year_health_and_safety_male_workers,
                    2,
                )
                if current_year_health_and_safety_male_workers
                else 0
            )

            current_year_female_workers_ratio = (
                round(
                    current_year_total_female_workers
                    / current_year_health_and_safety_female_workers,
                    2,
                )
                if current_year_health_and_safety_female_workers
                else 0
            )

            previous_year_male_workers_ratio = (
                round(
                    previous_year_total_male_workers
                    / previous_year_health_and_safety_male_workers,
                    2,
                )
                if previous_year_health_and_safety_male_workers
                else 0
            )

            previous_year_female_workers_ratio = (
                round(
                    previous_year_total_female_workers
                    / previous_year_health_and_safety_female_workers,
                    2,
                )
                if previous_year_health_and_safety_female_workers
                else 0
            )

            response_data["P3_EI_8"] = {
                "Employees": {
                    "current_year_record": {
                        "total_male_employees": current_year_total_male_employees,
                        "total_female_employees": current_year_total_female_employees,
                        "health_and_safety_male_employees": current_year_health_and_safety_male_employees,
                        "health_and_safety_female_employees": current_year_health_and_safety_female_employees,
                        "skill_upgradation_male_employees": current_year_skill_upgradation_male_employees,
                        "skill_upgradation_female_employees": current_year_skill_upgradation_female_employees,
                        "male_employees_ratio": (
                            round(
                                current_year_total_male_employees
                                / current_year_health_and_safety_male_employees,
                                2,
                            )
                            if current_year_health_and_safety_male_employees
                            else 0
                        ),
                        "female_employees_ratio": (
                            round(
                                current_year_total_female_employees
                                / current_year_health_and_safety_female_employees,
                                2,
                            )
                            if current_year_health_and_safety_female_employees
                            else 0
                        ),
                        "male_upgradation_ratio": (
                            round(
                                current_year_total_male_employees
                                / current_year_skill_upgradation_male_employees,
                                2,
                            )
                            if current_year_skill_upgradation_male_employees
                            else 0
                        ),
                        "female_upgradation_ratio": (
                            round(
                                current_year_total_female_employees
                                / current_year_skill_upgradation_female_employees,
                                2,
                            )
                            if current_year_skill_upgradation_female_employees
                            else 0
                        ),
                    },
                    "previous_year_record": {
                        "total_male_employees": previous_year_total_male_employees,
                        "total_female_employees": previous_year_total_female_employees,
                        "health_and_safety_male_employees": previous_year_health_and_safety_male_employees,
                        "health_and_safety_female_employees": previous_year_health_and_safety_female_employees,
                        "skill_upgradation_male_employees": previous_year_skill_upgradation_male_employees,
                        "skill_upgradation_female_employees": previous_year_skill_upgradation_female_employees,
                        "male_employees_ratio": (
                            round(
                                previous_year_total_male_employees
                                / previous_year_health_and_safety_male_employees,
                                2,
                            )
                            if previous_year_health_and_safety_male_employees
                            else 0
                        ),
                        "female_employees_ratio": (
                            round(
                                previous_year_total_female_employees
                                / previous_year_health_and_safety_female_employees,
                                2,
                            )
                            if previous_year_health_and_safety_female_employees
                            else 0
                        ),
                        "male_upgradation_ratio": (
                            round(
                                previous_year_total_male_employees
                                / previous_year_skill_upgradation_male_employees,
                                2,
                            )
                            if previous_year_skill_upgradation_male_employees
                            else 0
                        ),
                        "female_upgradation_ratio": (
                            round(
                                previous_year_total_female_employees
                                / previous_year_skill_upgradation_female_employees,
                                2,
                            )
                            if previous_year_skill_upgradation_female_employees
                            else 0
                        ),
                    },
                },
                "Workers": {
                    "current_year_record": {
                        "total_male_workers": current_year_total_male_workers,
                        "total_female_workers": current_year_total_female_workers,
                        "total_male_female_workers": round(
                            current_year_total_male_workers
                            + current_year_total_female_workers,
                            2,
                        ),
                        "health_and_safety_male_workers": current_year_health_and_safety_male_workers,
                        "health_and_safety_female_workers": current_year_health_and_safety_female_workers,
                        "total_health_and_safety_male_female_workers": round(
                            current_year_health_and_safety_male_workers
                            + current_year_health_and_safety_female_workers,
                            2,
                        ),
                        "skill_upgradation_male_workers": current_year_skill_upgradation_male_workers,
                        "skill_upgradation_female_workers": current_year_skill_upgradation_female_workers,
                        "skill_upgradation_male_female_workers": round(
                            current_year_skill_upgradation_male_workers
                            + current_year_skill_upgradation_female_workers,
                            2,
                        ),
                        "male_workers_ratio": (
                            round(
                                current_year_total_male_workers
                                / current_year_health_and_safety_male_workers,
                                2,
                            )
                            if current_year_health_and_safety_male_workers
                            else 0
                        ),
                        "female_workers_ratio": (
                            round(
                                current_year_total_female_workers
                                / current_year_health_and_safety_female_workers,
                                2,
                            )
                            if current_year_health_and_safety_female_workers
                            else 0
                        ),
                        "male_female_worker_ratio": (
                            round(
                                (
                                    current_year_male_workers_ratio
                                    / current_year_female_workers_ratio
                                )
                                * 100,
                                2,
                            )
                            if current_year_female_workers_ratio
                            else 0
                        ),
                        "male_upgradation_ratio": (
                            round(
                                current_year_total_male_workers
                                / current_year_skill_upgradation_male_workers,
                                2,
                            )
                            if current_year_skill_upgradation_male_workers
                            else 0
                        ),
                        "female_upgradation_ratio": (
                            round(
                                current_year_total_female_workers
                                / current_year_skill_upgradation_female_workers,
                                2,
                            )
                            if current_year_skill_upgradation_female_workers
                            else 0
                        ),
                    },
                    "previous_year_record": {
                        "total_male_workers": previous_year_total_male_workers,
                        "total_female_workers": previous_year_total_female_workers,
                        "total_male_female_workers": round(
                            previous_year_total_male_workers
                            + previous_year_total_female_workers,
                            2,
                        ),
                        "health_and_safety_male_workers": previous_year_health_and_safety_male_workers,
                        "health_and_safety_female_workers": previous_year_health_and_safety_female_workers,
                        "total_health_and_safety_male_female_workers": round(
                            previous_year_health_and_safety_male_workers
                            + previous_year_health_and_safety_female_workers,
                            2,
                        ),
                        "skill_upgradation_male_workers": previous_year_skill_upgradation_male_workers,
                        "skill_upgradation_female_workers": previous_year_skill_upgradation_female_workers,
                        "skill_upgradation_male_female_workers": round(
                            previous_year_skill_upgradation_male_workers
                            + previous_year_skill_upgradation_female_workers,
                            2,
                        ),
                        "male_workers_ratio": (
                            round(
                                previous_year_total_male_workers
                                / previous_year_health_and_safety_male_workers,
                                2,
                            )
                            if previous_year_health_and_safety_male_workers
                            else 0
                        ),
                        "female_workers_ratio": (
                            round(
                                previous_year_total_female_workers
                                / previous_year_health_and_safety_female_workers,
                                2,
                            )
                            if previous_year_health_and_safety_female_workers
                            else 0
                        ),
                        "male_female_worker_ratio": (
                            round(
                                (
                                    previous_year_male_workers_ratio
                                    / previous_year_female_workers_ratio
                                )
                                * 100,
                                2,
                            )
                            if previous_year_female_workers_ratio
                            else 0
                        ),
                        "male_upgradation_ratio": (
                            round(
                                previous_year_total_male_workers
                                / previous_year_skill_upgradation_male_workers,
                                2,
                            )
                            if previous_year_skill_upgradation_male_workers
                            else 0
                        ),
                        "female_upgradation_ratio": (
                            round(
                                previous_year_total_female_workers
                                / previous_year_skill_upgradation_female_workers,
                                2,
                            )
                            if previous_year_skill_upgradation_female_workers
                            else 0
                        ),
                    },
                },
            }

            ############################### P3 -  EI_9 emp #############################################
            total_emp_current_year_record = EmployeeSummary.objects.filter(
                Financial_Year=financial_year,
            )
            total_emp_previous_year_record = EmployeeSummary.objects.filter(
                Financial_Year=previous_financial_year,
            )
            # Calculate total number of male employees in the current financial year
            current_year_total_male_employees = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_emp_current_year_record
            )
            current_year_total_female_employees = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_emp_current_year_record
            )
            previous_year_total_male_employees = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_emp_previous_year_record
            )
            previous_year_total_female_employees = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_emp_previous_year_record
            )

            # Fetch performance and career reviews for the current and previous financial years
            performance_reviews_current_year = (
                Performance_And_Career_Reviews.objects.filter(
                    Financial_Year=financial_year, Segment="Employees"
                )
            )
            performance_reviews_previous_year = (
                Performance_And_Career_Reviews.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Employees"
                )
            )

            # Calculate total number of male and female employees in performance and career reviews for the current financial year
            current_year_performance_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in performance_reviews_current_year
            )
            current_year_performance_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in performance_reviews_current_year
            )

            # Calculate total number of male and female employees in performance and career reviews for the previous financial year
            previous_year_performance_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in performance_reviews_previous_year
            )
            previous_year_performance_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in performance_reviews_previous_year
            )

            total_male_female_employees_current_year = (
                current_year_total_male_employees + current_year_total_female_employees
            )
            performance_male_female_employees_current_year = (
                current_year_performance_male_employees
                + current_year_performance_female_employees
            )

            total_male_female_employees_previous_year = (
                previous_year_total_male_employees
                + previous_year_total_female_employees
            )
            performance_male_female_employees_previous_year = (
                previous_year_performance_male_employees
                + previous_year_performance_female_employees
            )

            # Fetch records for the current and previous financial years
            total_workers_current_year_record = WorkerSummary.objects.filter(
                Financial_Year=financial_year,
            )

            total_workers_previous_year_record = WorkerSummary.objects.filter(
                Financial_Year=previous_financial_year,
            )

            # Calculate total number of male and female workers in the current financial year
            current_year_total_male_workers = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_workers_current_year_record
            )
            current_year_total_female_workers = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_workers_current_year_record
            )

            # Calculate total number of male and female workers in the previous financial year
            previous_year_total_male_workers = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_workers_previous_year_record
            )
            previous_year_total_female_workers = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_workers_previous_year_record
            )

            ############## Fetch performance and career reviews for the current and previous financial years for Workers #########################
            performance_reviews_current_year_workers = (
                Performance_And_Career_Reviews.objects.filter(
                    Financial_Year=financial_year, Segment="Workers"
                )
            )

            performance_reviews_previous_year_workers = (
                Performance_And_Career_Reviews.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Workers"
                )
            )

            # Calculate total number of male and female workers in performance and career reviews for the current financial year
            current_year_performance_male_workers = sum(
                float(record.No_Of_Male or 0)
                for record in performance_reviews_current_year_workers
            )
            current_year_performance_female_workers = sum(
                float(record.No_Of_Female or 0)
                for record in performance_reviews_current_year_workers
            )

            # Calculate total number of male and female workers in performance and career reviews for the previous financial year
            previous_year_performance_male_workers = sum(
                float(record.No_Of_Male or 0)
                for record in performance_reviews_previous_year_workers
            )
            previous_year_performance_female_workers = sum(
                float(record.No_Of_Female or 0)
                for record in performance_reviews_previous_year_workers
            )

            # Calculate total male and female workers
            total_male_female_workers_current_year = (
                current_year_total_male_workers + current_year_total_female_workers
            )
            performance_male_female_workers_current_year = (
                current_year_performance_male_workers
                + current_year_performance_female_workers
            )

            total_male_female_workers_previous_year = (
                previous_year_total_male_workers + previous_year_total_female_workers
            )
            performance_male_female_workers_previous_year = (
                previous_year_performance_male_workers
                + previous_year_performance_female_workers
            )

            response_data["P3_EI_9"] = {
                "Employees": {
                    "current_year_record": {
                        "total_male_employees": current_year_total_male_employees,
                        "total_female_employees": current_year_total_female_employees,
                        "total_male_female_employees": total_male_female_employees_current_year,
                        "performance_male_employees": current_year_performance_male_employees,
                        "performance_female_employees": current_year_performance_female_employees,
                        "performance_male_female_employees": performance_male_female_employees_current_year,
                        # Ratios for the current year (rounded to 2 decimal places)
                        "male_employees_ratio": (
                            round(
                                (
                                    current_year_performance_male_employees
                                    / current_year_total_male_employees
                                )
                                * 100,
                                2,
                            )
                            if current_year_total_male_employees
                            else 0
                        ),
                        "female_employees_ratio": (
                            round(
                                (
                                    current_year_performance_female_employees
                                    / current_year_total_female_employees
                                )
                                * 100,
                                2,
                            )
                            if current_year_total_female_employees
                            else 0
                        ),
                        "male_female_employees_ratio": (
                            round(
                                (
                                    performance_male_female_employees_current_year
                                    / total_male_female_employees_current_year
                                )
                                * 100,
                                2,
                            )
                            if total_male_female_employees_current_year
                            else 0
                        ),
                    },
                    "previous_year_record": {
                        "total_male_employees": previous_year_total_male_employees,
                        "total_female_employees": previous_year_total_female_employees,
                        "total_male_female_employees": total_male_female_employees_previous_year,
                        "performance_male_employees": previous_year_performance_male_employees,
                        "performance_female_employees": previous_year_performance_female_employees,
                        "performance_male_female_employees": performance_male_female_employees_previous_year,
                        # Ratios for the previous year (rounded to 2 decimal places)
                        "male_employees_ratio": (
                            round(
                                (
                                    previous_year_performance_male_employees
                                    / previous_year_total_male_employees
                                )
                                * 100,
                                2,
                            )
                            if previous_year_total_male_employees
                            else 0
                        ),
                        "female_employees_ratio": (
                            round(
                                (
                                    previous_year_performance_female_employees
                                    / previous_year_total_female_employees
                                )
                                * 100,
                                2,
                            )
                            if previous_year_total_female_employees
                            else 0
                        ),
                        "male_female_employees_ratio": (
                            round(
                                (
                                    performance_male_female_employees_previous_year
                                    / total_male_female_employees_previous_year
                                )
                                * 100,
                                2,
                            )
                            if total_male_female_employees_previous_year
                            else 0
                        ),
                    },
                },
                "Workers": {
                    "current_year_record": {
                        "total_male_workers": current_year_total_male_workers,
                        "total_female_workers": current_year_total_female_workers,
                        "total_male_female_workers": total_male_female_workers_current_year,
                        "performance_male_workers": current_year_performance_male_workers,
                        "performance_female_workers": current_year_performance_female_workers,
                        "performance_male_female_workers": performance_male_female_workers_current_year,
                        # Ratios for the current year (rounded to 2 decimal places)
                        "male_workers_ratio": (
                            round(
                                (
                                    current_year_performance_male_workers
                                    / current_year_total_male_workers
                                )
                                * 100,
                                2,
                            )
                            if current_year_total_male_workers
                            else 0
                        ),
                        "female_workers_ratio": (
                            round(
                                (
                                    current_year_performance_female_workers
                                    / current_year_total_female_workers
                                )
                                * 100,
                                2,
                            )
                            if current_year_total_female_workers
                            else 0
                        ),
                        "male_female_workers_ratio": (
                            round(
                                (
                                    performance_male_female_workers_current_year
                                    / total_male_female_workers_current_year
                                )
                                * 100,
                                2,
                            )
                            if total_male_female_workers_current_year
                            else 0
                        ),
                    },
                    "previous_year_record": {
                        "total_male_workers": previous_year_total_male_workers,
                        "total_female_workers": previous_year_total_female_workers,
                        "total_male_female_workers": total_male_female_workers_previous_year,
                        "performance_male_workers": previous_year_performance_male_workers,
                        "performance_female_workers": previous_year_performance_female_workers,
                        "performance_male_female_workers": performance_male_female_workers_previous_year,
                        # Ratios for the previous year (rounded to 2 decimal places)
                        "male_workers_ratio": (
                            round(
                                (
                                    previous_year_performance_male_workers
                                    / previous_year_total_male_workers
                                )
                                * 100,
                                2,
                            )
                            if previous_year_total_male_workers
                            else 0
                        ),
                        "female_workers_ratio": (
                            round(
                                (
                                    previous_year_performance_female_workers
                                    / previous_year_total_female_workers
                                )
                                * 100,
                                2,
                            )
                            if previous_year_total_female_workers
                            else 0
                        ),
                        "male_female_workers_ratio": (
                            round(
                                (
                                    performance_male_female_workers_previous_year
                                    / total_male_female_workers_previous_year
                                )
                                * 100,
                                2,
                            )
                            if total_male_female_workers_previous_year
                            else 0
                        ),
                    },
                },
            }

            ##################### P3 EI 11 ##############################################
            # ---------- Lost_Time_Injury_Frequency_Rate ----------------------------#
            # Fetch Lost Time Injury Frequency Rate for the current and previous financial years
            ltifr_current_year = Lost_Time_Injury_Frequency_Rate.objects.filter(
                Financial_Year=financial_year, Segment="Employees"
            )

            ltifr_previous_year = Lost_Time_Injury_Frequency_Rate.objects.filter(
                Financial_Year=previous_financial_year, Segment="Employees"
            )
            current_year_total_frequency_rate_employees = sum(
                float(record.Total_Frequency_Rate.to_decimal() or 0)
                for record in ltifr_current_year
            )
            previous_year_total_frequency_rate_employees = sum(
                float(record.Total_Frequency_Rate.to_decimal() or 0)
                for record in ltifr_previous_year
            )

            # Fetch Lost Time Injury Frequency Rate for Workers for the current financial year
            ltifr_current_year_workers = Lost_Time_Injury_Frequency_Rate.objects.filter(
                Financial_Year=financial_year, Segment="Workers"
            )
            ltifr_previous_year_workers = (
                Lost_Time_Injury_Frequency_Rate.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Workers"
                )
            )
            current_year_total_frequency_rate_workers = sum(
                float(record.Total_Frequency_Rate.to_decimal() or 0)
                for record in ltifr_current_year_workers
            )
            previous_year_total_frequency_rate_workers = sum(
                float(record.Total_Frequency_Rate.to_decimal() or 0)
                for record in ltifr_previous_year_workers
            )

            # ---------- Total_Work_Related_Injuries ----------------------------#
            injuries_current_year_employees = (
                Total_Work_Related_Injuries.objects.filter(
                    Financial_Year=financial_year, Segment="Employees"
                )
            )
            injuries_previous_year_employees = (
                Total_Work_Related_Injuries.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Employees"
                )
            )
            current_year_total_injuries_employees = sum(
                float(record.Total_Injuries_Rate.to_decimal() or 0)
                for record in injuries_current_year_employees
            )
            previous_year_total_injuries_employees = sum(
                float(record.Total_Injuries_Rate.to_decimal() or 0)
                for record in injuries_previous_year_employees
            )

            # Fetch Total Work Related Injuries for Workers for the current and previous financial years
            injuries_current_year_workers = Total_Work_Related_Injuries.objects.filter(
                Financial_Year=financial_year, Segment="Workers"
            )
            injuries_previous_year_workers = Total_Work_Related_Injuries.objects.filter(
                Financial_Year=previous_financial_year, Segment="Workers"
            )
            current_year_total_injuries_workers = sum(
                float(record.Total_Injuries_Rate.to_decimal() or 0)
                for record in injuries_current_year_workers
            )
            previous_year_total_injuries_workers = sum(
                float(record.Total_Injuries_Rate.to_decimal() or 0)
                for record in injuries_previous_year_workers
            )

            # ---------- No_Of_Fatalities ----------------------------#
            fatalities_current_year_employees = No_Of_Fatalities.objects.filter(
                Financial_Year=financial_year, Segment="Employees"
            )
            fatalities_previous_year_employees = No_Of_Fatalities.objects.filter(
                Financial_Year=previous_financial_year, Segment="Employees"
            )
            current_year_total_fatalities_employees = sum(
                float(record.Total_No_Of_Fatalities.to_decimal() or 0)
                for record in fatalities_current_year_employees
            )
            previous_year_total_fatalities_employees = sum(
                float(record.Total_No_Of_Fatalities.to_decimal() or 0)
                for record in fatalities_previous_year_employees
            )

            # Fetch No Of Fatalities for Workers for the current and previous financial years
            fatalities_current_year_workers = No_Of_Fatalities.objects.filter(
                Financial_Year=financial_year, Segment="Workers"
            )
            fatalities_previous_year_workers = No_Of_Fatalities.objects.filter(
                Financial_Year=previous_financial_year, Segment="Workers"
            )
            current_year_total_fatalities_workers = sum(
                float(record.Total_No_Of_Fatalities.to_decimal() or 0)
                for record in fatalities_current_year_workers
            )
            previous_year_total_fatalities_workers = sum(
                float(record.Total_No_Of_Fatalities.to_decimal() or 0)
                for record in fatalities_previous_year_workers
            )

            # ---------- Injury_Or_Ill_Health ----------------------------#
            injury_or_ill_health_current_year_employees = (
                Injury_Or_Ill_Health.objects.filter(
                    Financial_Year=financial_year, Segment="Employees"
                )
            )
            injury_or_ill_health_previous_year_employees = (
                Injury_Or_Ill_Health.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Employees"
                )
            )
            current_year_total_injury_or_ill_health_employees = sum(
                float(record.Total_Injury_Or_Ill_Health_Rate.to_decimal() or 0)
                for record in injury_or_ill_health_current_year_employees
            )
            previous_year_total_injury_or_ill_health_employees = sum(
                float(record.Total_Injury_Or_Ill_Health_Rate.to_decimal() or 0)
                for record in injury_or_ill_health_previous_year_employees
            )

            # Fetch Injury Or Ill Health for Workers for the current and previous financial years
            injury_or_ill_health_current_year_workers = (
                Injury_Or_Ill_Health.objects.filter(
                    Financial_Year=financial_year, Segment="Workers"
                )
            )
            injury_or_ill_health_previous_year_workers = (
                Injury_Or_Ill_Health.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Workers"
                )
            )
            current_year_total_injury_or_ill_health_workers = sum(
                float(record.Total_Injury_Or_Ill_Health_Rate.to_decimal() or 0)
                for record in injury_or_ill_health_current_year_workers
            )
            previous_year_total_injury_or_ill_health_workers = sum(
                float(record.Total_Injury_Or_Ill_Health_Rate.to_decimal() or 0)
                for record in injury_or_ill_health_previous_year_workers
            )

            response_data["P3_EI_11"] = {
                "Lost_Time_Injury_Frequency_Rate": {
                    "current_year_total_frequency_rate_employees": current_year_total_frequency_rate_employees,
                    "previous_year_total_frequency_rate_employees": previous_year_total_frequency_rate_employees,
                    "current_year_total_frequency_rate_workers": current_year_total_frequency_rate_workers,
                    "previous_year_total_frequency_rate_workers": previous_year_total_frequency_rate_workers,
                },
                "Total_Work_Related_Injuries": {
                    "current_year_total_injuries_employees": current_year_total_injuries_employees,
                    "previous_year_total_injuries_employees": previous_year_total_injuries_employees,
                    "current_year_total_injuries_workers": current_year_total_injuries_workers,
                    "previous_year_total_injuries_workers": previous_year_total_injuries_workers,
                },
                "No_Of_Fatalities": {
                    "current_year_total_fatalities_employees": current_year_total_fatalities_employees,
                    "previous_year_total_fatalities_employees": previous_year_total_fatalities_employees,
                    "current_year_total_fatalities_workers": current_year_total_fatalities_workers,
                    "previous_year_total_fatalities_workers": previous_year_total_fatalities_workers,
                },
                "Injury_Or_Ill_Health": {
                    "current_year_total_injury_or_ill_health_employees": current_year_total_injury_or_ill_health_employees,
                    "previous_year_total_injury_or_ill_health_employees": previous_year_total_injury_or_ill_health_employees,
                    "current_year_total_injury_or_ill_health_workers": current_year_total_injury_or_ill_health_workers,
                    "previous_year_total_injury_or_ill_health_workers": previous_year_total_injury_or_ill_health_workers,
                },
            }

            # Fetch Sustainable_Sourcing for the current  financial years
            Sustainable_Sourcing_current_year_record = (
                Sustainable_Sourcing.objects.filter(Financial_Year=financial_year)
            )
            current_year_total_sustainable_sourcing = sum(
                float(
                    record.Percent_of_Material_Input_Sustainably_Sourced.to_decimal()
                    or 0
                )
                for record in Sustainable_Sourcing_current_year_record
            )

            if current_year_total_sustainable_sourcing:
                response_data["P2_EI_2"] = [current_year_total_sustainable_sourcing]
            else:
                response_data["P2_EI_2"] = ["NA"]

            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except APIException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError as e:
            return Response(
                {"error": f"TypeError: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SectionAView(APIView):
    def get(self, request):
        try:
            financial_year = request.query_params.get("financial_year", None)

            if financial_year is None:
                return Response(
                    {"error": "financial_year parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            start_year = int(financial_year[2:6])
            previous_financial_year = f"FY{start_year-1}-{start_year}"
           
            response_data = {}

            company_profile_object = Company_Profile.objects.first()
            # print("company_profile_object:",model_to_dict(company_profile_object),"-----------")

            obj_paid = Paid_up_Capital.objects.filter(
                Financial_Year=financial_year
            ).first()

            business_activity_details_obj = Business_Activity_Details.objects.all()

            if business_activity_details_obj:
                business_activity_details_list = list(
                    business_activity_details_obj.values(
                        "Name_of_Business_Activity", "Description"
                    )
                )

                for elem in business_activity_details_list:
                    business_activity_obj = Business_Activity.objects.filter(
                        Financial_Year=financial_year
                    ).values("Total_Percent_Turnover", "Business_Activity_and_Turnover")

                    if business_activity_obj:
                        activities = business_activity_obj[0].get(
                            "Business_Activity_and_Turnover", []
                        )
                        found = False

                        for activity in activities:
                            if activity.get("Business_Activity") == elem.get(
                                "Name_of_Business_Activity"
                            ):  # Match with 'Business_Activity_and_Turnover'
                                elem["Percent_Turnover"] = activity.get(
                                    "Percent_Turnover", 0
                                )
                                found = True
                                break

                        if not found:
                            elem["Percent_Turnover"] = 0
                    else:
                        elem["Percent_Turnover"] = 0
            else:
                business_activity_details_list = [
                    {
                        "Name_of_Business_Activity": "-",
                        "Description": "-",
                        "Percent_Turnover": "",
                    }
                ]

            products_services_details_obj = Products_Services_Details.objects.all()

            if products_services_details_obj:
                products_services_details_list = list(
                    products_services_details_obj.values(
                        "Name_of_Product_Service", "NIC_Code"
                    )
                )

                for elem in products_services_details_list:
                    product_service_obj = Products_Services.objects.filter(
                        Financial_Year=financial_year
                    ).values("Total_Percent_Turnover", "Products_Services_and_Turnover")

                    if product_service_obj:
                        activities = product_service_obj[0].get(
                            "Products_Services_and_Turnover", []
                        )
                        found = False

                        for activity in activities:
                            if activity.get("Product_Service") == elem.get(
                                "Name_of_Product_Service"
                            ):
                                elem["Percent_Turnover"] = activity.get(
                                    "Percent_Turnover", 0
                                )
                                found = True
                                break

                        if not found:
                            elem["Percent_Turnover"] = 0
                    else:
                        elem["Percent_Turnover"] = 0
            else:
                products_services_details_list = [
                    {
                        "Name_of_Product_Service": "-",
                        "NIC_Code": "-",
                        "Percent_Turnover": 0,
                    }
                ]

            # Section a EI 18
            try:
                offices_and_plants_obj = Offices_and_Plants.objects.get(
                    Financial_Year=financial_year
                )

                no_of_national_plants = offices_and_plants_obj.No_of_National_Plants
                no_of_national_offices = offices_and_plants_obj.No_of_National_Offices
                no_of_international_plants = (
                    offices_and_plants_obj.No_of_International_Plants
                )
                no_of_international_offices = (
                    offices_and_plants_obj.No_of_International_Offices
                )

                total_national_offices_plants = (
                    no_of_national_plants + no_of_national_offices
                )
                total_international_offices_plants = (
                    no_of_international_plants + no_of_international_offices
                )
            except Offices_and_Plants.DoesNotExist:
                no_of_national_plants = no_of_national_offices = (
                    no_of_international_plants
                ) = no_of_international_offices = "-"
                total_national_offices_plants = total_international_offices_plants = "-"

            markets_served_obj = Markets_Served.objects.values(
                "National_No_of_States", "International_No_of_Countries"
            )

            if not markets_served_obj:  # If markets_served_obj is empty
                markets_served_data = [
                    {"National_No_of_States": "-", "International_No_of_Countries": "-"}
                ]
            else:
                markets_served_data = [
                    {
                        "National_No_of_States": (
                            item["National_No_of_States"]
                            if item["National_No_of_States"]
                            else "-"
                        ),
                        "International_No_of_Countries": (
                            item["International_No_of_Countries"]
                            if item["International_No_of_Countries"]
                            else "-"
                        ),
                    }
                    for item in markets_served_obj
                ]

            exports_obj = Exports.objects.filter(Financial_Year=financial_year).first()

            description_obj_d = Descriptions.objects.filter(
                Heading="type_of_customer"
            ).first()

            employee_summary_json = calculate_section_A_20_a_employees_data(
                financial_year
            )

            worker_summary_json = calculate_section_A_20_a_workers_data(financial_year)

            diff_abled_emp_json = (
                calculate_section_A_20_b_differently_abled_employees_data(
                    financial_year
                )
            )

            diff_abled_workers_json = (
                calculate_section_A_20_b_differently_abled_workers_data(financial_year)
            )

            management_json = calculate_section_A_21_Management(financial_year)

            employee_json = calculate_section_A_22_Management(financial_year)

            worker_json = calculate_section_A_22_Worker(financial_year)

            holdings_obj = Holdings.objects.values(
                "Name_of_Holding",
                "Type_of_Holding",
                "Percent_of_Share_Held",
                "Participates_in_Business_Responsibility",
            )

            if not holdings_obj:  # If holdings_obj is empty
                holdings_data = [
                    {
                        "Name_of_Holding": "-",
                        "Type_of_Holding": "-",
                        "Percent_of_Share_Held": "-",
                        "Participates_in_Business_Responsibility": "-",
                    }
                ]
            else:
                holdings_data = []
                for item in holdings_obj:
                    percent_of_share_held = item["Percent_of_Share_Held"]

                    # Convert Decimal128 or Decimal to string for serialization
                    if isinstance(percent_of_share_held, Decimal128):
                        percent_of_share_held = str(percent_of_share_held.to_decimal())
                    elif isinstance(percent_of_share_held, Decimal):
                        percent_of_share_held = str(percent_of_share_held)
                    elif not percent_of_share_held:
                        percent_of_share_held = "-"

                    participates_value = item["Participates_in_Business_Responsibility"]

                    # Assuming you want to represent null values as "-"
                    if participates_value in [None, ""]:
                        participates_status = "-"
                    else:
                        participates_status = participates_value  # Will take the string value (e.g., "Yes" or "No")

                    holdings_data.append(
                        {
                            "Name_of_Holding": (
                                item["Name_of_Holding"]
                                if item["Name_of_Holding"]
                                else "-"
                            ),
                            "Type_of_Holding": (
                                item["Type_of_Holding"]
                                if item["Type_of_Holding"]
                                else "-"
                            ),
                            "Percent_of_Share_Held": percent_of_share_held,
                            "Participates_in_Business_Responsibility": participates_status,
                        }
                    )

            turnover_obj = Turnover.objects.filter(
                Financial_Year=financial_year
            ).first()

            networth_obj = Networth.objects.filter(
                Financial_Year=financial_year
            ).first()

            material_obj = Material_Business_Conduct_Issue.objects.filter(
                Financial_Year=financial_year
            ).values(
                "Material_Issue_Identified",
                "Risk_or_Opportunity",
                "Rationale_for_Identification",
                "Approach_to_Adapt_or_Mitigate",
                "Positive_and_Negative_Financial_Implications",
            )

            if not material_obj:  # If material_obj is empty
                material_data = [
                    {
                        "Material_Issue_Identified": "-",
                        "Risk_or_Opportunity": "-",
                        "Rationale_for_Identification": "-",
                        "Approach_to_Adapt_or_Mitigate": "-",
                        "Positive_and_Negative_Financial_Implications": "-",
                    }
                ]
            else:
                material_data = [
                    {
                        "Material_Issue_Identified": (
                            item["Material_Issue_Identified"]
                            if item["Material_Issue_Identified"]
                            else "-"
                        ),
                        "Risk_or_Opportunity": (
                            item["Risk_or_Opportunity"]
                            if item["Risk_or_Opportunity"]
                            else "-"
                        ),
                        "Rationale_for_Identification": (
                            item["Rationale_for_Identification"]
                            if item["Rationale_for_Identification"]
                            else "-"
                        ),
                        "Approach_to_Adapt_or_Mitigate": (
                            item["Approach_to_Adapt_or_Mitigate"]
                            if item["Approach_to_Adapt_or_Mitigate"]
                            else "-"
                        ),
                        "Positive_and_Negative_Financial_Implications": (
                            item["Positive_and_Negative_Financial_Implications"]
                            if item["Positive_and_Negative_Financial_Implications"]
                            else "-"
                        ),
                    }
                    for item in material_obj
                ]

            firstname = request.user.firstname
            lastname = request.user.lastname

            # Retrieve the phone extension and phone number
            phone_number = request.user.phone_number or "No Contact Provided"
            phone_ext = getattr(
                request.user, "phone_extension", "No Extension Provided"
            )  # Use 'getattr' to handle cases where 'phone_ext' may not exist

            # Combine phone extension and phone number
            contact_info = f"{phone_ext} - {phone_number}"

            # List of values to populate the dictionary
            section_data_values = [
                f"{firstname} {lastname}",  # Name
                contact_info,  # Contact
                request.user.email or "No Email Provided",  # Email
            ]

            # List of constant keys
            section_data_keys = ["Name", "Contact", "Email"]

            # Use zip to create a dictionary from keys and values
            section_a_12_data = dict(zip(section_data_keys, section_data_values))
            
            # $$$$$$$$$$$$$$$$$$$$$$$$ section A EI_25 $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
            stack_holder_group = [
                "Investors",
                "Shareholders",
                "Customers",
                "Communities",
                "Employees And Workers",
                "Value Chain Partners",
                "Others",
            ]

            Transparency_current_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=financial_year, Stack_Holder_Group="Investors"
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                )
            )

            first_record = {
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
                }
            if Transparency_current_year_record:
                first_record['Field_Complaint'] = Transparency_current_year_record[0]['Field_Complaint']
                first_record['Pending_Complaint'] = Transparency_current_year_record[0]['Pending_Complaint']
                first_record['Remarks'] = Transparency_current_year_record[0]['Remarks']
                first_record['grievance_redressal_mechanism_in_place'] = Transparency_current_year_record[0]['grievance_redressal_mechanism_in_place']
                
                

        

            # Fetch previous year records for Investors
            Transparency_previous_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=previous_financial_year,
                    Stack_Holder_Group="Investors",
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                    # "Weblink",
                )
            )
            
            second_record = {
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
                    # "Weblink": "-",
            }
            
            if Transparency_previous_year_record:
                second_record['Field_Complaint'] = Transparency_previous_year_record[0]['Field_Complaint']
                second_record['Pending_Complaint'] = Transparency_previous_year_record[0]['Pending_Complaint']
                second_record['Remarks'] = Transparency_previous_year_record[0]['Remarks']
                second_record['grievance_redressal_mechanism_in_place'] = Transparency_previous_year_record[0]['grievance_redressal_mechanism_in_place']
                
            
            # ----------------------------------------------------------------------- #
            # Fetch current year records for Shareholders
            Shareholders_current_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=financial_year, Stack_Holder_Group="Shareholders"
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                    
                )
            )
            Shareholders_first_record = {
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
            }
            

            if Shareholders_current_year_record:
                Shareholders_first_record['Field_Complaint'] = Shareholders_current_year_record[0]['Field_Complaint']
                Shareholders_first_record['Pending_Complaint'] = Shareholders_current_year_record[0]['Pending_Complaint']
                Shareholders_first_record['Remarks'] = Shareholders_current_year_record[0]['Remarks']
                Shareholders_first_record['grievance_redressal_mechanism_in_place'] = Shareholders_current_year_record[0]['grievance_redressal_mechanism_in_place']
                
                
                
                
           
            
            Shareholders_previous_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=previous_financial_year,
                    Stack_Holder_Group="Shareholders",
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                    # "Weblink",
                )
            )
            shareholders_second_record = {
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
                    
                
            }
            

            if Shareholders_previous_year_record:
                
                
                shareholders_second_record['Field_Complaint'] = Shareholders_previous_year_record[0]['Field_Complaint']
                shareholders_second_record['Pending_Complaint'] = Shareholders_previous_year_record[0]['Pending_Complaint']
                shareholders_second_record['Remarks'] = Shareholders_previous_year_record[0]['Remarks']
                shareholders_second_record['grievance_redressal_mechanism_in_place'] = Shareholders_previous_year_record[0]['grievance_redressal_mechanism_in_place']
                   
            # ----------------------------------------------------------------------- #

            # Fetch current year records for Customers
            Customers_current_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=financial_year, Stack_Holder_Group="Customers"
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                    # "Weblink",
                )
            )
            customers_first_record ={
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
                    # "Weblink": "-",
            }

            if Customers_current_year_record:
                # Use 'or "-"' to replace None values with "-"
                
                customers_first_record['Field_Complaint'] = Customers_current_year_record[0]['Field_Complaint']
                customers_first_record['Pending_Complaint'] = Customers_current_year_record[0]['Pending_Complaint']
                customers_first_record['Remarks'] = Customers_current_year_record[0]['Remarks']
                customers_first_record['grievance_redressal_mechanism_in_place'] = Customers_current_year_record[0]['grievance_redressal_mechanism_in_place']
                

            # Fetch previous year records for Customers
            Customers_previous_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=previous_financial_year,
                    Stack_Holder_Group="Customers",
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                    # "Weblink",
                )
            )
            customers_second_record ={
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
                    # "Weblink": "-",
            }

            if Customers_previous_year_record:
                # Use 'or "-"' to replace None values with "-"
                 
                customers_second_record['Field_Complaint'] = Customers_previous_year_record[0]['Field_Complaint']
                customers_second_record['Pending_Complaint'] = Customers_previous_year_record[0]['Pending_Complaint']
                customers_second_record['Remarks'] = Customers_previous_year_record[0]['Remarks']
                customers_second_record['grievance_redressal_mechanism_in_place'] = Customers_previous_year_record[0]['grievance_redressal_mechanism_in_place']
                

            # ----------------------------------------------------------------------- #
            
            Communities_current_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=financial_year, Stack_Holder_Group="Communities"
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                    # "Weblink",
                )
            )
            communities_first_record = {
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
                }
            
            if Communities_current_year_record:
                 
                communities_first_record['Field_Complaint'] = Communities_current_year_record[0]['Field_Complaint']
                communities_first_record['Pending_Complaint'] = Communities_current_year_record[0]['Pending_Complaint']
                communities_first_record['Remarks'] = Communities_current_year_record[0]['Remarks']
                communities_first_record['grievance_redressal_mechanism_in_place'] = Communities_current_year_record[0]['grievance_redressal_mechanism_in_place']
                
            # Fetch previous year records for Communities
            Communities_previous_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=previous_financial_year,
                    Stack_Holder_Group="Communities",
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                    "Weblink",
                )
            )
            communities_second_record ={
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
                    # "Weblink": "-",
            }
            

            if Communities_previous_year_record:
                communities_second_record['Field_Complaint'] = Communities_previous_year_record[0]['Field_Complaint']
                communities_second_record['Pending_Complaint'] = Communities_previous_year_record[0]['Pending_Complaint']
                communities_second_record['Remarks'] = Communities_previous_year_record[0]['Remarks']
                communities_second_record['grievance_redressal_mechanism_in_place'] = Communities_previous_year_record[0]['grievance_redressal_mechanism_in_place']
                

            # ----------------------------------------------------------------------- #

            # Fetch current year records for Employees And Workers
            Employees_and_Workers_current_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=financial_year,
                    Stack_Holder_Group="Employees And Workers",
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                    # "Weblink",
                )
            )
            employees_and_workers_first_record ={
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
                }

            if Employees_and_Workers_current_year_record:
                # Use 'or "-"' to replace None values with "-"
                employees_and_workers_first_record['Field_Complaint'] = Employees_and_Workers_current_year_record[0]['Field_Complaint']
                employees_and_workers_first_record['Pending_Complaint'] = Employees_and_Workers_current_year_record[0]['Pending_Complaint']
                employees_and_workers_first_record['Remarks'] = Employees_and_Workers_current_year_record[0]['Remarks']
                employees_and_workers_first_record['grievance_redressal_mechanism_in_place'] = Employees_and_Workers_current_year_record[0]['grievance_redressal_mechanism_in_place']
                

            # Fetch previous year records for Employees And Workers
            Employees_and_Workers_previous_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=previous_financial_year,
                    Stack_Holder_Group="Employees And Workers",
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                    # "Weblink",
                )
            )
            employees_and_workers_second_record ={
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
                    # "Weblink": "-",
            }

            if Employees_and_Workers_previous_year_record:
                # Use 'or "-"' to replace None values with "-"
                employees_and_workers_second_record['Field_Complaint'] = Employees_and_Workers_previous_year_record[0]['Field_Complaint']
                employees_and_workers_second_record['Pending_Complaint'] = Employees_and_Workers_previous_year_record[0]['Pending_Complaint']
                employees_and_workers_second_record['Remarks'] = Employees_and_Workers_previous_year_record[0]['Remarks']
                employees_and_workers_second_record['grievance_redressal_mechanism_in_place'] = Employees_and_Workers_previous_year_record[0]['grievance_redressal_mechanism_in_place']
                
            # Fetch current year records for Value Chain Partners
            Value_Chain_Partners_current_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=financial_year,
                    Stack_Holder_Group="Value Chain Partners",
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                    # "Weblink",
                )
            )
            value_chain_partners_first_record =  {
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
                }

            if Value_Chain_Partners_current_year_record:
                # Use 'or "-"' to replace None values with "-"
                value_chain_partners_first_record['Field_Complaint'] = Value_Chain_Partners_current_year_record[0]['Field_Complaint']
                value_chain_partners_first_record['Pending_Complaint'] = Value_Chain_Partners_current_year_record[0]['Pending_Complaint']
                value_chain_partners_first_record['Remarks'] = Value_Chain_Partners_current_year_record[0]['Remarks']
                value_chain_partners_first_record['grievance_redressal_mechanism_in_place'] = Value_Chain_Partners_current_year_record[0]['grievance_redressal_mechanism_in_place']
                

            # Fetch previous year records for Value Chain Partners
            Value_Chain_Partners_previous_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=previous_financial_year,
                    Stack_Holder_Group="Value Chain Partners",
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                    # "Weblink",
                )
            )
            value_chain_partners_second_record =  {
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
                }

            if Value_Chain_Partners_previous_year_record:
                # Use 'or "-"' to replace None values with "-"
                value_chain_partners_second_record ['Field_Complaint'] = Value_Chain_Partners_previous_year_record[0]['Field_Complaint']
                value_chain_partners_second_record ['Pending_Complaint'] = Value_Chain_Partners_previous_year_record[0]['Pending_Complaint']
                value_chain_partners_second_record ['Remarks'] = Value_Chain_Partners_previous_year_record[0]['Remarks']
                value_chain_partners_second_record ['grievance_redressal_mechanism_in_place'] = Value_Chain_Partners_previous_year_record[0]['grievance_redressal_mechanism_in_place']
                

            # ----------------------------------------------------------------------- #

            # Fetch current year records for Others
            Others_current_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=financial_year, Stack_Holder_Group="Others"
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                    # "Weblink",
                )
            )
            others_first_record = {
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
                }

            if Others_current_year_record:
                others_first_record['Field_Complaint'] = Others_current_year_record[0]['Field_Complaint']
                others_first_record['Pending_Complaint'] = Others_current_year_record[0]['Pending_Complaint']
                others_first_record['Remarks'] = Others_current_year_record[0]['Remarks']
                others_first_record['grievance_redressal_mechanism_in_place'] = Others_current_year_record[0]['grievance_redressal_mechanism_in_place']
                

            # Fetch previous year records for Others
            Others_previous_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=previous_financial_year, Stack_Holder_Group="Others"
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                    # "Weblink",
                )
            )
            others_second_record = {
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
                    # "Weblink": "-",
            }

            if Others_previous_year_record:
                others_second_record['Field_Complaint'] = Others_previous_year_record[0]['Field_Complaint']
                others_second_record['Pending_Complaint'] = Others_previous_year_record[0]['Pending_Complaint']
                others_second_record['Remarks'] = Others_previous_year_record[0]['Remarks']
                others_second_record['grievance_redressal_mechanism_in_place'] = Others_previous_year_record[0]['grievance_redressal_mechanism_in_place']
                
            
            # -------------------------------------Suppliers----------------------------------------------- #

            # Fetch current year records for Others
            Suppliers_current_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=financial_year, Stack_Holder_Group="suppliers"
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                    # "Weblink",
                )
            )
            suppliers_first_record = {
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
                }

            if Suppliers_current_year_record:
                suppliers_first_record['Field_Complaint'] = Suppliers_current_year_record[0]['Field_Complaint']
                suppliers_first_record['Pending_Complaint'] = Suppliers_current_year_record[0]['Pending_Complaint']
                suppliers_first_record['Remarks'] = Suppliers_current_year_record[0]['Remarks']
                suppliers_first_record['grievance_redressal_mechanism_in_place'] = Suppliers_current_year_record[0]['grievance_redressal_mechanism_in_place']
                

            # Fetch previous year records for Suppliers
            Suppliers_previous_year_record = (
                TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=previous_financial_year, Stack_Holder_Group="suppliers"
                ).values(
                    "Field_Complaint",
                    "Pending_Complaint",
                    "Remarks",
                    "grievance_redressal_mechanism_in_place",
                    # "Weblink",
                )
            )
            suppliers_second_record = {
                    "Field_Complaint": 0,
                    "Pending_Complaint": 0,
                    "Remarks": "-",
                    "grievance_redressal_mechanism_in_place": "-",
                    # "Weblink": "-",
            }

            if Suppliers_previous_year_record:
                suppliers_second_record['Field_Complaint'] = Suppliers_previous_year_record[0]['Field_Complaint']
                suppliers_second_record['Pending_Complaint'] = Suppliers_previous_year_record[0]['Pending_Complaint']
                suppliers_second_record['Remarks'] = Suppliers_previous_year_record[0]['Remarks']
                suppliers_second_record['grievance_redressal_mechanism_in_place'] = Suppliers_previous_year_record[0]['grievance_redressal_mechanism_in_place']
                
            
            # ----------------------------------------------------------------------- #

            # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

            response_data = {
                "Section_A": {
                    "Section_A_1": [
                        {
                            "CIN": (
                                company_profile_object.CIN
                                if company_profile_object
                                else "-"
                            )
                        }
                    ],
                    "Section_A_2": [
                        {
                            "Company_Name": (
                                company_profile_object.Company_Name
                                if company_profile_object
                                else "-"
                            )
                        }
                    ],
                    "Section_A_3": [
                        {
                            "Year_of_Incorporation": (
                                company_profile_object.Year_of_Incorporation
                                if company_profile_object
                                else "-"
                            )
                        }
                    ],
                    "Section_A_4": [
                        {
                            "Registered_Office_Address_Line1": (
                                (
                                    f"{company_profile_object.Registered_Office_Address_Line1}, {company_profile_object.Registered_Office_Address_Line2}, {company_profile_object.Registered_Office_Pincode}"
                                )
                                if company_profile_object
                                else "-"
                            )
                        }
                    ],
                    "Section_A_5": [
                        {
                            "Corporate_Office_Address_Line1": (
                                (
                                    f"{company_profile_object.Corporate_Office_Address_Line1}, {company_profile_object.Corporate_Office_Address_Line2}, {company_profile_object.Corporate_Office_Pincode}"
                                )
                                if company_profile_object
                                else "-"
                            )
                        }
                    ],
                    "Section_A_6": [
                        {
                            "Email": (
                                company_profile_object.Email
                                if company_profile_object
                                else "-"
                            )
                        }
                    ],
                    "Section_A_7": [
                        {
                            "Phone_Ext_Phone_Number": (
                                (
                                    company_profile_object.Phone_Ext
                                    + "-"
                                    + str(company_profile_object.Phone_Number)
                                )
                                if company_profile_object
                                else "-"
                            )
                        }
                    ],
                    "Section_A_8": [
                        {
                            "Website": (
                                company_profile_object.Website
                                if company_profile_object
                                else "-"
                            )
                        }
                    ],
                    "Section_A_9": [
                        {"financial_year": financial_year if financial_year else "-"}
                    ],
                    "Section_A_10": [
                        {
                            "Shares_Listed_On": (
                                company_profile_object.Shares_Listed_On
                                if company_profile_object
                                else "-"
                            )
                        }
                    ],
                    "Section_A_11": [
                        {
                            "Paid_up_Capital": (
                                f"{float(obj_paid.Paid_up_Capital.to_decimal())} {obj_paid.Paid_Up_Capital_Unit}"
                                if obj_paid
                                else "-"
                            )
                        }
                    ],
                    "Section_A_12": [section_a_12_data],
                    "Section_A_13": [
                        {
                            "Reporting_Boundary": (
                                company_profile_object.Reporting_Boundary
                                if company_profile_object
                                else "-"
                            )
                        }
                    ],  # Assurance Provider
                    "Section_A_14": [
                        {
                            "Name_of_Assurance_Provider": (
                                company_profile_object.Name_of_Assurance_Provider
                                if company_profile_object
                                else "-"
                            )
                        }
                    ],  # Reporting Boundary
                    "Section_A_15": [
                        {
                            "Type_Of_Assurance": (
                                company_profile_object.Type_Of_Assurance
                                if company_profile_object
                                else "-"
                            )
                        }
                    ],
                    "Section_A_16": (
                        business_activity_details_list
                        if business_activity_details_list
                        else ["-"]
                    ),
                    "Section_A_17": (
                        products_services_details_list
                        if products_services_details_list
                        else ["-"]
                    ),
                    "Section_A_18_National": [
                        {
                            "no_of_national_plants": (
                                no_of_national_plants
                                if no_of_national_plants is not None
                                else "-"
                            ),
                            "no_of_national_offices": (
                                no_of_national_offices
                                if no_of_national_offices is not None
                                else "-"
                            ),
                            "total_national_offices_plants": (
                                total_national_offices_plants
                                if total_national_offices_plants is not None
                                else "-"
                            ),
                        }
                    ],
                    "Section_A_18_International": [
                        {
                            "no_of_international_plants": (
                                no_of_international_plants
                                if no_of_international_plants is not None
                                else "-"
                            ),
                            "no_of_international_offices": (
                                no_of_international_offices
                                if no_of_international_offices is not None
                                else "-"
                            ),
                            "total_international_offices_plants": (
                                total_international_offices_plants
                                if total_international_offices_plants is not None
                                else "-"
                            ),
                        }
                    ],
                    "Section_A_19_National": [
                        {
                            "National_No_of_States": (
                                item["National_No_of_States"]
                                if item["National_No_of_States"]
                                else "-"
                            )
                            for item in markets_served_data
                        }
                    ],
                    "Section_A_19_International": [
                        {
                            "International_No_of_Countries": (
                                item["International_No_of_Countries"]
                                if item["International_No_of_Countries"]
                                else "-"
                            )
                            for item in markets_served_data
                        }
                    ],
                    "Section_A_19_b": [
                        {
                            "Contribution_of_Turnover": (
                                float(exports_obj.Contribution_of_Turnover.to_decimal())
                                if exports_obj
                                else 0
                            )
                        }
                    ],
                    "Section_A_19_c": [
                        {
                            "Description": (
                                description_obj_d.Description
                                if description_obj_d
                                else "-"
                            )
                        }
                    ],
                    "Section_A_20_a_Employees": [
                        employee_summary_json if employee_summary_json else "-"
                    ],
                    "Section_A_20_a_Workers": [
                        worker_summary_json if worker_summary_json else "-"
                    ],
                    "Section_A_20_b_Diff_Abled_Employees": [
                        diff_abled_emp_json if diff_abled_emp_json else "-"
                    ],
                    "Section_A_20_b_Diff_Abled_Workers": [
                        diff_abled_workers_json if diff_abled_workers_json else "-"
                    ],
                    "Section_A_21_Management": [
                        management_json if management_json else "-"
                    ],
                    "Section_A_22_Permanent_Emp": (
                        employee_json if employee_json else ["-"]
                    ),
                    "Section_A_22_Permanent_Wkr": worker_json if worker_json else ["-"],
                    "Section_A_23": holdings_data if holdings_data else "-",
                    "Section_A_24_1": [
                        {
                            "CSR_Applicable": (
                                company_profile_object.CSR_Applicable
                                if company_profile_object
                                else "-"
                            )
                        }
                    ],
                    "Section_A_24_2": [
                        {
                            "Total_Turnover": (
                                float(turnover_obj.Total_Turnover.to_decimal())
                                if turnover_obj
                                else "-"
                            )
                        }
                    ],
                    "Section_A_24_3": [
                        {
                            "Total_Networth": (
                                float(networth_obj.Total_Networth.to_decimal())
                                if networth_obj
                                else "-"
                            )
                        }
                    ],
                    
                    "Section_A_25_Com": [
                        {
                            "Field_Complaint_current": communities_first_record["Field_Complaint"],
                            "grievance_redressal_mechanism_in_place_current": communities_first_record["grievance_redressal_mechanism_in_place"],
                            "Pending_Complaint_current": communities_first_record["Pending_Complaint"],
                            "Remarks_current": communities_first_record["Remarks"],
                            "Field_Complaint_previous": communities_second_record["Field_Complaint"],
                            "Pending_Complaint_previous": communities_second_record["Pending_Complaint"],
                            "Remarks_previous": communities_second_record["Remarks"],
                       
                        }
                    ],
                    "Section_A_25_Inv": [
                        {
                            "Field_Complaint_current": first_record["Field_Complaint"],
                            "grievance_redressal_mechanism_in_place_current": first_record["grievance_redressal_mechanism_in_place"],
                            "Pending_Complaint_current": first_record["Pending_Complaint"],
                            "Remarks_current": first_record["Remarks"],
                            "Field_Complaint_previous": second_record["Field_Complaint"],
                            "Pending_Complaint_previous": second_record["Pending_Complaint"],
                            "Remarks_previous": second_record["Remarks"],
                        }
                    ],
                    "Section_A_25_Share": [
                        {
                           "Field_Complaint_current": Shareholders_first_record["Field_Complaint"],
                            "grievance_redressal_mechanism_in_place_current": Shareholders_first_record["grievance_redressal_mechanism_in_place"],
                            "Pending_Complaint_current": Shareholders_first_record["Pending_Complaint"],
                            "Remarks_current": Shareholders_first_record["Remarks"],
                            "Field_Complaint_previous": shareholders_second_record["Field_Complaint"],
                            "Pending_Complaint_previous": shareholders_second_record["Pending_Complaint"],
                            "Remarks_previous": shareholders_second_record["Remarks"],
                       
                            
                        }
                    ],
                    "Section_A_25_Emp": [
                        {
                            "Field_Complaint_current": employees_and_workers_first_record["Field_Complaint"],
                            "grievance_redressal_mechanism_in_place_current": employees_and_workers_first_record["grievance_redressal_mechanism_in_place"],
                            "Pending_Complaint_current": employees_and_workers_first_record["Pending_Complaint"],
                            "Remarks_current": employees_and_workers_first_record["Remarks"],
                            "Field_Complaint_previous": employees_and_workers_second_record["Field_Complaint"],
                            "Pending_Complaint_previous": employees_and_workers_second_record["Pending_Complaint"],
                            "Remarks_previous": employees_and_workers_second_record["Remarks"],
                           }
                    ],
                    "Section_A_25_Cus": [
                        {
                            "Field_Complaint_current": customers_first_record["Field_Complaint"],
                            "grievance_redressal_mechanism_in_place_current": customers_first_record["grievance_redressal_mechanism_in_place"],
                            "Pending_Complaint_current": customers_first_record["Pending_Complaint"],
                            "Remarks_current": customers_first_record["Remarks"],
                            "Field_Complaint_previous": customers_second_record["Field_Complaint"],
                            "Pending_Complaint_previous": customers_second_record["Pending_Complaint"],
                            "Remarks_previous": customers_second_record["Remarks"],
                     
                        }
                    ],
                    "Section_A_25_Value": [
                        {
                            "Field_Complaint_current": value_chain_partners_first_record["Field_Complaint"],
                            "grievance_redressal_mechanism_in_place_current": value_chain_partners_first_record["grievance_redressal_mechanism_in_place"],
                            "Pending_Complaint_current": value_chain_partners_first_record["Pending_Complaint"],
                            "Remarks_current": value_chain_partners_first_record["Remarks"],
                            "Field_Complaint_previous": value_chain_partners_second_record["Field_Complaint"],
                            "Pending_Complaint_previous": value_chain_partners_second_record["Pending_Complaint"],
                            "Remarks_previous": value_chain_partners_second_record["Remarks"],
                    
                        }
                    ],
                    "Section_A_25_Other": [
                        {
                          "Field_Complaint_current": others_first_record["Field_Complaint"],
                            "grievance_redressal_mechanism_in_place_current": others_first_record["grievance_redressal_mechanism_in_place"],
                            "Pending_Complaint_current": others_first_record["Pending_Complaint"],
                            "Remarks_current": others_first_record["Remarks"],
                            "Field_Complaint_previous": others_second_record["Field_Complaint"],
                            "Pending_Complaint_previous": others_second_record["Pending_Complaint"],
                            "Remarks_previous": others_second_record["Remarks"],
                     
                            
                        }
                    ],
                    "Section_A_25_Suppliers": [
                        {
                          "Field_Complaint_current": suppliers_first_record["Field_Complaint"],
                            "grievance_redressal_mechanism_in_place_current": suppliers_first_record["grievance_redressal_mechanism_in_place"],
                            "Pending_Complaint_current": suppliers_first_record["Pending_Complaint"],
                            "Remarks_current": suppliers_first_record["Remarks"],
                            "Field_Complaint_previous": suppliers_second_record["Field_Complaint"],
                            "Pending_Complaint_previous": suppliers_second_record["Pending_Complaint"],
                            "Remarks_previous": suppliers_second_record["Remarks"],
                     
                            
                        }
                    ],
                    
                    "Section_A_26": material_data if material_data else "-",
                }
            }

            Brs_log = {
                "Financial_Year":financial_year,
                "Section":"Section-A",
                "User_Name":f"{request.user.firstname} {request.user.lastname}"
               
            }
                            
            brs_log_serializer = BRS_Report_LogSerializer(data=Brs_log)
            if brs_log_serializer.is_valid():
                brs_log_serializer.save()
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Data Not Available in Section A"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except APIException as e:
            return Response(
                {"error": f"APIException in Section A: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # except TypeError as e:
        #     return Response({'error': f'TypeError in Section A: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Unknown error in Section A: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SectionBView(APIView):

    def get(self, request):

        try:
            financial_year =  request.query_params.get("financial_year")
           
            description_obj = BRS_Policy_1.objects.filter(
                Model_Name__iexact="Principle_Core_Elements_NGRBC"
            ).first()
            section_b_1a = (
                [getattr(description_obj, f"P{i}", "NA") for i in range(1, 10)]
                if description_obj
                else ["-"] * 9
            )

            description_obj = BRS_Policy_1.objects.filter(
                Model_Name__iexact="Policy_Approved_by_Board"
            ).first()
            section_b_1b = (
                [getattr(description_obj, f"P{i}", "NA") for i in range(1, 10)]
                if description_obj
                else ["-"] * 9
            )

            description_obj = BRS_Policy_1.objects.filter(
                Model_Name="Web_Link_Policies"
            ).first()
            section_b_1c = description_obj.Description.split(", ") if description_obj and description_obj.Description else ["-"]

            description_obj = BRS_Policy_1.objects.filter(
                Model_Name="Policy_into_Procedures"
            ).first()
            section_b_2 = (
                [getattr(description_obj, f"P{i}", "NA") for i in range(1, 10)]
                if description_obj
                else ["-"] * 9
            )

            description_obj = BRS_Policy_1.objects.filter(
                Model_Name="Policies_Extend_Value_Chain_Partners"
            ).first()
            section_b_3 = (
                [getattr(description_obj, f"P{i}", "NA") for i in range(1, 10)]
                if description_obj
                else ["-"] * 9
            )

            description_obj = BRS_Policy_1.objects.filter(
                Model_Name="Name_of_National_International_Codes"
            ).first()
            section_b_4 = description_obj.Description if description_obj else "-"

            description_obj = BRS_Policy_1.objects.filter(
                Model_Name="Specific_Commitments_Goals_Targets"
            ).first()
            section_b_5 = description_obj.Description if description_obj else "-"

            description_obj = BRS_Policy_1.objects.filter(
                Model_Name="Performance_of_Entity_with_reasons"
            ).first()
            section_b_6 = description_obj.Description if description_obj else "-"

            description_obj = BRS_Policy_2.objects.filter(
                Model_Name="Statement_by_Director"
            ).first()
            section_b_7 = description_obj.Description if description_obj else "-"

            description_obj = BRS_Policy_2.objects.filter(
                Model_Name="Details_Highest_Authority"
            ).first()
            section_b_8 = description_obj.Description if description_obj else "-"

            description_obj = BRS_Policy_2.objects.filter(
                Model_Name="Entity_Specified_Commitee"
            ).first()
            section_b_9 = description_obj.Description if description_obj else "-"

            description_obj = BRS_Policy_2.objects.filter(
                Model_Name="Performance_Entities"
            ).first()
            section_b_10a = (
                [getattr(description_obj, f"P{i}", "NA") for i in range(1, 10)]
                if description_obj
                else ["NA"] * 9
            )

            description_obj = BRS_Policy_2.objects.filter(
                Model_Name="Compliance_Statutory_Requirements"
            ).first()
            section_b_10b = (
                [getattr(description_obj, f"P{i}", "NA") for i in range(1, 10)]
                if description_obj
                else ["NA"] * 9
            )

            description_obj = BRS_Policy_2.objects.filter(
                Model_Name="Performance_Frequency"
            ).first()
            section_b_10c = (
                [getattr(description_obj, f"P{i}", "NA") for i in range(1, 10)]
                if description_obj
                else ["NA"] * 9
            )
            section_b_10c_desc = (
                description_obj.Description if description_obj else "NA"
            ), (description_obj.Frequency if description_obj else "NA")

            description_obj = BRS_Policy_2.objects.filter(
                Model_Name="Compliance_Frequency"
            ).first()
            section_b_10d = (
                [getattr(description_obj, f"P{i}", "NA") for i in range(1, 10)]
                if description_obj
                else ["NA"] * 9
            )
            section_b_10d_desc = (
                description_obj.Description if description_obj else "NA"
            ), (description_obj.Frequency if description_obj else "NA")

            description_obj = BRS_Policy_2.objects.filter(
                Model_Name="Independent_Assessment"
            ).first()
            section_b_11 = (
                [getattr(description_obj, f"P{i}", "NA") for i in range(1, 10)]
                if description_obj
                else ["NA"] * 9
            )
            section_b_11_desc = description_obj.Description if description_obj else "NA"

            description_obj = BRS_Policy_1a.objects.filter(
                Model_Name="Principles_Material_Business"
            ).first()
            section_b_12a = (
                [getattr(description_obj, f"P{i}", "NA") for i in range(1, 10)]
                if description_obj
                else ["NA"] * 9
            )

            description_obj = BRS_Policy_1a.objects.filter(
                Model_Name="Position_Formulate_Policies"
            ).first()
            section_b_12b = (
                [getattr(description_obj, f"P{i}", "NA") for i in range(1, 10)]
                if description_obj
                else ["NA"] * 9
            )

            description_obj = BRS_Policy_1a.objects.filter(
                Model_Name="Financial_Human_Technical_Resources"
            ).first()
            section_b_12c = (
                [getattr(description_obj, f"P{i}", "NA") for i in range(1, 10)]
                if description_obj
                else ["NA"] * 9
            )

            description_obj = BRS_Policy_1a.objects.filter(
                Model_Name="Planned_Next_Financial_Year"
            ).first()

            section_b_12d = (
                [getattr(description_obj, f"P{i}", "NA") for i in range(1, 10)]
                if description_obj
                else ["NA"] * 9
            )

            description_obj = BRS_Policy_1a.objects.filter(
                Model_Name="Other_Reason"
            ).first()
            section_b_12e = description_obj.Description if description_obj else "-"

            response_data = {
                "Section_B": {
                    "Disclosure_1a": section_b_1a if section_b_1a else "-",
                    "Disclosure_1b": section_b_1b if section_b_1b else "-",
                    "Disclosure_1c": section_b_1c if section_b_1c else "-",
                    "Disclosure_2": section_b_2 if section_b_2 else "-",
                    "Disclosure_3": section_b_3 if section_b_3 else "-",
                    "Disclosure_4": [section_b_4 if section_b_4 else "-"],
                    "Disclosure_5": [section_b_5 if section_b_5 else "-"],
                    "Disclosure_6": [section_b_6 if section_b_6 else "-"],
                    "Goverance_7": [section_b_7 if section_b_7 else "-"],
                    "Goverance_8": [section_b_8 if section_b_8 else "-"],
                    "Goverance_9": [section_b_9 if section_b_9 else "-"],
                    "Goverance_10a": section_b_10a if section_b_10a else "-",
                    "Goverance_10b": section_b_10b if section_b_10b else "-",
                    "Goverance_10c": section_b_10c if section_b_10c else "-",
                    "Goverance_10c_desc": (
                        section_b_10c_desc if section_b_10c_desc else "-"
                    ),
                    "Goverance_10d": section_b_10d if section_b_10d else "-",
                    "Goverance_10d_desc": (
                        section_b_10d_desc if section_b_10d_desc else "-"
                    ),
                    "Goverance_11": section_b_11 if section_b_11 else "-",
                    "section_b_11_desc": (
                        section_b_11_desc if section_b_11_desc else "-"
                    ),
                    "Goverance_12a": section_b_12a if section_b_12a else "-",
                    "Goverance_12b": section_b_12b if section_b_12b else "-",
                    "Goverance_12c": section_b_12c if section_b_12c else "-",
                    "Goverance_12d": section_b_12d if section_b_12d else "-",
                    "Goverance_12e": [section_b_12e if section_b_12e else "-"],
                }
            }

            Brs_log = {
                "Financial_Year":financial_year,
                "Section":"Section-B",
                "User_Name":f"{request.user.firstname} {request.user.lastname}"
               
            }
                            
            brs_log_serializer = BRS_Report_LogSerializer(data=Brs_log)
            if brs_log_serializer.is_valid():
                brs_log_serializer.save()
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Data Not Available in Section B"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except APIException as e:
            return Response(
                {"error": f"APIException in Section B: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TypeError as e:
            return Response(
                {"error": f"TypeError in Section B: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Unknown error in Section B: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SectionCPrinciple1View(APIView):
    def get(self, request):
        try:
            response_data = {}
            financial_year = request.query_params.get("financial_year", None)
            if financial_year is None:
                return Response(
                    {"error": "financial_year parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Extract the starting year from the financial year string
            try:
                start_year = int(
                    financial_year.split("-")[0][2:]
                )  # Extract '2023' from 'FY2023-2024'
                previous_financial_year = (
                    f"FY{start_year-1}-{start_year}"  # 'FY2022-2023'
                )
            except (ValueError, IndexError):
                return Response(
                    {
                        "error": 'Invalid financial_year format. Expected format: "FY2023-2024"'
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Section C Principle 1 E1.1 - Awareness Programmes On ESG
            segments = [
                "Employees",
                "Workers",
                "Board Of Directors",
                "Key Managerial Personnel",
            ]

            # Initialize variables for each segment
            employees_data = {}
            workers_data = {}
            board_of_directors_data = {}
            key_managerial_personnel_data = {}

            for segment in segments:
                try:
                    awareness_programmes_obj = (
                        Awareness_Programmes_On_ESG.objects.filter(
                            Financial_Year=financial_year, Segment=segment
                        ).first()
                    )
                    segment_data = [
                        {
                            "total_no_of_programmes_held": (
                                awareness_programmes_obj.Total_No_Of_Programmes_Held
                                if awareness_programmes_obj
                                else "-"
                            ),
                            "topics_covered": (
                                awareness_programmes_obj.Topics_Covered
                                if awareness_programmes_obj
                                else "-"
                            ),
                            "percentage_of_persons": (
                                awareness_programmes_obj.Percentage_Of_Persons.to_decimal()
                                if awareness_programmes_obj
                                and awareness_programmes_obj.Percentage_Of_Persons
                                else "-"
                            ),
                        }
                    ]
                except Exception:
                    segment_data = ["-", "-", "-"]

                # Assign data to specific variables based on the segment
                if segment == "Employees":
                    employees_data = segment_data
                elif segment == "Workers":
                    workers_data = segment_data
                elif segment == "Board Of Directors":
                    board_of_directors_data = segment_data
                elif segment == "Key Managerial Personnel":
                    key_managerial_personnel_data = segment_data

            # Section C Principle 1 E1.2 - Monetary Penalties
            penalty_data = {}
            settlement_data = {}
            compounding_fee_data = {}
            monetary_types = ["Penalty/Fine", "Settelment", "Compounding Fee"]

            for mtype in monetary_types:
                try:
                    monetary_obj = Penalty_Monetary.objects.filter(
                        Financial_Year=financial_year, Monetary_Type=mtype
                    ).first()

                    if (
                        monetary_obj
                        and monetary_obj.NGRBC_Principle == "Not Applicable"
                    ):
                        # If NGRBC_Principle is "Not Applicable", set all fields to "NA"
                        monetary_data = [{
                           "NGRBC_principle": monetary_obj.NGRBC_Principle,
                            "name_of_agency": "-",
                            "amount": "-",
                            "brief_case":"-",
                            "has_an_appeal_been_prefered":"NA",
                        }]
                    else:
                        monetary_data = [
                            {
                                "NGRBC_principle": (
                                    monetary_obj.NGRBC_Principle
                                    if monetary_obj
                                    else "-"
                                ),
                                "name_of_agency": (
                                    monetary_obj.Name_of_agency if monetary_obj else "-"
                                ),
                                "amount": (
                                    f"{monetary_obj.Amount}₹"
                                    if monetary_obj and monetary_obj.Amount
                                    else "-"
                                ),
                                "brief_case": (
                                    monetary_obj.Brief_case if monetary_obj else "-"
                                ),
                                "has_an_appeal_been_prefered": (
                                    monetary_obj.Has_an_appeal_been_prefered
                                    if monetary_obj
                                    else "NA"
                                ),
                            }
                        ]
                except Exception:
                    monetary_data =  [{
                        "NGRBC_principle": "-",
                        "name_of_agency": "-",
                        "amount": "-",
                        "brief_case": "-",
                        "has_an_appeal_been_prefered": "NA",
                    }]

                # Assign to the appropriate variable based on Monetary Type
                if mtype == "Penalty/Fine":
                    penalty_data = monetary_data
                elif mtype == "Settelment":
                    settlement_data = monetary_data
                elif mtype == "Compounding Fee":
                    compounding_fee_data = monetary_data

            # Section C Principle 1 E1.2 - Non-Monetary Penalties
            imprisonment_data = {}
            punishment_data = {}
            non_monetary_types = ["Imprisonment", "Punishment"]

            for ntype in non_monetary_types:
                try:
                    non_monetary_obj = Penalty_Non_Monetary.objects.filter(
                        Financial_Year=financial_year, Non_Monetary_Type=ntype
                    ).first()

                    if (
                            non_monetary_obj
                            and non_monetary_obj.NGRBC_Principle == "Not Applicable"
                        ):
                            # If NGRBC_Principle is "Not Applicable", set all fields to "NA"
                            non_monetary_data = [{
                            "NGRBC_principle": non_monetary_obj.NGRBC_Principle,
                                "name_of_agency": "-",
                                "brief_case":"-",
                                "has_an_appeal_been_prefered":"NA",
                            }]
                    else:
                            non_monetary_data = [
                            {
                                "NGRBC_principle": (
                                    non_monetary_obj.NGRBC_Principle
                                    if non_monetary_obj
                                    else "-"
                                ),
                                "name_of_agency": (
                                    non_monetary_obj.Name_of_agency
                                    if non_monetary_obj
                                    else "-"
                                ),
                                "brief_case": (
                                    non_monetary_obj.Brief_case if non_monetary_obj else "-"
                                ),
                                "has_an_appeal_been_prefered": (
                                    non_monetary_obj.Has_an_appeal_been_prefered
                                    if non_monetary_obj
                                    else "NA"
                                ),
                            }
                        ]
                except Exception:
                    non_monetary_data = [{
                        "NGRBC_principle": "-",
                        "name_of_agency": "-",
                        "brief_case": "-",
                        "has_an_appeal_been_prefered": "NA",
                    }]

                # Assign to the appropriate variable based on Non-Monetary Type
                if ntype == "Imprisonment":
                    imprisonment_data = non_monetary_data
                elif ntype == "Punishment":
                    punishment_data = non_monetary_data

            # Section C Principle 1 E1.3 - Details of Appeals
            details_of_appeal = calculate_section_C_EI_3(financial_year)
            section_c_e1_3 = details_of_appeal

            # Section C Principle 1 E1.4 - Cases of Corruption
            try:
                description_obj_penalty = Policy_Details_Penalty.objects.filter(
                    Model_Name_Penalty="AntiCorruption"
                ).first()
                section_c_e1_4 = {
                    "Descriptions_Penalty": (
                        description_obj_penalty.Descriptions_Penalty
                        if description_obj_penalty
                        else "-"
                    )
                }
            except Exception:
                section_c_e1_4 = "-"

            # Section C Principle 1 E1.5 - Disciplinary Actions
            disciplinary_action = calculate_section_C_EI_5(
                financial_year, previous_financial_year
            )
            Current_Year_Directors = disciplinary_action["Current_Year_Directors"]
            Previous_Year_Directors = disciplinary_action["Previous_Year_Directors"]
            Current_Year_KMPs = disciplinary_action["Current_Year_KMPs"]
            Previous_Year_KMPs = disciplinary_action["Previous_Year_KMPs"]
            Current_Year_Employees = disciplinary_action["Current_Year_Employees"]
            Previous_Year_Employees = disciplinary_action["Previous_Year_Employees"]
            Current_Year_Workers = disciplinary_action["Current_Year_Workers"]
            Previous_Year_Workers = disciplinary_action["Previous_Year_Workers"]
            section_c_e1_5 = disciplinary_action

            # Section C Principle 1 E1.6 - Conflict of Interest Complaints
            conflict_of_interest_complaints = calculate_section_C_EI_6(
                financial_year, previous_financial_year
            )

            # Extract values from the result
            Current_Year_No_of_Conflicts_Director = conflict_of_interest_complaints[
                "Current_Year_No_of_Conflicts_Director"
            ]
            Current_Year_Remarks_Director = conflict_of_interest_complaints[
                "Current_Year_Remarks_Director"
            ]
            Current_Year_No_of_Conflicts_KMP = conflict_of_interest_complaints[
                "Current_Year_No_of_Conflicts_KMP"
            ]
            Current_Year_Remarks_KMP = conflict_of_interest_complaints[
                "Current_Year_Remarks_KMP"
            ]
            Previous_Year_No_of_Conflicts_Director = conflict_of_interest_complaints[
                "Previous_Year_No_of_Conflicts_Director"
            ]
            Previous_Year_Remarks_Director = conflict_of_interest_complaints[
                "Previous_Year_Remarks_Director"
            ]
            Previous_Year_No_of_Conflicts_KMP = conflict_of_interest_complaints[
                "Previous_Year_No_of_Conflicts_KMP"
            ]
            Previous_Year_Remarks_KMP = conflict_of_interest_complaints[
                "Previous_Year_Remarks_KMP"
            ]

            # Section C Principle 1 E1.7 - Involvement of Board Members
            try:
                description_obj = Policy_Details_Penalty.objects.filter(
                    Model_Name_Penalty="Cases of Corruption"
                ).first()
                section_c_e1_7 = {
                    "descriptions_penalty": (
                        description_obj.Descriptions_Penalty if description_obj else "-"
                    )
                }
            except Exception:
                section_c_e1_7 = "-"

            # Section C Principle 1 E1.8 - Involvement of Board Members
            try:
                current_year_data_number = (
                    NumberOfDaysOfAccountsPayablesModel.objects.filter(
                        Financial_Year=financial_year
                    )
                    .values_list("Days_Of_Accounts_Payables", flat=True)
                    .first()
                )
                current_year_data_number = (
                    current_year_data_number
                    if current_year_data_number is not None
                    else "-"
                )
            except Exception:
                current_year_data_number = "-"

            try:
                previous_year_data_number = (
                    NumberOfDaysOfAccountsPayablesModel.objects.filter(
                        Financial_Year=previous_financial_year
                    )
                    .values_list("Days_Of_Accounts_Payables", flat=True)
                    .first()
                )
                previous_year_data_number = (
                    previous_year_data_number
                    if previous_year_data_number is not None
                    else "-"
                )
            except Exception:
                previous_year_data_number = "-"

            # awareness_programmes_on_esg = calculate_section_C_Principle_1_LI_1(financial_year)
            # section_c_l1_1 = awareness_programmes_on_esg
            awareness_programme = (
                Awareness_Programmes_For_Value_Chain_Partners.objects.filter(
                    Financial_Year=financial_year
                ).values_list(
                    "Total_No_Of_Programmes_Held",
                    "Topics_Covered",
                    "Percentage_Of_Persons_Covered",
                )
            )

            description_obj = Policy_Details_Penalty.objects.filter(
                Model_Name_Penalty="Involving Members of the board"
            ).first()
            section_c_l1_2 = {
                "is_verified": description_obj.Is_Verified if description_obj else "-",
                "descriptions_penalty": (
                    description_obj.Descriptions_Penalty if description_obj else "-"
                ),
            }

            #    @@@@@@@@@@@@@@@@@@@@@@ p1 EI 9 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            sales_current_year_record = Concentration_Of_Sales.objects.filter(
                Financial_Year=financial_year
            ).values_list(
                "Sales_To_Dealers_Divided_BY_Distributors_As_Percent_Of_Total_Sales",
                "Number_Of_Dealers_Divided_BY_Distributors_To_Whom_Sales_Are_Made",
                "Sales_To_Top_Ten_Dealers_Divided_BY_Distributors_As_Percent_Of_Total_Sales_To_Dealers_Divided_BY_Distributors",
            )

            # Fetch previous year records
            sales_previous_year_record = Concentration_Of_Sales.objects.filter(
                Financial_Year=previous_financial_year
            ).values_list(
                "Sales_To_Dealers_Divided_BY_Distributors_As_Percent_Of_Total_Sales",
                "Number_Of_Dealers_Divided_BY_Distributors_To_Whom_Sales_Are_Made",
                "Sales_To_Top_Ten_Dealers_Divided_BY_Distributors_As_Percent_Of_Total_Sales_To_Dealers_Divided_BY_Distributors",
            )

            sales_current_year_value = (
                conversion(sales_current_year_record[0][0])
                if sales_current_year_record
                else 0
            )
            dealers_current_year_value = (
                conversion(sales_current_year_record[0][1])
                if sales_current_year_record
                else 0
            )
            top_ten_sales_current_year_value = (
                conversion(sales_current_year_record[0][2])
                if sales_current_year_record
                else 0
            )

            sales_previous_year_value = (
                conversion(sales_previous_year_record[0][0])
                if sales_previous_year_record
                else 0
            )
            dealers_previous_year_value = (
                conversion(sales_previous_year_record[0][1])
                if sales_previous_year_record
                else 0
            )
            top_ten_sales_previous_year_value = (
                conversion(sales_previous_year_record[0][2])
                if sales_previous_year_record
                else 0
            )
            # ----------------------------------------------------------------- #
            purchases_current_year_record = Concentration_Of_Purchases.objects.filter(
                Financial_Year=financial_year
            ).values_list(
                "Purchases_From_Trading_Houses_As_Percent_Of_Total_Purchases",
                "Number_Of_Trading_Houses_Where_Purchases_Are_Made",
                "Purchases_From_Top_Ten_Trading_Houses_As_Percent_Of_Total_Purchases_From_Trading_Houses",
            )

            # Fetch previous year records
            purchases_previous_year_record = Concentration_Of_Purchases.objects.filter(
                Financial_Year=previous_financial_year
            ).values_list(
                "Purchases_From_Trading_Houses_As_Percent_Of_Total_Purchases",
                "Number_Of_Trading_Houses_Where_Purchases_Are_Made",
                "Purchases_From_Top_Ten_Trading_Houses_As_Percent_Of_Total_Purchases_From_Trading_Houses",
            )

            # Extract values or set to "-" if no records are found
            purchases_current_year_value = (
                conversion(purchases_current_year_record[0][0])
                if purchases_current_year_record
                else 0
            )
            trading_houses_current_year_value = (
                conversion(purchases_current_year_record[0][1])
                if purchases_current_year_record
                else 0
            )
            top_ten_purchases_current_year_value = (
                conversion(purchases_current_year_record[0][2])
                if purchases_current_year_record
                else 0
            )

            purchases_previous_year_value = (
                conversion(purchases_previous_year_record[0][0])
                if purchases_previous_year_record
                else 0
            )
            trading_houses_previous_year_value = (
                conversion(purchases_previous_year_record[0][1])
                if purchases_previous_year_record
                else 0
            )
            top_ten_purchases_previous_year_value = (
                conversion(purchases_previous_year_record[0][2])
                if purchases_previous_year_record
                else 0
            )
            # ----------------------------------------------------------------- #
            rpts_current_year_record = ShareOfRPTs.objects.filter(
                Financial_Year=financial_year
            ).values_list(
                "Purchases_With_Related_Parties_As_Percent_Of_Total_Purchases",
                "Sales_To_Related_Parties_As_Percent_Of_Total_Sales",
                "Loans_And_Advances_To_Related_Parties_As_Percent_Of_Total_Loans_And_Advances",
                "Investments_In_Related_Parties_As_Percent_Of_Total_Investments",
            )

            rpts_previous_year_record = ShareOfRPTs.objects.filter(
                Financial_Year=previous_financial_year
            ).values_list(
                "Purchases_With_Related_Parties_As_Percent_Of_Total_Purchases",
                "Sales_To_Related_Parties_As_Percent_Of_Total_Sales",
                "Loans_And_Advances_To_Related_Parties_As_Percent_Of_Total_Loans_And_Advances",
                "Investments_In_Related_Parties_As_Percent_Of_Total_Investments",
            )

            purchases_rpt_current = (
                conversion(rpts_current_year_record[0][0])
                if rpts_current_year_record
                else 0
            )
            sales_rpt_current = (
                conversion(rpts_current_year_record[0][1])
                if rpts_current_year_record
                else 0
            )
            loans_advances_rpt_current = (
                conversion(rpts_current_year_record[0][2])
                if rpts_current_year_record
                else 0
            )
            investments_rpt_current = (
                conversion(rpts_current_year_record[0][3])
                if rpts_current_year_record
                else 0
            )

            purchases_rpt_previous = (
                conversion(rpts_previous_year_record[0][0])
                if rpts_previous_year_record
                else 0
            )
            sales_rpt_previous = (
                conversion(rpts_previous_year_record[0][1])
                if rpts_previous_year_record
                else 0
            )
            loans_advances_rpt_previous = (
                conversion(rpts_previous_year_record[0][2])
                if rpts_previous_year_record
                else 0
            )
            investments_rpt_previous = (
                conversion(rpts_previous_year_record[0][3])
                if rpts_previous_year_record
                else 0
            )

            # ----------------------------------------------------------------- #

            # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ #

            # Organizing the response as requested
            response_data = {
                "Section_C_P1": {
                    "Principle_1_E1_1_Emp": employees_data if employees_data else "-",
                    "Principle_1_E1_1_Workers": workers_data if workers_data else "-",
                    "Principle_1_E1_1_BOD": (
                        board_of_directors_data if board_of_directors_data else "-"
                    ),
                    "Principle_1_E1_1_KMP": (
                        key_managerial_personnel_data
                        if key_managerial_personnel_data
                        else "-"
                    ),
                    "Principle_1_E1_2_PD": penalty_data if penalty_data else "-",
                    "Principle_1_E1_2_SE": settlement_data if settlement_data else "-",
                    "Principle_1_E1_2_CF": (
                        compounding_fee_data if compounding_fee_data else "-"
                    ),
                    "Principle_1_E1_2_IMPLS": (
                        imprisonment_data if imprisonment_data else "-"
                    ),
                    "Principle_1_E1_2_PUNISH": (
                        punishment_data if punishment_data else "-"
                    ),
                    "Principle_1_E1_3": [section_c_e1_3 if section_c_e1_3 else "-"],
                    "Principle_1_E1_4": [section_c_e1_4 if section_c_e1_4 else "-"],
                    "Principle_1_E1_5_Directors": [
                        {
                            "current_year_directors": (
                                Current_Year_Directors if Current_Year_Directors else 0
                            ),
                            "previous_year_directors": (
                                Previous_Year_Directors
                                if Previous_Year_Directors
                                else 0
                            ),
                        }
                    ],
                    "Principle_1_E1_5_KMPs": [
                        {
                            "current_year_KMPs": (
                                Current_Year_KMPs if Current_Year_KMPs else 0
                            ),
                            "previous_year_KMPs": (
                                Previous_Year_KMPs if Previous_Year_KMPs else 0
                            ),
                        }
                    ],
                    "Principle_1_E1_5_Employees": [
                        {
                            "current_year_employees": (
                                Current_Year_Employees if Current_Year_Employees else 0
                            ),
                            "previous_year_employees": (
                                Previous_Year_Employees
                                if Previous_Year_Employees
                                else 0
                            ),
                        }
                    ],
                    "Principle_1_E1_5_Workers": [
                        {
                            "current_year_workers": (
                                Current_Year_Workers if Current_Year_Workers else 0
                            ),
                            "previous_year_workers": (
                                Previous_Year_Workers if Previous_Year_Workers else 0
                            ),
                        }
                    ],
                    "Principle_1_EI_6_Directors": [
                        {
                            "current_year_no_of_conflicts_director": (
                                conflict_of_interest_complaints[
                                    "Current_Year_No_of_Conflicts_Director"
                                ]
                                if conflict_of_interest_complaints[
                                    "Current_Year_No_of_Conflicts_Director"
                                ]
                                else 0
                            ),
                            "current_year_remarks_director": (
                                conflict_of_interest_complaints[
                                    "Current_Year_Remarks_Director"
                                ]
                                if conflict_of_interest_complaints[
                                    "Current_Year_Remarks_Director"
                                ]
                                else "NA"
                            ),
                            "previous_year_no_of_conflicts_director": (
                                conflict_of_interest_complaints[
                                    "Previous_Year_No_of_Conflicts_Director"
                                ]
                                if conflict_of_interest_complaints[
                                    "Previous_Year_No_of_Conflicts_Director"
                                ]
                                else 0
                            ),
                            "previous_year_remarks_director": (
                                conflict_of_interest_complaints[
                                    "Previous_Year_Remarks_Director"
                                ]
                                if conflict_of_interest_complaints[
                                    "Previous_Year_Remarks_Director"
                                ]
                                else "NA"
                            ),
                        }
                    ],
                    "Principle_1_EI_6_KMPs": [
                        {
                            "current_year_no_of_conflicts_KMP": (
                                conflict_of_interest_complaints[
                                    "Current_Year_No_of_Conflicts_KMP"
                                ]
                                if conflict_of_interest_complaints[
                                    "Current_Year_No_of_Conflicts_KMP"
                                ]
                                else 0
                            ),
                            "current_year_remarks_KMP": (
                                conflict_of_interest_complaints[
                                    "Current_Year_Remarks_KMP"
                                ]
                                if conflict_of_interest_complaints[
                                    "Current_Year_Remarks_KMP"
                                ]
                                else "NA"
                            ),
                            "previous_year_no_of_conflicts_KMP": (
                                conflict_of_interest_complaints[
                                    "Previous_Year_No_of_Conflicts_KMP"
                                ]
                                if conflict_of_interest_complaints[
                                    "Previous_Year_No_of_Conflicts_KMP"
                                ]
                                else 0
                            ),
                            "previous_year_remarks_KMP": (
                                conflict_of_interest_complaints[
                                    "Previous_Year_Remarks_KMP"
                                ]
                                if conflict_of_interest_complaints[
                                    "Previous_Year_Remarks_KMP"
                                ]
                                else "NA"
                            ),
                        }
                    ],
                    "Principle_1_E1_7": section_c_e1_7 if section_c_e1_7 else "-",
                    "Principle_1_E1_8": [
                        {
                            "current_year_days_of_accounts_payables": (
                                str(current_year_data_number)
                                if current_year_data_number
                                else "-"
                            ),
                            "previous_year_days_of_accounts_payables": (
                                str(previous_year_data_number)
                                if previous_year_data_number
                                else "-"
                            ),
                        }
                    ],
                    "Principle_1_E1_9_Purchases_a": [
                        {
                            "purchases_current_year_value": (
                                f"{purchases_current_year_value}%"
                                if purchases_current_year_value != 0
                                else 0
                            ),
                            "purchases_previous_year_value": (
                                f"{purchases_previous_year_value}%"
                                if purchases_previous_year_value != 0
                                else 0
                            ),
                        }
                    ],
                    "Principle_1_E1_9_Purchases_b": [
                        {
                            "trading_houses_current_year_value": trading_houses_current_year_value,
                            "trading_houses_previous_year_value": trading_houses_previous_year_value,
                        }
                    ],
                    "Principle_1_E1_9_Purchases_c": [
                        {
                            "top_ten_purchases_current_year_value": (
                                f"{top_ten_purchases_current_year_value}%"
                                if top_ten_purchases_current_year_value != 0
                                else 0
                            ),
                            "top_ten_purchases_previous_year_value": (
                                f"{top_ten_purchases_previous_year_value}%"
                                if top_ten_purchases_previous_year_value != 0
                                else 0
                            ),
                        }
                    ],
                    "Principle_1_E1_9_Sales_a": [
                        {
                            "sales_current_year_value": (
                                f"{sales_current_year_value}%"
                                if sales_current_year_value != 0
                                else 0
                            ),
                            "sales_previous_year_value": (
                                f"{sales_previous_year_value}%"
                                if sales_previous_year_value != 0
                                else 0
                            ),
                        }
                    ],
                    "Principle_1_E1_9_Sales_b": [
                        {
                            "dealers_current_year_value": dealers_current_year_value,
                            "dealers_previous_year_value": dealers_previous_year_value,
                        }
                    ],
                    "Principle_1_E1_9_Sales_c": [
                        {
                            "top_ten_sales_current_year_value": (
                                f"{top_ten_sales_current_year_value}%"
                                if top_ten_sales_current_year_value != 0
                                else 0
                            ),
                            "top_ten_sales_previous_year_value": (
                                f"{top_ten_sales_previous_year_value}%"
                                if top_ten_sales_previous_year_value != 0
                                else 0
                            ),
                        }
                    ],
                    "Principle_1_E1_9_RPTs_a": [
                        {
                            "purchases_rpt_current": (
                                f"{purchases_rpt_current}%"
                                if purchases_rpt_current != 0
                                else 0
                            ),
                            "purchases_rpt_previous": (
                                f"{purchases_rpt_previous}%"
                                if purchases_rpt_previous != 0
                                else 0
                            ),
                        }
                    ],
                    "Principle_1_E1_9_RPTs_b": [
                        {
                            "sales_rpt_current": (
                                f"{sales_rpt_current}%" if sales_rpt_current != 0 else 0
                            ),
                            "sales_rpt_previous": (
                                f"{sales_rpt_previous}%"
                                if sales_rpt_previous != 0
                                else 0
                            ),
                        }
                    ],
                    "Principle_1_E1_9_RPTs_c": [
                        {
                            "loans_advances_rpt_current": loans_advances_rpt_current,
                            "loans_advances_rpt_previous": loans_advances_rpt_previous,
                        }
                    ],
                    "Principle_1_E1_9_RPTs_d": [
                        {
                            "investments_rpt_current": investments_rpt_current,
                            "investments_rpt_previous": investments_rpt_previous,
                        }
                    ],
                    "Principle_1_LI_1": [
                        {
                            "total_no_of_programmes_held": (
                                awareness_programme[0][0]
                                if awareness_programme
                                else "-"
                            ),
                            "topics_covered": (
                                awareness_programme[0][1]
                                if awareness_programme
                                else "-"
                            ),
                            "Percentage_Of_Persons_Covered": (
                                conversion(awareness_programme[0][2])
                                if awareness_programme
                                else "-"
                            ),
                        }
                    ],
                    "Principle_1_LI_2": [section_c_l1_2 if section_c_l1_2 else "-"],
                }
            }

            Brs_log = {
                "Financial_Year":financial_year,
                "Section":"Principle 1",
                "User_Name":f"{request.user.firstname} {request.user.lastname}"
               
            }
                            
            brs_log_serializer = BRS_Report_LogSerializer(data=Brs_log)
            if brs_log_serializer.is_valid():
                brs_log_serializer.save()

            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Data Not Available in Principle_1"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except APIException as e:
            return Response(
                {"error": f"APIException in Principle_1: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TypeError as e:
            return Response(
                {"error": f"TypeError in Principle_1: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Unknown error in Principle_1: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SectionCPrinciple2View(APIView):
    def get(self, request):
        try:
            response_data = {}

            financial_year = request.query_params.get("financial_year", None)

            if financial_year is None:
                return Response(
                    {"error": "financial_year parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract the starting year from the financial year string
            try:
                start_year = int(
                    financial_year.split("-")[0][2:]
                )  # Extract '2023' from 'FY2023-2024'
                previous_financial_year = (
                    f"FY{start_year-1}-{start_year}"  # 'FY2022-2023'
                )
            except (ValueError, IndexError):
                return Response(
                    {
                        "error": 'Invalid financial_year format. Expected format: "FY2023-2024"'
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Principle_2_EI_1
            percent_of_investments = calculate_principle_2_EI_1(
                financial_year, previous_financial_year
            )
            Current_Year_R_and_D_Investments = percent_of_investments[
                "Current_Year_R_and_D_Investments"
            ]
            Current_Year_R_and_D_Investments = round(
                convert_to_float(Current_Year_R_and_D_Investments)
            )
            Previous_Year_R_and_D_Investments = percent_of_investments[
                "Previous_Year_R_and_D_Investments"
            ]
            Previous_Year_R_and_D_Investments = round(
                convert_to_float(Previous_Year_R_and_D_Investments)
            )
            R_and_D_Investment_Details = percent_of_investments[
                "R_and_D_Investment_Details"
            ]

            Current_Year_Capex = percent_of_investments["Current_Year_Capex"]
            Current_Year_Capex = round(convert_to_float(Current_Year_Capex), 2)
            Previous_Year_Capex = percent_of_investments["Previous_Year_Capex"]
            Previous_Year_Capex = round(convert_to_float(Previous_Year_Capex), 2)
            Capex_Investment_Details = percent_of_investments[
                "Capex_Investment_Details"
            ]

            if not isinstance(R_and_D_Investment_Details, (list, dict)):
                filtered_R_and_D_Investment_Details = R_and_D_Investment_Details

            if not isinstance(Capex_Investment_Details, (list, dict)):
                filtered_Capex_Investment_Details = Capex_Investment_Details

            # Principle_2_EI_2
            Is_Verified = "-"
            Total_Material_Input_ = " "
            Percent_of_Material_Input_Sustainably_Sourced = "-"

            try:
                # Fetch the record for the given financial year
                sourcing_records = Sustainable_Sourcing.objects.get(
                    Financial_Year=financial_year
                )

                # Extract values, defaulting to "-" if not available
                Total_Material_Input_ = (
                    sourcing_records.Total_Material_Input
                    if sourcing_records.Total_Material_Input
                    else " "
                )
                Percent_of_Material_Input_Sustainably_Sourced = (
                    conversion(
                        sourcing_records.Percent_of_Material_Input_Sustainably_Sourced
                    )
                    if sourcing_records.Percent_of_Material_Input_Sustainably_Sourced
                    else "-"
                )
                Is_Verified = (
                    sourcing_records.Is_Verified
                    if sourcing_records.Is_Verified
                    else "-"
                )

                # Enforce the condition: If Is_Verified is "Yes", ensure Total_Material_Input is provided
                if Is_Verified == "Yes" and Total_Material_Input_ == " ":
                    raise ValueError(
                        "Total_Material_Input is mandatory when Is_Verified is 'Yes'."
                    )

            except Sustainable_Sourcing.DoesNotExist:
                pass
            except ValueError as e:
                # Handle the error gracefully or log it
                Total_Material_Input_ = str(e)

            Principle_2_EI_2_value = {
                "Is_Verified": Is_Verified if Is_Verified else "-",
                "Total_Material_Input_": (
                    Total_Material_Input_ if Total_Material_Input_ != " " else " "
                ),
            }

            Principle_2_EI_2b_value = {
                "percent_of_material_input_sustainably_sourced": (
                    f"While as a practice, the majority of sourcing is done sustainably, "
                    f"{Percent_of_Material_Input_Sustainably_Sourced}% of input material was sourced from within India "
                    "(refer Principle 8 Essential Indicator No. 4). KPCL has developed a mechanism to track and monitor "
                    "the percentage of such input materials. 75% of value-contributors (manufacturing suppliers) are re-evaluated "
                    "every alternate year, and 25% of value-contributors (manufacturing suppliers) are self-assessed."
                    if Percent_of_Material_Input_Sustainably_Sourced != "-"
                    else "-"
                )
            }

            # Principle_2_EI_3
            description_obj_reclaim = DescriptionsProjectandPolicies.objects.filter(
                Module_Name="Reclaim of Product"
            ).first()
            # response_data = {
            #     "Description": description_obj.Description if description_obj else "NA"
            # }

            # Principle_2_EI_4
            description_obj = DescriptionsProjectandPolicies.objects.filter(
                Module_Name="Extended Producer Responsibility"
            ).first()
            Policies_E4 = description_obj.Description if description_obj else "-"

            # Principle_2_LI_1
            lifecycle_assessment = calculate_principle_2_LI_1(financial_year)
            NIC_Code = lifecycle_assessment["NIC_Code"]
            Name_of_Product_Service = lifecycle_assessment["Name_of_Product_Service"]
            Percent_of_Turnover_Contributed = lifecycle_assessment[
                "Percent_of_Turnover_Contributed"
            ]
            Boundary_for_Assessment = lifecycle_assessment["Boundary_for_Assessment"]
            Conducted_by_External_Agency = lifecycle_assessment[
                "Conducted_by_External_Agency"
            ]
            URL_of_Published_Results = lifecycle_assessment["URL_of_Published_Results"]
            Description_Assessment = lifecycle_assessment["Description_Assessment"]

            # Principle_2_LI_2
            concerns_and_action = calculate_principle_2_LI_2(financial_year)
            Name_of_Product_Service = concerns_and_action["Name_of_Product_Service"]
            Description = concerns_and_action["Description"]
            Action_Taken = concerns_and_action["Action_Taken"]
            Description_Concern = concerns_and_action["Description_Concern"]

            # Principle_2_LI_3
            recycled_data_for_current_year = (
                Recycled_or_Reused_Input_Material.objects.filter(
                    Financial_Year=financial_year
                )
            )
            recycled_data_for_previous_year = (
                Recycled_or_Reused_Input_Material.objects.filter(
                    Financial_Year=previous_financial_year
                )
            )

            Total_Material_Input = [
                "Foundry Steel (MT)",
                "Foundry Aluminium (MT)",
                "Foundry Sand (MT)",
                "Packaging Wood (CFT)",
                "Machine Oil (KL)",
            ]

            principle_2_li_3_foundry_steel = "-"
            principle_2_li_3_foundry_aluminium = "-"
            principle_2_li_3_foundry_sand = "-"
            principle_2_li_3_packaging_wood = "-"
            principle_2_li_3_machine_oil = "-"

            for material_type in Total_Material_Input:
                # Filter records for the specified material type and years
                current_year_record = recycled_data_for_current_year.filter(
                    Total_Material_Input=material_type
                ).first()
                previous_year_record = recycled_data_for_previous_year.filter(
                    Total_Material_Input=material_type
                ).first()

                # Get only the `Recycled_or_reused_Input_Material` values for each year
                current_year_value = (
                    safe_decimal_to_float(
                        getattr(
                            current_year_record,
                            "Recycled_or_reused_Input_Material",
                            None,
                        )
                    )
                    if current_year_record
                    else "-"
                )

                previous_year_value = (
                    safe_decimal_to_float(
                        getattr(
                            previous_year_record,
                            "Recycled_or_reused_Input_Material",
                            None,
                        )
                    )
                    if previous_year_record
                    else "-"
                )

                # Assign values based on material type
                if material_type == "Foundry Steel (MT)":
                    principle_2_li_3_foundry_steel = [
                        {
                            "current_year_value": current_year_value,
                            "previous_year_value": previous_year_value,
                        }
                    ]
                elif material_type == "Foundry Aluminium (MT)":
                    principle_2_li_3_foundry_aluminium = [
                        {
                            "current_year_value": current_year_value,
                            "previous_year_value": previous_year_value,
                        }
                    ]
                elif material_type == "Foundry Sand (MT)":
                    principle_2_li_3_foundry_sand = [
                        {
                            "current_year_value": current_year_value,
                            "previous_year_value": previous_year_value,
                        }
                    ]
                elif material_type == "Packaging Wood (CFT)":
                    principle_2_li_3_packaging_wood = [
                        {
                            "current_year_value": current_year_value,
                            "previous_year_value": previous_year_value,
                        }
                    ]
                elif material_type == "Machine Oil (KL)":
                    principle_2_li_3_machine_oil = [
                        {
                            "current_year_value": current_year_value,
                            "previous_year_value": previous_year_value,
                        }
                    ]

            # Principle_2_LI_4
            end_of_life_of_product = calculate_principle_2_LI_4(
                financial_year, previous_financial_year
            )
            Current_Year_Plastic_Reused = end_of_life_of_product[
                "Current_Year_Plastic_Reused"
            ]
            Current_Year_Plastic_Recycled = end_of_life_of_product[
                "Current_Year_Plastic_Recycled"
            ]
            Current_Year_Plastic_Disposed = end_of_life_of_product[
                "Current_Year_Plastic_Disposed"
            ]
            Current_Year_E_Waste_Reused = end_of_life_of_product[
                "Current_Year_E_Waste_Reused"
            ]
            Current_Year_E_Waste_Recycled = end_of_life_of_product[
                "Current_Year_E_Waste_Recycled"
            ]
            Current_Year_E_Waste_Disposed = end_of_life_of_product[
                "Current_Year_E_Waste_Disposed"
            ]
            Current_Year_Hazardous_Waste_Reused = end_of_life_of_product[
                "Current_Year_Hazardous_Waste_Reused"
            ]
            Current_Year_Hazardous_Waste_Recycled = end_of_life_of_product[
                "Current_Year_Hazardous_Waste_Recycled"
            ]
            Current_Year_Hazardous_Waste_Disposed = end_of_life_of_product[
                "Current_Year_Hazardous_Waste_Disposed"
            ]
            Current_Year_Other_Waste_Reused = end_of_life_of_product[
                "Current_Year_Other_Waste_Reused"
            ]
            Current_Year_Other_Waste_Recycled = end_of_life_of_product[
                "Current_Year_Other_Waste_Recycled"
            ]
            Current_Year_Other_Waste_Disposed = end_of_life_of_product[
                "Current_Year_Other_Waste_Disposed"
            ]
            Previous_Year_Plastic_Reused = end_of_life_of_product[
                "Previous_Year_Plastic_Reused"
            ]
            Previous_Year_Plastic_Recycled = end_of_life_of_product[
                "Previous_Year_Plastic_Recycled"
            ]
            Previous_Year_Plastic_Disposed = end_of_life_of_product[
                "Previous_Year_Plastic_Disposed"
            ]
            Previous_Year_E_Waste_Reused = end_of_life_of_product[
                "Previous_Year_E_Waste_Reused"
            ]
            Previous_Year_E_Waste_Recycled = end_of_life_of_product[
                "Previous_Year_E_Waste_Recycled"
            ]
            Previous_Year_E_Waste_Disposed = end_of_life_of_product[
                "Previous_Year_E_Waste_Disposed"
            ]
            Previous_Year_Hazardous_Waste_Reused = end_of_life_of_product[
                "Previous_Year_Hazardous_Waste_Reused"
            ]
            Previous_Year_Hazardous_Waste_Recycled = end_of_life_of_product[
                "Previous_Year_Hazardous_Waste_Recycled"
            ]
            Previous_Year_Hazardous_Waste_Disposed = end_of_life_of_product[
                "Previous_Year_Hazardous_Waste_Disposed"
            ]
            Previous_Year_Other_Waste_Reused = end_of_life_of_product[
                "Previous_Year_Other_Waste_Reused"
            ]
            Previous_Year_Other_Waste_Recycled = end_of_life_of_product[
                "Previous_Year_Other_Waste_Recycled"
            ]
            Previous_Year_Other_Waste_Disposed = end_of_life_of_product[
                "Previous_Year_Other_Waste_Disposed"
            ]

            # Principle_2_LI_5
            reclaimed_products_and_packaging = calculate_principle_2_LI_5(
                financial_year
            )
            Product_Category = reclaimed_products_and_packaging["Product_Category"]
            Percent_of_Reclaimed = reclaimed_products_and_packaging[
                "Percent_of_Reclaimed"
            ]

            response_data = {
                "Section_C_P2": {
                    "Principle_2_EI_1_R&D": [
                        {
                            "current_year_R_and_D_investments": (
                                f"{Current_Year_R_and_D_Investments}%"
                                if Current_Year_R_and_D_Investments != 0
                                else 0
                            ),
                            "previous_year_R_and_D_investments": (
                                f"{Previous_Year_R_and_D_Investments}%"
                                if Previous_Year_R_and_D_Investments != 0
                                else 0
                            ),
                            "R_and_D_investment_details": (
                                R_and_D_Investment_Details
                                if R_and_D_Investment_Details
                                else "-"
                            ),
                        }
                    ],
                    "Principle_2_EI_1_Capex": [
                        {
                            "current_year_capex": (
                                f"{Current_Year_Capex}%"
                                if Current_Year_Capex != 0
                                else 0
                            ),
                            "previous_year_capex": (
                                f"{Previous_Year_Capex}%"
                                if Previous_Year_Capex != 0
                                else 0
                            ),
                            "capex_investment_details": (
                                Capex_Investment_Details
                                if Capex_Investment_Details
                                else "-"
                            ),
                        }
                    ],
                    "Principle_2_EI_2": [Principle_2_EI_2_value],
                    "Principle_2_EI_2b": [Principle_2_EI_2b_value],
                    "Principle_2_EI_3": [
                        {
                            "description": (
                                description_obj_reclaim.Description
                                if description_obj_reclaim
                                else "-"
                            )
                        }
                    ],
                    "Principle_2_EI_4": [{"description": Policies_E4}],
                    "Principle_2_LI_1": [
                        {
                            "NIC_code": NIC_Code if NIC_Code else "-",
                            "name_of_product_service": (
                                Name_of_Product_Service
                                if Name_of_Product_Service
                                else "-"
                            ),
                            "percent_of_turnover_contributed": (
                                Percent_of_Turnover_Contributed
                                if Percent_of_Turnover_Contributed
                                else "-"
                            ),
                            "boundary_for_assessment": (
                                Boundary_for_Assessment
                                if Boundary_for_Assessment
                                else "-"
                            ),
                            "conducted_by_external_agency": (
                                Conducted_by_External_Agency
                                if Conducted_by_External_Agency
                                else "-"
                            ),
                            "URL_of_published_results": (
                                URL_of_Published_Results
                                if URL_of_Published_Results
                                else "-"
                            ),
                            "description_assessment": (
                                Description_Assessment
                                if Description_Assessment
                                else "-"
                            ),
                        }
                    ],
                    "Principle_2_LI_2": [
                        {
                            "name_of_product_service": (
                                Name_of_Product_Service
                                if Name_of_Product_Service
                                else "-"
                            ),
                            "description": Description if Description else "-",
                            "action_taken": Action_Taken if Action_Taken else "-",
                            "description_concern": (
                                Description_Concern if Description_Concern else "-"
                            ),
                        }
                    ],
                    "Principle_2_LI_3_Foundry_Steel": principle_2_li_3_foundry_steel,
                    "Principle_2_LI_3_Foundry_Aluminium": principle_2_li_3_foundry_aluminium,
                    "Principle_2_LI_3_Foundry_Sand": principle_2_li_3_foundry_sand,
                    "Principle_2_LI_3_Packaging_Wood": principle_2_li_3_packaging_wood,
                    "Principle_2_LI_3_Machine_Oil": principle_2_li_3_machine_oil,
                    "Principle_2_LI_4_plastic": [
                        {
                            "current_year_plastic_reused": (
                                Current_Year_Plastic_Reused
                                if Current_Year_Plastic_Reused is not None
                                else "NA"
                            ),
                            "current_year_plastic_recycled": (
                                Current_Year_Plastic_Recycled
                                if Current_Year_Plastic_Recycled is not None
                                else "NA"
                            ),
                            "current_year_plastic_disposed": (
                                Current_Year_Plastic_Disposed
                                if Current_Year_Plastic_Disposed is not None
                                else "NA"
                            ),
                            "previous_year_plastic_reused": (
                                Previous_Year_Plastic_Reused
                                if Previous_Year_Plastic_Reused is not None
                                else "NA"
                            ),
                            "previous_year_plastic_recycled": (
                                Previous_Year_Plastic_Recycled
                                if Previous_Year_Plastic_Recycled is not None
                                else "NA"
                            ),
                            "previous_year_plastic_disposed": (
                                Previous_Year_Plastic_Disposed
                                if Previous_Year_Plastic_Disposed is not None
                                else "NA"
                            ),
                        }
                    ],
                    "Principle_2_LI_4_e_waste": [
                        {
                            "current_year_e_waste_reused": (
                                Current_Year_E_Waste_Reused
                                if Current_Year_E_Waste_Reused is not None
                                else "NA"
                            ),
                            "current_year_e_waste_recycled": (
                                Current_Year_E_Waste_Recycled
                                if Current_Year_E_Waste_Recycled is not None
                                else "NA"
                            ),
                            "current_year_e_waste_disposed": (
                                Current_Year_E_Waste_Disposed
                                if Current_Year_E_Waste_Disposed is not None
                                else "NA"
                            ),
                            "previous_year_e_waste_reused": (
                                Previous_Year_E_Waste_Reused
                                if Previous_Year_E_Waste_Reused is not None
                                else "NA"
                            ),
                            "previous_year_e_waste_recycled": (
                                Previous_Year_E_Waste_Recycled
                                if Previous_Year_E_Waste_Recycled is not None
                                else "NA"
                            ),
                            "previous_year_e_waste_disposed": (
                                Previous_Year_E_Waste_Disposed
                                if Previous_Year_E_Waste_Disposed is not None
                                else "NA"
                            ),
                        }
                    ],
                    "Principle_2_LI_4_hazardous": [
                        {
                            "current_year_hazardous_waste_reused": (
                                Current_Year_Hazardous_Waste_Reused
                                if Current_Year_Hazardous_Waste_Reused is not None
                                else "NA"
                            ),
                            "current_year_hazardous_waste_recycled": (
                                Current_Year_Hazardous_Waste_Recycled
                                if Current_Year_Hazardous_Waste_Recycled is not None
                                else "NA"
                            ),
                            "current_year_hazardous_waste_disposed": (
                                Current_Year_Hazardous_Waste_Disposed
                                if Current_Year_Hazardous_Waste_Disposed is not None
                                else "NA"
                            ),
                            "previous_year_hazardous_waste_reused": (
                                Previous_Year_Hazardous_Waste_Reused
                                if Previous_Year_Hazardous_Waste_Reused is not None
                                else "NA"
                            ),
                            "previous_year_hazardous_waste_recycled": (
                                Previous_Year_Hazardous_Waste_Recycled
                                if Previous_Year_Hazardous_Waste_Recycled is not None
                                else "NA"
                            ),
                            "previous_year_hazardous_waste_disposed": (
                                Previous_Year_Hazardous_Waste_Disposed
                                if Previous_Year_Hazardous_Waste_Disposed is not None
                                else "NA"
                            ),
                        }
                    ],
                    "Principle_2_LI_4_other": [
                        {
                            "current_year_other_waste_Reused": (
                                Current_Year_Other_Waste_Reused
                                if Current_Year_Other_Waste_Reused is not None
                                else "NA"
                            ),
                            "current_year_other_waste_recycled": (
                                Current_Year_Other_Waste_Recycled
                                if Current_Year_Other_Waste_Recycled is not None
                                else "NA"
                            ),
                            "current_year_other_waste_disposed": (
                                Current_Year_Other_Waste_Disposed
                                if Current_Year_Other_Waste_Disposed is not None
                                else "NA"
                            ),
                            "previous_year_other_waste_reused": (
                                Previous_Year_Other_Waste_Reused
                                if Previous_Year_Other_Waste_Reused is not None
                                else "NA"
                            ),
                            "previous_year_other_waste_recycled": (
                                Previous_Year_Other_Waste_Recycled
                                if Previous_Year_Other_Waste_Recycled is not None
                                else "NA"
                            ),
                            "previous_year_other_waste_disposed": (
                                Previous_Year_Other_Waste_Disposed
                                if Previous_Year_Other_Waste_Disposed is not None
                                else "NA"
                            ),
                        }
                    ],
                    "Principle_2_LI_5": [
                        {
                            "product_category": (
                                Product_Category if Product_Category else "-"
                            ),
                            "percent_of_reclaimed": (
                                Percent_of_Reclaimed if Percent_of_Reclaimed else "-"
                            ),
                        }
                    ],
                }
            }

            Brs_log = {
                "Financial_Year":financial_year,
                "Section":"Principle 2",
                "User_Name":f"{request.user.firstname} {request.user.lastname}"
               
            }
                            
            brs_log_serializer = BRS_Report_LogSerializer(data=Brs_log)
            if brs_log_serializer.is_valid():
                brs_log_serializer.save()


            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Data Not Available in Principle_2"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except APIException as e:
            return Response(
                {"error": f"APIException in Principle_2: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TypeError as e:
            return Response(
                {"error": f"TypeError in Principle_2: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Unknown error in Principle_2: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SectionCPrinciple3View(APIView):

    def get(self, request):
        try:
            financial_year = request.query_params.get("financial_year", None)
            start_year = int(financial_year[2:6])
            previous_financial_year = f"FY{start_year-1}-{start_year}"
            try:
                description_obj_EI_3 = Policy_Details_Health_safety.objects.get(
                    Model_Name_Health_safety="Rights of Persons"
                )
                description_obj_EI_3 = (
                    description_obj_EI_3.Descriptions_Health_safety
                    if description_obj_EI_3
                    else "-"
                )

            except ObjectDoesNotExist:
                description_obj_EI_3 = "-"

            try:
                description_obj_EI_4 = Policy_Details_Health_safety.objects.get(
                    Model_Name_Health_safety="Equal opportunity"
                )
                description_obj_EI_4 = (
                    description_obj_EI_4.Descriptions_Health_safety
                    if description_obj_EI_4
                    else "-"
                )
            except ObjectDoesNotExist:
                description_obj_EI_4 = "-"

            # Initialize the rate variables
            return_to_work_rate_for_male_employee = Decimal(0.0)
            return_to_work_rate_for_female_employee = Decimal(0.0)
            retention_rate_for_male_employee = Decimal(0.0)
            retention_rate_for_female_employee = Decimal(0.0)
            return_to_work_rate_male_worker = Decimal(0.0)
            return_to_work_rate_female_worker = Decimal(0.0)
            retention_rate_for_male_worker = Decimal(0.0)
            retention_rate_for_female_worker = Decimal(0.0)
            total_return_to_work_rate_employee = Decimal(0.0)
            total_retention_rate_employee = Decimal(0.0)
            total_return_to_work_rate_of_workers = Decimal(0.0)
            total_retention_rate_workers = Decimal(0.0)

            filtered_records = (
                Post_Paternal_Leave_For_Permanent_Employee_And_Worker.objects.filter(
                    Financial_Year__in=[financial_year]
                )
            )

            # Accumulate the rates from the filtered records
            for record in filtered_records:
                return_to_work_rate_for_male_employee += Decimal(
                    str(record.Return_To_Work_Rate_For_Male_Employee or 0)
                )
                return_to_work_rate_for_female_employee += Decimal(
                    str(record.Return_To_Work_Rate_For_Female_Employee or 0)
                )
                retention_rate_for_male_employee += Decimal(
                    str(record.Retention_Rate_For_Male_Employee or 0)
                )
                retention_rate_for_female_employee += Decimal(
                    str(record.Retention_Rate_For_Female_Employee or 0)
                )
                return_to_work_rate_male_worker += Decimal(
                    str(record.Return_To_Work_Rate_Male_Workers or 0)
                )
                return_to_work_rate_female_worker += Decimal(
                    str(record.Return_To_Work_Rate_Female_Workers or 0)
                )
                retention_rate_for_male_worker += Decimal(
                    str(record.Retention_Rate_For_Male_Workers or 0)
                )
                retention_rate_for_female_worker += Decimal(
                    str(record.Retention_Rate_For_Female_Workers or 0)
                )
                total_return_to_work_rate_employee += Decimal(
                    str(record.Total_Return_To_Work_Rate_Employee or 0)
                )
                total_return_to_work_rate_of_workers += Decimal(
                    str(record.Total_Return_To_Work_Rate_Of_Workers or 0)
                )
                total_retention_rate_employee += Decimal(
                    str(record.Total_Retention_Rate_Employee or 0)
                )
                total_retention_rate_workers += Decimal(
                    str(record.Total_Retention_Rate_Workers or 0)
                )
            # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&7

            grievances_redress_obj1 = (
                Receive_and_redress_grievances_mechanism.objects.filter(
                    Segment="Employee", Type="Permanent"
                ).values("Description", "Yes_No")
            )
            grievances_redress_obj2 = (
                Receive_and_redress_grievances_mechanism.objects.filter(
                    Segment="Employee", Type="Non-Permanent"
                ).values("Description", "Yes_No")
            )
            grievances_redress_obj3 = (
                Receive_and_redress_grievances_mechanism.objects.filter(
                    Segment="Worker", Type="Permanent"
                ).values("Description", "Yes_No")
            )
            grievances_redress_obj4 = (
                Receive_and_redress_grievances_mechanism.objects.filter(
                    Segment="Worker", Type="Non-Permanent"
                ).values("Description", "Yes_No")
            )

            # Fetch records for the current financial year for the "Employees" segment
            current_year_employee_records = On_Skill_Upgradation.objects.filter(
                Financial_Year=financial_year, Segment="Employees"
            )
            # Fetch records for the previous financial year for the "Employees" segment
            previous_year_employee_records = On_Skill_Upgradation.objects.filter(
                Financial_Year=previous_financial_year, Segment="Employees"
            )
            # Calculate total number of male employees in the current financial year
            current_total_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in current_year_employee_records
            )
            current_total_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in current_year_employee_records
            )
            # Calculate total number of male employees in the previous financial year
            previous_total_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in previous_year_employee_records
            )
            previous_total_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in previous_year_employee_records
            )
            total_emp_current_year = EmployeeSummary.objects.filter(
                Financial_Year=financial_year,
            )
            total_emp_previous_year = EmployeeSummary.objects.filter(
                Financial_Year=previous_financial_year,
            )
            # Calculate total number of male employees in the current financial year
            current_year_total_male_employees = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_emp_current_year
            )
            current_year_total_female_employees = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_emp_current_year
            )
            previous_year_total_male_employees = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_emp_previous_year
            )
            previous_year_total_female_employees = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_emp_previous_year
            )
            # Fetch health and safety measures for the current and previous financial years
            health_and_safety_measures_current_year = (
                On_Health_And_Safety_Measures.objects.filter(
                    Financial_Year=financial_year, Segment="Employees"
                )
            )
            health_and_safety_measures_previous_year = (
                On_Health_And_Safety_Measures.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Employees"
                )
            )
            # Calculate total number of male and female employees in health and safety measures for the current financial year
            current_year_health_and_safety_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in health_and_safety_measures_current_year
            )
            current_year_health_and_safety_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in health_and_safety_measures_current_year
            )
            # Calculate total number of male and female employees in health and safety measures for the previous financial year
            previous_year_health_and_safety_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in health_and_safety_measures_previous_year
            )
            previous_year_health_and_safety_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in health_and_safety_measures_previous_year
            )
            # Fetch skill upgradation records for the current and previous financial years
            skill_upgradation_current_year = On_Skill_Upgradation.objects.filter(
                Financial_Year=financial_year, Segment="Employees"
            )
            skill_upgradation_previous_year = On_Skill_Upgradation.objects.filter(
                Financial_Year=previous_financial_year, Segment="Employees"
            )
            # Calculate total number of male and female employees in skill upgradation for the current financial year
            current_year_skill_upgradation_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in skill_upgradation_current_year
            )
            current_year_skill_upgradation_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in skill_upgradation_current_year
            )
            # Calculate total number of male and female employees in skill upgradation for the previous financial year
            previous_year_skill_upgradation_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in skill_upgradation_previous_year
            )
            previous_year_skill_upgradation_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in skill_upgradation_previous_year
            )

            ############################### P3 - EI_8 for WorkSummary #############################################
            # WorkSummary calculations
            total_work_current_year = WorkerSummary.objects.filter(
                Financial_Year=financial_year
            )
            total_work_previous_year = WorkerSummary.objects.filter(
                Financial_Year=previous_financial_year
            )
            current_year_total_male_workers = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_work_current_year
            )
            current_year_total_female_workers = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_work_current_year
            )
            previous_year_total_male_workers = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_work_previous_year
            )
            previous_year_total_female_workers = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_work_previous_year
            )
            health_and_safety_measures_work_current_year = (
                On_Health_And_Safety_Measures.objects.filter(
                    Financial_Year=financial_year, Segment="Workers"
                )
            )
            health_and_safety_measures_work_previous_year = (
                On_Health_And_Safety_Measures.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Workers"
                )
            )
            current_year_health_and_safety_male_workers = sum(
                float(record.No_Of_Male or 0)
                for record in health_and_safety_measures_work_current_year
            )
            current_year_health_and_safety_female_workers = sum(
                float(record.No_Of_Female or 0)
                for record in health_and_safety_measures_work_current_year
            )
            previous_year_health_and_safety_male_workers = sum(
                float(record.No_Of_Male or 0)
                for record in health_and_safety_measures_work_previous_year
            )
            previous_year_health_and_safety_female_workers = sum(
                float(record.No_Of_Female or 0)
                for record in health_and_safety_measures_work_previous_year
            )
            skill_upgradation_work_current_year = On_Skill_Upgradation.objects.filter(
                Financial_Year=financial_year, Segment="Workers"
            )
            skill_upgradation_work_previous_year = On_Skill_Upgradation.objects.filter(
                Financial_Year=previous_financial_year, Segment="Workers"
            )
            current_year_skill_upgradation_male_workers = sum(
                float(record.No_Of_Male or 0)
                for record in skill_upgradation_work_current_year
            )
            current_year_skill_upgradation_female_workers = sum(
                float(record.No_Of_Female or 0)
                for record in skill_upgradation_work_current_year
            )
            previous_year_skill_upgradation_male_workers = sum(
                float(record.No_Of_Male or 0)
                for record in skill_upgradation_work_previous_year
            )
            previous_year_skill_upgradation_female_workers = sum(
                float(record.No_Of_Female or 0)
                for record in skill_upgradation_work_previous_year
            )

            current_year_male_workers_ratio = (
                round(
                    current_year_health_and_safety_male_workers
                    / current_year_total_male_workers,
                    2,
                )
                if current_year_total_male_workers
                else 0
            )
            current_year_female_workers_ratio = (
                round(
                    current_year_health_and_safety_female_workers
                    / current_year_total_female_workers,
                    2,
                )
                if current_year_total_female_workers
                else 0
            )
            previous_year_male_workers_ratio = (
                round(
                    previous_year_health_and_safety_male_workers
                    / previous_year_total_male_workers,
                    2,
                )
                if previous_year_total_male_workers
                else 0
            )
            previous_year_female_workers_ratio = (
                round(
                    previous_year_health_and_safety_female_workers
                    / previous_year_total_female_workers,
                    2,
                )
                if previous_year_total_female_workers
                else 0
            )

            total_emp_current_year_record = EmployeeSummary.objects.filter(
                Financial_Year=financial_year,
            )
            total_emp_previous_year_record = EmployeeSummary.objects.filter(
                Financial_Year=previous_financial_year,
            )
            # Calculate total number of male employees in the current financial year
            current_year_total_male_employees = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_emp_current_year_record
            )
            current_year_total_female_employees = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_emp_current_year_record
            )
            previous_year_total_male_employees = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_emp_previous_year_record
            )
            previous_year_total_female_employees = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_emp_previous_year_record
            )
            # Fetch performance and career reviews for the current and previous financial years
            performance_reviews_current_year = (
                Performance_And_Career_Reviews.objects.filter(
                    Financial_Year=financial_year, Segment="Employees"
                )
            )
            performance_reviews_previous_year = (
                Performance_And_Career_Reviews.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Employees"
                )
            )
            # Calculate total number of male and female employees in performance and career reviews for the current financial year
            current_year_performance_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in performance_reviews_current_year
            )
            current_year_performance_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in performance_reviews_current_year
            )
            # Calculate total number of male and female employees in performance and career reviews for the previous financial year
            previous_year_performance_male_employees = sum(
                float(record.No_Of_Male or 0)
                for record in performance_reviews_previous_year
            )
            previous_year_performance_female_employees = sum(
                float(record.No_Of_Female or 0)
                for record in performance_reviews_previous_year
            )
            total_male_female_employees_current_year = (
                current_year_total_male_employees + current_year_total_female_employees
            )
            performance_male_female_employees_current_year = (
                current_year_performance_male_employees
                + current_year_performance_female_employees
            )
            total_male_female_employees_previous_year = (
                previous_year_total_male_employees
                + previous_year_total_female_employees
            )
            performance_male_female_employees_previous_year = (
                previous_year_performance_male_employees
                + previous_year_performance_female_employees
            )
            # Fetch records for the current and previous financial years
            total_workers_current_year_record = WorkerSummary.objects.filter(
                Financial_Year=financial_year,
            )
            total_workers_previous_year_record = WorkerSummary.objects.filter(
                Financial_Year=previous_financial_year,
            )
            # Calculate total number of male and female workers in the current financial year
            current_year_total_male_workers = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_workers_current_year_record
            )
            current_year_total_female_workers = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_workers_current_year_record
            )
            # Calculate total number of male and female workers in the previous financial year
            previous_year_total_male_workers = sum(
                float(record.Total_Male.to_decimal() or 0)
                for record in total_workers_previous_year_record
            )
            previous_year_total_female_workers = sum(
                float(record.Total_Female.to_decimal() or 0)
                for record in total_workers_previous_year_record
            )
            ############## Fetch performance and career reviews for the current and previous financial years for Workers #########################
            performance_reviews_current_year_workers = (
                Performance_And_Career_Reviews.objects.filter(
                    Financial_Year=financial_year, Segment="Workers"
                )
            )
            performance_reviews_previous_year_workers = (
                Performance_And_Career_Reviews.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Workers"
                )
            )
            # Calculate total number of male and female workers in performance and career reviews for the current financial year
            current_year_performance_male_workers = sum(
                float(record.No_Of_Male or 0)
                for record in performance_reviews_current_year_workers
            )
            current_year_performance_female_workers = sum(
                float(record.No_Of_Female or 0)
                for record in performance_reviews_current_year_workers
            )
            # Calculate total number of male and female workers in performance and career reviews for the previous financial year
            previous_year_performance_male_workers = sum(
                float(record.No_Of_Male or 0)
                for record in performance_reviews_previous_year_workers
            )
            previous_year_performance_female_workers = sum(
                float(record.No_Of_Female or 0)
                for record in performance_reviews_previous_year_workers
            )
            # Calculate total male and female workers
            total_male_female_workers_current_year = (
                current_year_total_male_workers + current_year_total_female_workers
            )
            performance_male_female_workers_current_year = (
                current_year_performance_male_workers
                + current_year_performance_female_workers
            )
            total_male_female_workers_previous_year = (
                previous_year_total_male_workers + previous_year_total_female_workers
            )
            performance_male_female_workers_previous_year = (
                previous_year_performance_male_workers
                + previous_year_performance_female_workers
            )

            try:
                description_obj_10_A = Policy_Details_Health_safety.objects.get(
                    Model_Name_Health_safety="Occupational Health"
                )
                description_obj_10_A = (
                    description_obj_10_A.Descriptions_Health_safety
                    if description_obj_10_A
                    else "-"
                )
            except ObjectDoesNotExist:
                description_obj_10_A = "-"

            try:
                description_obj_10_B = Policy_Details_Health_safety.objects.get(
                    Model_Name_Health_safety="Work Related Hazards"
                )
                description_obj_10_B = (
                    description_obj_10_B.Descriptions_Health_safety
                    if description_obj_10_B
                    else "-"
                )
            except ObjectDoesNotExist:
                description_obj_10_B = "-"

            description_obj_10_C = None
            try:
                description_obj_10_C = Policy_Details_Health_safety.objects.get(
                    Model_Name_Health_safety="Workers to Report"
                )
                is_verified_10_C = (
                    description_obj_10_C.Is_Verified if description_obj_10_C else "-"
                )
                desc_10_C = (
                    description_obj_10_C.Descriptions_Health_safety
                    if description_obj_10_C
                    else "-"
                )
            except ObjectDoesNotExist:
                is_verified_10_C = "-"
                desc_10_C = "-"

            description_obj_10_D = None
            try:
                description_obj_10_D = Policy_Details_Health_safety.objects.get(
                    Model_Name_Health_safety="Workers of Entity"
                )
                is_verified_10_D = (
                    description_obj_10_D.Is_Verified if description_obj_10_D else "-"
                )
                desc_10_D = (
                    description_obj_10_D.Descriptions_Health_safety
                    if description_obj_10_D
                    else "-"
                )
            except ObjectDoesNotExist:
                is_verified_10_D = "-"
                desc_10_D = "-"

            # Fetch Lost Time Injury Frequency Rate for the current and previous financial years
            ltifr_current_year = Lost_Time_Injury_Frequency_Rate.objects.filter(
                Financial_Year=financial_year, Segment="Employees"
            )
            ltifr_previous_year = Lost_Time_Injury_Frequency_Rate.objects.filter(
                Financial_Year=previous_financial_year, Segment="Employees"
            )
            current_year_total_frequency_rate_employees = sum(
                float(record.Total_Frequency_Rate.to_decimal() or 0)
                for record in ltifr_current_year
            )
            previous_year_total_frequency_rate_employees = sum(
                float(record.Total_Frequency_Rate.to_decimal() or 0)
                for record in ltifr_previous_year
            )
            # Fetch Lost Time Injury Frequency Rate for Workers for the current financial year
            ltifr_current_year_workers = Lost_Time_Injury_Frequency_Rate.objects.filter(
                Financial_Year=financial_year, Segment="Workers"
            )
            ltifr_previous_year_workers = (
                Lost_Time_Injury_Frequency_Rate.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Workers"
                )
            )
            current_year_total_frequency_rate_workers = sum(
                float(record.Total_Frequency_Rate.to_decimal() or 0)
                for record in ltifr_current_year_workers
            )
            previous_year_total_frequency_rate_workers = sum(
                float(record.Total_Frequency_Rate.to_decimal() or 0)
                for record in ltifr_previous_year_workers
            )
            # ---------- Total_Work_Related_Injuries ----------------------------#
            injuries_current_year_employees = (
                Total_Work_Related_Injuries.objects.filter(
                    Financial_Year=financial_year, Segment="Employees"
                )
            )
            injuries_previous_year_employees = (
                Total_Work_Related_Injuries.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Employees"
                )
            )
            current_year_total_injuries_employees = sum(
                float(record.Total_Injuries_Rate.to_decimal() or 0)
                for record in injuries_current_year_employees
            )
            previous_year_total_injuries_employees = sum(
                float(record.Total_Injuries_Rate.to_decimal() or 0)
                for record in injuries_previous_year_employees
            )
            # Fetch Total Work Related Injuries for Workers for the current and previous financial years
            injuries_current_year_workers = Total_Work_Related_Injuries.objects.filter(
                Financial_Year=financial_year, Segment="Workers"
            )
            injuries_previous_year_workers = Total_Work_Related_Injuries.objects.filter(
                Financial_Year=previous_financial_year, Segment="Workers"
            )
            current_year_total_injuries_workers = sum(
                float(record.Total_Injuries_Rate.to_decimal() or 0)
                for record in injuries_current_year_workers
            )
            previous_year_total_injuries_workers = sum(
                float(record.Total_Injuries_Rate.to_decimal() or 0)
                for record in injuries_previous_year_workers
            )

            # ---------- No_Of_Fatalities ----------------------------#
            fatalities_current_year_employees = No_Of_Fatalities.objects.filter(
                Financial_Year=financial_year, Segment="Employees"
            )
            fatalities_previous_year_employees = No_Of_Fatalities.objects.filter(
                Financial_Year=previous_financial_year, Segment="Employees"
            )
            current_year_total_fatalities_employees = sum(
                float(record.Total_No_Of_Fatalities.to_decimal() or 0)
                for record in fatalities_current_year_employees
            )
            previous_year_total_fatalities_employees = sum(
                float(record.Total_No_Of_Fatalities.to_decimal() or 0)
                for record in fatalities_previous_year_employees
            )
            # Fetch No Of Fatalities for Workers for the current and previous financial years
            fatalities_current_year_workers = No_Of_Fatalities.objects.filter(
                Financial_Year=financial_year, Segment="Workers"
            )
            fatalities_previous_year_workers = No_Of_Fatalities.objects.filter(
                Financial_Year=previous_financial_year, Segment="Workers"
            )
            current_year_total_fatalities_workers = sum(
                float(record.Total_No_Of_Fatalities.to_decimal() or 0)
                for record in fatalities_current_year_workers
            )
            previous_year_total_fatalities_workers = sum(
                float(record.Total_No_Of_Fatalities.to_decimal() or 0)
                for record in fatalities_previous_year_workers
            )
            # ---------- Injury_Or_Ill_Health ----------------------------#
            injury_or_ill_health_current_year_employees = (
                Injury_Or_Ill_Health.objects.filter(
                    Financial_Year=financial_year, Segment="Employees"
                )
            )
            injury_or_ill_health_previous_year_employees = (
                Injury_Or_Ill_Health.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Employees"
                )
            )
            current_year_total_injury_or_ill_health_employees = sum(
                float(record.Total_Injury_Or_Ill_Health_Rate.to_decimal() or 0)
                for record in injury_or_ill_health_current_year_employees
            )
            previous_year_total_injury_or_ill_health_employees = sum(
                float(record.Total_Injury_Or_Ill_Health_Rate.to_decimal() or 0)
                for record in injury_or_ill_health_previous_year_employees
            )
            # Fetch Injury Or Ill Health for Workers for the current and previous financial years
            injury_or_ill_health_current_year_workers = (
                Injury_Or_Ill_Health.objects.filter(
                    Financial_Year=financial_year, Segment="Workers"
                )
            )
            injury_or_ill_health_previous_year_workers = (
                Injury_Or_Ill_Health.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Workers"
                )
            )
            current_year_total_injury_or_ill_health_workers = sum(
                float(record.Total_Injury_Or_Ill_Health_Rate.to_decimal() or 0)
                for record in injury_or_ill_health_current_year_workers
            )
            previous_year_total_injury_or_ill_health_workers = sum(
                float(record.Total_Injury_Or_Ill_Health_Rate.to_decimal() or 0)
                for record in injury_or_ill_health_previous_year_workers
            )

            try:
                description_obj_pd_5 = Policy_Details_Health_safety.objects.get(
                    Model_Name_Health_safety="Healthy Workplace"
                )
                description_obj_pd_5 = (
                    description_obj_pd_5.Descriptions_Health_safety
                    if description_obj_pd_5
                    else "-"
                )
            except ObjectDoesNotExist:
                description_obj_pd_5 = "-"

            current_working_condition = (
                Health_and_safety_related_complaints.objects.filter(
                    Financial_Year=financial_year, Complaint_Type="Working Conditions"
                ).first()
            )

            current_health_safety = Health_and_safety_related_complaints.objects.filter(
                Financial_Year=financial_year, Complaint_Type="Health & Safety"
            ).first()

            # Fetch data for the previous financial year
            previous_working_condition = (
                Health_and_safety_related_complaints.objects.filter(
                    Financial_Year=previous_financial_year,
                    Complaint_Type="Working Conditions",
                ).first()
            )

            previous_health_safety = (
                Health_and_safety_related_complaints.objects.filter(
                    Financial_Year=previous_financial_year,
                    Complaint_Type="Health & Safety",
                ).first()
            )

            try:
                assessment_of_the_year = (
                    Assessment_Of_Plants_And_Offices_Health_And_Safety.objects.get(
                        Financial_Year=financial_year
                    )
                )
                Working_Conditions = (
                    str(
                        assessment_of_the_year.Percentage_Assessed_For_Working_Conditions
                    )
                    if assessment_of_the_year.Percentage_Assessed_For_Working_Conditions
                    else "-"
                )
                Health_And_Safety = (
                    str(
                        assessment_of_the_year.Percentage_Assessed_For_Health_And_Safety
                    )
                    if assessment_of_the_year.Percentage_Assessed_For_Health_And_Safety
                    else "-"
                )
            except Assessment_Of_Plants_And_Offices_Health_And_Safety.DoesNotExist:
                Working_Conditions = "-"
                Health_And_Safety = "-"

            try:
                description_obj_pd4 = Policy_Details_Health_safety.objects.get(
                    Model_Name_Health_safety="Safety Related Incidence"
                )
                description_obj_pd4 = (
                    description_obj_pd4.Descriptions_Health_safety
                    if description_obj_pd4
                    else "-"
                )
            except ObjectDoesNotExist:
                description_obj_pd4 = "-"

            try:
                description_obj_pd1 = Policy_Details_Health_safety.objects.filter(
                    Model_Name_Health_safety="Value Chain Partners"
                ).first()
                description_obj_pd1 = (
                    description_obj_pd1.Descriptions_Health_safety
                    if description_obj_pd1
                    else "-"
                )
            except ObjectDoesNotExist:
                description_obj_pd1 = "-"

            ##################P3 LI 1 Employees,Workers ############################################
            description_obj_pd3 = "-"
            description_obj_pd2 = "-"

            try:
                description_obj_pd3 = Policy_Details_Health_safety.objects.get(
                    Model_Name_Health_safety="Event of Death employees"
                )
                is_verified_pd3 = (
                    description_obj_pd3.Is_Verified if description_obj_pd3 else "-"
                )
                desc_pd3 = (
                    description_obj_pd3.Descriptions_Health_safety
                    if description_obj_pd3
                    else "-"
                )
            except ObjectDoesNotExist:
                is_verified_pd3 = "-"
                desc_pd3 = "-"

            try:
                description_obj_pd2 = Policy_Details_Health_safety.objects.get(
                    Model_Name_Health_safety="Event of death workers"
                )
                is_verified_pd2 = (
                    description_obj_pd2.Is_Verified if description_obj_pd2 else "-"
                )
                desc_pd2 = (
                    description_obj_pd2.Descriptions_Health_safety
                    if description_obj_pd2
                    else "-"
                )
            except ObjectDoesNotExist:
                is_verified_pd2 = "-"
                desc_pd2 = "-"

            principle_3_li_1 = [
                f"Employee: {'Yes' if description_obj_pd3 and is_verified_pd3 else 'No'}",
                f"Worker: {'Yes' if description_obj_pd2 and is_verified_pd2 else 'No'}",
            ]
            principle_3_li_1 = [{
              "Employee":   f"Employee: {'Yes' if desc_pd3 == 'Yes' else 'No'}",
             "Worker" :  f"Worker: {'Yes' if  desc_pd2 == 'Yes' else 'No'}",
            }]
            ########################################################################################

            # Initialize totals for both current and previous years
            current_year_total_no_of_affected_employees = 0
            current_year_total_no_of_affected_workers = 0
            current_year_rehabilitated_and_placed_in_suitable_employee = 0
            current_year_rehabilitated_and_placed_in_suitable_workers = 0

            previous_year_total_no_of_affected_employees = 0
            previous_year_total_no_of_affected_workers = 0
            previous_year_rehabilitated_and_placed_in_suitable_employee = 0
            previous_year_rehabilitated_and_placed_in_suitable_workers = 0

            # Get the records for the current financial year
            current_year_records = (
                Suffered_High_Consequence_Work_Related_Injury.objects.filter(
                    Financial_Year=financial_year,
                )
            )

            # Add the values from the current year records
            for record in current_year_records:
                current_year_total_no_of_affected_employees += (
                    record.Total_No_Of_Affected_Employees or 0
                )
                current_year_total_no_of_affected_workers += (
                    record.Total_No_Of_Affected_Workers or 0
                )
                current_year_rehabilitated_and_placed_in_suitable_employee += (
                    record.Rehabilitated_And_Placed_In_Suitable_Employee or 0
                )
                current_year_rehabilitated_and_placed_in_suitable_workers += (
                    record.Rehabilitated_And_Placed_In_Suitable_Workers or 0
                )

            # Get the records for the previous financial year
            previous_year_records = (
                Suffered_High_Consequence_Work_Related_Injury.objects.filter(
                    Financial_Year=previous_financial_year,
                )
            )

            # Add the values from the previous year records
            for record in previous_year_records:
                previous_year_total_no_of_affected_employees += (
                    record.Total_No_Of_Affected_Employees or 0
                )
                previous_year_total_no_of_affected_workers += (
                    record.Total_No_Of_Affected_Workers or 0
                )
                previous_year_rehabilitated_and_placed_in_suitable_employee += (
                    record.Rehabilitated_And_Placed_In_Suitable_Employee or 0
                )
                previous_year_rehabilitated_and_placed_in_suitable_workers += (
                    record.Rehabilitated_And_Placed_In_Suitable_Workers or 0
                )

            try:
                description_obj_pd = Policy_Details_Health_safety.objects.get(
                    Model_Name_Health_safety="Transition Assistance PGM"
                )
                description_obj_pd = (
                    description_obj_pd.Descriptions_Health_safety
                    if description_obj_pd is not None
                    else "-"
                )
            except ObjectDoesNotExist:
                description_obj_pd = "-"

            ##################################### P3 LI 5 #########################################################################
            current_data = {
                "Percentage_Assessed_For_Working_Conditions": 0,
                "Percentage_Assessed_For_Health_And_Safety": 0,
                "Number_of_Supplier": 0,
            }
            previous_data = {
                "Percentage_Assessed_For_Working_Conditions": 0,
                "Percentage_Assessed_For_Health_And_Safety": 0,
                "Number_of_Supplier": 0,
            }

            # Fetch current financial year data
            try:
                current_assessment = (
                    Assessment_Of_Value_Chain_Partners_Health_And_Safety.objects.get(
                        Financial_Year=financial_year
                    )
                )
                current_data["Percentage_Assessed_For_Working_Conditions"] = (
                    str(current_assessment.Percentage_Assessed_For_Working_Conditions)
                    if current_assessment.Percentage_Assessed_For_Working_Conditions
                    is not None
                    else 0
                )
                current_data["Percentage_Assessed_For_Health_And_Safety"] = (
                    str(current_assessment.Percentage_Assessed_For_Health_And_Safety)
                    if current_assessment.Percentage_Assessed_For_Health_And_Safety
                    is not None
                    else 0
                )
                current_data["Number_of_Supplier"] = (
                    str(current_assessment.Number_of_Supplier)
                    if current_assessment.Number_of_Supplier is not None
                    else 0
                )
            except Assessment_Of_Value_Chain_Partners_Health_And_Safety.DoesNotExist:
                # Data remains 0 as initialized
                pass

            # Fetch previous financial year data
            try:
                previous_assessment = (
                    Assessment_Of_Value_Chain_Partners_Health_And_Safety.objects.get(
                        Financial_Year=previous_financial_year
                    )
                )
                previous_data["Percentage_Assessed_For_Working_Conditions"] = (
                    str(previous_assessment.Percentage_Assessed_For_Working_Conditions)
                    if previous_assessment.Percentage_Assessed_For_Working_Conditions
                    is not None
                    else 0
                )
                previous_data["Percentage_Assessed_For_Health_And_Safety"] = (
                    str(previous_assessment.Percentage_Assessed_For_Health_And_Safety)
                    if previous_assessment.Percentage_Assessed_For_Health_And_Safety
                    is not None
                    else 0
                )
                previous_data["Number_of_Supplier"] = (
                    str(previous_assessment.Number_of_Supplier)
                    if previous_assessment.Number_of_Supplier is not None
                    else 0
                )
            except Assessment_Of_Value_Chain_Partners_Health_And_Safety.DoesNotExist:
                # Data remains 0 as initialized
                pass

            #########################################################################################################3
            try:
                description_obj_Policy = Policy_Details_Health_safety.objects.get(
                    Model_Name_Health_safety="Working of Partners"
                )
                description_obj_Policy = (
                    description_obj_Policy.Descriptions_Health_safety
                    if description_obj_Policy
                    else "-"
                )
            except ObjectDoesNotExist:
                description_obj_Policy = "-"

            ##################### p3 2 ###########################################################
            # Fetch records for current year and previous year
            records_current = Retirement_Benefits.objects.filter(
                Financial_Year=financial_year, Segment="Employees"
            )
            records_previous = Retirement_Benefits.objects.filter(
                Financial_Year=previous_financial_year, Segment="Employees"
            )

            records_wrk_current = Retirement_Benefits.objects.filter(
                Financial_Year=financial_year, Segment="Workers"
            )
            records_wrk_previous = Retirement_Benefits.objects.filter(
                Financial_Year=previous_financial_year, Segment="Workers"
            )

            # Initialize totals for current year
            total_pf_employees_current = 0
            total_pf_wrk_current = 0

            total_gratuity_employees_current = 0
            total_gratuity_wrk_current = 0

            total_esi_employees_current = 0
            total_esi_wrk_current = 0

            total_other_employees_current = 0
            total_other_wrk_current = 0

            total_super_annuation_employees_current = 0
            total_super_annuation_wrk_current = 0
            
           


            total_deducted_and_deposited_pf_employees_current = "-"
            total_deducted_and_deposited_super_annuation_employees_current = "-"
            total_deducted_and_deposited_gratuity_employees_current = "-"
            total_deducted_and_deposited_esi_employees_current = "-"
            total_deducted_and_deposited_other_employees_current = "-"

            total_deducted_and_deposited_pf_wrk_current = "-"
            total_deducted_and_deposited_super_annuation_wrk_current = "-"
            total_deducted_and_deposited_gratuity_wrk_current = "-"
            total_deducted_and_deposited_esi_wrk_current = "-"
            total_deducted_and_deposited_other_wrk_current = "-"

            # Initialize totals for previous year
            total_pf_employees_previous = 0
            total_pf_wrk_previous = 0

            total_gratuity_employees_previous = 0
            total_gratuity_wrk_previous = 0

            total_esi_employees_previous = 0
            total_esi_wrk_previous = 0

            total_other_employees_previous = 0
            total_other_wrk_previous = 0

            total_super_annuation_employees_previous = 0
            total_super_annuation_wrk_previous = 0

            total_deducted_and_deposited_pf_employees_previous = "-"
            total_deducted_and_deposited_super_annuation_employees_previous = "-"
            total_deducted_and_deposited_gratuity_employees_previous = "-"
            total_deducted_and_deposited_esi_employees_previous = "-"
            total_deducted_and_deposited_other_employees_previous = "-"

            total_deducted_and_deposited_pf_wrk_previous = "-"
            total_deducted_and_deposited_super_annuation_wrk_previous = "-"
            total_deducted_and_deposited_gratuity_wrk_previous = "-"
            total_deducted_and_deposited_esi_wrk_previous = "-"
            total_deducted_and_deposited_other_wrk_previous = "-"

            # Helper function to safely convert Decimal128 to float
            def to_float(value):
                if isinstance(value, Decimal):
                    return float(value)
                return float(str(value or 0))

            # Calculate totals for current year
            for record in records_current:
                total_pf_employees_current += to_float(record.Total_Covered_PF)
                total_gratuity_employees_current += to_float(
                    record.Total_Covered_Gratuity
                )
                total_esi_employees_current += to_float(record.Total_Covered_ESI)
                total_other_employees_current += to_float(record.Total_Covered_Other)
                total_super_annuation_employees_current += to_float(record.Total_Covered_Superannuation)
                
                total_deducted_and_deposited_pf_employees_current = (
                    record.Deducted_And_Deposited_PF or "-"
                )
                total_deducted_and_deposited_gratuity_employees_current = (
                    record.Deducted_And_Deposited_Gratuity or "-"
                )
                total_deducted_and_deposited_esi_employees_current = (
                    record.Deducted_And_Deposited_ESI or "-"
                )
                total_deducted_and_deposited_other_employees_current = (
                    record.Deducted_And_Deposited_Other or "-"
                )
                total_deducted_and_deposited_super_annuation_employees_current = (
                    record. Deducted_And_Deposited_Superannuation or "-"
                )

            # Calculate totals for previous year
            for record in records_previous:
                total_pf_employees_previous += to_float(record.Total_Covered_PF)
                total_gratuity_employees_previous += to_float(
                    record.Total_Covered_Gratuity
                )
                total_esi_employees_previous += to_float(record.Total_Covered_ESI)
                total_other_employees_previous += to_float(record.Total_Covered_Other)
                total_super_annuation_employees_previous += to_float(record.Total_Covered_Superannuation)
                
                total_deducted_and_deposited_pf_employees_previous = (
                    record.Deducted_And_Deposited_PF or "-"
                )
                total_deducted_and_deposited_gratuity_employees_previous = (
                    record.Deducted_And_Deposited_Gratuity or "-"
                )
                total_deducted_and_deposited_esi_employees_previous = (
                    record.Deducted_And_Deposited_ESI or "-"
                )
                total_deducted_and_deposited_other_employees_previous = (
                    record.Deducted_And_Deposited_Other or "-"
                )

                total_deducted_and_deposited_super_annuation_employees_previous = (
                    record. Deducted_And_Deposited_Superannuation or "-"
                )

            for record in records_wrk_current:
                total_pf_wrk_current += to_float(record.Total_Covered_PF)
                total_gratuity_wrk_current += to_float(record.Total_Covered_Gratuity)
                total_esi_wrk_current += to_float(record.Total_Covered_ESI)
                total_other_wrk_current += to_float(record.Total_Covered_Other)
                total_super_annuation_wrk_current += to_float(record.Total_Covered_Superannuation)
                



                total_deducted_and_deposited_pf_wrk_current = record.Deducted_And_Deposited_PF or ""
                total_deducted_and_deposited_gratuity_wrk_current = (
                    record.Deducted_And_Deposited_Gratuity or ""
                )
                total_deducted_and_deposited_esi_wrk_current = (
                    record.Deducted_And_Deposited_ESI or ""
                )
                total_deducted_and_deposited_other_wrk_current = (
                    record.Deducted_And_Deposited_Other or ""
                )

                total_deducted_and_deposited_super_annuation_wrk_current = (
                    record.Deducted_And_Deposited_Superannuation or ""
                )

            for record in records_wrk_previous:
                total_pf_wrk_previous += to_float(record.Total_Covered_PF)
                total_gratuity_wrk_previous += to_float(record.Total_Covered_Gratuity)
                total_esi_wrk_previous += to_float(record.Total_Covered_ESI)
                total_other_wrk_previous += to_float(record.Total_Covered_Other)
                total_super_annuation_wrk_previous += to_float(record.Total_Covered_Superannuation)

                total_deducted_and_deposited_pf_wrk_previous = record.Deducted_And_Deposited_PF or ""
                total_deducted_and_deposited_gratuity_wrk_previous = (
                    record.Deducted_And_Deposited_Gratuity or ""
                )
                total_deducted_and_deposited_esi_wrk_previous = (
                    record.Deducted_And_Deposited_ESI or ""
                )
                total_deducted_and_deposited_other_wrk_previous = (
                    record.Deducted_And_Deposited_Other or ""
                )
                total_deducted_and_deposited_super_annuation_wrk_previous = (
                    record.Deducted_And_Deposited_Superannuation or ""
                )


            ############################### P3 1c ############################################################
            current_year_records = CostIncurredOnWellbeingMeasures.objects.filter(
                Financial_Year=financial_year
            )
            current_year_cost = sum(
                conversion(record.percentage_cost_incurred)
                for record in current_year_records
            )

            previous_year_records = CostIncurredOnWellbeingMeasures.objects.filter(
                Financial_Year=previous_financial_year
            )
            previous_year_cost = sum(
                conversion(record.percentage_cost_incurred)
                for record in previous_year_records
            )

            # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Principle_3_EI_7 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2
            def conversion_(value):
                """Convert Decimal128, Decimal, int, or float to float, or return 0 if None."""
                if value is None:
                    return 0.0
                elif isinstance(value, Decimal128):
                    # Convert Decimal128 to Decimal, then to float
                    return float(value.to_decimal())
                elif isinstance(value, Decimal):
                    return float(value)
                elif isinstance(value, (int, float)):
                    return float(value)
                else:
                    return 0.0

            # Employee Summary for Current Year
            employee_records_current_year = EmployeeSummary.objects.filter(
                Financial_Year=financial_year
            )
            total_male_permanent_employees_current_year = 0
            total_female_permanent_employees_current_year = 0

            for emp in employee_records_current_year:
                total_male_permanent_employees_current_year += (
                    conversion_(emp.Male_Permanent) or 0
                )
                total_female_permanent_employees_current_year += (
                    conversion_(emp.Female_Permanent) or 0
                )

            # Employee Summary for Previous Year
            employee_records_previous_year = EmployeeSummary.objects.filter(
                Financial_Year=previous_financial_year
            )
            total_male_permanent_employees_previous_year = 0
            total_female_permanent_employees_previous_year = 0

            for emp in employee_records_previous_year:
                total_male_permanent_employees_previous_year += (
                    conversion_(emp.Male_Permanent) or 0
                )
                total_female_permanent_employees_previous_year += (
                    conversion_(emp.Female_Permanent) or 0
                )

            # Employees' Membership in Associations or Unions
            emp_membership_current_year_records = (
                Employees_Membership_In_Association_Or_Unions.objects.filter(
                    Financial_Year=financial_year
                )
            )
            emp_membership_previous_year_records = (
                Employees_Membership_In_Association_Or_Unions.objects.filter(
                    Financial_Year=previous_financial_year
                )
            )

            total_male_emp_membership_current_year = sum(
                float(conversion_(record.Permanent_Males))
                for record in emp_membership_current_year_records
            )
            total_female_emp_membership_current_year = sum(
                float(conversion_(record.Permanent_Females))
                for record in emp_membership_current_year_records
            )

            total_male_emp_membership_previous_year = sum(
                float(conversion_(record.Permanent_Males))
                for record in emp_membership_previous_year_records
            )
            total_female_emp_membership_previous_year = sum(
                float(conversion_(record.Permanent_Females))
                for record in emp_membership_previous_year_records
            )

            # Worker Summary for Current and Previous Years
            worker_records_current_year = WorkerSummary.objects.filter(
                Financial_Year=financial_year
            )
            worker_records_previous_year = WorkerSummary.objects.filter(
                Financial_Year=previous_financial_year
            )

            total_male_permanent_workers_current_year = sum(
                float(conversion_(record.Male_Permanent))
                for record in worker_records_current_year
            )
            total_female_permanent_workers_current_year = sum(
                float(conversion_(record.Female_Permanent))
                for record in worker_records_current_year
            )

            total_male_permanent_workers_previous_year = sum(
                float(conversion_(record.Male_Permanent))
                for record in worker_records_previous_year
            )
            total_female_permanent_workers_previous_year = sum(
                float(conversion_(record.Female_Permanent))
                for record in worker_records_previous_year
            )

            # Workers' Membership in Associations or Unions
            wrk_membership_current_year_records = (
                Workers_Membership_In_Association_Or_Unions.objects.filter(
                    Financial_Year=financial_year
                )
            )
            wrk_membership_previous_year_records = (
                Workers_Membership_In_Association_Or_Unions.objects.filter(
                    Financial_Year=previous_financial_year
                )
            )

            total_male_wrk_membership_current_year = sum(
                float(conversion_(record.Permanent_Males))
                for record in wrk_membership_current_year_records
            )
            total_female_wrk_membership_current_year = sum(
                float(conversion_(record.Permanent_Females))
                for record in wrk_membership_current_year_records
            )

            total_male_wrk_membership_previous_year = sum(
                float(conversion_(record.Permanent_Males))
                for record in wrk_membership_previous_year_records
            )
            total_female_wrk_membership_previous_year = sum(
                float(conversion_(record.Permanent_Females))
                for record in wrk_membership_previous_year_records
            )

            response_value1 = (
                round(
                    (
                        (
                            total_male_emp_membership_current_year
                            + total_female_emp_membership_current_year
                        )
                        / (
                            total_male_permanent_employees_current_year
                            + total_female_permanent_employees_current_year
                        )
                        * 100
                    ),
                    2,
                )
                if total_male_permanent_employees_current_year
                and total_female_permanent_employees_current_year not in [None, 0]
                else 0
            )

            response_value2 = (
                round(
                    (
                        (
                            total_male_emp_membership_previous_year
                            + total_female_emp_membership_previous_year
                        )
                        / (
                            total_male_permanent_employees_previous_year
                            + total_female_permanent_employees_previous_year
                        )
                        * 100
                    ),
                    2,
                )
                if total_male_permanent_employees_previous_year
                and total_female_permanent_employees_previous_year not in [None, 0]
                else 0
            )

            response_value3 = (
                round(
                    (
                        total_male_emp_membership_current_year
                        / total_male_permanent_employees_current_year
                    )
                    * 100,
                    2,
                )
                if total_male_permanent_employees_current_year not in [None, 0]
                else 0
            )
            response_value4 = (
                round(
                    (
                        total_male_emp_membership_previous_year
                        / total_male_permanent_employees_previous_year
                    )
                    * 100,
                    2,
                )
                if total_male_permanent_employees_previous_year not in [None, 0]
                else 0
            )
            response_value5 = (
                round(
                    (
                        total_female_emp_membership_current_year
                        / total_female_permanent_employees_current_year
                    )
                    * 100,
                    2,
                )
                if total_female_permanent_employees_current_year not in [None, 0]
                else 0
            )
            response_value6 = (
                round(
                    (
                        total_female_emp_membership_previous_year
                        / total_female_permanent_employees_previous_year
                    )
                    * 100,
                    2,
                )
                if total_female_permanent_employees_previous_year not in [None, 0]
                else 0
            )
            response_value7 = (
                round(
                    (
                        (
                            total_male_wrk_membership_current_year
                            + total_female_wrk_membership_current_year
                        )
                        / (
                            total_male_permanent_workers_current_year
                            + total_female_permanent_workers_current_year
                        )
                        * 100
                    ),
                    2,
                )
                if total_male_permanent_workers_current_year
                and total_female_permanent_workers_current_year not in [None, 0]
                else 0
            )
            response_value8 = (
                round(
                    (
                        (
                            total_male_wrk_membership_previous_year
                            + total_female_wrk_membership_previous_year
                        )
                        / (
                            total_male_permanent_workers_previous_year
                            + total_female_permanent_workers_previous_year
                        )
                        * 100
                    ),
                    2,
                )
                if total_male_permanent_workers_previous_year
                and total_female_permanent_workers_previous_year not in [None, 0]
                else 0
            )

            response_value9 = (
                round(
                    (
                        total_male_wrk_membership_current_year
                        / total_male_permanent_workers_current_year
                    )
                    * 100,
                    2,
                )
                if total_male_permanent_workers_current_year not in [None, 0]
                else 0
            )
            response_value10 = (
                round(
                    (
                        total_male_wrk_membership_previous_year
                        / total_male_permanent_workers_previous_year
                    )
                    * 100,
                    2,
                )
                if total_male_permanent_workers_previous_year not in [None, 0]
                else 0
            )
            response_value11 = (
                round(
                    (
                        total_female_wrk_membership_current_year
                        / total_female_permanent_workers_current_year
                    )
                    * 100,
                    2,
                )
                if total_female_permanent_workers_current_year not in [None, 0]
                else 0
            )
            response_value12 = (
                round(
                    (
                        total_female_wrk_membership_previous_year
                        / total_female_permanent_workers_previous_year
                    )
                    * 100,
                    2,
                )
                if total_female_permanent_workers_previous_year not in [None, 0]
                else 0
            )
            # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2


            response_data = {
                "Section_C_P3": {
                    "Principle_3_EI_1_1a": [
                        get_totals(financial_year, "Employees", "Permanent"),
                        get_totals(financial_year, "Employees", "Non-Permanent"),
                    ],
                    "Principle_3_EI_1_1b": [
                        get_totals(financial_year, "Workers", "Permanent"),
                        get_totals(financial_year, "Workers", "Non-Permanent"),
                    ],
                    "Principle_3_EI_1_1c": [
                        {
                            "current_year_cost": (
                                current_year_cost if current_year_cost else "-"
                            ),
                            "previous_year_cost": (
                                previous_year_cost if previous_year_cost else "-"
                            ),
                        }
                    ],
                    "Principle_3_EI_2_PF": [
                        {
                            "total_pf_employees_current": total_pf_employees_current,
                            "total_pf_wrk_current": total_pf_wrk_current,
                            "total_deducted_pf_employees_current": total_deducted_and_deposited_pf_employees_current,
                            "total_pf_employees_previous": total_pf_employees_previous,
                            "total_pf_wrk_previous": total_pf_wrk_previous,
                            "total_deducted_pf_employees_previous":total_deducted_and_deposited_pf_employees_previous,
                        }
                    ],
                    "Principle_3_EI_2_GRT": [
                        {
                            "total_gratuity_employees_current": total_gratuity_employees_current,
                            "total_gratuity_wrk_current": total_gratuity_wrk_current,
                            "total_deducted_and_deposited_gratuity_employees_current": total_deducted_and_deposited_gratuity_employees_current,
                            "total_gratuity_employees_previous": total_gratuity_employees_previous,
                            "total_gratuity_wrk_previous": total_gratuity_wrk_previous,
                            "total_deducted_and_deposited_gratuity_employees_previous": total_deducted_and_deposited_gratuity_employees_previous,
                        }
                    ],
                    "Principle_3_EI_2_ESI": [
                        {
                            "total_esi_employees_current": total_esi_employees_current,
                            "total_esi_wrk_current": total_esi_wrk_current,
                            "total_deducted_and_deposited_esi_employees_current": total_deducted_and_deposited_esi_employees_current,
                            "total_esi_employees_previous": total_esi_employees_previous,
                            "total_esi_wrk_previous": total_esi_wrk_previous,
                            "total_deducted_and_deposited_esi_employees_previous": total_deducted_and_deposited_esi_employees_previous,
                        }
                    ],
                    "Principle_3_EI_2_OTHER": [
                        {
                            "total_other_employees_current": total_other_employees_current,
                            "total_other_wrk_current": total_other_wrk_current,
                            "total_deducted_and_deposited_other_employees_current": total_deducted_and_deposited_other_employees_current,
                            "total_other_employees_previous": total_other_employees_previous,
                            "total_other_wrk_previous": total_other_wrk_previous,
                            "total_deducted_and_deposited_other_employees_previous": total_deducted_and_deposited_other_employees_previous,
                        }
                    ],
                     "Principle_3_EI_2_SUPERANNUATION": [
                        {
                            "total_super_annuation_employees_current": total_super_annuation_employees_current,
                            "total_super_annuation_wrk_current": total_super_annuation_wrk_current,
                            "total_deducted_and_deposited_super_annuation_employees_current": total_deducted_and_deposited_super_annuation_employees_current,
                            "total_super_annuation_employees_previous": total_super_annuation_employees_previous,
                            "total_super_annuation_wrk_previous": total_super_annuation_wrk_previous,
                            "total_deducted_and_deposited_super_annuation_employees_previous": total_deducted_and_deposited_super_annuation_employees_previous,
                        }
                    ],
                    "Principle_3_EI_3": [
                        {"description_obj_EI_3": description_obj_EI_3}
                    ],
                    "Principle_3_EI_4": [
                        {"description_obj_EI_4": description_obj_EI_4}
                    ],
                    "Principle_3_EI_5_MALE": [
                        {
                            "return_to_work_rate_for_male_employee": (
                                return_to_work_rate_for_male_employee
                                if return_to_work_rate_for_male_employee != 0
                                else "-"
                            ),
                            "retention_rate_for_male_employee": (
                                retention_rate_for_male_employee
                                if retention_rate_for_male_employee != 0
                                else "-"
                            ),
                            "return_to_work_rate_male_worker": (
                                return_to_work_rate_male_worker
                                if return_to_work_rate_male_worker != 0
                                else "-"
                            ),
                            "retention_rate_for_male_worker": (
                                retention_rate_for_male_worker
                                if retention_rate_for_male_worker != 0
                                else "-"
                            ),
                        }
                    ],
                    "Principle_3_EI_5_FEMALE": [{
                        "return_to_work_rate_for_female_employee":
                        (
                            return_to_work_rate_for_female_employee
                            if return_to_work_rate_for_female_employee != 0
                            else "-"
                        ),
                        "retention_rate_for_female_employee":
                        (
                            retention_rate_for_female_employee
                            if retention_rate_for_female_employee != 0
                            else "-"
                        ),
                        "return_to_work_rate_female_worker":
                        (
                            return_to_work_rate_female_worker
                            if return_to_work_rate_female_worker != 0
                            else "-"
                        ),
                        "retention_rate_for_female_worker":
                        (
                            retention_rate_for_female_worker
                            if retention_rate_for_female_worker != 0
                            else "-"
                        ),
                    }],
                    "Principle_3_EI_5_TOTAL": [{
                        "total_return_to_work_rate_employee":
                        (
                            total_return_to_work_rate_employee
                            if total_return_to_work_rate_employee != 0
                            else "-"
                        ),
                        "total_retention_rate_employee":
                        (
                            total_retention_rate_employee
                            if total_retention_rate_employee != 0
                            else "-"
                        ),
                        "total_return_to_work_rate_of_workers":
                        (
                            total_return_to_work_rate_of_workers
                            if total_return_to_work_rate_of_workers != 0
                            else "-"
                        ),
                        "total_retention_rate_workers":
                        (
                            total_retention_rate_workers
                            if total_retention_rate_workers != 0
                            else "-"
                        ),
                    }],
                  "Principle_3_EI_6_PEM_EMP": [
                        {
                            "grievances_redress_pem_emp": 
                                f"{item['Yes_No'].upper()},{item['Description']}" 
                                if item["Yes_No"].lower() == "yes" and item.get("Description") 
                                else "-"
                                for item in grievances_redress_obj1
                        } if grievances_redress_obj1 else {
                            "grievances_redress_pem_emp": "-"
                        }
                    ],


                    "Principle_3_EI_6_NON_EMP": [
                        {
                            "grievances_redress_non_pem_emp": 
                                f"{item['Yes_No'].upper()},{item['Description']}"
                                if item["Yes_No"] == "Yes"
                                else "-"
                                for item in grievances_redress_obj2
                        }if grievances_redress_obj2 else {
                            "grievances_redress_pem_emp": "-"
                        }
                        
                    ],

                    "Principle_3_EI_6_PEM_WRK": [
                        {
                            "grievances_redress_pem_wrk": 
                                f"{item['Yes_No'].upper()},{item['Description']}"
                                if item["Yes_No"] == "Yes"
                                else "-"
                                for item in grievances_redress_obj3
                         } if grievances_redress_obj3 else {
                            "grievances_redress_pem_emp": "-"
                        }
                        
                    ],

                    "Principle_3_EI_6_NON_WRK": [
                        {
                            "grievances_redress_non_pem_wrk": 
                                f"{item['Yes_No'].upper()},{item['Description']}"
                                if item["Yes_No"] == "Yes"
                                else "-"
                                for item in grievances_redress_obj4
                        }if grievances_redress_obj4 else {
                            "grievances_redress_pem_emp": "-"
                        }
                        
                    ],


                    "Principle_3_EI_7_EMP_TOTAL": [{
                         "current_year_total_permanent_employees":
                        (
                            (
                                total_male_permanent_employees_current_year
                                + total_female_permanent_employees_current_year
                            )
                            if total_male_permanent_employees_current_year
                            and total_female_permanent_employees_current_year
                            is not None
                            else 0
                        ),
                         "current_year_total_membership":
                        (
                            (
                                total_male_emp_membership_current_year
                                + total_female_emp_membership_current_year
                            )
                            if total_male_emp_membership_current_year
                            and total_female_emp_membership_current_year is not None
                            else 0
                        ),
                         "current_year_membership_percentage": f"{response_value1}%",
                        "previous_year_total_permanent_employees":
                        (
                            (
                                total_male_permanent_employees_previous_year
                                + total_female_permanent_employees_previous_year
                            )
                            if total_male_permanent_employees_previous_year
                            and total_female_permanent_employees_previous_year
                            is not None
                            else 0
                        ),
                         "previous_year_total_membership":
                        (
                            (
                                total_male_emp_membership_previous_year
                                + total_female_emp_membership_previous_year
                            )
                            if total_male_emp_membership_previous_year
                            and total_female_emp_membership_previous_year is not None
                            else 0
                        ),
                        "previous_year_membership_percentage": f"{response_value2}%",
                }],
                
                    "Principle_3_EI_7_EMP_MALE": [{
                        "current_year_total_permanent_employees_male":
                        (
                            total_male_permanent_employees_current_year
                            if total_male_permanent_employees_current_year is not None
                            else 0
                        ),
                         "current_year_total_membership_male":
                        (
                            total_male_emp_membership_current_year
                            if total_male_emp_membership_current_year is not None
                            else 0
                        ),
                        "current_year_membership_percentage_male": f"{response_value3}%",
                        "previous_year_total_permanent_employees_male":
                        (
                            total_male_permanent_employees_previous_year
                            if total_male_permanent_employees_previous_year is not None
                            else 0
                        ),
                        "previous_year_total_membership_male":
                        (
                            total_male_emp_membership_previous_year
                            if total_male_emp_membership_previous_year is not None
                            else 0
                        ),
                        "previous_year_membership_percentage_male":f"{response_value4}%",
                    }],

                    "Principle_3_EI_7_EMP_FEMALE": [{
                        "current_year_total_permanent_employees_female":
                        (
                            total_female_permanent_employees_current_year
                            if total_female_permanent_employees_current_year is not None
                            else 0
                        ),
                        "current_year_total_membership_female":
                        (
                            total_female_emp_membership_current_year
                            if total_female_emp_membership_current_year is not None
                            else 0
                        ),
                        "current_year_membership_percentage_female": f"{response_value5}%",
                        # if total_female_permanent_employees_current_year is not None else 0,
                        "previous_year_total_permanent_employees_female":
                        (
                            total_female_permanent_employees_previous_year
                            if total_female_permanent_employees_previous_year
                            is not None
                            else 0
                        ),
                        "previous_year_total_membership_female":
                        (
                            total_female_emp_membership_previous_year
                            if total_female_emp_membership_previous_year is not None
                            else 0
                        ),
                        "previous_year_membership_percentage_female": f"{response_value6}%",
                        # if total_female_permanent_employees_previous_year not in  [None,0] else 0
                    }],

                    "Principle_3_EI_7_WRK_TOTAL": [{
                        "current_year_total_permanent_workers":
                        (
                            (
                                total_male_permanent_workers_current_year
                                + total_female_permanent_workers_current_year
                            )
                            if total_male_permanent_workers_current_year
                            and total_female_permanent_workers_current_year is not None
                            else 0
                        ),
                        "current_year_total_membership_workers":
                        (
                            (
                                total_male_wrk_membership_current_year
                                + total_female_wrk_membership_current_year
                            )
                            if total_male_wrk_membership_current_year
                            and total_female_wrk_membership_current_year is not None
                            else 0
                        ),
                        "current_year_membership_percentage_workers": f"{response_value7}%",
                        "previous_year_total_permanent_workers":
                        (
                            (
                                total_male_permanent_workers_previous_year
                                + total_female_permanent_workers_previous_year
                            )
                            if total_male_permanent_workers_previous_year
                            and total_female_permanent_workers_previous_year is not None
                            else 0
                        ),
                        "previous_year_total_membership_workers":
                        (
                            (
                                total_male_wrk_membership_previous_year
                                + total_female_wrk_membership_previous_year
                            )
                            if total_male_wrk_membership_previous_year
                            and total_female_wrk_membership_previous_year
                            else 0
                        ),
                         "previous_year_membership_percentage_workers": f"{response_value8}%",
                    }],


                    "Principle_3_EI_7_WRK_MALE": [{
                         "current_year_total_permanent_workers":
                        (
                            total_male_permanent_workers_current_year
                            if total_male_permanent_workers_current_year
                            else 0
                        ),
                        "current_year_total_membership_workers":
                        (
                            total_male_wrk_membership_current_year
                            if total_male_wrk_membership_current_year
                            else 0
                        ),
                        "current_year_membership_percentage_workers": f"{response_value9}%",
                        "previous_year_total_permanent_workers":
                        (
                            total_male_permanent_workers_previous_year
                            if total_male_permanent_workers_previous_year
                            else 0
                        ),
                        "previous_year_total_membership_workers":
                        (
                            total_male_wrk_membership_previous_year
                            if total_male_wrk_membership_previous_year
                            else 0
                        ),
                        "previous_year_membership_percentage_workers": f"{response_value10}%",
                    }],

                    "Principle_3_EI_7_WRK_FEMALE": [{
                        "current_year_total_permanent_workers":
                        (
                            total_female_permanent_workers_current_year
                            if total_female_permanent_workers_current_year
                            else 0
                        ),
                        "current_year_total_membership_workers":
                        (
                            total_female_wrk_membership_current_year
                            if total_female_wrk_membership_current_year
                            else 0
                        ),
                        "current_year_membership_percentage_workers": f"{response_value11}%",
                        "previous_year_total_permanent_workers":
                        (
                            total_female_permanent_workers_previous_year
                            if total_female_permanent_workers_previous_year
                            else 0
                        ),
                        "previous_year_total_membership_workers": 
                        (
                            total_female_wrk_membership_previous_year
                            if total_female_wrk_membership_previous_year
                            else 0
                        ),
                        "previous_year_membership_percentage_workers": f"{response_value12}%",
                    }],

                    "Principle_3_EI_8_EMP_MALE": [{
                                "current_year_total_employees": (
                                    current_year_total_male_employees
                                    if current_year_total_male_employees
                                    else 0
                                ),
                                "current_year_health_and_safety_employees": (
                                    current_year_health_and_safety_male_employees
                                    if current_year_health_and_safety_male_employees
                                    else 0
                                ),
                                "current_year_health_and_safety_percentage": (
                                    round(
                                        (
                                            current_year_health_and_safety_male_employees
                                            / current_year_total_male_employees
                                            * 100
                                        ), 2, ) if current_year_total_male_employees  else 0
                                ),
                                "current_year_skill_upgradation_employees": (
                                    current_year_skill_upgradation_male_employees
                                    if current_year_skill_upgradation_male_employees
                                    else 0
                                ),
                                "current_year_skill_upgradation_percentage": (
                                    round(
                                        (
                                            current_year_skill_upgradation_male_employees
                                            / current_year_total_male_employees
                                            * 100
                                        ), 2,)
                                    if current_year_total_male_employees  else 0
                                ),
                                "previous_year_total_employees": (
                                    previous_year_total_male_employees
                                    if previous_year_total_male_employees
                                    else 0
                                ),
                                "previous_year_health_and_safety_employees": (
                                    previous_year_health_and_safety_male_employees
                                    if previous_year_health_and_safety_male_employees
                                    else 0
                                ),
                                "previous_year_health_and_safety_percentage": (
                                    round(
                                        (
                                            previous_year_health_and_safety_male_employees
                                            / previous_year_total_male_employees
                                            * 100
                                        ), 2, )  if previous_year_total_male_employees else 0
                                ),
                                "previous_year_skill_upgradation_employees": (
                                    previous_year_skill_upgradation_male_employees
                                    if previous_year_skill_upgradation_male_employees
                                    else 0
                                ),
                                "previous_year_skill_upgradation_percentage": (
                                    round(
                                        (
                                            previous_year_skill_upgradation_male_employees
                                            / previous_year_total_male_employees
                                            * 100
                                        ),  2, )
                                    if previous_year_total_male_employees else 0
                                ),
                            }],
 
                    "Principle_3_EI_8_EMP_FEMALE": [
                            {
                                "current_year_total_employees": current_year_total_female_employees or 0,
                                "current_year_health_and_safety_employees": current_year_health_and_safety_female_employees or 0,
                                "current_year_health_and_safety_percentage": (
                                    round(
                                        current_year_health_and_safety_female_employees
                                        / current_year_total_female_employees * 100, 2
                                    )
                                    if current_year_total_female_employees else 0
                                ),
                                "current_year_skill_upgradation_employees": current_year_skill_upgradation_female_employees or 0,
                                "current_year_skill_upgradation_percentage": (
                                    round(
                                        current_year_skill_upgradation_female_employees
                                        / current_year_total_female_employees * 100, 2
                                    )
                                    if current_year_total_female_employees else 0
                                ),
                                "previous_year_total_employees": previous_year_total_female_employees or 0,
                                "previous_year_health_and_safety_employees": previous_year_health_and_safety_female_employees or 0,
                                "previous_year_health_and_safety_percentage": (
                                    round(
                                        previous_year_health_and_safety_female_employees
                                        / previous_year_total_female_employees * 100, 2
                                    )
                                    if previous_year_total_female_employees else 0
                                ),
                                "previous_year_skill_upgradation_employees": previous_year_skill_upgradation_female_employees or 0,
                                "previous_year_skill_upgradation_percentage": (
                                    round(
                                        previous_year_skill_upgradation_female_employees
                                        / previous_year_total_female_employees * 100, 2
                                    )
                                    if previous_year_total_female_employees else 0
                                ),
                            }
                                            ],
                    "Principle_3_EI_8_EMP_TOTAL": [
                            {
                                "current_year_total_employees": round(
                                    (current_year_total_male_employees or 0)
                                    + (current_year_total_female_employees or 0), 2
                                ),
                                "current_year_health_and_safety_employees": round(
                                    (current_year_health_and_safety_male_employees or 0)
                                    + (current_year_health_and_safety_female_employees or 0), 2
                                ),
                                "current_year_health_and_safety_percentage": (
                                    round(
                                        ( (current_year_health_and_safety_male_employees or 0)
                                            + (current_year_health_and_safety_female_employees or 0))  / (
                                            (current_year_total_male_employees or 0)
                                            + (current_year_total_female_employees or 0)
                                        )  * 100,  2, )
                                    if current_year_total_male_employees or current_year_total_female_employees else 0
                                ),
                                "current_year_skill_upgradation_employees": round(
                                    (current_year_skill_upgradation_male_employees or 0)
                                    + (current_year_skill_upgradation_female_employees or 0), 2
                                ),
                                "current_year_skill_upgradation_percentage": (
                                    round(
                                        (
                                            (current_year_skill_upgradation_male_employees or 0)
                                            + (current_year_skill_upgradation_female_employees or 0)  )/ (
                                            (current_year_total_male_employees or 0)
                                            + (current_year_total_female_employees or 0)
                                        ) * 100, 2, )
                                    if current_year_total_male_employees or current_year_total_female_employees else 0
                                ),
                                "previous_year_total_employees": round(
                                    (previous_year_total_male_employees or 0)
                                    + (previous_year_total_female_employees or 0), 2
                                ),
                                "previous_year_health_and_safety_employees": round(
                                    (previous_year_health_and_safety_male_employees or 0)
                                    + (previous_year_health_and_safety_female_employees or 0), 2
                                ),
                                "previous_year_health_and_safety_percentage": (
                                    round(
                                        ( (previous_year_health_and_safety_male_employees or 0) + (previous_year_health_and_safety_female_employees or 0) )
                                        / ( (previous_year_total_male_employees or 0) + (previous_year_total_female_employees or 0) ) * 100, 2, )
                                    if previous_year_total_male_employees or previous_year_total_female_employees else 0
                                ),
                                "previous_year_skill_upgradation_employees": round(
                                    (previous_year_skill_upgradation_male_employees or 0)
                                    + (previous_year_skill_upgradation_female_employees or 0), 2
                                ),
                                "previous_year_skill_upgradation_percentage": (
                                    round(
                                        (
                                            (previous_year_skill_upgradation_male_employees or 0) + (previous_year_skill_upgradation_female_employees or 0) ) 
                                            / ( (previous_year_total_male_employees or 0) + (previous_year_total_female_employees or 0) ) * 100, 2, ) 
                                            if previous_year_total_male_employees or previous_year_total_female_employees else 0),
                            }
                        ],

                        "Principle_3_EI_8_WRK_MALE": [{
                                "current_year_total_male_workers": current_year_total_male_workers or 0,
                                "current_year_health_and_safety_male_workers": current_year_health_and_safety_male_workers or 0,
                                "current_year_health_and_safety_percentage": round(
                                    (current_year_health_and_safety_male_workers / current_year_total_male_workers * 100), 2
                                ) if current_year_total_male_workers else 0,
                                "current_year_skill_upgradation_male_workers": current_year_skill_upgradation_male_workers or 0,
                                "current_year_skill_upgradation_percentage": round(
                                    (current_year_skill_upgradation_male_workers / current_year_total_male_workers * 100), 2
                                ) if current_year_total_male_workers else 0,
                                "previous_year_total_male_workers": previous_year_total_male_workers or 0,
                                "previous_year_health_and_safety_male_workers": previous_year_health_and_safety_male_workers or 0,
                                "previous_year_health_and_safety_percentage": round(
                                    (previous_year_health_and_safety_male_workers / previous_year_total_male_workers * 100), 2
                                ) if previous_year_total_male_workers else 0,
                                "previous_year_skill_upgradation_male_workers": previous_year_skill_upgradation_male_workers or 0,
                                "previous_year_skill_upgradation_percentage": round(
                                    (previous_year_skill_upgradation_male_workers / previous_year_total_male_workers * 100), 2
                                ) if previous_year_total_male_workers else 0,
                            }
                        ],

                    "Principle_3_EI_8_WRK_FEMALE": [{
                            "current_year_total_female_workers": current_year_total_female_workers or 0,
                            "current_year_health_and_safety_female_workers": current_year_health_and_safety_female_workers or 0,
                            "current_year_health_and_safety_percentage": round(
                                (current_year_health_and_safety_female_workers / current_year_total_female_workers * 100), 2
                            ) if current_year_total_female_workers else 0,
                            "current_year_skill_upgradation_female_workers": current_year_skill_upgradation_female_workers or 0,
                            "current_year_skill_upgradation_percentage": round(
                                (current_year_skill_upgradation_female_workers / current_year_total_female_workers * 100), 2
                            ) if current_year_total_female_workers else 0,
                            "previous_year_total_female_workers": previous_year_total_female_workers or 0,
                            "previous_year_health_and_safety_female_workers": previous_year_health_and_safety_female_workers or 0,
                            "previous_year_health_and_safety_percentage": round(
                                (previous_year_health_and_safety_female_workers / previous_year_total_female_workers * 100), 2
                            ) if previous_year_total_female_workers else 0,
                            "previous_year_skill_upgradation_female_workers": previous_year_skill_upgradation_female_workers or 0,
                            "previous_year_skill_upgradation_percentage": round(
                                (previous_year_skill_upgradation_female_workers / previous_year_total_female_workers * 100), 2
                            ) if previous_year_total_female_workers else 0,
                        }
                    ],

                    "Principle_3_EI_8_WRK_TOTAL": [{                
                        "total_workers_current_year":
                        (
                            round(
                                current_year_total_male_workers
                                + current_year_total_female_workers,
                                2,
                            )
                            if current_year_total_male_workers is not None
                            and current_year_total_female_workers is not None
                            else 0
                        ),
                        "health_and_safety_workers_current_year":
                        (
                            round(
                                current_year_health_and_safety_male_workers
                                + current_year_health_and_safety_female_workers,
                                2,
                            )
                            if current_year_health_and_safety_male_workers is not None
                            and current_year_health_and_safety_female_workers
                            is not None
                            else 0
                        ),
                        "health_and_safety_percentage_current_year":   
                        (
                            round(
                                (
                                    (
                                        current_year_health_and_safety_male_workers
                                        + current_year_health_and_safety_female_workers
                                    )
                                    / (
                                        current_year_total_male_workers
                                        + current_year_total_female_workers
                                    )
                                    * 100
                                ),
                                2,
                            )
                            if current_year_total_male_workers
                            and current_year_total_female_workers
                            else 0
                        ),
                         "skill_upgradation_workers_current_year": 
                        (
                            round(
                                current_year_skill_upgradation_male_workers
                                + current_year_skill_upgradation_female_workers,
                                2,
                            )
                            if current_year_skill_upgradation_male_workers is not None
                            and current_year_skill_upgradation_female_workers
                            is not None
                            else 0
                        ),
                        "skill_upgradation_percentage_current_year": 
                        (
                            round(
                                (
                                    (
                                        current_year_skill_upgradation_male_workers
                                        + current_year_skill_upgradation_female_workers
                                    )
                                    / (
                                        current_year_total_male_workers
                                        + current_year_total_female_workers
                                    )
                                    * 100
                                ),
                                2,
                            )
                            if current_year_total_male_workers
                            and current_year_total_female_workers
                            else 0
                        ),
                       "total_workers_previous_year":
                        (
                            round(
                                previous_year_total_male_workers
                                + previous_year_total_female_workers,
                                2,
                            )
                            if previous_year_total_male_workers is not None
                            and previous_year_total_female_workers is not None
                            else 0
                        ),
                        "health_and_safety_workers_previous_year":
                        (
                            round(
                                previous_year_health_and_safety_male_workers
                                + previous_year_health_and_safety_female_workers,
                                2,
                            )
                            if previous_year_health_and_safety_male_workers is not None
                            and previous_year_health_and_safety_female_workers
                            is not None
                            else 0
                        ),
                        "health_and_safety_percentage_previous_year":
                        (
                            round(
                                (
                                    (
                                        previous_year_health_and_safety_male_workers
                                        + previous_year_health_and_safety_female_workers
                                    )
                                    / (
                                        previous_year_total_male_workers
                                        + previous_year_total_female_workers
                                    )
                                    * 100
                                ),
                                2,
                            )
                            if previous_year_total_male_workers
                            and previous_year_total_female_workers
                            else 0
                        ),
                        "skill_upgradation_workers_previous_year":
                        (
                            round(
                                previous_year_skill_upgradation_male_workers
                                + previous_year_skill_upgradation_female_workers,
                                2,
                            )
                            if previous_year_skill_upgradation_male_workers is not None
                            and previous_year_skill_upgradation_female_workers
                            is not None
                            else 0
                        ),



                         "skill_upgradation_percentage_previous_year":
                        (
                            round(
                            (
                                (
                                    previous_year_skill_upgradation_male_workers + 
                                    previous_year_skill_upgradation_female_workers )  
                                    / (

                             previous_year_total_male_workers  
                             + previous_year_total_female_workers )
                               * 100
                            ), 
                            2,
                            ) if previous_year_total_male_workers
                            and previous_year_total_female_workers else 0
                        )}],


                            

                    "Principle_3_EI_9_EMP_MALE":[ {
                        "current_year_total_male_employees": current_year_total_male_employees or "-",
                        "current_year_performance_male_employees": current_year_performance_male_employees or "-",
                        "current_year_performance_percentage": (
                            round((current_year_performance_male_employees / current_year_total_male_employees) * 100, 2)
                            if current_year_total_male_employees else "-"
                        ),
                        "previous_year_total_male_employees": previous_year_total_male_employees or "-",
                        "previous_year_performance_male_employees": previous_year_performance_male_employees or "-",
                        "previous_year_performance_percentage": (
                            round((previous_year_performance_male_employees / previous_year_total_male_employees) * 100, 2)
                            if previous_year_total_male_employees else "-"
                        ),
                    }],

                    "Principle_3_EI_9_EMP_FEMALE":[ {
                            "current_year_total_female_employees": current_year_total_female_employees or "-",
                            "current_year_performance_female_employees": current_year_performance_female_employees or "-",
                            "current_year_performance_percentage": (
                                round((current_year_performance_female_employees / current_year_total_female_employees) * 100, 2)
                                if current_year_total_female_employees else "-"
                            ),
                            "previous_year_total_female_employees": previous_year_total_female_employees or "-",
                            "previous_year_performance_female_employees": previous_year_performance_female_employees or "-",
                            "previous_year_performance_percentage": (
                                round((previous_year_performance_female_employees / previous_year_total_female_employees) * 100, 2)
                                if previous_year_total_female_employees else "-"
                            ),
                        }],

                    "Principle_3_EI_9_EMP_TOTAL":[ {
                        "total_male_female_employees_current_year": total_male_female_employees_current_year or "-",
                        "performance_male_female_employees_current_year": performance_male_female_employees_current_year or "-",
                        "performance_percentage_current_year": (
                            round((performance_male_female_employees_current_year / total_male_female_employees_current_year) * 100, 2)
                            if total_male_female_employees_current_year else "-"
                        ),
                        "total_male_female_employees_previous_year": total_male_female_employees_previous_year or "-",
                        "performance_male_female_employees_previous_year": performance_male_female_employees_previous_year or "-",
                        "performance_percentage_previous_year": (
                            round((performance_male_female_employees_previous_year / total_male_female_employees_previous_year) * 100, 2)
                            if total_male_female_employees_previous_year else "-"
                        ),
                    }],

                    "Principle_3_EI_9_WRK_MALE":[ {
                            "current_year_total_male_workers": current_year_total_male_workers or "-",
                            "current_year_performance_male_workers": current_year_performance_male_workers or "-",
                            "current_year_performance_percentage": (
                                round((current_year_performance_male_workers / current_year_total_male_workers) * 100, 2)
                                if current_year_total_male_workers else "-"
                            ),
                            "previous_year_total_male_workers": previous_year_total_male_workers or "-",
                            "previous_year_performance_male_workers": previous_year_performance_male_workers or "-",
                            "previous_year_performance_percentage": (
                                round((previous_year_performance_male_workers / previous_year_total_male_workers) * 100, 2)
                                if previous_year_total_male_workers else "-"
                            ),
                        }],

                    "Principle_3_EI_9_WRK_FEMALE": [{
                            "current_year_total_female_workers": current_year_total_female_workers or "-",
                            "current_year_performance_female_workers": current_year_performance_female_workers or "-",
                            "current_year_performance_percentage": (
                                round((current_year_performance_female_workers / current_year_total_female_workers) * 100, 2)
                                if current_year_total_female_workers else "-"
                            ),
                            "previous_year_total_female_workers": previous_year_total_female_workers or "-",
                            "previous_year_performance_female_workers": previous_year_performance_female_workers or "-",
                            "previous_year_performance_percentage": (
                                round((previous_year_performance_female_workers / previous_year_total_female_workers) * 100, 2)
                                if previous_year_total_female_workers else "-"
                            ),
                        }],

                    "Principle_3_EI_9_WRK_TOTAL":[{
                            "total_male_female_workers_current_year": total_male_female_workers_current_year or "-",
                            "performance_male_female_workers_current_year": performance_male_female_workers_current_year or "-",
                            "performance_percentage_current_year": (
                                round((performance_male_female_workers_current_year / total_male_female_workers_current_year) * 100, 2)
                                if total_male_female_workers_current_year else "-"
                            ),
                            "total_male_female_workers_previous_year": total_male_female_workers_previous_year or "-",
                            "performance_male_female_workers_previous_year": performance_male_female_workers_previous_year or "-",
                            "performance_percentage_previous_year": (
                                round((performance_male_female_workers_previous_year / total_male_female_workers_previous_year) * 100, 2)
                                if total_male_female_workers_previous_year else "-"
                            ),
                        }],


                    "Principle_3_EI_10_a": [{"description_obj_10_A":description_obj_10_A}],
                    "Principle_3_EI_10_b": [{"description_obj_10_B":description_obj_10_B}],
                    "Principle_3_EI_10_c": [{"is_verified_10_C":is_verified_10_C}],
                    "Principle_3_EI_10_d": [{"is_verified_10_D":is_verified_10_D}],
                    "Principle_3_EI_10_c_desc": [{"desc_10_C":desc_10_C}],
                    "Principle_3_EI_10_d_desc": [{"desc_10_D":desc_10_D}],

                    "Principle_3_EI_11_L_T_I_EMP": [{
                        "current_year_total_frequency_rate_employees":
                        (
                            current_year_total_frequency_rate_employees
                            if current_year_total_frequency_rate_employees is not None
                            else 0
                        ),
                        "previous_year_total_frequency_rate_employees":
                        (
                            previous_year_total_frequency_rate_employees
                            if previous_year_total_frequency_rate_employees is not None
                            else 0
                        ),
                 }],

                    "Principle_3_EI_11_L_T_I_WRK": [{
                        "current_year_total_frequency_rate_workers":
                        (
                            current_year_total_frequency_rate_workers
                            if current_year_total_frequency_rate_workers is not None
                            else 0
                        ),
                        "previous_year_total_frequency_rate_workers":
                        (
                            previous_year_total_frequency_rate_workers
                            if previous_year_total_frequency_rate_workers is not None
                            else 0
                        ),
                    }],

                    "Principle_3_EI_11_T_W_R_I_EMP": [{
                        "current_year_total_injuries_employees":
                        (
                            current_year_total_injuries_employees
                            if current_year_total_injuries_employees is not None
                            else 0
                        ),
                        "previous_year_total_injuries_employees":
                        (
                            previous_year_total_injuries_employees
                            if previous_year_total_injuries_employees is not None
                            else 0
                        ),
                    }],
                    "Principle_3_EI_11_T_W_R_I_WRK": [{
                        "current_year_total_injuries_workers":
                        (
                            current_year_total_injuries_workers
                            if current_year_total_injuries_workers is not None
                            else 0
                        ),
                        "previous_year_total_injuries_workers":
                        (
                            previous_year_total_injuries_workers
                            if previous_year_total_injuries_workers is not None
                            else 0
                        ),
                    }],
                    "Principle_3_EI_11_N_O_F_EMP": [{
                        "current_year_total_fatalities_employees":
                        (
                            current_year_total_fatalities_employees
                            if current_year_total_fatalities_employees is not None
                            else 0
                        ),
                        "previous_year_total_fatalities_employees":
                        (
                            previous_year_total_fatalities_employees
                            if previous_year_total_fatalities_employees is not None
                            else 0
                        ),
                    }],
                    "Principle_3_EI_11_N_O_F_WRK": [{
                        "current_year_total_fatalities_workers":
                        (
                            current_year_total_fatalities_workers
                            if current_year_total_fatalities_workers is not None
                            else 0
                        ),
                        "previous_year_total_fatalities_workers":
                        (
                            previous_year_total_fatalities_workers
                            if previous_year_total_fatalities_workers is not None
                            else 0
                        ),
                    }],
                    "Principle_3_EI_11_I_O_I_H_EMP": [{
                        "current_year_total_injury_health_employees":
                        (
                            current_year_total_injury_or_ill_health_employees
                            if current_year_total_injury_or_ill_health_employees
                            is not None
                            else 0
                        ),
                        "previous_year_total_injury_health_employees":
                        (
                            previous_year_total_injury_or_ill_health_employees
                            if previous_year_total_injury_or_ill_health_employees
                            is not None
                            else 0
                        ),
                    }],
                    "Principle_3_EI_11_I_O_I_H_WRK": [{
                        "current_year_injury_or_ill_health_workers": current_year_total_injury_or_ill_health_workers if current_year_total_injury_or_ill_health_workers is not None else 0,
                        "previous_year_injury_or_ill_health_workers": previous_year_total_injury_or_ill_health_workers if previous_year_total_injury_or_ill_health_workers is not None else 0,
                    }],

                    "Principle_3_EI_12": [{"description_obj_pd_5":description_obj_pd_5}],
                    "Principle_3_EI_13_WC": [{
                            "current_filed_during_year": current_working_condition.Filed_During_The_Year if current_working_condition else "-",
                            "current_pending_resolution_eoy": current_working_condition.Pending_Resolution_At_The_EOY if current_working_condition else "-",
                            "current_remark": current_working_condition.Remark if current_working_condition else "-",
                            "previous_filed_during_year": previous_working_condition.Filed_During_The_Year if previous_working_condition else "-",
                            "previous_pending_resolution_eoy": previous_working_condition.Pending_Resolution_At_The_EOY if previous_working_condition else "-",
                            "previous_remark": previous_working_condition.Remark if previous_working_condition else "-",
                        }],
               
                    "Principle_3_EI_13_HS":[ {
                        "current_filed_during_year": current_health_safety.Filed_During_The_Year if current_health_safety else "-",
                        "current_pending_resolution_eoy": current_health_safety.Pending_Resolution_At_The_EOY if current_health_safety else "-",
                        "current_remark": current_health_safety.Remark if current_health_safety else "-",
                        "previous_filed_during_year": previous_health_safety.Filed_During_The_Year if previous_health_safety else "-",
                        "previous_pending_resolution_eoy": previous_health_safety.Pending_Resolution_At_The_EOY if previous_health_safety else "-",
                        "previous_remark": previous_health_safety.Remark if previous_health_safety else "-",
                    }],

                    "Principle_3_EI_14a": [{"Working_Conditions":Working_Conditions}],
                    "Principle_3_EI_14b": [{"Health_And_Safety":Health_And_Safety}],
                    "Principle_3_EI_15": [{"description_obj_pd4":description_obj_pd4}],
                    "Principle_3_LI_1": principle_3_li_1,
                    "Principle_3_LI_2": [{"description_obj_pd1":description_obj_pd1}],

                    "Principle_3_LI_3_EMP": [{
                         "current_year_total_no_of_affected_employees":
                        (
                            current_year_total_no_of_affected_employees
                            if current_year_total_no_of_affected_employees is not None
                            else 0
                        ),
                        "previous_year_total_no_of_affected_employees":
                        (
                            previous_year_total_no_of_affected_employees
                            if previous_year_total_no_of_affected_employees is not None
                            else 0
                        ),
                        "current_year_rehabilitated_and_placed_in_suitable_employee": 
                        (
                            current_year_rehabilitated_and_placed_in_suitable_employee
                            if current_year_rehabilitated_and_placed_in_suitable_employee
                            is not None
                            else 0
                        ),
                        "previous_year_rehabilitated_and_placed_in_suitable_employee":
                        (
                            previous_year_rehabilitated_and_placed_in_suitable_employee
                            if previous_year_rehabilitated_and_placed_in_suitable_employee
                            is not None
                            else 0
                        ),
                    }],

                    "Principle_3_LI_3_WKR": [{
                        "current_year_total_no_of_affected_workers":
                        (
                            current_year_total_no_of_affected_workers
                            if current_year_total_no_of_affected_workers is not None
                            else 0
                        ),
                        "previous_year_total_no_of_affected_workers":
                        (
                            previous_year_total_no_of_affected_workers
                            if previous_year_total_no_of_affected_workers is not None
                            else 0
                        ),
                        "current_year_rehabilitated_workers":
                        (
                            current_year_rehabilitated_and_placed_in_suitable_workers
                            if current_year_rehabilitated_and_placed_in_suitable_workers
                            is not None
                            else 0
                        ),
                         "previous_year_rehabilitated_workers":
                        (
                            previous_year_rehabilitated_and_placed_in_suitable_workers
                            if previous_year_rehabilitated_and_placed_in_suitable_workers
                            is not None
                            else 0
                        ),
                    }],

                    "Principle_3_LI_4": [{"description_obj_pd":description_obj_pd}],
                    "Principle_3_LI_5a": [{
                        "current_year_health_and_safety":   current_data["Percentage_Assessed_For_Health_And_Safety"],
                        "previous_year_health_and_safety":   previous_data["Percentage_Assessed_For_Health_And_Safety"],
                    }],
                    "Principle_3_LI_5b": [{
                        "current_year_working_conditions":    current_data["Percentage_Assessed_For_Working_Conditions"],
                        "previous_year_working_conditions":    previous_data["Percentage_Assessed_For_Working_Conditions"],
                    }],
                    "Principle_3_LI_5c": [{
                        "current_year_number_of_supplier":   current_data["Number_of_Supplier"],
                        "previous_year_number_of_supplier":    previous_data["Number_of_Supplier"],
                    }],
                    "Principle_3_LI_6": [{"description_obj_Policy":description_obj_Policy}],
                }
            }

            Brs_log = {
                "Financial_Year":financial_year,
                "Section":"Principle 3",
                "User_Name":f"{request.user.firstname} {request.user.lastname}"
               
            }
                            
            brs_log_serializer = BRS_Report_LogSerializer(data=Brs_log)
            if brs_log_serializer.is_valid():
                brs_log_serializer.save()

            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Data Not Available in Principle_3"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except APIException as e:
            return Response(
                {"error": f"APIException in Principle_3: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TypeError as e:
            return Response(
                {"error": f"TypeError in Principle_3: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Unknown error in Principle_3: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class Principle4View(APIView):
    def get(self, request):
        try:
            response_data = {}

            financial_year = request.query_params.get("financial_year", None)

            if financial_year is None:
                return Response(
                    {"error": "financial_year parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract the starting year from the financial year string
            try:
                start_year = int(
                    financial_year.split("-")[0][2:]
                )  # Extract '2023' from 'FY2023-2024'
                previous_financial_year = (
                    f"FY{start_year-1}-{start_year}"  # 'FY2022-2023'
                )
            except (ValueError, IndexError):
                return Response(
                    {
                        "error": 'Invalid financial_year format. Expected format: "FY2023-2024"'
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            description_obj_P4_EI_1 = Stakeholders_Details.objects.filter(
                Model_Name_Stakeholder="Stakeholder Groups"
            ).first()
            stake = (
                description_obj_P4_EI_1.Description if description_obj_P4_EI_1 else "-"
            )

            stakeholders = List_Stakeholder_Groups.objects.values(
                "Stack_Holder_Group",
                "Vulnerable_And_Marginalized",
                "Channels_Of_Communication",
                "Frequency_Of_Engagement",
                "Purpose_And_Scope_Of_Engagement",
            )

            if not stakeholders:  # If stakeholders is empty
                stakeholders_data = [
                    {
                        "Stack_Holder_Group": "-",
                        "Vulnerable_And_Marginalized": "-",
                        "Channels_Of_Communication": "-",
                        "Frequency_Of_Engagement": "-",
                        "Purpose_And_Scope_Of_Engagement": "-",
                    }
                ]
            else:
                stakeholders_data = [
                    {
                        "Stack_Holder_Group": (
                            item["Stack_Holder_Group"]
                            if item["Stack_Holder_Group"]
                            else "-"
                        ),
                        "Vulnerable_And_Marginalized": (
                            item["Vulnerable_And_Marginalized"]
                            if item["Vulnerable_And_Marginalized"]
                            else "-"
                        ),
                        "Channels_Of_Communication": (
                            item["Channels_Of_Communication"]
                            if item["Channels_Of_Communication"]
                            else "-"
                        ),
                        "Frequency_Of_Engagement": (
                            item["Frequency_Of_Engagement"]
                            if item["Frequency_Of_Engagement"]
                            else "-"
                        ),
                        "Purpose_And_Scope_Of_Engagement": (
                            item["Purpose_And_Scope_Of_Engagement"]
                            if item["Purpose_And_Scope_Of_Engagement"]
                            else "-"
                        ),
                    }
                    for item in stakeholders
                ]

            description_obj_P4_LI_1 = Stakeholders_Details.objects.filter(
                Model_Name_Stakeholder="Processes for Consultation"
            ).first()
            process = (
                description_obj_P4_LI_1.Description if description_obj_P4_LI_1 else "-"
            )

            description_obj_P4_LI_2 = Stakeholders_Details.objects.filter(
                # Model_Name_Stakeholder="Stakeholder Consultation"
                Model_Name_Stakeholder="Marginalized Stakeholder Groups"

            ).first()
            consultation = (
                description_obj_P4_LI_2.Description if description_obj_P4_LI_2 else "-"
            )

            description_obj_P4_LI_3 = Stakeholders_Details.objects.filter(
                # Model_Name_Stakeholder="Marginalized Stakeholder Groups"
                Model_Name_Stakeholder="Stakeholder Consultation"
            ).first()
            group = (
                description_obj_P4_LI_3.Description if description_obj_P4_LI_3 else "-"
            )

           
            response_data = {
               "Section_C_P4":{
                   
       
                   "Principle_4_EI_1": [{"stake":stake}] ,
                   "Principle_4_EI_2": stakeholders_data if stakeholders_data else "-",
                   "Principle_4_LI_1": [{"process":process}],
                   "Principle_4_LI_2": [{"consultation":consultation}] ,
                   "Principle_4_LI_3": [{"group":group}],
               }
            }
                 
            Brs_log = {
                "Financial_Year":financial_year,
                "Section":"Principle 4",
                "User_Name":f"{request.user.firstname} {request.user.lastname}"
               
            }
                            
            brs_log_serializer = BRS_Report_LogSerializer(data=Brs_log)
            if brs_log_serializer.is_valid():
                brs_log_serializer.save()

            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Data Not Available in Principle_4"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except APIException as e:
            return Response(
                {"error": f"APIException in Principle_4: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TypeError as e:
            return Response(
                {"error": f"TypeError in Principle_4: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Unknown error in Principle_4: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class Principle5View(APIView):

    def get(self, request):
        try:

            response_data = {}

            financial_year = request.query_params.get("financial_year", None)

            if financial_year is None:
                return Response(
                    {"error": "financial_year parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract the starting year from the financial year string
            try:
                start_year = int(
                    financial_year.split("-")[0][2:]
                )  # Extract '2023' from 'FY2023-2024'
                previous_financial_year = (
                    f"FY{start_year-1}-{start_year}"  # 'FY2022-2023'
                )
            except (ValueError, IndexError):
                return Response(
                    {
                        "error": 'Invalid financial_year format. Expected format: "FY2023-2024"'
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            ############################### P5 - EI_1 for Employees #########################################
            # Fetch records for the current financial year for the "Employees" segment
            current_year_employee_records = (
                On_Human_Rights_Issues_And_Policies.objects.filter(
                    Financial_Year=financial_year, Segment="Employees"
                )
            )
            # Fetch records for the previous financial year for the "Employees" segment
            previous_year_employee_records = (
                On_Human_Rights_Issues_And_Policies.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Employees"
                )
            )
            # Calculate total number of male employees in the current financial year
            current_total_permanent_employees = sum(
                float(record.Total_Permanent_Covered or 0)
                for record in current_year_employee_records
            )
            current_total_non_permanent_employees = sum(
                float(record.Total_Non_Permanent_Covered or 0)
                for record in current_year_employee_records
            )
            # Calculate total number of male employees in the previous financial year
            previous_total_permanent_employees = sum(
                float(record.Total_Permanent_Covered or 0)
                for record in previous_year_employee_records
            )
            previous_total_non_permanent_employees = sum(
                float(record.Total_Non_Permanent_Covered or 0)
                for record in previous_year_employee_records
            )
            total_emp_current_year = EmployeeSummary.objects.filter(
                Financial_Year=financial_year,
            )
            total_emp_previous_year = EmployeeSummary.objects.filter(
                Financial_Year=previous_financial_year,
            )
            # Initialize totals for current year
            total_male_permanent_current_year = 0
            total_female_permanent_current_year = 0
            # Manually sum the Male_Permanent and Female_Permanent for current year
            for emp in total_emp_current_year:
                total_male_permanent_current_year += (
                    emp.Male_Permanent.to_decimal() or 0
                )
                total_female_permanent_current_year += (
                    emp.Female_Permanent.to_decimal() or 0
                )
            # Initialize totals for previous year
            total_male_permanent_previous_year = 0
            total_female_permanent_previous_year = 0
            # Manually sum the Male_Permanent and Female_Permanent for previous year
            for emp in total_emp_previous_year:
                total_male_permanent_previous_year += (
                    emp.Male_Permanent.to_decimal() or 0
                )
                total_female_permanent_previous_year += (
                    emp.Female_Permanent.to_decimal() or 0
                )
            total_permanent_current_year = (
                total_male_permanent_current_year + total_female_permanent_current_year
            )
            total_permanent_previous_year = (
                total_male_permanent_previous_year
                + total_female_permanent_previous_year
            )
            # Initialize totals for current year (non-permanent)
            total_male_non_permanent_current_year = 0
            total_female_non_permanent_current_year = 0
            # Manually sum the Male_Non_Permanent and Female_Non_Permanent for current year
            for emp in total_emp_current_year:
                total_male_non_permanent_current_year += (
                    emp.Male_Non_Permanent.to_decimal() or 0
                )
                total_female_non_permanent_current_year += (
                    emp.Female_Non_Permanent.to_decimal() or 0
                )
            # Initialize totals for previous year (non-permanent)
            total_male_non_permanent_previous_year = 0
            total_female_non_permanent_previous_year = 0
            for emp in total_emp_previous_year:
                total_male_non_permanent_previous_year += (
                    emp.Male_Non_Permanent.to_decimal() or 0
                )
                total_female_non_permanent_previous_year += (
                    emp.Female_Non_Permanent.to_decimal() or 0
                )
            total_non_permanent_current_year = (
                total_male_non_permanent_current_year
                + total_female_non_permanent_current_year
            )
            total_non_permanent_previous_year = (
                total_male_non_permanent_previous_year
                + total_female_non_permanent_previous_year
            )

            # -----------------------Workers -------------------------------------------
            # Fetch records for the current financial year for the "Workers" segment
            current_year_worker_records = (
                On_Human_Rights_Issues_And_Policies.objects.filter(
                    Financial_Year=financial_year, Segment="Workers"
                )
            )
            # Fetch records for the previous financial year for the "Workers" segment
            previous_year_worker_records = (
                On_Human_Rights_Issues_And_Policies.objects.filter(
                    Financial_Year=previous_financial_year, Segment="Workers"
                )
            )
            # Calculate total number of permanent workers in the current financial year
            current_total_permanent_workers = sum(
                float(record.Total_Permanent_Covered or 0)
                for record in current_year_worker_records
            )
            current_total_non_permanent_workers = sum(
                float(record.Total_Non_Permanent_Covered or 0)
                for record in current_year_worker_records
            )
            # Calculate total number of permanent workers in the previous financial year
            previous_total_permanent_workers = sum(
                float(record.Total_Permanent_Covered or 0)
                for record in previous_year_worker_records
            )
            previous_total_non_permanent_workers = sum(
                float(record.Total_Non_Permanent_Covered or 0)
                for record in previous_year_worker_records
            )
            # Query data for current and previous financial year from WorkSummary model
            total_work_current_year = WorkerSummary.objects.filter(
                Financial_Year=financial_year,
            )
            total_work_previous_year = WorkerSummary.objects.filter(
                Financial_Year=previous_financial_year,
            )
            # Initialize totals for current year (permanent)
            total_male_permanent_current_year_work = 0
            total_female_permanent_current_year_work = 0
            # Manually sum the Male_Permanent and Female_Permanent for current year (work)
            for work in total_work_current_year:
                total_male_permanent_current_year_work += (
                    work.Male_Permanent.to_decimal() or 0
                )
                total_female_permanent_current_year_work += (
                    work.Female_Permanent.to_decimal() or 0
                )
            # Initialize totals for previous year (permanent)
            total_male_permanent_previous_year_work = 0
            total_female_permanent_previous_year_work = 0
            # Manually sum the Male_Permanent and Female_Permanent for previous year (work)
            for work in total_work_previous_year:
                total_male_permanent_previous_year_work += (
                    work.Male_Permanent.to_decimal() or 0
                )
                total_female_permanent_previous_year_work += (
                    work.Female_Permanent.to_decimal() or 0
                )
            # Total for permanent workers for current and previous years
            total_permanent_current_year_work = (
                total_male_permanent_current_year_work
                + total_female_permanent_current_year_work
            )
            total_permanent_previous_year_work = (
                total_male_permanent_previous_year_work
                + total_female_permanent_previous_year_work
            )
            # Initialize totals for current year (non-permanent)
            total_male_non_permanent_current_year_work = 0
            total_female_non_permanent_current_year_work = 0
            # Manually sum the Male_Non_Permanent and Female_Non_Permanent for current year (work)
            for work in total_work_current_year:
                total_male_non_permanent_current_year_work += (
                    work.Male_Non_Permanent.to_decimal() or 0
                )
                total_female_non_permanent_current_year_work += (
                    work.Female_Non_Permanent.to_decimal() or 0
                )
            # Initialize totals for previous year (non-permanent)
            total_male_non_permanent_previous_year_work = 0
            total_female_non_permanent_previous_year_work = 0
            # Manually sum the Male_Non_Permanent and Female_Non_Permanent for previous year (work)
            for work in total_work_previous_year:
                total_male_non_permanent_previous_year_work += (
                    work.Male_Non_Permanent.to_decimal() or 0
                )
                total_female_non_permanent_previous_year_work += (
                    work.Female_Non_Permanent.to_decimal() or 0
                )
            # Total for non-permanent workers for current and previous years
            total_non_permanent_current_year_work = (
                total_male_non_permanent_current_year_work
                + total_female_non_permanent_current_year_work
            )
            total_non_permanent_previous_year_work = (
                total_male_non_permanent_previous_year_work
                + total_female_non_permanent_previous_year_work
            )

            ################################################## P5 EI 2 ########################################################3

            total_emp_current_year = EmployeeSummary.objects.filter(
                Financial_Year=financial_year,
            )
            total_emp_previous_year = EmployeeSummary.objects.filter(
                Financial_Year=previous_financial_year,
            )
            # Initialize totals for current year
            total_male_permanent_current_year = 0
            total_female_permanent_current_year = 0
            # Manually sum the Male_Permanent and Female_Permanent for current year
            for emp in total_emp_current_year:
                total_male_permanent_current_year += (
                    emp.Male_Permanent.to_decimal() or 0
                )
                total_female_permanent_current_year += (
                    emp.Female_Permanent.to_decimal() or 0
                )

            total_permanent_Emp_current_year = (
                total_male_permanent_current_year + total_female_permanent_current_year
            )
            # Initialize totals for previous year
            total_male_permanent_previous_year = 0
            total_female_permanent_previous_year = 0
            # Manually sum the Male_Permanent and Female_Permanent for previous year
            for emp in total_emp_previous_year:
                total_male_permanent_previous_year += (
                    emp.Male_Permanent.to_decimal() or 0
                )
                total_female_permanent_previous_year += (
                    emp.Female_Permanent.to_decimal() or 0
                )
            # Fetch records for the current financial year for "Permanent" and "Non-Permanent" employees
            current_year_permanent_employee_records = Wages_Paid.objects.filter(
                Financial_Year=financial_year, Segment="Employees", Type="Permanent"
            )
            current_year_non_permanent_employee_records = Wages_Paid.objects.filter(
                Financial_Year=financial_year, Segment="Employees", Type="Non-Permanent"
            )
            # Fetch records for the previous financial year for "Permanent" and "Non-Permanent" employees
            previous_year_permanent_employee_records = Wages_Paid.objects.filter(
                Financial_Year=previous_financial_year,
                Segment="Employees",
                Type="Permanent",
            )
            previous_year_non_permanent_employee_records = Wages_Paid.objects.filter(
                Financial_Year=previous_financial_year,
                Segment="Employees",
                Type="Non-Permanent",
            )
            # Calculate total number of permanent male and female employees in the current financial year
            current_total_permanent_Males_With_Equal_To_Minimum_Wages_employees = sum(
                float(record.Males_With_Equal_To_Minimum_Wages or 0)
                for record in current_year_permanent_employee_records
            )
            current_total_permanent_females_With_Equal_To_Minimum_Wages_employees = sum(
                float(record.Females_With_Equal_To_Minimum_Wages or 0)
                for record in current_year_permanent_employee_records
            )
            current_total_non_permanent_male_employees = sum(
                float(record.Males_With_Equal_To_Minimum_Wages or 0)
                for record in current_year_non_permanent_employee_records
            )
            current_total_non_permanent_female_employees = sum(
                float(record.Females_With_Equal_To_Minimum_Wages or 0)
                for record in current_year_non_permanent_employee_records
            )
            current_permanent_male_employees_more_than_minimum_wages = sum(
                float(record.Males_With_More_Than_Minimum_Wages or 0)
                for record in current_year_permanent_employee_records
            )
            current_permanent_female_employees_more_than_minimum_wages = sum(
                float(record.Females_With_More_Than_Minimum_Wages or 0)
                for record in current_year_permanent_employee_records
            )
            current_non_permanent_male_employees_more_than_minimum_wages = sum(
                float(record.Males_With_More_Than_Minimum_Wages or 0)
                for record in current_year_non_permanent_employee_records
            )
            current_non_permanent_female_employees_more_than_minimum_wages = sum(
                float(record.Females_With_More_Than_Minimum_Wages or 0)
                for record in current_year_non_permanent_employee_records
            )
            # Calculate total number of permanent male and female employees in the previous financial year
            previous_total_permanent_male_employees = sum(
                float(record.Males_With_Equal_To_Minimum_Wages or 0)
                for record in previous_year_permanent_employee_records
            )
            previous_total_permanent_female_employees = sum(
                float(record.Females_With_Equal_To_Minimum_Wages or 0)
                for record in previous_year_permanent_employee_records
            )
            # Calculate total number of non-permanent male and female employees in the previous financial year
            previous_total_non_permanent_male_employees = sum(
                float(record.Males_With_Equal_To_Minimum_Wages or 0)
                for record in previous_year_non_permanent_employee_records
            )
            previous_total_non_permanent_female_employees = sum(
                float(record.Females_With_Equal_To_Minimum_Wages or 0)
                for record in previous_year_non_permanent_employee_records
            )
            previous_permanent_male_employees_more_than_minimum_wages = sum(
                float(record.Males_With_More_Than_Minimum_Wages or 0)
                for record in previous_year_permanent_employee_records
            )
            previous_permanent_female_employees_more_than_minimum_wages = sum(
                float(record.Females_With_More_Than_Minimum_Wages or 0)
                for record in previous_year_permanent_employee_records
            )
            # Calculate total number of non-permanent male and female employees in the current financial year
            previous_non_permanent_male_employees_more_than_minimum_wages = sum(
                float(record.Males_With_More_Than_Minimum_Wages or 0)
                for record in previous_year_non_permanent_employee_records
            )
            previous_non_permanent_female_employees_more_than_minimum_wages = sum(
                float(record.Females_With_More_Than_Minimum_Wages or 0)
                for record in previous_year_non_permanent_employee_records
            )

            # --------------------------------- Workers --------------------------------------#
            # Fetch records for the current and previous financial years for Workers
            total_workers_current_year = WorkerSummary.objects.filter(
                Financial_Year=financial_year,
            )
            total_workers_previous_year = WorkerSummary.objects.filter(
                Financial_Year=previous_financial_year,
            )
            # Initialize totals for current year workers
            total_male_permanent_workers_current_year = 0
            total_female_permanent_workers_current_year = 0
            total_male_non_permanent_workers_current_year = 0
            total_female_non_permanent_workers_current_year = 0

            # Manually sum the Male_Permanent and Female_Permanent for current year workers
            for worker in total_workers_current_year:
                total_male_permanent_workers_current_year += (
                    worker.Male_Permanent.to_decimal() or 0
                )
                total_female_permanent_workers_current_year += (
                    worker.Female_Permanent.to_decimal() or 0
                )
                total_male_non_permanent_workers_current_year += (
                    worker.Male_Non_Permanent.to_decimal() or 0
                )
                total_female_non_permanent_workers_current_year += (
                    worker.Female_Non_Permanent.to_decimal() or 0
                )

            # Initialize totals for previous year workers
            total_male_permanent_workers_previous_year = 0
            total_female_permanent_workers_previous_year = 0
            total_male_non_permanent_workers_previous_year = 0
            total_female_non_permanent_workers_previous_year = 0
            # Manually sum the Male_Permanent and Female_Permanent for previous year workers
            for worker in total_workers_previous_year:
                total_male_permanent_workers_previous_year += (
                    worker.Male_Permanent.to_decimal() or 0
                )
                total_female_permanent_workers_previous_year += (
                    worker.Female_Permanent.to_decimal() or 0
                )
                total_male_non_permanent_workers_previous_year += (
                    worker.Male_Non_Permanent.to_decimal() or 0
                )
                total_female_non_permanent_workers_previous_year += (
                    worker.Female_Non_Permanent.to_decimal() or 0
                )

            # Calculate Non-Permanent workers in a similar way:
            current_year_non_permanent_worker_records = Wages_Paid.objects.filter(
                Financial_Year=financial_year, Segment="Workers", Type="Non-Permanent"
            )
            current_year_permanent_worker_records = Wages_Paid.objects.filter(
                Financial_Year=financial_year, Segment="Workers", Type="Permanent"
            )
            previous_year_non_permanent_worker_records = Wages_Paid.objects.filter(
                Financial_Year=previous_financial_year,
                Segment="Workers",
                Type="Non-Permanent",
            )
            previous_year_permanent_worker_records = Wages_Paid.objects.filter(
                Financial_Year=previous_financial_year,
                Segment="Workers",
                Type="Permanent",
            )
            # Current and previous year Non-Permanent workers
            current_non_permanent_male_worker_With_Equal_To_Minimum_Wages = sum(
                float(record.Males_With_Equal_To_Minimum_Wages or 0)
                for record in current_year_non_permanent_worker_records
            )
            current_non_permanent_female_worker_With_Equal_To_Minimum_Wages = sum(
                float(record.Females_With_Equal_To_Minimum_Wages or 0)
                for record in current_year_non_permanent_worker_records
            )
            current_non_permanent_male_worker_more_than_minimum_wages = sum(
                float(record.Males_With_More_Than_Minimum_Wages or 0)
                for record in current_year_non_permanent_worker_records
            )
            current_non_permanent_female_worker_more_than_minimum_wages = sum(
                float(record.Females_With_More_Than_Minimum_Wages or 0)
                for record in current_year_non_permanent_worker_records
            )
            current_permanent_male_worker_more_than_minimum_wages = sum(
                float(record.Males_With_More_Than_Minimum_Wages or 0)
                for record in current_year_permanent_worker_records
            )
            current_permanent_female_worker_more_than_minimum_wages = sum(
                float(record.Females_With_More_Than_Minimum_Wages or 0)
                for record in current_year_permanent_worker_records
            )
            current_permanen_Males_With_Equal_To_Minimum_Wages = sum(
                float(record.Males_With_Equal_To_Minimum_Wages or 0)
                for record in current_year_permanent_worker_records
            )
            current_permanent_females_With_Equal_To_Minimum_Wages = sum(
                float(record.Females_With_Equal_To_Minimum_Wages or 0)
                for record in current_year_permanent_worker_records
            )
            previous_total_non_permanent_Males_With_Equal_To_Minimum_Wages_workers = (
                sum(
                    float(record.Males_With_Equal_To_Minimum_Wages or 0)
                    for record in previous_year_non_permanent_worker_records
                )
            )
            previous_total_non_permanent_females_With_Equal_To_Minimum_Wages_workers = (
                sum(
                    float(record.Females_With_Equal_To_Minimum_Wages or 0)
                    for record in previous_year_non_permanent_worker_records
                )
            )
            previous_total_non_permanent_males_With_More_Than_Minimum_Wages_workers = (
                sum(
                    float(record.Males_With_More_Than_Minimum_Wages or 0)
                    for record in previous_year_non_permanent_worker_records
                )
            )
            previous_total_non_permanent_Females_With_More_Than_Minimum_Wages_workers = sum(
                float(record.Females_With_More_Than_Minimum_Wages or 0)
                for record in previous_year_non_permanent_worker_records
            )
            previous_total_permanent_Males_With_Equal_To_Minimum_Wages_workers = sum(
                float(record.Males_With_Equal_To_Minimum_Wages or 0)
                for record in previous_year_permanent_worker_records
            )
            previous_total_permanent_females_With_Equal_To_Minimum_Wages_workers = sum(
                float(record.Females_With_Equal_To_Minimum_Wages or 0)
                for record in previous_year_permanent_worker_records
            )
            previous_total_permanent_males_With_More_Than_Minimum_Wages_workers = sum(
                float(record.Males_With_More_Than_Minimum_Wages or 0)
                for record in previous_year_permanent_worker_records
            )
            previous_total_permanent_Females_With_More_Than_Minimum_Wages_workers = sum(
                float(record.Females_With_More_Than_Minimum_Wages or 0)
                for record in previous_year_permanent_worker_records
            )

            def sum_field(records, field):
                return sum(float(getattr(record, field, 0) or 0) for record in records)

            # Usage
            current_non_permanent_male_worker_With_Equal_To_Minimum_Wages = sum_field(
                current_year_non_permanent_worker_records,
                "Males_With_Equal_To_Minimum_Wages",
            )
            current_non_permanent_female_worker_With_Equal_To_Minimum_Wages = sum_field(
                current_year_non_permanent_worker_records,
                "Females_With_Equal_To_Minimum_Wages",
            )

            # --------------------------Principle_5_EI_3a-----------------------------------------

            def decimal_from_decimal128(value):
                if isinstance(value, Decimal128):
                    return Decimal(value.to_decimal())  # Converts Decimal128 to Decimal
                return (
                    Decimal(value) if value else Decimal("0.0")
                )  # Handles Decimal and None values

            # Initialize sums for Board of Directors
            total_male_board_of_directors = Decimal("0.0")
            total_female_board_of_directors = Decimal("0.0")

            # Fetch and sum up Board of Directors data
            for director in Management_Board_of_Directors.objects.filter(
                Financial_Year=financial_year, Gender="Male"
            ):
                total_male_board_of_directors += decimal_from_decimal128(
                    director.Total_Board_of_Directors
                )

            for director in Management_Board_of_Directors.objects.filter(
                Financial_Year=financial_year, Gender="Female"
            ):
                total_female_board_of_directors += decimal_from_decimal128(
                    director.Total_Board_of_Directors
                )

            # Initialize sums for Key Management Personnel
            total_male_key_management = Decimal("0.0")
            total_female_key_management = Decimal("0.0")

            # Fetch and sum up Key Management Personnel data
            for key_management in Key_Management_Personnel.objects.filter(
                Financial_Year=financial_year, Gender="Male"
            ):
                total_male_key_management += decimal_from_decimal128(
                    key_management.Total_Key_Management_Personnel
                )

            for key_management in Key_Management_Personnel.objects.filter(
                Financial_Year=financial_year, Gender="Female"
            ):
                total_female_key_management += decimal_from_decimal128(
                    key_management.Total_Key_Management_Personnel
                )

            # Initialize sums for permanent employees
            total_male_permanent_employees = Decimal("0.0")
            total_female_permanent_employees = Decimal("0.0")

            # Fetch and sum up employee summary records
            for summary in EmployeeSummary.objects.filter(
                Financial_Year=financial_year
            ):
                total_male_permanent_employees += decimal_from_decimal128(
                    summary.Male_Permanent
                )
                total_female_permanent_employees += decimal_from_decimal128(
                    summary.Female_Permanent
                )

            # Initialize sums for permanent workers
            total_male_permanent_workers = Decimal("0.0")
            total_female_permanent_workers = Decimal("0.0")

            # Fetch and sum up worker summary records
            for summary in WorkerSummary.objects.filter(Financial_Year=financial_year):
                total_male_permanent_workers += decimal_from_decimal128(
                    summary.Male_Permanent
                )
                total_female_permanent_workers += decimal_from_decimal128(
                    summary.Female_Permanent
                )

            try:
                # Fetch the latest record from Median_Remuneration_Salary_Wages
                median_data = Median_Remuneration_Salary_Wages.objects.get(
                    Financial_Year=financial_year
                )
            except ObjectDoesNotExist:
                # Provide default values if no median data is found
                median_data = {
                    "Males_Board_Of_Directors": Decimal("0.0"),
                    "Females_Board_Of_Directors": Decimal("0.0"),
                    "Males_Key_Management_Personnel": Decimal("0.0"),
                    "Females_Key_Management_Personnel": Decimal("0.0"),
                    "Males_Employees": Decimal("0.0"),
                    "Females_Employees": Decimal("0.0"),
                    "Males_Workers": Decimal("0.0"),
                    "Females_Workers": Decimal("0.0"),
                }

            # %%%%%%%%%%%%%%%%%%%%% p5 3b %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

            current_year_records = Job_Creation_In_Smaller_Town.objects.filter(
                Financial_Year=financial_year
            )
            current_year_sum = sum(
                conversion(record.Gross_Wages_Paid_To_Females_As_Divided_Of_Total_Wages)
                for record in current_year_records
            )

            # Fetch the sum of Gross_Wages_Paid_To_Females_As_Divided_Of_Total_Wages for the previous financial year
            previous_year_records = Job_Creation_In_Smaller_Town.objects.filter(
                Financial_Year=previous_financial_year
            )
            previous_year_sum = sum(
                conversion(record.Gross_Wages_Paid_To_Females_As_Divided_Of_Total_Wages)
                for record in previous_year_records
            )

            # ---------------------------------------------------------------------#
    
            # description_obj4 = Policy_Details_Human_Rights.objects.filter(
            #         Model_Name_Human_Rights="Focal Point"
            # ).first()

            # print("============",description_obj4)


            # description_obj4_value = "-"
            # try:
            #     description_obj4 = Policy_Details_Human_Rights.objects.filter(
            #         Model_Name_Human_Rights="Focal Point"
            #     ).first()
            #     if description_obj4:
            #         description_obj4_value = description_obj4.Is_Verified 
            #         description_obj4_value = description_obj4.Descriptions_Human_Rights
            # except Policy_Details_Human_Rights.DoesNotExist:
            #     pass

            # print("======///======",description_obj4_value)
               
                    

            description_obj4_value_is_verified = "-"
            description_obj4_value_descriptions = "-"

            try:
                description_obj4 = Policy_Details_Human_Rights.objects.filter(
                    Model_Name_Human_Rights="Focal Point"
                ).first()
                if description_obj4:
                    description_obj4_value_is_verified = description_obj4.Is_Verified
                    description_obj4_value_descriptions = description_obj4.Descriptions_Human_Rights
            except Policy_Details_Human_Rights.DoesNotExist:
                pass

          


            description_obj5_value = "-"
            try:
                description_obj5 = Policy_Details_Human_Rights.objects.filter(
                    Model_Name_Human_Rights="Internal Mechanism"
                ).first()
                if description_obj5:
                    description_obj5_value = description_obj5.Descriptions_Human_Rights
            except Policy_Details_Human_Rights.DoesNotExist:
                pass

           

            ######################P3 EI 6 ##################################################3
            current_year_Child_Labour = Human_Rights_related_complaints.objects.filter(
                Financial_Year=financial_year, Complaint_Type="Child Labour"
            ).first()

            previous_year_Child_Labour = Human_Rights_related_complaints.objects.filter(
                Financial_Year=previous_financial_year, Complaint_Type="Child Labour"
            ).first()

            current_year_Forced_Labour_Involuntary_Labour = (
                Human_Rights_related_complaints.objects.filter(
                    Financial_Year=financial_year,
                    Complaint_Type="Forced Labour/Involuntary Labour",
                ).first()
            )

            previous_year_Forced_Labour_Involuntary_Labour = (
                Human_Rights_related_complaints.objects.filter(
                    Financial_Year=previous_financial_year,
                    Complaint_Type="Forced Labour/Involuntary Labour",
                ).first()
            )

            current_year_Sexual_Harassement = (
                Human_Rights_related_complaints.objects.filter(
                    Financial_Year=financial_year, Complaint_Type="Sexual Harassement"
                ).first()
            )

            previous_year_Sexual_Harassement = (
                Human_Rights_related_complaints.objects.filter(
                    Financial_Year=previous_financial_year,
                    Complaint_Type="Sexual Harassement",
                ).first()
            )

            current_year_Discrimination_at_workplace = (
                Human_Rights_related_complaints.objects.filter(
                    Financial_Year=financial_year,
                    Complaint_Type="Discrimination at workplace",
                ).first()
            )

            previous_year_Discrimination_at_workplace = (
                Human_Rights_related_complaints.objects.filter(
                    Financial_Year=previous_financial_year,
                    Complaint_Type="Discrimination at workplace",
                ).first()
            )

            current_year_Wages = Human_Rights_related_complaints.objects.filter(
                Financial_Year=financial_year, Complaint_Type="Wages"
            ).first()

            previous_year_Wages = Human_Rights_related_complaints.objects.filter(
                Financial_Year=previous_financial_year, Complaint_Type="Wages"
            ).first()

            current_year_Other_Human_Rights_Related_Issues = (
                Human_Rights_related_complaints.objects.filter(
                    Financial_Year=financial_year,
                    Complaint_Type="Other Human Rights Related Issues",
                ).first()
            )

            previous_year_Other_Human_Rights_Related_Issues = (
                Human_Rights_related_complaints.objects.filter(
                    Financial_Year=previous_financial_year,
                    Complaint_Type="Other Human Rights Related Issues",
                ).first()
            )

            ####################################################################################################

            description_obj8 = Policy_Details_Human_Rights.objects.filter(
                Model_Name_Human_Rights="Adverse Consequences"
            ).first()

            # description_obj9 = Policy_Details_Human_Rights.objects.filter(
            #     Model_Name_Human_Rights="Business Agreement"
            # ).first()


            # print("============",description_obj9)


            description_obj9_value_is_verified = "-"
            description_obj9_value_descriptions = "-"

            try:
                description_obj9 = Policy_Details_Human_Rights.objects.filter(
                    Model_Name_Human_Rights="Business Agreement"
                ).first()
                if description_obj9:
                    description_obj9_value_is_verified = description_obj9.Is_Verified
                    description_obj9_value_descriptions = description_obj9.Descriptions_Human_Rights
            except Policy_Details_Human_Rights.DoesNotExist:
                pass

            # print("======///======",description_obj9_value_is_verified)
            # print("======///======",description_obj9_value_descriptions)



            Assessment = (
                Assessment_of_plants_and_offices_Policies_and_Penalties.objects.filter(
                    Financial_Year=financial_year
                )
            )
            response_data["Principle_5_EI_10"] = {
                "Child_Labour": [],
                "Forced_Involuntary_Labour": [],
                "Sexual_Harasement": [],
                "Discrimination_at_workplace": [],
                "Wages": [],
                "Others": [],
            }

            # Define the to_decimal function
            def safe_to_decimal(value):
                try:
                    # Convert Decimal128 to string first, then to Decimal
                    if isinstance(value, Decimal128):
                        value = str(value)
                    return (
                        Decimal(value)
                        if value is not None and value != ""
                        else Decimal("0.0")
                    )
                except (InvalidOperation, ValueError, TypeError):
                    return Decimal("0.0")  # Return 0.0 if the value cannot be converted

            Assessment_data_plant = list(
                Assessment_of_plants_and_offices_Policies_and_Penalties.objects.values("Corrective_Action")
            )

            # Check if data is empty and handle the "Nil" case
            if not Assessment_data_plant:
                data_plant = [{"Corrective_Action": "Nil"}]
            else:
                data_plant = Assessment_data_plant

            description_objL1 = Policy_Details_Human_Rights.objects.filter(
                Model_Name_Human_Rights="Details of a Business"
            ).first()

            description_objL2 = Policy_Details_Human_Rights.objects.filter(
                Model_Name_Human_Rights="Scope and Coverage"
            ).first()

            description_objL3 = Policy_Details_Human_Rights.objects.filter(
                Model_Name_Human_Rights="Entity Accessible"
            ).first()

            Assessment_value = Assessment_of_value_chain_partners_Policies_and_Penalties.objects.filter(
                Financial_Year=financial_year
            )
            response_data["Principle_5_LI_4"] = {
                "Child_Labour": [],
                "Forced_Involuntary_Labour": [],
                "Sexual_Harasement": [],
                "Discrimination_at_workplace": [],
                "Wages": [],
                "Others": [],
                "Number_of_Suppliers": [],
            }

            # Define the to_decimal function
            def safe_to_decimal(value):
                try:
                    # Convert Decimal128 to string first, then to Decimal
                    if isinstance(value, Decimal128):
                        value = str(value)
                    return (
                        Decimal(value)
                        if value is not None and value != ""
                        else Decimal("0.0")
                    )
                except (InvalidOperation, ValueError, TypeError):
                    return Decimal("0.0")

            current_data_p5 = {
                "Child_Labour": "-",
                "Forced_Involuntary_Labour": "-",
                "Sexual_Harasement": "-",
                "Discrimination_at_workplace": "-",
                "Wages": "-",
                "Others": "-",
                "Corrective_Action": "-",
                "Percentage_for_Others": "-",
                "Number_of_Suppliers": "-",
            }
            previous_data_p5 = {
                "Child_Labour": "-",
                "Forced_Involuntary_Labour": "-",
                "Sexual_Harasement": "-",
                "Discrimination_at_workplace": "-",
                "Wages": "-",
                "Others": "-",
                "Corrective_Action": "-",
                "Percentage_for_Others": "-",
                "Number_of_Suppliers": "-",
            }

            # Fetch current financial year data
            try:
                current_assessment = Assessment_of_value_chain_partners_Policies_and_Penalties.objects.get(
                    Financial_Year=financial_year
                )
                current_data_p5["Child_Labour"] = (
                    str(current_assessment.Child_Labour)
                    if current_assessment.Child_Labour
                    else "-"
                )
                current_data_p5["Forced_Involuntary_Labour"] = (
                    str(current_assessment.Forced_Involuntary_Labour)
                    if current_assessment.Forced_Involuntary_Labour
                    else "-"
                )
                current_data_p5["Sexual_Harasement"] = (
                    str(current_assessment.Sexual_Harasement)
                    if current_assessment.Sexual_Harasement
                    else "-"
                )
                current_data_p5["Discrimination_at_workplace"] = (
                    str(current_assessment.Discrimination_at_workplace)
                    if current_assessment.Discrimination_at_workplace
                    else "-"
                )
                current_data_p5["Wages"] = (
                    str(current_assessment.Wages) if current_assessment.Wages else "-"
                )
                current_data_p5["Others"] = (
                    str(current_assessment.Others) if current_assessment.Others else "-"
                )
                current_data_p5["Corrective_Action"] = (
                    str(current_assessment.Corrective_Action)
                    if current_assessment.Corrective_Action
                    else "-"
                )
                current_data_p5["Percentage_for_Others"] = (
                    str(current_assessment.Percentage_for_Others)
                    if current_assessment.Percentage_for_Others
                    else "-"
                )
                current_data_p5["Number_of_Suppliers"] = (
                    str(current_assessment.Number_of_Suppliers)
                    if current_assessment.Number_of_Suppliers
                    else "-"
                )

            except (
                Assessment_of_value_chain_partners_Policies_and_Penalties.DoesNotExist
            ):
                pass

            # Fetch previous financial year data
             # Fetch previous financial year data
            try:
                previous_assessment = Assessment_of_value_chain_partners_Policies_and_Penalties.objects.get(
                    Financial_Year=previous_financial_year
                )
                previous_data_p5["Child_Labour"] = (
                    str(previous_assessment.Child_Labour)
                    if previous_assessment.Child_Labour
                    else "-"
                )

                previous_data_p5["Forced_Involuntary_Labour"] = (
                    str(previous_assessment.Forced_Involuntary_Labour)
                    if previous_assessment.Forced_Involuntary_Labour
                    else "-"
                )
                previous_data_p5["Sexual_Harasement"] = (
                    str(previous_assessment.Sexual_Harasement)
                    if previous_assessment.Sexual_Harasement
                    else "-"
                )
                previous_data_p5["Discrimination_at_workplace"] = (
                    str(previous_assessment.Discrimination_at_workplace)
                    if previous_assessment.Discrimination_at_workplace
                    else "-"
                )
                previous_data_p5["Wages"] = (
                    str(previous_assessment.Wages) if previous_assessment.Wages else "Nil"
                )
                previous_data_p5["Others"] = (
                    str(previous_assessment.Others)
                    if previous_assessment.Others
                    else "-"
                )
                previous_data_p5["Corrective_Action"] = (
                    str(previous_assessment.Corrective_Action)
                    if previous_assessment.Corrective_Action
                    else "-"
                )
                previous_data_p5["Percentage_for_Others"] = (
                    str(previous_assessment.Percentage_for_Others)
                    if previous_assessment.Percentage_for_Others
                    else "-"
                )
                previous_data_p5["Number_of_Suppliers"] = (
                    str(previous_assessment.Number_of_Suppliers)
                    if previous_assessment.Number_of_Suppliers
                    else "-"
                )

            except (
                Assessment_of_value_chain_partners_Policies_and_Penalties.DoesNotExist
            ):
                pass

            Assessment_data = list(
                                Assessment_of_value_chain_partners_Policies_and_Penalties.objects.values("Corrective_Action")
                            )

                # Check if data is empty and handle the "Nil" case
            if not Assessment_data:
                data_value = [{"Corrective_Action": "NA"}]
            else:
                data_value = Assessment_data


            # @@@@@@@@@@@@@@@@@@@@@@ P5 EI 7 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # Filter records for the current financial year
            current_year_records = (
                Receive_And_Redress_Grievance_Mechanism.objects.filter(
                    Financial_Year=financial_year
                )
            )
            # print('current_year_records: ', current_year_records)
            previous_year_records = (
                Receive_And_Redress_Grievance_Mechanism.objects.filter(
                    Financial_Year=previous_financial_year
                )
            )
            # print('previous_year_records: ', previous_year_records)

            current_female_sum = 0.0
            current_percent_female_sum = 0.0
            current_upheld_set = set()

            # Calculate sums for current year records
            current_upheld_string = 0
            for record in current_year_records:
                current_female_sum += conversion(
                    record.Female or 0
                )  # Add directly without sum()
                current_percent_female_sum += conversion(
                    record.Percent_Of_Female_Employee_Divided_By_Worker or 0
                )  # Add directly without sum()
                if record.Upheld:
                    # current_upheld_set.add(record.Upheld.strip())
                    current_upheld_string += int(record.Upheld)

            # current_upheld_string = ", ".join(current_upheld_set)
            # Initialize sums for previous year
            previous_female_sum = 0.0
            previous_percent_female_sum = 0.0
            previous_upheld_set = set()

            # Calculate sums for previous year records
            previous_upheld_string = 0
            for record in previous_year_records:
                previous_female_sum += conversion(
                    record.Female
                )  # Add directly without sum()
                previous_percent_female_sum += conversion(
                    record.Percent_Of_Female_Employee_Divided_By_Worker
                )  # Add directly without sum()
                if record.Upheld:
                    previous_upheld_string += int(record.Upheld)
                    # previous_upheld_set.add(record.Upheld.strip())

            # previous_upheld_string = ", ".join(previous_upheld_set)

            # @@@@@@@@@@@@@@@@@@@@@@ @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            response_data = {
                "Section_C_P5":{
                   

                    "Principal_5_EI_1_EMP_PERMANENT": [{
                              
                            
                            "total_permanent_current_year": total_permanent_current_year if total_permanent_current_year else "-",
                            "current_total_permanent_employees": current_total_permanent_employees if current_total_permanent_employees else "-",
                            "current_year_percentage_emp_permanent": round(
                                (safe_float(current_total_permanent_employees) / safe_float(total_permanent_current_year))*100, 2
                            ) if total_permanent_current_year else "-",
                            "total_permanent_previous_year": total_permanent_previous_year if total_permanent_previous_year else "-",
                            "previous_total_permanent_employees": previous_total_permanent_employees if previous_total_permanent_employees else "-",
                            "previous_year_percentage_emp_permanent": round(
                                safe_float(previous_total_permanent_employees) / safe_float(total_permanent_previous_year)*100, 2
                            ) if total_permanent_previous_year else "-"
                               
                }],
                    "Principal_5_EI_1_EMP_NON_PERMANENT": [{
                              
                           
                            "total_non_permanent_current_year": total_non_permanent_current_year if total_non_permanent_current_year else "-",
                            "current_total_non_permanent_employees": current_total_non_permanent_employees if current_total_non_permanent_employees else "-",
                            "current_year_percentage_emp_non_permanent": round(
                                safe_float(current_total_non_permanent_employees) / safe_float(total_non_permanent_current_year)*100, 2
                            ) if total_non_permanent_current_year else "-",
                            
                            "total_non_permanent_previous_year": total_non_permanent_previous_year if total_non_permanent_previous_year else "-",
                            "previous_total_non_permanent_employees": previous_total_non_permanent_employees if previous_total_non_permanent_employees else "-",
                            "previous_year_percentage_emp_non_permanent": round(
                                safe_float(previous_total_non_permanent_employees) / safe_float(total_non_permanent_previous_year)*100, 2
                            ) if total_non_permanent_previous_year else "-"
 
                               
                }],
                    "Principal_5_EI_1_WKR_PERMANENT": [{
                              
                               
                                "total_permanent_current_year_work": total_permanent_current_year_work if total_permanent_current_year_work else "-",
                                "current_total_permanent_workers": current_total_permanent_workers if current_total_permanent_workers else "-",
                                "current_year_percentage_wkr_permanent": round(
                                    safe_float(current_total_permanent_workers) / safe_float(total_permanent_current_year_work)*100, 2
                                ) if total_permanent_current_year_work else "-",
                               
                                "total_permanent_previous_year_work": total_permanent_previous_year_work if total_permanent_previous_year_work else "-",
                                "previous_total_permanent_workers": previous_total_permanent_workers if previous_total_permanent_workers else "-",
                                "previous_year_percentage_wkr_permanent": round(
                                    safe_float(previous_total_permanent_workers) / safe_float(total_permanent_previous_year_work)*100, 2
                                ) if total_permanent_previous_year_work else "-"

                }],
                                
                    "Principal_5_EI_1_WKR_NON_PERMANENT": [{
                              
                              
                            "total_non_permanent_current_year_work": total_non_permanent_current_year_work if total_non_permanent_current_year_work else "-",
                            "current_total_non_permanent_workers": current_total_non_permanent_workers if current_total_non_permanent_workers else "-",
                            "current_year_percentage_wkr_non_permanent": round(
                                safe_float(current_total_non_permanent_workers) / safe_float(total_non_permanent_current_year_work)*100, 2
                            ) if total_non_permanent_current_year_work else "-",
                           
                            "total_non_permanent_previous_year_work": total_non_permanent_previous_year_work if total_non_permanent_previous_year_work else "-",
                            "previous_total_non_permanent_workers": previous_total_non_permanent_workers if previous_total_non_permanent_workers else "-",
                            "previous_year_percentage_wkr_non_permanent": round(
                                safe_float(previous_total_non_permanent_workers) / safe_float(total_non_permanent_previous_year_work)*100, 2
                            ) if total_non_permanent_previous_year_work else "-"

                }],
                    
                    "Principal_5_EI_1_TOTAL_EMP": [{
                               
                            "total_current_year_employees": (total_permanent_current_year + total_non_permanent_current_year) if (total_permanent_current_year + total_non_permanent_current_year) else "-",
                            "current_total_employees": (current_total_permanent_employees + current_total_non_permanent_employees) if (current_total_permanent_employees + current_total_non_permanent_employees) else "-",
                            "current_year_percentage_total": round(
                               
                                (safe_float(current_total_permanent_employees) + safe_float(current_total_non_permanent_employees))/
                                 (safe_float(total_permanent_current_year) + safe_float(total_non_permanent_current_year))*100 , 2
                            ) if total_permanent_current_year and total_non_permanent_current_year else "-",

                           
                            "total_previous_year_employees": (total_permanent_previous_year + total_non_permanent_previous_year) if (total_permanent_previous_year + total_non_permanent_previous_year) else "-",
                            "previous_total_employees": (previous_total_permanent_employees + previous_total_non_permanent_employees) if (previous_total_permanent_employees + previous_total_non_permanent_employees) else "-",
                            "previous_year_percentage_total": round(
                               
                                (safe_float(previous_total_permanent_employees) + safe_float(previous_total_non_permanent_employees))/
                                 (safe_float(total_permanent_previous_year) + safe_float(total_non_permanent_previous_year)) *100 , 2
                            ) if total_permanent_previous_year and total_non_permanent_previous_year else "-"

                               
                }],


                        "Principal_5_EI_1_TOTAL_WKR": [{
                              
                               
                            "current_year_total_work": (total_permanent_current_year_work + total_non_permanent_current_year_work) if (total_permanent_current_year_work + total_non_permanent_current_year_work) else "-",
                            "current_year_total_workers": (current_total_permanent_workers + current_total_non_permanent_workers) if (current_total_permanent_workers + current_total_non_permanent_workers) else "-",
                            "current_year_percentage_total_wkr": round(
                               
                                (safe_float(current_total_permanent_workers) + safe_float(current_total_non_permanent_workers))/
                                 (safe_float(total_permanent_current_year_work) + safe_float(total_non_permanent_current_year_work))*100 , 2
                            ) if total_permanent_current_year_work and  total_non_permanent_current_year_work else "-",
                           
                            "previous_year_total_work": (total_permanent_previous_year_work + total_non_permanent_previous_year_work) if (total_permanent_previous_year_work + total_non_permanent_previous_year_work) else "-",
                            "previous_year_total_workers": (previous_total_permanent_workers + previous_total_non_permanent_workers) if (previous_total_permanent_workers + previous_total_non_permanent_workers) else "-",
                            "previous_year_percentage_total_wkr": round(
                               
                                (safe_float(previous_total_permanent_workers) + safe_float(previous_total_non_permanent_workers))/ (safe_float(total_permanent_previous_year_work) + safe_float(total_non_permanent_previous_year_work))*100, 2
                            ) if total_permanent_previous_year_work + total_non_permanent_previous_year_work else "-"
                                            
                }],
                          
                          
                          
                        "Principal_5_EI_2_EMP_PERMANENT_MALE": [{
                              
                                "total_male_permanent_current_year": total_male_permanent_current_year if total_male_permanent_current_year else 0,
                                "current_total_permanent_Males_With_Equal_To_Minimum_Wages_employees": current_total_permanent_Males_With_Equal_To_Minimum_Wages_employees if current_total_permanent_Males_With_Equal_To_Minimum_Wages_employees else 0,
                                "current_minimum_wage_ratio": safe_divide(current_total_permanent_Males_With_Equal_To_Minimum_Wages_employees, total_male_permanent_current_year) if total_male_permanent_current_year else 0,
                                "current_permanent_male_employees_more_than_minimum_wages": current_permanent_male_employees_more_than_minimum_wages if current_permanent_male_employees_more_than_minimum_wages else 0,
                                "current_permanent_above_minimum_wage_ratio": safe_divide(current_permanent_male_employees_more_than_minimum_wages, total_male_permanent_current_year) if total_male_permanent_current_year else 0,
                                "total_male_permanent_previous_year": total_male_permanent_previous_year if total_male_permanent_previous_year else 0,
                                "previous_total_permanent_male_employees": previous_total_permanent_male_employees if previous_total_permanent_male_employees else 0,
                                "previous_minimum_wage_ratio": safe_divide(previous_total_permanent_male_employees, total_male_permanent_previous_year) if total_male_permanent_previous_year else 0,
                                "previous_permanent_male_employees_more_than_minimum_wages": previous_permanent_male_employees_more_than_minimum_wages if previous_permanent_male_employees_more_than_minimum_wages else 0,
                                "previous_above_minimum_wage_ratio": safe_divide(previous_permanent_male_employees_more_than_minimum_wages, total_male_permanent_previous_year) if total_male_permanent_previous_year else 0

                }],
                               
                        "Principal_5_EI_2_EMP_PERMANENT_FEMALE": [{
                              
                                "total_female_permanent_current_year": total_female_permanent_current_year if total_female_permanent_current_year else 0,
                                "current_total_permanent_females_with_equal_to_minimum_wages_employees": current_total_permanent_females_With_Equal_To_Minimum_Wages_employees if current_total_permanent_females_With_Equal_To_Minimum_Wages_employees else 0,
                                "ratio_of_current_total_permanent_females_with_minimum_wages": safe_divide(current_total_permanent_females_With_Equal_To_Minimum_Wages_employees, total_female_permanent_current_year) if total_female_permanent_current_year else 0,
                                "current_permanent_female_employees_more_than_minimum_wages": current_permanent_female_employees_more_than_minimum_wages if current_permanent_female_employees_more_than_minimum_wages else 0,
                                "ratio_of_current_permanent_female_employees_more_than_minimum_wages": safe_divide(current_permanent_female_employees_more_than_minimum_wages, total_female_permanent_current_year) if total_female_permanent_current_year else 0,
                                "total_female_permanent_previous_year": total_female_permanent_previous_year if total_female_permanent_previous_year else 0,
                                "previous_total_permanent_female_employees": previous_total_permanent_female_employees if previous_total_permanent_female_employees else 0,
                                "ratio_of_previous_total_permanent_female_employees": safe_divide(previous_total_permanent_female_employees, total_female_permanent_previous_year) if total_female_permanent_previous_year else 0,
                                "previous_permanent_female_employees_more_than_minimum_wages": previous_permanent_female_employees_more_than_minimum_wages if previous_permanent_female_employees_more_than_minimum_wages else 0,
                                "ratio_of_previous_permanent_female_employees_more_than_minimum_wages": safe_divide(previous_permanent_female_employees_more_than_minimum_wages, total_female_permanent_previous_year) if total_female_permanent_previous_year else 0

                }],
                               
                        "Principal_5_EI_2_PERMANENT_TOTAL_EMP": [{
                            "total_permanent_employees": (total_male_permanent_current_year + total_female_permanent_current_year) if  (total_male_permanent_current_year + total_female_permanent_current_year) else 0,
                            "permanent_employees_equal_to_minimum_wages": (current_total_permanent_Males_With_Equal_To_Minimum_Wages_employees + current_total_permanent_females_With_Equal_To_Minimum_Wages_employees)if  (current_total_permanent_Males_With_Equal_To_Minimum_Wages_employees + current_total_permanent_females_With_Equal_To_Minimum_Wages_employees) else 0,
                            "percentage_employees_equal_to_minimum_wages": safe_divide((current_total_permanent_Males_With_Equal_To_Minimum_Wages_employees + current_total_permanent_females_With_Equal_To_Minimum_Wages_employees), (total_male_permanent_current_year + total_female_permanent_current_year)) if (total_male_permanent_current_year + total_female_permanent_current_year) else 0,

                            "permanent_employees_more_than_minimum_wages": (current_permanent_male_employees_more_than_minimum_wages + current_permanent_female_employees_more_than_minimum_wages) if (current_permanent_male_employees_more_than_minimum_wages + current_permanent_female_employees_more_than_minimum_wages) else 0,
                            "percentage_employees_more_than_minimum_wages": safe_divide((current_permanent_male_employees_more_than_minimum_wages + current_permanent_female_employees_more_than_minimum_wages), (total_male_permanent_current_year + total_female_permanent_current_year)) if (total_male_permanent_current_year + total_female_permanent_current_year) else 0,

                            # Previous year data
                            "total_permanent_previous_employees": (total_male_permanent_previous_year + total_female_permanent_previous_year) if (total_male_permanent_previous_year + total_female_permanent_previous_year) else 0,
                            "previous_permanent_employees_equal_to_minimum_wages": (previous_total_permanent_male_employees + previous_total_permanent_female_employees) if (previous_total_permanent_male_employees + previous_total_permanent_female_employees) else 0,
                            "previous_percentage_employees_equal_to_minimum_wages": safe_divide((previous_total_permanent_male_employees + previous_total_permanent_female_employees), (total_male_permanent_previous_year + total_female_permanent_previous_year)) if (total_male_permanent_previous_year + total_female_permanent_previous_year) else 0,

                            "previous_permanent_employees_more_than_minimum_wages": (previous_permanent_male_employees_more_than_minimum_wages + previous_permanent_female_employees_more_than_minimum_wages) if (previous_permanent_male_employees_more_than_minimum_wages + previous_permanent_female_employees_more_than_minimum_wages) else 0,
                            "previous_percentage_employees_more_than_minimum_wages": safe_divide((previous_permanent_male_employees_more_than_minimum_wages + previous_permanent_female_employees_more_than_minimum_wages), (total_male_permanent_previous_year + total_female_permanent_previous_year)) if (total_male_permanent_previous_year + total_female_permanent_previous_year) else 0
                }],


                        "Principal_5_EI_2_EMP_NON_PERMANENT_MALE": [{
                                "total_male_non_permanent_current_year": total_male_non_permanent_current_year if total_male_non_permanent_current_year else 0,
                                "current_total_non_permanent_male_employees": current_total_non_permanent_male_employees if current_total_non_permanent_male_employees else 0,
                                "current_total_non_permanent_male_ratio": safe_divide(current_total_non_permanent_male_employees, total_male_non_permanent_current_year) if total_male_non_permanent_current_year else 0,
                                "current_non_permanent_male_employees_above_minimum_wage": current_non_permanent_male_employees_more_than_minimum_wages if current_non_permanent_male_employees_more_than_minimum_wages else 0,
                                "current_ratio_above_minimum_wage": safe_divide(current_non_permanent_male_employees_more_than_minimum_wages, total_male_non_permanent_current_year) if total_male_non_permanent_current_year else 0,
                                "total_male_non_permanent_previous_year": total_male_non_permanent_previous_year if total_male_non_permanent_previous_year else 0,
                                "previous_total_non_permanent_male_employees": previous_total_non_permanent_male_employees if previous_total_non_permanent_male_employees else 0,
                                "previous_total_non_permanent_male_ratio": safe_divide(previous_total_non_permanent_male_employees, total_male_non_permanent_previous_year) if total_male_non_permanent_previous_year else 0,
                                "previous_non_permanent_male_employees_above_minimum_wage": previous_non_permanent_male_employees_more_than_minimum_wages if previous_non_permanent_male_employees_more_than_minimum_wages else 0,
                                "previous_ratio_above_minimum_wage": safe_divide(previous_non_permanent_male_employees_more_than_minimum_wages, total_male_non_permanent_previous_year) if total_male_non_permanent_previous_year else 0

                }],
                                  
                        "Principal_5_EI_2_EMP_NON_PERMANENT_FEMALE": [{
                              
                                "total_female_non_permanent_current_year": total_female_non_permanent_current_year if total_female_non_permanent_current_year else 0,
                                "current_total_non_permanent_female_employees": current_total_non_permanent_female_employees if current_total_non_permanent_female_employees else 0,
                                "current_year_percentage": safe_divide(current_total_non_permanent_female_employees, total_female_non_permanent_current_year) if total_female_non_permanent_current_year else 0,
                                "current_non_permanent_female_employees_more_than_minimum_wages": current_non_permanent_female_employees_more_than_minimum_wages if current_non_permanent_female_employees_more_than_minimum_wages else 0,
                                "current_year_above_minimum_wages_percentage": safe_divide(current_non_permanent_female_employees_more_than_minimum_wages, total_female_non_permanent_current_year) if total_female_non_permanent_current_year else 0,
                                "total_female_non_permanent_previous_year": total_female_non_permanent_previous_year if total_female_non_permanent_previous_year else 0,
                                "previous_total_non_permanent_female_employees": previous_total_non_permanent_female_employees if previous_total_non_permanent_female_employees else 0,
                                "previous_year_percentage": safe_divide(previous_total_non_permanent_female_employees, total_female_non_permanent_previous_year) if total_female_non_permanent_previous_year else 0,
                                "previous_non_permanent_female_employees_more_than_minimum_wages": previous_non_permanent_female_employees_more_than_minimum_wages if previous_non_permanent_female_employees_more_than_minimum_wages else 0,
                                "previous_year_above_minimum_wages_percentage": safe_divide(previous_non_permanent_female_employees_more_than_minimum_wages, total_female_non_permanent_previous_year) if total_female_non_permanent_previous_year else 0
                                
                               
                }],

                        "Principal_5_EI_2_NON_PERMANENT_TOTAL_EMP": [{
                            # Current year data
                            "total_non_permanent_employees_current_year": (total_male_non_permanent_current_year + total_female_non_permanent_current_year) if (total_male_non_permanent_current_year + total_female_non_permanent_current_year) else 0,
                            "current_non_permanent_employees": (current_total_non_permanent_male_employees + current_total_non_permanent_female_employees) if (current_total_non_permanent_male_employees + current_total_non_permanent_female_employees) else 0,
                            "current_year_ratio": safe_divide((current_total_non_permanent_male_employees + current_total_non_permanent_female_employees), (total_male_non_permanent_current_year + total_female_non_permanent_current_year)) if (total_male_non_permanent_current_year + total_female_non_permanent_current_year) else 0,

                            "current_employees_above_minimum_wage": (current_non_permanent_male_employees_more_than_minimum_wages + current_non_permanent_female_employees_more_than_minimum_wages) if (current_non_permanent_male_employees_more_than_minimum_wages + current_non_permanent_female_employees_more_than_minimum_wages) else 0,
                            "current_non_permanent_above_minimum_wage_ratio": safe_divide((current_non_permanent_male_employees_more_than_minimum_wages + current_non_permanent_female_employees_more_than_minimum_wages), (total_male_non_permanent_current_year + total_female_non_permanent_current_year)) if (total_male_non_permanent_current_year + total_female_non_permanent_current_year) else 0,

                            # Previous year data
                            "total_non_permanent_employees_previous_year": (total_male_non_permanent_previous_year + total_female_non_permanent_previous_year) if (total_male_non_permanent_previous_year + total_female_non_permanent_previous_year) else 0,
                            "previous_non_permanent_employees": (previous_total_non_permanent_male_employees + previous_total_non_permanent_female_employees) if (previous_total_non_permanent_male_employees + previous_total_non_permanent_female_employees) else 0,
                            "previous_year_ratio": safe_divide((previous_total_non_permanent_male_employees + previous_total_non_permanent_female_employees), (total_male_non_permanent_previous_year + total_female_non_permanent_previous_year)) if (total_male_non_permanent_previous_year + total_female_non_permanent_previous_year) else 0,

                            "previous_employees_above_minimum_wage": (previous_non_permanent_male_employees_more_than_minimum_wages + previous_non_permanent_female_employees_more_than_minimum_wages) if (previous_non_permanent_male_employees_more_than_minimum_wages + previous_non_permanent_female_employees_more_than_minimum_wages) else 0,
                            "previous_above_minimum_wage_ratio": safe_divide((previous_non_permanent_male_employees_more_than_minimum_wages + previous_non_permanent_female_employees_more_than_minimum_wages), (total_male_non_permanent_previous_year + total_female_non_permanent_previous_year)) if (total_male_non_permanent_previous_year + total_female_non_permanent_previous_year) else 0
                }],
                        

                        "Principal_5_EI_2_WKR_PERMANENT_FEMALE": [{
                                "total_female_permanent_workers_current_year": total_female_permanent_workers_current_year if total_female_permanent_workers_current_year else 0,
                                "current_permanent_females_equal_to_minimum_wages": current_permanent_females_With_Equal_To_Minimum_Wages if current_permanent_females_With_Equal_To_Minimum_Wages else 0,
                                "proportion_females_equal_to_minimum_wages": safe_divide(current_permanent_females_With_Equal_To_Minimum_Wages, total_female_permanent_workers_current_year) if total_female_permanent_workers_current_year else 0,
                                "current_permanent_females_more_than_minimum_wages": current_permanent_female_worker_more_than_minimum_wages if current_permanent_female_worker_more_than_minimum_wages else 0,
                                "proportion_females_more_than_minimum_wages": safe_divide(current_permanent_female_worker_more_than_minimum_wages, total_female_permanent_workers_current_year) if total_female_permanent_workers_current_year else 0,
                                "total_female_permanent_workers_previous_year": total_female_permanent_workers_previous_year if total_female_permanent_workers_previous_year else 0,
                                "previous_females_equal_to_minimum_wages": previous_total_permanent_females_With_Equal_To_Minimum_Wages_workers if previous_total_permanent_females_With_Equal_To_Minimum_Wages_workers else 0,
                                "proportion_previous_females_equal_to_minimum_wages": safe_divide(previous_total_permanent_females_With_Equal_To_Minimum_Wages_workers, total_female_permanent_workers_previous_year) if total_female_permanent_workers_previous_year else 0,
                                "previous_females_more_than_minimum_wages": previous_total_permanent_Females_With_More_Than_Minimum_Wages_workers if previous_total_permanent_Females_With_More_Than_Minimum_Wages_workers else 0,
                                "proportion_previous_females_more_than_minimum_wages": safe_divide(previous_total_permanent_Females_With_More_Than_Minimum_Wages_workers, total_female_permanent_workers_previous_year) if total_female_permanent_workers_previous_year else 0,
                }],      
                        "Principal_5_EI_2_WKR_PERMANENT_MALE": [{
                                "total_male_permanent_workers_current_year": total_male_permanent_workers_current_year if total_male_permanent_workers_current_year else 0,
                                "current_permanen_males_with_equal_to_minimum_wages": current_permanen_Males_With_Equal_To_Minimum_Wages if current_permanen_Males_With_Equal_To_Minimum_Wages else 0,
                                "ratio_current_permanen_males_equal_to_minimum_wages": safe_divide(current_permanen_Males_With_Equal_To_Minimum_Wages, total_male_permanent_workers_current_year) if total_male_permanent_workers_current_year else 0,
                                "current_permanent_male_worker_more_than_minimum_wages": current_permanent_male_worker_more_than_minimum_wages if current_permanent_male_worker_more_than_minimum_wages else 0,
                                "ratio_current_permanent_male_more_than_minimum_wages": safe_divide(current_permanent_male_worker_more_than_minimum_wages, total_male_permanent_workers_current_year) if total_male_permanent_workers_current_year else 0,
                                "total_male_permanent_workers_previous_year": total_male_permanent_workers_previous_year if total_male_permanent_workers_previous_year else 0,
                                "previous_total_permanent_males_equal_to_minimum_wages_workers": previous_total_permanent_Males_With_Equal_To_Minimum_Wages_workers if previous_total_permanent_Males_With_Equal_To_Minimum_Wages_workers else 0,
                                "ratio_previous_permanent_males_equal_to_minimum_wages": safe_divide(previous_total_permanent_Males_With_Equal_To_Minimum_Wages_workers, total_male_permanent_workers_previous_year) if total_male_permanent_workers_previous_year else 0,
                                "previous_total_permanent_males_more_than_minimum_wages_workers": previous_total_permanent_males_With_More_Than_Minimum_Wages_workers if previous_total_permanent_males_With_More_Than_Minimum_Wages_workers else 0,
                                "ratio_previous_permanent_males_more_than_minimum_wages": safe_divide(previous_total_permanent_males_With_More_Than_Minimum_Wages_workers, total_male_permanent_workers_previous_year) if total_male_permanent_workers_previous_year else 0,
                }],  

                        "Principal_5_EI_2_WKR_PERMANENT_TOTAL_WRK": [{
                                # Current year data
                                "total_permanent_workers": (total_male_permanent_workers_current_year + total_female_permanent_workers_current_year) if (total_male_permanent_workers_current_year + total_female_permanent_workers_current_year) else 0,
                                "workers_equal_to_minimum_wages": (current_permanen_Males_With_Equal_To_Minimum_Wages + current_permanent_females_With_Equal_To_Minimum_Wages) if (current_permanen_Males_With_Equal_To_Minimum_Wages + current_permanent_females_With_Equal_To_Minimum_Wages) else 0,
                                "percentage_equal_to_minimum_wages": safe_divide((current_permanen_Males_With_Equal_To_Minimum_Wages + current_permanent_females_With_Equal_To_Minimum_Wages), (total_male_permanent_workers_current_year + total_female_permanent_workers_current_year)) if (total_male_permanent_workers_current_year + total_female_permanent_workers_current_year) else 0,

                                "workers_more_than_minimum_wages": (current_permanent_male_worker_more_than_minimum_wages + current_permanent_female_worker_more_than_minimum_wages) if (current_permanent_male_worker_more_than_minimum_wages + current_permanent_female_worker_more_than_minimum_wages) else 0,
                                "percentage_more_than_minimum_wages_wkr_permanent": safe_divide((current_permanent_male_worker_more_than_minimum_wages + current_permanent_female_worker_more_than_minimum_wages), (total_male_permanent_workers_current_year + total_female_permanent_workers_current_year)) if (total_male_permanent_workers_current_year + total_female_permanent_workers_current_year) else 0,

                                # Previous year data
                                "total_permanent_workers_previous": (total_male_permanent_workers_previous_year + total_female_permanent_workers_previous_year) if (total_male_permanent_workers_previous_year + total_female_permanent_workers_previous_year) else 0,
                                "previous_permanent_workers_equal_to_minimum_wages": (previous_total_permanent_Males_With_Equal_To_Minimum_Wages_workers + previous_total_permanent_females_With_Equal_To_Minimum_Wages_workers) if (previous_total_permanent_Males_With_Equal_To_Minimum_Wages_workers + previous_total_permanent_females_With_Equal_To_Minimum_Wages_workers) else 0,
                                "percentage_equal_to_minimum_wages_previous": safe_divide((previous_total_permanent_Males_With_Equal_To_Minimum_Wages_workers + previous_total_permanent_females_With_Equal_To_Minimum_Wages_workers), (total_male_permanent_workers_previous_year + total_female_permanent_workers_previous_year)) if (total_male_permanent_workers_previous_year + total_female_permanent_workers_previous_year) else 0,

                                "workers_more_than_minimum_wages_previous": (previous_total_permanent_males_With_More_Than_Minimum_Wages_workers + previous_total_permanent_Females_With_More_Than_Minimum_Wages_workers) if (previous_total_permanent_males_With_More_Than_Minimum_Wages_workers + previous_total_permanent_Females_With_More_Than_Minimum_Wages_workers) else 0,
                                "percentage_more_than_minimum_wages_previous": safe_divide((previous_total_permanent_males_With_More_Than_Minimum_Wages_workers + previous_total_permanent_Females_With_More_Than_Minimum_Wages_workers), (total_male_permanent_workers_previous_year + total_female_permanent_workers_previous_year)) if (total_male_permanent_workers_previous_year + total_female_permanent_workers_previous_year) else 0,
                }],


                        "Principal_5_EI_2_WKR_NON_PERMANENT_MALE": [{
                                "total_male_non_permanent_workers_current_year": total_male_non_permanent_workers_current_year if total_male_non_permanent_workers_current_year else 0,
                                "current_non_permanent_male_worker_With_Equal_To_Minimum_Wages": current_non_permanent_male_worker_With_Equal_To_Minimum_Wages if current_non_permanent_male_worker_With_Equal_To_Minimum_Wages else 0,
                                "current_non_permanent_male_worker_With_Equal_To_Minimum_Wages_ratio": safe_divide(current_non_permanent_male_worker_With_Equal_To_Minimum_Wages, total_male_non_permanent_workers_current_year) if total_male_non_permanent_workers_current_year else 0,
                                "current_non_permanent_male_worker_more_than_minimum_wages": current_non_permanent_male_worker_more_than_minimum_wages if current_non_permanent_male_worker_more_than_minimum_wages else 0,
                                "current_non_permanent_male_worker_more_than_minimum_wages_ratio": safe_divide(current_non_permanent_male_worker_more_than_minimum_wages, total_male_non_permanent_workers_current_year) if total_male_non_permanent_workers_current_year else 0,
                                "total_male_non_permanent_workers_previous_year": total_male_non_permanent_workers_previous_year if total_male_non_permanent_workers_previous_year else 0,
                                "previous_total_non_permanent_Males_With_Equal_To_Minimum_Wages_workers": previous_total_non_permanent_Males_With_Equal_To_Minimum_Wages_workers if previous_total_non_permanent_Males_With_Equal_To_Minimum_Wages_workers else 0,
                                "previous_total_non_permanent_Males_With_Equal_To_Minimum_Wages_workers_ratio": safe_divide(previous_total_non_permanent_Males_With_Equal_To_Minimum_Wages_workers, total_male_non_permanent_workers_previous_year) if total_male_non_permanent_workers_previous_year else 0,
                                "previous_total_non_permanent_males_With_More_Than_Minimum_Wages_workers": previous_total_non_permanent_males_With_More_Than_Minimum_Wages_workers if previous_total_non_permanent_males_With_More_Than_Minimum_Wages_workers else 0,
                                "previous_total_non_permanent_males_With_More_Than_Minimum_Wages_workers_ratio": safe_divide( previous_total_non_permanent_males_With_More_Than_Minimum_Wages_workers, total_male_non_permanent_workers_previous_year) if total_male_non_permanent_workers_previous_year else 0,
                }],
                            
                        "Principal_5_EI_2_WKR_NON_PERMANENT_FEMALE": [{
                                "total_female_non_permanent_workers_current_year": total_female_non_permanent_workers_current_year if total_female_non_permanent_workers_current_year else 0,
                                "current_non_permanent_female_worker_With_Equal_To_Minimum_Wages": current_non_permanent_female_worker_With_Equal_To_Minimum_Wages if current_non_permanent_female_worker_With_Equal_To_Minimum_Wages else 0,
                                "current_non_permanent_female_worker_With_Equal_To_Minimum_Wages_percentage": safe_divide(current_non_permanent_female_worker_With_Equal_To_Minimum_Wages, total_female_non_permanent_workers_current_year) if total_female_non_permanent_workers_current_year else 0,
                                "current_non_permanent_female_worker_more_than_minimum_wages": current_non_permanent_female_worker_more_than_minimum_wages if current_non_permanent_female_worker_more_than_minimum_wages else 0,
                                "current_non_permanent_female_worker_more_than_minimum_wages_percentage": safe_divide(current_non_permanent_female_worker_more_than_minimum_wages, total_female_non_permanent_workers_current_year) if total_female_non_permanent_workers_current_year else 0,
                                "total_female_non_permanent_workers_previous_year": total_female_non_permanent_workers_previous_year if total_female_non_permanent_workers_previous_year else 0,
                                "previous_total_non_permanent_females_With_Equal_To_Minimum_Wages_workers": previous_total_non_permanent_females_With_Equal_To_Minimum_Wages_workers if previous_total_non_permanent_females_With_Equal_To_Minimum_Wages_workers else 0,
                                "previous_total_non_permanent_females_With_Equal_To_Minimum_Wages_workers_percentage": safe_divide(previous_total_non_permanent_females_With_Equal_To_Minimum_Wages_workers, total_female_non_permanent_workers_previous_year) if total_female_non_permanent_workers_previous_year else 0,
                                "previous_total_non_permanent_Females_With_More_Than_Minimum_Wages_workers": previous_total_non_permanent_Females_With_More_Than_Minimum_Wages_workers if previous_total_non_permanent_Females_With_More_Than_Minimum_Wages_workers else 0,
                                "previous_total_non_permanent_Females_With_More_Than_Minimum_Wages_workers_percentage": safe_divide(previous_total_non_permanent_Females_With_More_Than_Minimum_Wages_workers, total_female_non_permanent_workers_previous_year) if total_female_non_permanent_workers_previous_year else 0,
                }],
                            
                        "Principal_5_EI_2_WKR_NON_PERMANENT_TOTAL_WRK": [{
                        # Current year data
                        "total_non_permanent_workers": (total_male_non_permanent_workers_current_year + total_female_non_permanent_workers_current_year) if (total_male_non_permanent_workers_current_year + total_female_non_permanent_workers_current_year) else 0,
                        "total_non_permanent_workers_with_equal_minimum_wages": (current_non_permanent_male_worker_With_Equal_To_Minimum_Wages + current_non_permanent_female_worker_With_Equal_To_Minimum_Wages) if (current_non_permanent_male_worker_With_Equal_To_Minimum_Wages + current_non_permanent_female_worker_With_Equal_To_Minimum_Wages) else 0,
                        "percentage_equal_minimum_wages": safe_divide((current_non_permanent_male_worker_With_Equal_To_Minimum_Wages + current_non_permanent_female_worker_With_Equal_To_Minimum_Wages), (total_male_non_permanent_workers_current_year + total_female_non_permanent_workers_current_year)) if (total_male_non_permanent_workers_current_year + total_female_non_permanent_workers_current_year) else 0,

                        "total_non_permanent_workers_with_more_than_minimum_wages": (current_non_permanent_male_worker_more_than_minimum_wages + current_non_permanent_female_worker_more_than_minimum_wages) if (current_non_permanent_male_worker_more_than_minimum_wages + current_non_permanent_female_worker_more_than_minimum_wages) else 0,
                        "percentage_more_than_minimum_wages_wkr_non_permanent": safe_divide((current_non_permanent_male_worker_more_than_minimum_wages + current_non_permanent_female_worker_more_than_minimum_wages), (total_male_non_permanent_workers_current_year + total_female_non_permanent_workers_current_year)) if (total_male_non_permanent_workers_current_year + total_female_non_permanent_workers_current_year) else 0,

                        # Previous year data
                        "total_non_permanent_workers_previous_year": (total_male_non_permanent_workers_previous_year + total_female_non_permanent_workers_previous_year) if (total_male_non_permanent_workers_previous_year + total_female_non_permanent_workers_previous_year) else 0,
                        "total_non_permanent_workers_with_equal_minimum_wages_previous_year": (previous_total_non_permanent_Males_With_Equal_To_Minimum_Wages_workers + previous_total_non_permanent_females_With_Equal_To_Minimum_Wages_workers) if (previous_total_non_permanent_Males_With_Equal_To_Minimum_Wages_workers + previous_total_non_permanent_females_With_Equal_To_Minimum_Wages_workers) else 0,
                        "percentage_equal_minimum_wages_previous_year": safe_divide((previous_total_non_permanent_Males_With_Equal_To_Minimum_Wages_workers + previous_total_non_permanent_females_With_Equal_To_Minimum_Wages_workers), (total_male_non_permanent_workers_previous_year + total_female_non_permanent_workers_previous_year)) if (total_male_non_permanent_workers_previous_year + total_female_non_permanent_workers_previous_year) else 0,

                        "total_non_permanent_workers_with_more_than_minimum_wages_previous_year": (previous_total_non_permanent_males_With_More_Than_Minimum_Wages_workers + previous_total_non_permanent_Females_With_More_Than_Minimum_Wages_workers) if (previous_total_non_permanent_males_With_More_Than_Minimum_Wages_workers + previous_total_non_permanent_Females_With_More_Than_Minimum_Wages_workers) else 0,
                        "percentage_more_than_minimum_wages_previous_year": safe_divide((previous_total_non_permanent_males_With_More_Than_Minimum_Wages_workers + previous_total_non_permanent_Females_With_More_Than_Minimum_Wages_workers), (total_male_non_permanent_workers_previous_year + total_female_non_permanent_workers_previous_year)) if (total_male_non_permanent_workers_previous_year + total_female_non_permanent_workers_previous_year) else 0,
                }],




                        "Principle_5_EI_3a_BOD": [{
                            "total_male_board_of_directors": total_male_board_of_directors if total_male_board_of_directors else 0,
                            "median_male_board_of_directors": decimal_from_decimal128(getattr(median_data, 'Males_Board_Of_Directors', None)) if median_data else 0,
                            "total_female_board_of_directors": total_female_board_of_directors if total_female_board_of_directors else 0,
                            "median_female_board_of_directors": decimal_from_decimal128(getattr(median_data, 'Females_Board_Of_Directors', None)) if median_data else 0,
                }],
                        
                        "Principle_5_EI_3a_KMP": [{
                            "total_male_key_management": total_male_key_management if total_male_key_management else 0,
                            "male_key_management_median": decimal_from_decimal128(getattr(median_data, 'Males_Key_Management_Personnel', None)) if median_data else 0,
                            "total_female_key_management": total_female_key_management if total_female_key_management else 0,
                            "female_key_management_median": decimal_from_decimal128(getattr(median_data, 'Females_Key_Management_Personnel', None)) if median_data else 0,
                }],
                        
                        "Principle_5_EI_3a_EMP": [{
                            "total_male_permanent_employees": total_male_permanent_employees if total_male_permanent_employees else 0,
                            "median_males_employees": decimal_from_decimal128(getattr(median_data, 'Males_Employees', None)) if median_data else 0,
                            "total_female_permanent_employees": total_female_permanent_employees if total_female_permanent_employees else 0,
                            "median_females_employees": decimal_from_decimal128(getattr(median_data, 'Females_Employees', None)) if median_data else 0,
                }],
                        
                        "Principle_5_EI_3a_WKRs": [{
                            "total_male_permanent_workers": total_male_permanent_workers if total_male_permanent_workers else 0,
                            "males_workers": decimal_from_decimal128(getattr(median_data, 'Males_Workers', None)) if median_data else 0,
                            "total_female_permanent_workers": total_female_permanent_workers if total_female_permanent_workers else 0,
                            "females_workers": decimal_from_decimal128(getattr(median_data, 'Females_Workers', None)) if median_data else 0,
                }],
                        "Principle_5_EI_3b": [{ "current_year": f'{(current_year_sum)}%' if current_year_sum else "-" , 
                                               "previous_year": f'{(previous_year_sum)}%' if previous_year_sum else "-" }] ,  

                        "Principle_5_EI_4": [{"Is_Verified": description_obj4_value_is_verified if description_obj4_value_is_verified else "-",
                                            #   "Descriptions_Human_Rights": None if description_obj4 and description_obj4.Descriptions_Human_Rights=="No" else "-"
                                              "Descriptions_Human_Rights": description_obj4_value_descriptions if description_obj4_value_descriptions else "-"
                                              }],
                        
                        
                       
                        "Principle_5_EI_5": [{"Principle_5_EI_5": description_obj5_value }],

                        "Principle_5_EI_6_CL": [{
                                        "filed_during_the_year": safe_decimal_to_float(current_year_Child_Labour.Filed_During_The_Year) if current_year_Child_Labour else "0",
                                        "pending_resolution_at_the_eoy": safe_decimal_to_float(current_year_Child_Labour.Pending_Resolution_At_The_EOY) if current_year_Child_Labour else "0",
                                        "remark": current_year_Child_Labour.Remark if current_year_Child_Labour else "NA",

                                        "filed_during_the_previous_year": safe_decimal_to_float(previous_year_Child_Labour.Filed_During_The_Year) if previous_year_Child_Labour else "0",
                                        "pending_resolution_at_the_eoy_previous": safe_decimal_to_float(previous_year_Child_Labour.Pending_Resolution_At_The_EOY) if previous_year_Child_Labour else "0",
                                        "remark_previous": previous_year_Child_Labour.Remark if previous_year_Child_Labour else "NA",
                                                                    
                                
                                    
                }],
                        "Principle_5_EI_6_Discrimination": [{
                                "filed_during_the_year": safe_decimal_to_float(current_year_Discrimination_at_workplace.Filed_During_The_Year) if current_year_Discrimination_at_workplace else "0",
                                "pending_resolution_at_the_eoy": safe_decimal_to_float(current_year_Discrimination_at_workplace.Pending_Resolution_At_The_EOY) if current_year_Discrimination_at_workplace else "0",
                                "remark": current_year_Discrimination_at_workplace.Remark if current_year_Discrimination_at_workplace else "NA",

                                "filed_during_the_previous_year": safe_decimal_to_float(previous_year_Discrimination_at_workplace.Filed_During_The_Year) if previous_year_Discrimination_at_workplace else "0",
                                "pending_resolution_at_the_eoy_previous": safe_decimal_to_float(previous_year_Discrimination_at_workplace.Pending_Resolution_At_The_EOY) if previous_year_Discrimination_at_workplace else "0",
                                "remark_previous": previous_year_Discrimination_at_workplace.Remark if previous_year_Discrimination_at_workplace else "NA",
                }],
                            
                        "Principle_5_EI_6_SH": [{
                                "filed_during_the_year": safe_decimal_to_float(current_year_Sexual_Harassement.Filed_During_The_Year) if current_year_Sexual_Harassement else "0",
                                "pending_resolution_at_the_eoy": safe_decimal_to_float(current_year_Sexual_Harassement.Pending_Resolution_At_The_EOY) if current_year_Sexual_Harassement else "0",
                                "remark": current_year_Sexual_Harassement.Remark if current_year_Sexual_Harassement else "NA",

                                "filed_during_the_previous_year": safe_decimal_to_float(previous_year_Sexual_Harassement.Filed_During_The_Year) if previous_year_Sexual_Harassement else "0",
                                "pending_resolution_at_the_eoy_previous": safe_decimal_to_float(previous_year_Sexual_Harassement.Pending_Resolution_At_The_EOY) if previous_year_Sexual_Harassement else "0",
                                "remark_previous": previous_year_Sexual_Harassement.Remark if previous_year_Sexual_Harassement else "NA",
                }],
                            
                        "Principle_5_EI_6_FL": [{
                                "filed_during_the_year": safe_decimal_to_float(current_year_Forced_Labour_Involuntary_Labour.Filed_During_The_Year) if current_year_Forced_Labour_Involuntary_Labour else "0",
                                "pending_resolution_at_the_eoy": safe_decimal_to_float(current_year_Forced_Labour_Involuntary_Labour.Pending_Resolution_At_The_EOY) if current_year_Forced_Labour_Involuntary_Labour else "0",
                                "remark": current_year_Forced_Labour_Involuntary_Labour.Remark if current_year_Forced_Labour_Involuntary_Labour else "NA",

                                "filed_during_the_previous_year": safe_decimal_to_float(previous_year_Forced_Labour_Involuntary_Labour.Filed_During_The_Year) if previous_year_Forced_Labour_Involuntary_Labour else "0",
                                "pending_resolution_at_the_eoy_previous": safe_decimal_to_float(previous_year_Forced_Labour_Involuntary_Labour.Pending_Resolution_At_The_EOY) if previous_year_Forced_Labour_Involuntary_Labour else "0",
                                "remark_previous": previous_year_Forced_Labour_Involuntary_Labour.Remark if previous_year_Forced_Labour_Involuntary_Labour else "NA",
                }],

                        "Principle_5_EI_6_WAGES": [{
                                "filed_during_the_year": safe_decimal_to_float(current_year_Wages.Filed_During_The_Year) if current_year_Wages else "0",
                                "pending_resolution_at_the_eoy": safe_decimal_to_float(current_year_Wages.Pending_Resolution_At_The_EOY) if current_year_Wages else "0",
                                "remark": current_year_Wages.Remark if current_year_Wages else "NA",
 
                                "filed_during_the_previous_year": safe_decimal_to_float(previous_year_Wages.Filed_During_The_Year) if previous_year_Wages else "0",
                                "pending_resolution_at_the_eoy_previous": safe_decimal_to_float(previous_year_Wages.Pending_Resolution_At_The_EOY) if previous_year_Wages else "0",
                                "remark_previous": previous_year_Wages.Remark if previous_year_Wages else "NA",
                }],

                        "Principle_5_EI_6_OTHER": [{
                                "filed_during_the_year": safe_decimal_to_float(current_year_Other_Human_Rights_Related_Issues.Filed_During_The_Year) if current_year_Other_Human_Rights_Related_Issues else "0",
                                "pending_resolution_at_the_eoy": safe_decimal_to_float(current_year_Other_Human_Rights_Related_Issues.Pending_Resolution_At_The_EOY) if current_year_Other_Human_Rights_Related_Issues else "0",
                                "remark": current_year_Other_Human_Rights_Related_Issues.Remark if current_year_Other_Human_Rights_Related_Issues else "NA",

                                "filed_during_the_previous_year": safe_decimal_to_float(previous_year_Other_Human_Rights_Related_Issues.Filed_During_The_Year) if previous_year_Other_Human_Rights_Related_Issues else "0",
                                "pending_resolution_at_the_eoy_previous": safe_decimal_to_float(previous_year_Other_Human_Rights_Related_Issues.Pending_Resolution_At_The_EOY) if previous_year_Other_Human_Rights_Related_Issues else "0",
                                "remark_previous": previous_year_Other_Human_Rights_Related_Issues.Remark if previous_year_Other_Human_Rights_Related_Issues else "NA",
                }],
                        "Principle_5_EI_7_total": [{"current_female_sum": current_female_sum if current_female_sum else "-" , 
                                                   "previous_female_sum": previous_female_sum if previous_female_sum else "-"}],

                        "Principle_5_EI_7_complaint": [{"current_percent_female_sum": round(current_percent_female_sum, 2) if current_percent_female_sum else"-", 
                                                       "previous_percent_female_sum": round(previous_percent_female_sum, 2) if previous_percent_female_sum else "-"}],

                        "Principle_5_EI_7_upheld": [{"current": current_upheld_string if current_upheld_string else "-", 
                                                     "previous": previous_upheld_string if previous_upheld_string else "-"}],

                        "Principle_5_EI_8": [{"Principle_5_EI_8": description_obj8.Descriptions_Human_Rights if description_obj8 else "-"}],
                
                        # "Principle_5_EI_9": [{"Principle_5_EI_9": description_obj9.Is_Verified if description_obj9 else "-"}],

                        "Principle_5_EI_9":  [{"Is_Verified": description_obj9_value_is_verified if description_obj9_value_is_verified else "-",
                                              "Descriptions_Human_Rights": description_obj9_value_descriptions if description_obj9_value_descriptions else "-"
                                              }],
                        "Principle_5_EI_10_CL": [{
                            "Principle_5_EI_10_CL": safe_to_decimal(record.Child_Labour) if record.Child_Labour is not None else "-" for record in Assessment
                            }]  if Assessment else [{"Principle_5_EI_10_CL":"-"}],
                        
                        
                        "Principle_5_EI_10_FL": [{
                            "Principle_5_EI_10_FL": safe_to_decimal(record.Forced_Involuntary_Labour) if record.Forced_Involuntary_Labour is not None else "-" for record in Assessment
                }] if Assessment else [{"Principle_5_EI_10_FL":"-"}],
                        
                        "Principle_5_EI_10_SH": [{
                            "Principle_5_EI_10_SH": safe_to_decimal(record.Sexual_Harasement) if record.Sexual_Harasement is not None else "-" for record in Assessment
                }] if Assessment else [{"Principle_5_EI_10_SH":"-"}],
                       
                       
                        "Principle_5_EI_10_DESCRIMINATION": [{
                            "Principle_5_EI_10_DESCRIMINATION": safe_to_decimal(record.Discrimination_at_workplace) if record.Discrimination_at_workplace is not None else "-" for record in Assessment
                }] if Assessment else [{"Principle_5_EI_10_DESCRIMINATION":"-"}],
                       
                        "Principle_5_EI_10_WAGES": [{
                            "Principle_5_EI_10_WAGES": safe_to_decimal(record.Wages) if record.Wages is not None else "-" for record in Assessment
                }] if Assessment else [{"Principle_5_EI_10_WAGES":"-"}],
                       
                       
                        "Principle_5_EI_10_OTHER": [{
                           "Principle_5_EI_10_OTHER": f"{record.Others} - {record.Percentage_for_Others} %" if record.Others else "-" for record in Assessment
                }] if Assessment else [{"Principle_5_EI_10_OTHER":"-"}],

                                    
            
                        "Principle_5_EI_11" : [{"Principle_5_EI_11": data_plant}],
                        
                        "Principle_5_LI_1" : [{"Principle_5_LI_1": description_objL1.Descriptions_Human_Rights if description_objL1 else "-"}],

                        "Principle_5_LI_2" : [{"Principle_5_LI_2": description_objL2.Descriptions_Human_Rights if description_objL2 else "-"}],

                        "Principle_5_LI_3" : [{"Is_Verified": description_objL3.Is_Verified if description_objL3 else "-",
                                              "Descriptions_Human_Rights": description_objL3.Descriptions_Human_Rights if description_objL3 else "-"}],
                        
                        "Principle_5_LI_4_CL": [{
                            "current_data": current_data_p5['Child_Labour'] if current_data_p5['Child_Labour'] != "-" else "-",
                            "previous_data": previous_data_p5['Child_Labour'] if previous_data_p5['Child_Labour'] != "-" else "-"
                }],

                        "Principle_5_LI_4_FL": [{
                            "current_data": current_data_p5['Forced_Involuntary_Labour'] if current_data_p5['Forced_Involuntary_Labour'] != "-" else "-",
                            "previous_data": previous_data_p5['Forced_Involuntary_Labour'] if previous_data_p5['Forced_Involuntary_Labour'] != "-" else "-"
                }],

                        "Principle_5_LI_4_SH": [{
                            "current_data": current_data_p5['Sexual_Harasement'] if current_data_p5['Sexual_Harasement'] != "-" else "-",
                            "previous_data": previous_data_p5['Sexual_Harasement'] if previous_data_p5['Sexual_Harasement'] != "-" else "-"
                }],

                        "Principle_5_LI_4_DESCRIMINATION": [{
                            "current_data": current_data_p5['Discrimination_at_workplace'] if current_data_p5['Discrimination_at_workplace'] != "-" else "-",
                            "previous_data": previous_data_p5['Discrimination_at_workplace'] if previous_data_p5['Discrimination_at_workplace'] != "-" else "-"
                }],

                        "Principle_5_LI_4_WAGES": [{
                            "current_data": current_data_p5['Wages'] if current_data_p5['Wages'] != "-" else "-",
                            "previous_data": previous_data_p5['Wages'] if previous_data_p5['Wages'] != "-" else "-"
                }],

                        "Principle_5_LI_4_OTHER": [
                            {
                                "current_data": (
                                    "Nil" if current_data_p5.get('Others') == 'Nil' and current_data_p5.get('Percentage_for_Others') == 'Nil'
                                    else f"{current_data_p5['Others']} - {current_data_p5['Percentage_for_Others']}" 
                                ),
                                "previous_data": (
                                    "Nil" if previous_data_p5.get('Others') == 'Nil' and previous_data_p5.get('Percentage_for_Others') == 'Nil'
                                    else f"{previous_data_p5['Others']} - {previous_data_p5['Percentage_for_Others']}" 
                                )
                            }
                        ],

                        "Principle_5_LI_4_NOS": [{
                            "current_data": current_data_p5['Number_of_Suppliers'] if current_data_p5['Number_of_Suppliers'] != "-" else "-",
                            "previous_data": previous_data_p5['Number_of_Suppliers'] if previous_data_p5['Number_of_Suppliers'] != "-" else "-"
            }],

                        "Principle_5_LI_5" : [{"Principle_5_LI_5": data_value}],


                }
            }
            
            Brs_log = {
                "Financial_Year":financial_year,
                "Section":"Principle 5",
                "User_Name":f"{request.user.firstname} {request.user.lastname}"
               
            }
                            
            brs_log_serializer = BRS_Report_LogSerializer(data=Brs_log)
            if brs_log_serializer.is_valid():
                brs_log_serializer.save()
            

            return Response(response_data, status = status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Data Not Available in Principle_5"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except APIException as e:
            return Response(
                {"error": f"APIException in Principle_5: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TypeError as e:
            return Response(
                {"error": f"TypeError in Principle_5: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Unknown error in Principle_5: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def safe_to_float(*values):
    def convert(value):
        if isinstance(value, Decimal):
            # Convert Python's Decimal to float
            return float(value)
        elif isinstance(value, (int, float)):
            # If it's already int or float, return it as is
            return float(value)
        return 0.0  # Default to 0.0 if None or invalid type

    return [convert(value) for value in values]


def safe_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return float(value or 0)


def safe_to_decimal(*values):
    result = []
    for value in values:
        try:
            result.append(
                Decimal(value) if value is not None and value != "" else Decimal("0.0")
            )
        except (InvalidOperation, ValueError):
            result.append(Decimal("0.0"))  # Return 0.0 if the value cannot be converted
    return result


class Principle_6_Report_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            if user_role == "Plant Operations" or user_role == "ESG Lead":

                financial_year = request.query_params.get("financial_year", None)

                if financial_year is None:
                    return Response(
                        {"error": "financial_year parameter is required"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Extract the start year from the financial year string (assumes format is 'FYYYYY-YYYY')
                start_year = int(financial_year[2:6])
                previous_financial_year = f"FY{start_year-1}-{start_year}"

                # EI_ABC
                current_year_records_electricity_consumption_solar = (
                    Electricity_Consumption_GJ.objects.filter(
                        Financial_Year=financial_year, Source="Solar"
                    )
                )
                previous_year_records_electricity_consumption_solar = (
                    Electricity_Consumption_GJ.objects.filter(
                        Financial_Year=previous_financial_year, Source="Solar"
                    )
                )
                current_year_records_electricity_consumption_hydroelectric = (
                    Electricity_Consumption_GJ.objects.filter(
                        Financial_Year=financial_year, Source="Hydel"
                    )
                )
                previous_year_records_electricity_consumption_hydroelectric = (
                    Electricity_Consumption_GJ.objects.filter(
                        Financial_Year=previous_financial_year, Source="Hydel"
                    )
                )
                current_year_records_electricity_consumption_wind = (
                    Electricity_Consumption_GJ.objects.filter(
                        Financial_Year=financial_year, Source="Wind"
                    )
                )
                previous_year_records_electricity_consumption_wind = (
                    Electricity_Consumption_GJ.objects.filter(
                        Financial_Year=previous_financial_year, Source="Wind"
                    )
                )

                # Sum the Total_Electricity_Consumption values for the current year
                current_total_electricity_consumption_solar = sum(
                    float(record.Total_Electricity_Consumption.to_decimal())
                    for record in current_year_records_electricity_consumption_solar
                )
                previous_total_electricity_consumption_solar = sum(
                    float(record.Total_Electricity_Consumption.to_decimal())
                    for record in previous_year_records_electricity_consumption_solar
                )
                current_total_electricity_consumption_hydroelectric = sum(
                    float(record.Total_Electricity_Consumption.to_decimal())
                    for record in current_year_records_electricity_consumption_hydroelectric
                )
                previous_total_electricity_consumption_hydroelectric = sum(
                    float(record.Total_Electricity_Consumption.to_decimal())
                    for record in previous_year_records_electricity_consumption_hydroelectric
                )
                current_total_electricity_consumption_wind = sum(
                    float(record.Total_Electricity_Consumption.to_decimal())
                    for record in current_year_records_electricity_consumption_wind
                )
                previous_total_electricity_consumption_wind = sum(
                    float(record.Total_Electricity_Consumption.to_decimal())
                    for record in previous_year_records_electricity_consumption_wind
                )

                # EI_DEF
                current_year_records_electricity_consumption_grid = (
                    Electricity_Consumption_GJ.objects.filter(
                        Financial_Year=financial_year, Source="Grid"
                    )
                )
                previous_year_records_electricity_consumption_grid = (
                    Electricity_Consumption_GJ.objects.filter(
                        Financial_Year=previous_financial_year, Source="Grid"
                    )
                )
                current_total_electricity_consumption_grid = sum(
                    float(record.Total_Electricity_Consumption.to_decimal())
                    for record in current_year_records_electricity_consumption_grid
                )
                previous_total_electricity_consumption_grid = sum(
                    float(record.Total_Electricity_Consumption.to_decimal())
                    for record in previous_year_records_electricity_consumption_grid
                )

                # EI1_E
                current_year_records_fuel_consumption = (
                    Fuel_Consumption_Onsite_Combustion_GJ.objects.filter(
                        Financial_Year=financial_year,
                    )
                )
                previous_year_records_fuel_consumption = (
                    Fuel_Consumption_Onsite_Combustion_GJ.objects.filter(
                        Financial_Year=previous_financial_year,
                    )
                )
                current_total_fuel_consumption = sum(
                    float(record.Total_Fuel_Consumption.to_decimal())
                    for record in current_year_records_fuel_consumption
                )
                previous_total_fuel_consumption = sum(
                    float(record.Total_Fuel_Consumption.to_decimal())
                    for record in previous_year_records_fuel_consumption
                )

                current_year_total = (
                    round(
                        current_total_electricity_consumption_solar
                        + current_total_electricity_consumption_hydroelectric
                        + current_total_electricity_consumption_wind,
                        2,
                    )
                    + round(current_total_electricity_consumption_grid, 2)
                    + round(current_total_fuel_consumption, 2)
                )
                previous_year_total = (
                    round(
                        previous_total_electricity_consumption_solar
                        + previous_total_electricity_consumption_hydroelectric
                        + previous_total_electricity_consumption_wind,
                        2,
                    )
                    + round(previous_total_electricity_consumption_grid, 2)
                    + round(previous_total_fuel_consumption, 2)
                )

                current_year_records_intensity = Turnover.objects.filter(
                    Financial_Year=financial_year
                )
                previous_year_records_intensity = Turnover.objects.filter(
                    Financial_Year=previous_financial_year
                )

                total_intensity_current = sum(
                    float(record.Total_Turnover.to_decimal())
                    for record in current_year_records_intensity
                )
                total_intensity_previous = sum(
                    float(record.Total_Turnover.to_decimal())
                    for record in previous_year_records_intensity
                )

                ei_g = (
                    ((current_year_total / total_intensity_current) * 22.4 / 10)
                    if total_intensity_current != 0
                    else 0
                )
                ei_g_ = (
                    ((previous_year_total / total_intensity_previous) * 22.4 / 10)
                    if total_intensity_previous != 0
                    else 0
                )

                EI1_Ans1 = []
                filtered_assessments = (
                    Energy_Assessment_by_External_Agency.objects.filter(
                        Financial_Year=financial_year
                    )
                )
                for assessment in filtered_assessments:
                    agency_name = assessment.Agency_Name
                    description = assessment.Description
                    EI1_Ans1.append("Agency Name : " + agency_name)
                    EI1_Ans1.append("Description : " + description)
                if not EI1_Ans1:
                    EI1_Ans1 = ["NA"]

                # EI1G
                current_year_records_energy_intensity = Energy_Intensity.objects.filter(
                    Financial_Year=financial_year
                )
                previous_year_records_energy_intensity = (
                    Energy_Intensity.objects.filter(
                        Financial_Year=previous_financial_year
                    )
                )

                current_total_energy_intensity = sum(
                    float(record.Total_Energy_Intensity.to_decimal())
                    for record in current_year_records_energy_intensity
                )
                previous_total_energy_intensity = sum(
                    float(record.Total_Energy_Intensity.to_decimal())
                    for record in previous_year_records_energy_intensity
                )

                # EI2_ANS
                # Sustainability - Project and Policy Details Q.1
                description_Q_1 = []
                try:
                    description_record_Q_1 = DescriptionsProjectandPolicies.objects.get(
                        Module_Name="Sites Facilities"
                    )
                    description_Q_1 = (
                        description_record_Q_1.Description
                        if description_record_Q_1
                        else ["NA"]
                    )
                except DescriptionsProjectandPolicies.DoesNotExist:
                    description_Q_1 = ["NA"]

                # 777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777777
                # EI3
                current_year_records_surface_water_withdrawal = (
                    Water_withdrawal_By_Source.objects.filter(
                        Financial_Year=financial_year, Source="Surface Water"
                    )
                )
                previous_year_records_surface_water_withdrawal = (
                    Water_withdrawal_By_Source.objects.filter(
                        Financial_Year=previous_financial_year, Source="Surface Water"
                    )
                )

                current_year_records_ground_water_withdrawal = (
                    Water_withdrawal_By_Source.objects.filter(
                        Financial_Year=financial_year, Source="Ground Water"
                    )
                )
                previous_year_records_ground_water_withdrawal = (
                    Water_withdrawal_By_Source.objects.filter(
                        Financial_Year=previous_financial_year, Source="Ground Water"
                    )
                )
                current_year_records_third_party_water_withdrawal = (
                    Water_withdrawal_By_Source.objects.filter(
                        Financial_Year=financial_year, Source="Third Party Water"
                    )
                )
                previous_year_records_third_party_water_withdrawal = (
                    Water_withdrawal_By_Source.objects.filter(
                        Financial_Year=previous_financial_year,
                        Source="Third Party Water",
                    )
                )
                current_year_records_seawater_withdrawal = (
                    Water_withdrawal_By_Source.objects.filter(
                        Financial_Year=financial_year, Source="Sea Water"
                    )
                )
                previous_year_records_seawater_withdrawal = (
                    Water_withdrawal_By_Source.objects.filter(
                        Financial_Year=previous_financial_year, Source="Sea Water"
                    )
                )
                current_year_records_other_withdrawal = (
                    Water_withdrawal_By_Source.objects.filter(
                        Financial_Year=financial_year, Source="Others"
                    )
                )
                previous_year_records_other_withdrawal = (
                    Water_withdrawal_By_Source.objects.filter(
                        Financial_Year=previous_financial_year, Source="Others"
                    )
                )

                current_total_surface_water_withdrawal = sum(
                    float(record.Total_Water_withdrawal.to_decimal())
                    for record in current_year_records_surface_water_withdrawal
                )
                previous_total_surface_water_withdrawal = sum(
                    float(record.Total_Water_withdrawal.to_decimal())
                    for record in previous_year_records_surface_water_withdrawal
                )

                current_total_ground_water_withdrawal = sum(
                    float(record.Total_Water_withdrawal.to_decimal())
                    for record in current_year_records_ground_water_withdrawal
                )
                previous_total_ground_water_withdrawal = sum(
                    float(record.Total_Water_withdrawal.to_decimal())
                    for record in previous_year_records_ground_water_withdrawal
                )

                current_total_third_party_water_withdrawal = sum(
                    float(record.Total_Water_withdrawal.to_decimal())
                    for record in current_year_records_third_party_water_withdrawal
                )
                previous_total_third_party_water_withdrawal = sum(
                    float(record.Total_Water_withdrawal.to_decimal())
                    for record in previous_year_records_third_party_water_withdrawal
                )

                current_total_seawater_withdrawal = sum(
                    float(record.Total_Water_withdrawal.to_decimal())
                    for record in current_year_records_seawater_withdrawal
                )
                previous_total_seawater_withdrawal = sum(
                    float(record.Total_Water_withdrawal.to_decimal())
                    for record in previous_year_records_seawater_withdrawal
                )

                current_total_other_withdrawal = sum(
                    float(record.Total_Water_withdrawal.to_decimal())
                    for record in current_year_records_other_withdrawal
                )
                previous_total_other_withdrawal = sum(
                    float(record.Total_Water_withdrawal.to_decimal())
                    for record in previous_year_records_other_withdrawal
                )

                current_year_records_water_consumption = (
                    Water_Consumption.objects.filter(Financial_Year=financial_year)
                )
                previous_year_records_water_consumption = (
                    Water_Consumption.objects.filter(
                        Financial_Year=previous_financial_year
                    )
                )

                current_total_water_consumption = sum(
                    float(record.Total_Consumption.to_decimal())
                    for record in current_year_records_water_consumption
                )
                previous_total_water_consumption = sum(
                    float(record.Total_Consumption.to_decimal())
                    for record in previous_year_records_water_consumption
                )

                current_year_records_water_intensity = Water_Intensity.objects.filter(
                    Financial_Year=financial_year
                )
                previous_year_records_water_intensity = Water_Intensity.objects.filter(
                    Financial_Year=previous_financial_year
                )

                current_total_water_intensity = sum(
                    float(record.Total_Water_Intensity.to_decimal())
                    for record in current_year_records_water_intensity
                )
                previous_total_water_intensity = sum(
                    float(record.Total_Water_Intensity.to_decimal())
                    for record in previous_year_records_water_intensity
                )

                EI3_Ans = []
                filtered_assessments = (
                    Water_Assessment_By_External_Agency.objects.filter(
                        Financial_Year=financial_year
                    )
                )
                for assessment in filtered_assessments:
                    agency_name = assessment.Agency_Name
                    description = assessment.Description
                    EI3_Ans.append("Agency Name : " + agency_name)
                    EI3_Ans.append("Description : " + description)
                if not EI3_Ans:
                    EI3_Ans = ["NA"]

                # EI4
                current_year_records_surface_water_without_discharge = (
                    Water_Discharge_To_Destination_Without_Treatment.objects.filter(
                        Financial_Year=financial_year, Destination="Surface Water"
                    )
                )
                previous_year_records_surface_water_without_discharge = (
                    Water_Discharge_To_Destination_Without_Treatment.objects.filter(
                        Financial_Year=previous_financial_year,
                        Destination="Surface Water",
                    )
                )
                current_total_surface_water_without_discharge = sum(
                    float(record.Total_Water_Discharge_Without_Treatment.to_decimal())
                    for record in current_year_records_surface_water_without_discharge
                )
                previous_total_surface_water_without_discharge = sum(
                    float(record.Total_Water_Discharge_Without_Treatment.to_decimal())
                    for record in previous_year_records_surface_water_without_discharge
                )

                current_year_records_ground_water_without_discharge = (
                    Water_Discharge_To_Destination_Without_Treatment.objects.filter(
                        Financial_Year=financial_year, Destination="Ground Water"
                    )
                )
                previous_year_records_ground_water_without_discharge = (
                    Water_Discharge_To_Destination_Without_Treatment.objects.filter(
                        Financial_Year=previous_financial_year,
                        Destination="Ground Water",
                    )
                )
                current_total_ground_water_without_discharge = sum(
                    float(record.Total_Water_Discharge_Without_Treatment.to_decimal())
                    for record in current_year_records_ground_water_without_discharge
                )
                previous_total_ground_water_without_discharge = sum(
                    float(record.Total_Water_Discharge_Without_Treatment.to_decimal())
                    for record in previous_year_records_ground_water_without_discharge
                )

                current_year_records_surface_water_with_discharge = (
                    Water_Discharge_To_Destination_With_Treatment.objects.filter(
                        Financial_Year=financial_year, Destination="Surface Water"
                    )
                )
                previous_year_records_surface_water_with_discharge = (
                    Water_Discharge_To_Destination_With_Treatment.objects.filter(
                        Financial_Year=previous_financial_year,
                        Destination="Surface Water",
                    )
                )
                current_year_records_ground_water_with_discharge = (
                    Water_Discharge_To_Destination_With_Treatment.objects.filter(
                        Financial_Year=financial_year, Destination="Ground Water"
                    )
                )
                previous_year_records_ground_water_with_discharge = (
                    Water_Discharge_To_Destination_With_Treatment.objects.filter(
                        Financial_Year=previous_financial_year,
                        Destination="Ground Water",
                    )
                )
                current_total_surface_water_with_discharge = sum(
                    float(record.Total_Water_Discharge_With_Treatment.to_decimal())
                    for record in current_year_records_surface_water_with_discharge
                )
                previous_total_surface_water_with_discharge = sum(
                    float(record.Total_Water_Discharge_With_Treatment.to_decimal())
                    for record in previous_year_records_surface_water_with_discharge
                )

                current_total_ground_water_with_discharge = sum(
                    float(record.Total_Water_Discharge_With_Treatment.to_decimal())
                    for record in current_year_records_ground_water_with_discharge
                )
                previous_total_ground_water_with_discharge = sum(
                    float(record.Total_Water_Discharge_With_Treatment.to_decimal())
                    for record in previous_year_records_ground_water_with_discharge
                )

                current_year_records_level_of_treatment = (
                    Water_Discharge_To_Destination_With_Treatment.objects.filter(
                        Financial_Year=financial_year, Destination="Level of Treatment"
                    )
                )
                previous_year_records_level_of_treatment = (
                    Water_Discharge_To_Destination_With_Treatment.objects.filter(
                        Financial_Year=previous_financial_year,
                        Destination="Level of Treatment",
                    )
                )
                current_Total_level_of_treatment = sum(
                    float(record.Total_Water_Discharge_With_Treatment.to_decimal())
                    for record in current_year_records_level_of_treatment
                )
                previous_Total_level_of_treatment = sum(
                    float(record.Total_Water_Discharge_With_Treatment.to_decimal())
                    for record in previous_year_records_level_of_treatment
                )

                current_year_records_third_party_water_without_discharge = (
                    Water_Discharge_To_Destination_Without_Treatment.objects.filter(
                        Financial_Year=financial_year, Destination="Third Party Water"
                    )
                )
                previous_year_records_third_party_water_without_discharge = (
                    Water_Discharge_To_Destination_Without_Treatment.objects.filter(
                        Financial_Year=previous_financial_year,
                        Destination="Third Party Water",
                    )
                )
                current_total_third_party_water_without_discharge = sum(
                    float(record.Total_Water_Discharge_Without_Treatment.to_decimal())
                    for record in current_year_records_third_party_water_without_discharge
                )
                previous_total_third_party_water_without_discharge = sum(
                    float(record.Total_Water_Discharge_Without_Treatment.to_decimal())
                    for record in previous_year_records_third_party_water_without_discharge
                )

                current_year_records_other_water_without_discharge = (
                    Water_Discharge_To_Destination_Without_Treatment.objects.filter(
                        Financial_Year=financial_year, Destination="Others"
                    )
                )
                previous_year_records_other_water_without_discharge = (
                    Water_Discharge_To_Destination_Without_Treatment.objects.filter(
                        Financial_Year=previous_financial_year, Destination="Others"
                    )
                )

                current_total_other_without_discharge = sum(
                    float(record.Total_Water_Discharge_Without_Treatment.to_decimal())
                    for record in current_year_records_other_water_without_discharge
                )
                previous_total_other_without_discharge = sum(
                    float(record.Total_Water_Discharge_Without_Treatment.to_decimal())
                    for record in previous_year_records_other_water_without_discharge
                )

                current_year_records_third_party_water_with_discharge = (
                    Water_Discharge_To_Destination_With_Treatment.objects.filter(
                        Financial_Year=financial_year, Destination="Third Party Water"
                    )
                )
                previous_year_records_third_party_water_with_discharge = (
                    Water_Discharge_To_Destination_With_Treatment.objects.filter(
                        Financial_Year=previous_financial_year,
                        Destination="Third Party Water",
                    )
                )
                current_total_third_party_water_with_discharge = sum(
                    float(record.Total_Water_Discharge_With_Treatment.to_decimal())
                    for record in current_year_records_third_party_water_with_discharge
                )
                previous_total_third_party_water_with_discharge = sum(
                    float(record.Total_Water_Discharge_With_Treatment.to_decimal())
                    for record in previous_year_records_third_party_water_with_discharge
                )

                current_year_records_seawater_with_discharge = (
                    Water_Discharge_To_Destination_With_Treatment.objects.filter(
                        Financial_Year=financial_year, Destination="Sea Water"
                    )
                )
                previous_year_records_seawater_with_discharge = (
                    Water_Discharge_To_Destination_With_Treatment.objects.filter(
                        Financial_Year=previous_financial_year, Destination="Sea Water"
                    )
                )
                current_year_records_other_water_with_discharge = (
                    Water_Discharge_To_Destination_With_Treatment.objects.filter(
                        Financial_Year=financial_year, Destination="Others"
                    )
                )
                previous_year_records_other_water_with_discharge = (
                    Water_Discharge_To_Destination_With_Treatment.objects.filter(
                        Financial_Year=previous_financial_year, Destination="Others"
                    )
                )

                current_total_seawater_with_discharge = sum(
                    float(record.Total_Water_Discharge_With_Treatment.to_decimal())
                    for record in current_year_records_seawater_with_discharge
                )
                previous_total_seawater_with_discharge = sum(
                    float(record.Total_Water_Discharge_With_Treatment.to_decimal())
                    for record in previous_year_records_seawater_with_discharge
                )

                current_total_other_with_discharge = sum(
                    float(record.Total_Water_Discharge_With_Treatment.to_decimal())
                    for record in current_year_records_other_water_with_discharge
                )
                previous_total_other_with_discharge = sum(
                    float(record.Total_Water_Discharge_With_Treatment.to_decimal())
                    for record in previous_year_records_other_water_with_discharge
                )

                current_year_records_seawater_without_discharge = (
                    Water_Discharge_To_Destination_Without_Treatment.objects.filter(
                        Financial_Year=financial_year, Destination="Sea Water"
                    )
                )
                previous_year_records_seawater_without_discharge = (
                    Water_Discharge_To_Destination_Without_Treatment.objects.filter(
                        Financial_Year=previous_financial_year, Destination="Sea Water"
                    )
                )
                current_total_seawater_without_discharge = sum(
                    float(record.Total_Water_Discharge_Without_Treatment.to_decimal())
                    for record in current_year_records_seawater_without_discharge
                )
                previous_total_seawater_without_discharge = sum(
                    float(record.Total_Water_Discharge_Without_Treatment.to_decimal())
                    for record in previous_year_records_seawater_without_discharge
                )

                Total_current_F = round(
                    (
                        current_total_surface_water_without_discharge
                        + current_total_ground_water_without_discharge
                        + current_total_surface_water_with_discharge
                        + current_total_ground_water_with_discharge
                        + current_Total_level_of_treatment
                        + current_total_third_party_water_without_discharge
                        + current_total_other_without_discharge
                        + current_total_third_party_water_with_discharge
                        + current_total_seawater_with_discharge
                        + current_total_other_with_discharge
                        + current_total_seawater_without_discharge
                    ),
                    2,
                )

                Total_pervious_F = round(
                    (
                        previous_total_surface_water_without_discharge
                        + previous_total_ground_water_without_discharge
                        + previous_total_surface_water_with_discharge
                        + previous_total_ground_water_with_discharge
                        + previous_Total_level_of_treatment
                        + previous_total_third_party_water_without_discharge
                        + previous_total_other_without_discharge
                        + previous_total_third_party_water_with_discharge
                        + previous_total_seawater_with_discharge
                        + previous_total_other_with_discharge
                        + previous_total_seawater_without_discharge
                    ),
                    2,
                )

                EI4_Ans = []
                filtered_assessments = (
                    Water_Assessment_By_External_Agency.objects.filter(
                        Financial_Year=financial_year
                    )
                )
                for assessment in filtered_assessments:
                    agency_name = assessment.Agency_Name
                    description = assessment.Description
                    EI4_Ans.append("Agency Name : " + agency_name)
                    EI4_Ans.append("Description : " + description)
                if not EI4_Ans:
                    EI4_Ans = ["NA"]

                # EI5
                # Sustainability - Project and Policy Details Q.3
                description_zero_liquid_discharge = []
                try:
                    description_record_Zero_liquid_Discharge = (
                        DescriptionsProjectandPolicies.objects.get(
                            Module_Name="Zero liquid Discharge"
                        )
                    )
                    description_zero_liquid_discharge = (
                        description_record_Zero_liquid_Discharge.Description
                    )
                except DescriptionsProjectandPolicies.DoesNotExist:
                    description_zero_liquid_discharge = ["NA"]

                ei6_totals = calculate_air_emissions_totals(
                    financial_year, previous_financial_year
                )

                # EI7
                # Emissions Scope1
                # current_year_records_scope1_emissions = Scope1_Emissions_by_Facilities.objects.filter(Financial_Year=financial_year)
                # previous_year_records_scope1_emissions = Scope1_Emissions_by_Facilities.objects.filter(Financial_Year=previous_financial_year)

                # current_total_scope1_emissions = sum(float(record.Total_Emission.to_decimal()) for record in current_year_records_scope1_emissions) /1000
                # previous_total_scope1_emissions = sum(float(record.Total_Emission.to_decimal()) for record in previous_year_records_scope1_emissions) /1000

                current_year_records_scope1_emissions = (
                    Scope1_Emissions_by_GHG_Type.objects.filter(
                        Financial_Year=financial_year, GHG_Type="CO2E"
                    )
                )
                previous_year_records_scope1_emissions = (
                    Scope1_Emissions_by_GHG_Type.objects.filter(
                        Financial_Year=previous_financial_year, GHG_Type="CO2E"
                    )
                )

                current_total_scope1_emissions = (
                    sum(
                        float(record.Total_Emission.to_decimal())
                        for record in current_year_records_scope1_emissions
                    )
                    / 1000
                )
                previous_total_scope1_emissions = (
                    sum(
                        float(record.Total_Emission.to_decimal())
                        for record in previous_year_records_scope1_emissions
                    )
                    / 1000
                )

                # Emissions Scope2
                current_year_records_scope2_emissions = (
                    Scope2_Emissions_by_Facilities.objects.filter(
                        Financial_Year=financial_year
                    )
                )
                previous_year_records_scope2_emissions = (
                    Scope2_Emissions_by_Facilities.objects.filter(
                        Financial_Year=previous_financial_year
                    )
                )

                current_total_scope2_emissions = sum(
                    float(record.Total_Emission.to_decimal())
                    for record in current_year_records_scope2_emissions
                )
                previous_total_scope2_emissions = sum(
                    float(record.Total_Emission.to_decimal())
                    for record in previous_year_records_scope2_emissions
                )

                EI7_Ans = []
                filtered_assessments = (
                    Emission_Assessment_By_External_Agency.objects.filter(
                        Financial_Year=financial_year
                    )
                )
                for assessment in filtered_assessments:
                    agency_name = assessment.Agency
                    description = assessment.Description
                    EI7_Ans.append("Agency Name : " + agency_name)
                    EI7_Ans.append("Description : " + description)
                if not EI7_Ans:
                    EI7_Ans = ["NA"]

                # EI8
                # Sustainability - Project and Policy Details Q.5
                description_green_house = []
                try:
                    description_record_green_house = (
                        DescriptionsProjectandPolicies.objects.get(
                            Module_Name="Green House"
                        )
                    )
                    description_green_house = description_record_green_house.Description
                except DescriptionsProjectandPolicies.DoesNotExist:
                    description_green_house = ["NA"]

                # EI9
                # Waste - Waste_Generated
                # Plastic
                current_year_records_plastic_waste = Waste_Generated.objects.filter(
                    Financial_Year=financial_year, Type="Plastic"
                )
                previous_year_records_plastic_waste = Waste_Generated.objects.filter(
                    Financial_Year=previous_financial_year, Type="Plastic"
                )
                current_total_plastic_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in current_year_records_plastic_waste
                )
                previous_total_plastic_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in previous_year_records_plastic_waste
                )
                # E-Waste
                current_year_records_e_waste = Waste_Generated.objects.filter(
                    Financial_Year=financial_year, Type="E-Waste"
                )
                previous_year_records_e_waste = Waste_Generated.objects.filter(
                    Financial_Year=previous_financial_year, Type="E-Waste"
                )
                current_total_e_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in current_year_records_e_waste
                )
                previous_total_e_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in previous_year_records_e_waste
                )
                # Bio-Medical
                current_year_records_bio_medical_waste = Waste_Generated.objects.filter(
                    Financial_Year=financial_year, Type="Bio-Medical"
                )
                previous_year_records_bio_medical_waste = (
                    Waste_Generated.objects.filter(
                        Financial_Year=previous_financial_year, Type="Bio-Medical"
                    )
                )
                current_total_bio_medical_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in current_year_records_bio_medical_waste
                )
                previous_total_bio_medical_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in previous_year_records_bio_medical_waste
                )
                # Construction and Demolition
                current_year_records_construction_waste = (
                    Waste_Generated.objects.filter(
                        Financial_Year=financial_year,
                        Type="Construction and Demolition",
                    )
                )
                previous_year_records_construction_waste = (
                    Waste_Generated.objects.filter(
                        Financial_Year=previous_financial_year,
                        Type="Construction and Demolition",
                    )
                )
                current_total_construction_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in current_year_records_construction_waste
                )
                previous_total_construction_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in previous_year_records_construction_waste
                )
                # Battery
                current_year_records_battery_waste = Waste_Generated.objects.filter(
                    Financial_Year=financial_year, Type="Battery"
                )
                previous_year_records_battery_waste = Waste_Generated.objects.filter(
                    Financial_Year=previous_financial_year, Type="Battery"
                )
                current_total_battery_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in current_year_records_battery_waste
                )
                previous_total_battery_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in previous_year_records_battery_waste
                )
                # Radioactive
                current_year_records_radioactive_waste = Waste_Generated.objects.filter(
                    Financial_Year=financial_year, Type="Radioactive"
                )
                previous_year_records_radioactive_waste = (
                    Waste_Generated.objects.filter(
                        Financial_Year=previous_financial_year, Type="Radioactive"
                    )
                )
                current_total_radioactive_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in current_year_records_radioactive_waste
                )
                previous_total_radioactive_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in previous_year_records_radioactive_waste
                )
                # Other Hazardous
                current_year_records_other_hazardous_waste = (
                    Waste_Generated.objects.filter(
                        Financial_Year=financial_year, Type="Other Hazardous"
                    )
                )
                previous_year_records_other_hazardous_waste = (
                    Waste_Generated.objects.filter(
                        Financial_Year=previous_financial_year, Type="Other Hazardous"
                    )
                )
                current_total_other_hazardous_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in current_year_records_other_hazardous_waste
                )
                previous_total_other_hazardous_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in previous_year_records_other_hazardous_waste
                )
                # Other Non-Hazardous
                current_year_records_other_non_hazardous_waste = (
                    Waste_Generated.objects.filter(
                        Financial_Year=financial_year, Type="Other Non-Hazardous"
                    )
                )
                previous_year_records_other_non_hazardous_waste = (
                    Waste_Generated.objects.filter(
                        Financial_Year=previous_financial_year,
                        Type="Other Non-Hazardous",
                    )
                )
                current_total_other_non_hazardous_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in current_year_records_other_non_hazardous_waste
                )
                previous_total_other_non_hazardous_waste = sum(
                    float(record.Waste_Generated_Total.to_decimal())
                    for record in previous_year_records_other_non_hazardous_waste
                )
                # Watse - Waste_Recovered
                # Recycled
                current_year_records_recycled = Waste_Recovered.objects.filter(
                    Financial_Year=financial_year, Waste_Recovered_Category="Recycled"
                )
                previous_year_records_recycled = Waste_Recovered.objects.filter(
                    Financial_Year=previous_financial_year,
                    Waste_Recovered_Category="Recycled",
                )
                current_total_recycled = sum(
                    float(record.Waste_Recovered_Total.to_decimal())
                    for record in current_year_records_recycled
                )
                previous_total_recycled = sum(
                    float(record.Waste_Recovered_Total.to_decimal())
                    for record in previous_year_records_recycled
                )
                # Re-Used
                current_year_records_reused = Waste_Recovered.objects.filter(
                    Financial_Year=financial_year, Waste_Recovered_Category="Re-Used"
                )
                previous_year_records_reused = Waste_Recovered.objects.filter(
                    Financial_Year=previous_financial_year,
                    Waste_Recovered_Category="Re-Used",
                )
                current_total_reused = sum(
                    float(record.Waste_Recovered_Total.to_decimal())
                    for record in current_year_records_reused
                )
                previous_total_reused = sum(
                    float(record.Waste_Recovered_Total.to_decimal())
                    for record in previous_year_records_reused
                )
                # Other-Recovery Operations
                current_year_records_other_recovery = Waste_Recovered.objects.filter(
                    Financial_Year=financial_year,
                    Waste_Recovered_Category="Other-Recovery Operations",
                )
                previous_year_records_other_recovery = Waste_Recovered.objects.filter(
                    Financial_Year=previous_financial_year,
                    Waste_Recovered_Category="Other-Recovery Operations",
                )
                current_total_other_recovery = sum(
                    float(record.Waste_Recovered_Total.to_decimal())
                    for record in current_year_records_other_recovery
                )
                previous_total_other_recovery = sum(
                    float(record.Waste_Recovered_Total.to_decimal())
                    for record in previous_year_records_other_recovery
                )
                # Calculate the sums for all Waste_Recovered categories
                total_current_recovered = (
                    current_total_recycled
                    + current_total_reused
                    + current_total_other_recovery
                )
                total_previous_recovered = (
                    previous_total_recycled
                    + previous_total_reused
                    + previous_total_other_recovery
                )
                # Waste - Waste_Disposed
                # Incineration
                current_year_records_incineration = Waste_Disposed.objects.filter(
                    Financial_Year=financial_year,
                    Waste_Disposed_Category="Incineration",
                )
                previous_year_records_incineration = Waste_Disposed.objects.filter(
                    Financial_Year=previous_financial_year,
                    Waste_Disposed_Category="Incineration",
                )
                current_total_incineration = sum(
                    float(record.Waste_Disposed_Total.to_decimal())
                    for record in current_year_records_incineration
                )
                previous_total_incineration = sum(
                    float(record.Waste_Disposed_Total.to_decimal())
                    for record in previous_year_records_incineration
                )
                # Landfilling
                current_year_records_landfilling = Waste_Disposed.objects.filter(
                    Financial_Year=financial_year, Waste_Disposed_Category="Landfilling"
                )
                previous_year_records_landfilling = Waste_Disposed.objects.filter(
                    Financial_Year=previous_financial_year,
                    Waste_Disposed_Category="Landfilling",
                )
                current_total_landfilling = sum(
                    float(record.Waste_Disposed_Total.to_decimal())
                    for record in current_year_records_landfilling
                )
                previous_total_landfilling = sum(
                    float(record.Waste_Disposed_Total.to_decimal())
                    for record in previous_year_records_landfilling
                )
                # Other Disposal Operations
                current_year_records_other_disposal = Waste_Disposed.objects.filter(
                    Financial_Year=financial_year,
                    Waste_Disposed_Category="Other Disposal Operations",
                )
                previous_year_records_other_disposal = Waste_Disposed.objects.filter(
                    Financial_Year=previous_financial_year,
                    Waste_Disposed_Category="Other Disposal Operations",
                )
                current_total_other_disposal = sum(
                    float(record.Waste_Disposed_Total.to_decimal())
                    for record in current_year_records_other_disposal
                )
                previous_total_other_disposal = sum(
                    float(record.Waste_Disposed_Total.to_decimal())
                    for record in previous_year_records_other_disposal
                )

                # Calculate the sums for all Waste_Disposed categories
                total_current_disposed = (
                    current_total_incineration
                    + current_total_landfilling
                    + current_total_other_disposal
                )
                total_previous_disposed = (
                    previous_total_incineration
                    + previous_total_landfilling
                    + previous_total_other_disposal
                )

                current_sum_abcdefgh = (
                    current_total_plastic_waste
                    + current_total_e_waste
                    + current_total_bio_medical_waste
                    + current_total_construction_waste
                    + current_total_battery_waste
                    + current_total_radioactive_waste
                    + current_total_other_hazardous_waste
                    + current_total_other_non_hazardous_waste
                )
                previous_sum_abcdefgh = (
                    previous_total_plastic_waste
                    + previous_total_e_waste
                    + previous_total_bio_medical_waste
                    + previous_total_construction_waste
                    + previous_total_battery_waste
                    + previous_total_radioactive_waste
                    + previous_total_other_hazardous_waste
                    + previous_total_other_non_hazardous_waste
                )
                # WASTE_INTENSITY
                current_year_records_waste_intensity = Waste_Intensity.objects.filter(
                    Financial_Year=financial_year,
                )
                previous_year_records_waste_intensity = Waste_Intensity.objects.filter(
                    Financial_Year=previous_financial_year,
                )
                current_total_Waste_Intensity = sum(
                    float(record.Total_Waste_Intensity.to_decimal())
                    for record in current_year_records_waste_intensity
                )
                previous_total_Waste_Intensity = sum(
                    float(record.Total_Waste_Intensity.to_decimal())
                    for record in previous_year_records_waste_intensity
                )

                EI9_Ans = []
                filtered_assessments = (
                    Waste_Assessment_By_External_Agency.objects.filter(
                        Financial_Year=financial_year
                    )
                )
                for assessment in filtered_assessments:
                    agency_name = assessment.Agency_Name
                    description = assessment.Description
                    EI9_Ans.append("Agency Name : " + agency_name)
                    EI9_Ans.append("Description : " + description)
                if not EI9_Ans:
                    EI9_Ans = ["NA"]

                # EI10
                # Sustainability - Project and Policy Details Q.2
                description_waste_management = []
                try:
                    description_record_waste_management = (
                        DescriptionsProjectandPolicies.objects.get(
                            Module_Name="Waste Management"
                        )
                    )
                    description_waste_management = (
                        description_record_waste_management.Description
                    )
                except ObjectDoesNotExist:
                    description_waste_management = ["NA"]

                # Q.11
                # import pdb;pdb.set_trace()
                all_records = Operations_In_Ecologically_Sensitive_Areas.objects.all()
                print(list(all_records.values()),"-----------------------")

                if not all_records:  # Check if the queryset is empty
                    # If no records exist in the database, return all keys with "-"
                    records_list_Q_11 = [
                        {
                            "Facility": "-",
                            "Operation": "-",
                            "Clearance": "-",
                            "Reason": "-",
                        }
                    ]
                else:
                    records_list_Q_11 = []
                    for record in all_records :
                        if record.Reason and not any(
                            [
                                record.Facility,
                                record.Operation,
                                record.Clearance,
                            ]
                        ):
                            # Only Reason has a value
                            formatted_record = {
                                "Facility": "-",
                                "Operation": "-",
                                "Clearance": "-",
                                "Reason": record.Reason,
                            }
                        else:
                            # Some keys have values, others do not
                            formatted_record = {
                                "Facility": record.Facility or "-",
                                "Operation": record.Operation or "-",
                                "Clearance": record.Clearance or "-",
                                "Reason": record.Reason or "-",
                            }
                        records_list_Q_11.append(formatted_record)

                # Q.12
                try:
                    all_records_q12 = (
                        Environmental_Impact_Assessments_Of_Projects_Undertaken.objects.all()
                    )

                    if not all_records_q12:  # Check if the queryset is empty
                        # Return default values if no records exist
                        records_list_Q_12 = [
                            {
                                "Name_of_project": "-",
                                "Project_details": "-",
                                "Eia_notification_no": "-",
                                "Date": "-",
                                "Conducted_by_external_agency": "-",
                                "In_public_domain": "-",
                                "Results": "-",
                            }
                        ]
                    else:
                        records_list_Q_12 = []
                        for record in all_records_q12:
                            # Format each record with field values or default values
                            formatted_record = {
                                "Name_of_project": record.Name_of_project or "-",
                                "Project_details": record.Project_details or "-",
                                "Eia_notification_no": record.Eia_notification_no
                                or "-",
                                "Date": (
                                    record.Date.strftime("%Y-%m-%d")
                                    if record.Date
                                    else "-"
                                ),
                                "Conducted_by_external_agency": record.Conducted_by_external_agency
                                or "-",
                                "In_public_domain": record.In_public_domain or "-",
                                "Results": record.Results or "-",
                            }
                            records_list_Q_12.append(formatted_record)
                except ObjectDoesNotExist:
                    # Fallback in case of database access error
                    records_list_Q_12 = [
                        {
                            "Name_of_project": "-",
                            "Project_details": "-",
                            "Eia_notification_no": "-",
                            "Date": "-",
                            "Conducted_by_external_agency": "-",
                            "In_public_domain": "-",
                            "Results": "-",
                        }
                    ]

                try:
                    all_records_q13 = (
                        Non_Compliance_With_The_Applicable_Environmental_Law.objects.all()
                    )

                    if not all_records_q13:  # Check if the queryset is empty
                        # If no records exist, return a dictionary with "-" for all fields
                        records_list_Q_13 = [
                            {
                                "The_law_regulations_guidlines_which_was_not_complied_with": "-",
                                "Details_of_non_compliance": "-",
                                "Any_fine_penalties_action": "-",
                                "Corrective_action_taken_if_any": "-",
                            }
                        ]
                    else:
                        records_list_Q_13 = []
                        for record in all_records_q13:
                            # Apply the logic: If any field is empty, set it to "-"
                            formatted_record = {
                                "The_law_regulations_guidlines_which_was_not_complied_with": record.The_law_regulations_guidlines_which_was_not_complied_with
                                or "-",
                                "Details_of_non_compliance": record.Details_of_non_compliance
                                or "-",
                                "Any_fine_penalties_action": record.Any_fine_penalties_action
                                or "-",
                                "Corrective_action_taken_if_any": record.Corrective_action_taken_if_any
                                or "-",
                            }
                            records_list_Q_13.append(formatted_record)
                except ObjectDoesNotExist:
                    # In case of an exception (e.g., database issue), return the default value
                    records_list_Q_13 = [
                        {
                            "The_law_regulations_guidlines_which_was_not_complied_with": "-",
                            "Details_of_non_compliance": "-",
                            "Any_fine_penalties_action": "-",
                            "Corrective_action_taken_if_any": "-",
                        }
                    ]

                try:
                    water_queryset = Water_Stress_Areas.objects.all()
                    records_list_Q1_1_2 = list(water_queryset.values())
                except ObjectDoesNotExist:
                    records_list_Q1_1_2 = "-"

                # Q.1
                # Define sources
                sources = [
                    "Surface Water",
                    "Ground Water",
                    "Third Party Water",
                    "Sea Water",
                    "Others",
                ]
                # Initialize dictionaries to store aggregated data
                current_year_data = {source: 0.0 for source in sources}
                previous_year_data = {source: 0.0 for source in sources}
                current_total_consumption = 0.0
                previous_total_consumption = 0.0
                current_total_intensity = 0.0
                previous_total_intensity = 0.0
                # Retrieve all facilities in the water stress area
                try:
                    facilities = Water_Stress_Areas.objects.values_list(
                        "Facility", flat=True
                    )
                    if not facilities:
                        facilities = []
                except ObjectDoesNotExist:
                    facilities = []

                # Iterate over each facility
                for facility in facilities:
                    # Query Water_withdrawal_By_Source for the current financial year across this facility
                    current_year_records = Water_withdrawal_By_Source.objects.filter(
                        Facility=facility,
                        Source__in=sources,
                        Financial_Year=financial_year,
                    )
                    # print(f"Query for current year records for {facility}: Source__in={sources}, Financial_Year={financial_year}")
                    # print(f"Current year records for {facility}: {list(current_year_records)}")
                    # Calculate the total for current financial year for this facility
                    for record in current_year_records:
                        if record.Total_Water_withdrawal is not None:
                            current_year_data[record.Source] += float(
                                str(record.Total_Water_withdrawal or 0)
                            )
                    # Query Water_withdrawal_By_Source for the previous financial year across this facility
                    previous_year_records = Water_withdrawal_By_Source.objects.filter(
                        Facility=facility,
                        Source__in=sources,
                        Financial_Year=previous_financial_year,
                    )
                    # print(f"Query for previous year records for {facility}: Source__in={sources}, Financial_Year={previous_financial_year}")
                    # print(f"Previous year records for {facility}: {list(previous_year_records)}")
                    # Calculate the total for previous financial year for this facility
                    for record in previous_year_records:
                        if record.Total_Water_withdrawal is not None:
                            previous_year_data[record.Source] += float(
                                str(record.Total_Water_withdrawal or 0)
                            )
                    # Get Total_Consumption from Water_Consumption model for this facility
                    current_consumption_records = Water_Consumption.objects.filter(
                        Facility=facility, Financial_Year=financial_year
                    )
                    previous_consumption_records = Water_Consumption.objects.filter(
                        Facility=facility, Financial_Year=previous_financial_year
                    )
                    # print(f"Query for current consumption records for {facility}: Financial_Year={financial_year}")
                    # print(f"Current consumption records for {facility}: {list(current_consumption_records)}")
                    # Calculate total consumption for current and previous years for this facility
                    for record in current_consumption_records:
                        if record.Total_Consumption is not None:
                            current_total_consumption += float(
                                str(record.Total_Consumption or 0)
                            )
                    # print(f"Query for previous consumption records for {facility}: Financial_Year={previous_financial_year}")
                    # print(f"Previous consumption records for {facility}: {list(previous_consumption_records)}")
                    for record in previous_consumption_records:
                        if record.Total_Consumption is not None:
                            previous_total_consumption += float(
                                str(record.Total_Consumption or 0)
                            )
                    current_intensity_records = Water_Intensity.objects.filter(
                        Facility__in=facilities, Financial_Year=financial_year
                    )
                    # Calculate total intensity for current financial year
                    for record in current_intensity_records:
                        if record.Total_Water_Intensity is not None:
                            current_total_intensity += float(
                                str(record.Total_Water_Intensity or 0)
                            )
                    # Query Water_Intensity for the previous financial year across all facilities
                    previous_intensity_records = Water_Intensity.objects.filter(
                        Facility__in=facilities, Financial_Year=previous_financial_year
                    )
                    # Calculate total intensity for previous financial year
                    for record in previous_intensity_records:
                        if record.Total_Water_Intensity is not None:
                            previous_total_intensity += float(
                                str(record.Total_Water_Intensity or 0)
                            )

                # Define destinations
                destinations = [
                    "Surface Water",
                    "Ground Water",
                    "Third Party Water",
                    "Sea Water",
                    "Others",
                ]
                # Initialize dictionaries to store aggregated data
                current_year_discharge_with_treatment = {
                    destination: 0.0 for destination in destinations
                }
                previous_year_discharge_with_treatment = {
                    destination: 0.0 for destination in destinations
                }
                current_year_discharge_without_treatment = {
                    destination: 0.0 for destination in destinations
                }
                previous_year_discharge_without_treatment = {
                    destination: 0.0 for destination in destinations
                }
                # Retrieve all facilities in the water stress area
                try:
                    facilities = Water_Stress_Areas.objects.values_list(
                        "Facility", flat=True
                    )
                    if not facilities:
                        facilities = []
                except ObjectDoesNotExist:
                    facilities = []

                # Iterate over each facility
                for facility in facilities:
                    # Query and aggregate data for Water_Discharge_To_Destination_With_Treatment
                    for model, year, dest_dict in [
                        (
                            Water_Discharge_To_Destination_With_Treatment,
                            financial_year,
                            current_year_discharge_with_treatment,
                        ),
                        (
                            Water_Discharge_To_Destination_With_Treatment,
                            previous_financial_year,
                            previous_year_discharge_with_treatment,
                        ),
                        (
                            Water_Discharge_To_Destination_Without_Treatment,
                            financial_year,
                            current_year_discharge_without_treatment,
                        ),
                        (
                            Water_Discharge_To_Destination_Without_Treatment,
                            previous_financial_year,
                            previous_year_discharge_without_treatment,
                        ),
                    ]:
                        records = model.objects.filter(
                            Facility=facility,
                            Destination__in=destinations,
                            Financial_Year=year,
                        )
                        for record in records:
                            if (
                                model == Water_Discharge_To_Destination_With_Treatment
                                and record.Total_Water_Discharge_With_Treatment
                                is not None
                            ):
                                dest_dict[record.Destination] += float(
                                    str(
                                        record.Total_Water_Discharge_With_Treatment or 0
                                    )
                                )
                            elif (
                                model
                                == Water_Discharge_To_Destination_Without_Treatment
                                and record.Total_Water_Discharge_Without_Treatment
                                is not None
                            ):
                                dest_dict[record.Destination] += float(
                                    str(
                                        record.Total_Water_Discharge_Without_Treatment
                                        or 0
                                    )
                                )

                current_year_total_discharge = sum(
                    current_year_discharge_with_treatment.values()
                ) + sum(current_year_discharge_without_treatment.values())
                previous_year_total_discharge = sum(
                    previous_year_discharge_with_treatment.values()
                ) + sum(previous_year_discharge_without_treatment.values())

                LI1_Ans = []
                filtered_assessments = (
                    Water_Assessment_By_External_Agency.objects.filter(
                        Financial_Year=financial_year
                    )
                )
                for assessment in filtered_assessments:
                    agency_name = assessment.Agency_Name
                    description = assessment.Description
                    LI1_Ans.append("Agency Name : " + agency_name)
                    LI1_Ans.append("Description : " + description)
                if not LI1_Ans:
                    LI1_Ans = ["NA"]

                current_year_records_scope3_emission_by_facilities = (
                    Scope3_Emissions_by_Facilities.objects.filter(
                        Financial_Year=financial_year
                    )
                )
                previous_year_records_scope3_emission_by_facilities = (
                    Scope3_Emissions_by_Facilities.objects.filter(
                        Financial_Year=financial_year
                    )
                )

                current_year_records_scope3_intensity = Scope3_Intensity.objects.filter(
                    Financial_Year=financial_year
                )
                previous_year_records_scope3_intensity = (
                    Scope3_Intensity.objects.filter(Financial_Year=financial_year)
                )

                current_total_scope3_emission_by_facilities = (
                    sum(
                        float(record.Total_Emission.to_decimal())
                        for record in current_year_records_scope3_emission_by_facilities
                    )
                    / 1000
                )
                previous_total_scope3_emission_by_facilities = (
                    sum(
                        float(record.Total_Emission.to_decimal())
                        for record in previous_year_records_scope3_emission_by_facilities
                    )
                    / 1000
                )

                current_total_scope3_intensity = sum(
                    float(record.Total_Intensity.to_decimal())
                    for record in current_year_records_scope3_intensity
                )
                previous_total_scope3_intensity = sum(
                    float(record.Total_Intensity.to_decimal())
                    for record in previous_year_records_scope3_intensity
                )

                LI2_Ans2 = []
                filtered_assessments = (
                    Emission_Assessment_By_External_Agency.objects.filter(
                        Financial_Year=financial_year
                    )
                )
                for assessment in filtered_assessments:
                    agency_name = assessment.Agency
                    description = assessment.Description
                    LI2_Ans2.append("Agency Name : " + agency_name)
                    LI2_Ans2.append("Description : " + description)
                if not LI2_Ans2:
                    LI2_Ans2 = ["NA"]

                # Sustainability - Project and Policy Details Q.1
                try:
                    description_record_Q_3_ = (
                        DescriptionsProjectandPolicies.objects.get(
                            Module_Name="Significant Impact"
                        )
                    )
                    description_Q_3 = description_record_Q_3_.Description
                except DescriptionsProjectandPolicies.DoesNotExist:
                    description_record_Q_3_ = ["NA"]
                    description_Q_3 = "NA"

                # Q.4
                # description_record_Q_4_ = Initiatives_Towards_Carbon_Zero.objects.all()
                # description_Q_4 = list(description_record_Q_4_.values("Initiative_undertaken","Details_of_the_initiative","Outcome_of_the_initiative","Web_link"))
                
                try:
   
                    description_record_Q_4_ = Initiatives_Towards_Carbon_Zero.objects.all()
                    
                    if not description_record_Q_4_:  # Check if the queryset is empty
                        # Return default values if no records exist
                        description_Q_4 = [
                            {
                                "Initiative_undertaken": "-",
                                "Details_of_the_initiative": "-",
                                "Outcome_of_the_initiative": "-",
                                "Web_link": "-",
                            }
                        ]
                    else:
                        description_Q_4 = []
                        for record in description_record_Q_4_:
                            # Format each record with field values or default values
                            formatted_record = {
                                "Initiative_undertaken": record.Initiative_undertaken or "-",
                                "Details_of_the_initiative": record.Details_of_the_initiative or "-",
                                "Outcome_of_the_initiative": record.Outcome_of_the_initiative or "-",
                                "Web_link": record.Web_link or "-",
                            }
                            description_Q_4.append(formatted_record)

                except ObjectDoesNotExist:
                    # Fallback in case of database access error
                    description_Q_4 = [
                        {
                            "Initiative_undertaken": "-",
                            "Details_of_the_initiative": "-",
                            "Outcome_of_the_initiative": "-",
                            "Web_link": "-",
                        }
                    ]

                # Sustainability - Project and Policy Details Q.7
                description_Q_5 = "-"
                try:
                    description_record_Q_5 = DescriptionsProjectandPolicies.objects.get(
                        Module_Name="Continuity Disaster Management"
                    )
                    description_Q_5 = description_record_Q_5.Description
                except DescriptionsProjectandPolicies.DoesNotExist:
                    pass

                # Sustainability - Project and Policy Details Q.8

                description_Q_6 = "-"
                try:
                    description_record_Q_6 = DescriptionsProjectandPolicies.objects.get(
                        Module_Name="Adverse Impact"
                    )
                    description_Q_6 = description_record_Q_6.Description
                except DescriptionsProjectandPolicies.DoesNotExist:
                    pass

                description_Q_7 = "-"
                try:
                    description_record_Q_7 = DescriptionsProjectandPolicies.objects.get(
                        Module_Name="Value Chain"
                    )
                    description_Q_7 = description_record_Q_7.Description
                except DescriptionsProjectandPolicies.DoesNotExist:
                    # Keep description_Q_7 as "-" if no matching record is found
                    pass

                response_data = {

                    'EI': {
                        'EI1_A': [{
                            "current_total_electricity_consumption_solar": round(
                            current_total_electricity_consumption_solar +
                            current_total_electricity_consumption_hydroelectric +
                            current_total_electricity_consumption_wind, 2
                        ),
                        "previous_total_electricity_consumption_solar": round(
                            previous_total_electricity_consumption_solar +
                            previous_total_electricity_consumption_hydroelectric +
                            previous_total_electricity_consumption_wind, 2)
                        }],
                        'EI1_B': [{"no_data1":"-",
                                   "no_data2":"-"}],
                        
                        'EI1_C': [{"no_data3":"-",
                                   "no_data4":"-"}],
                        
                        'EI1_ABC': [{"ABC_Current":round(current_total_electricity_consumption_solar +
                                current_total_electricity_consumption_hydroelectric +
                                current_total_electricity_consumption_wind, 2),
                           "ABC_Previous": round(previous_total_electricity_consumption_solar +
                                previous_total_electricity_consumption_hydroelectric +
                                previous_total_electricity_consumption_wind, 2)}],
                        'EI1_D': [{
                           "grid_current":round(current_total_electricity_consumption_grid, 2),
                            "grid_previous":round(previous_total_electricity_consumption_grid, 2)
                        }],
                        'EI1_E': [
                            {"current_total_fuel_consumption":round(current_total_fuel_consumption, 2),
                            "previous_total_fuel_consumption":round(previous_total_fuel_consumption, 2)
                        }],
                        'EI1_F': [{"no_data5":"-",
                                   "no_data6":"-"}],
                        
                        'EI1_DEF': [{"DEF_Current":round(current_total_electricity_consumption_grid+current_total_fuel_consumption,2),
                                     "DEF_Previous":round(previous_total_electricity_consumption_grid+previous_total_fuel_consumption,2)}],

                        'EI1_ABCDEF': [{"ABCDEF_Current":round(current_year_total,2),
                                       "ABCDEF_Previous":round(previous_year_total,2)}],

                        'EI1_G': [{
                           "G_Current": round((current_year_total / total_intensity_current)/10, 2) if total_intensity_current != 0 else 0,
                           "G_Previous": round((previous_year_total / total_intensity_previous)/10, 2) if total_intensity_previous != 0 else 0
                        }],

                    
                        'EI1_H': [{"H_C":round(ei_g,2),
                                  "H_P":round(ei_g_,2)}],
                        
                        'EI1_I':[{"no_data7":"-",
                                  "no_data8":"-"}],

                        'EI1_J':[{"no_data9":"-",
                                  "no_data10":"-"}],

                        "EI1_Ans" : EI1_Ans1,


                        "EI2_Ans" : [{"description_Q_1":description_Q_1}],



                        "EI3_A": [{
                           "Current_surface_water":round(current_total_surface_water_withdrawal, 2),
                           "Previous_surface_water":round(previous_total_surface_water_withdrawal, 2)
                        }],
                        "EI3_B": [{
                           "Current_ground_water":round(current_total_ground_water_withdrawal, 2),
                           "Previous_ground_water": round(previous_total_ground_water_withdrawal, 2)
                       } ],
                        "EI3_C": [{
                           "current_third_party_water":round(current_total_third_party_water_withdrawal, 2),
                            "previous_third_party_water":round(previous_total_third_party_water_withdrawal, 2)
                        }],
                        "EI3_D": [{
                            "current_seawater_withdrawal":round(current_total_seawater_withdrawal, 2),
                           "previous_seawater_withdrawal":round(previous_total_seawater_withdrawal, 2)
                        }],
                        "EI3_E": [{
                            "current_other_withdrawal":round(current_total_other_withdrawal, 2),
                            "previous_other_withdrawal":round(previous_total_other_withdrawal, 2)
                        }],
                        "EI3_ABCDE": [{
                            "all_current":round(
                                current_total_surface_water_withdrawal +
                                current_total_ground_water_withdrawal +
                                current_total_third_party_water_withdrawal +
                                current_total_seawater_withdrawal +
                                current_total_other_withdrawal, 2
                            ),
                            "all_previous":round(
                                previous_total_surface_water_withdrawal +
                                previous_total_ground_water_withdrawal +
                                previous_total_third_party_water_withdrawal +
                                previous_total_seawater_withdrawal +
                                previous_total_other_withdrawal, 2
                            )
                        }],
                        "EI3_F": [{
                            "current_total_water_consumption":round(current_total_water_consumption, 2),
                            "previous_total_water_consumption":round(previous_total_water_consumption, 2)
                        }],
                        "EI3_G": [{
                            "current_intensity":round((current_total_water_consumption / total_intensity_current)/10, 2) if total_intensity_current != 0 else 0,
                            "previous_intensity":round((previous_total_water_consumption / total_intensity_previous)/10, 2) if total_intensity_previous != 0 else 0
                        }],
                        "EI3_H" : [{"current_H":round(((current_total_water_consumption / total_intensity_current)*22.4/10), 2) if total_intensity_current != 0 else 0,
                                "previous_H":round(((previous_total_water_consumption / total_intensity_previous)*22.4/10), 2) if total_intensity_previous != 0 else 0 }],

                        "EI3_I" : [{"no_data11":"-",
                                    "no_data12":"-"}],
                        "EI3_J" : [{"no_data13":"-",
                                    "no_data14":"-"}],
                        "EI3_Ans" : EI3_Ans,

                        "EI4_A1": [{
                           "current_water_without_discharge":round(current_total_surface_water_without_discharge, 2) if current_total_surface_water_without_discharge is not None else "NA",
                           "previous_water_without_discharge":round(previous_total_surface_water_without_discharge, 2) if previous_total_surface_water_without_discharge is not None else "NA"
                        }],
                        "EI4_A2": [{
                            "current_surface_water_with_discharge":round((current_total_surface_water_with_discharge or 0) + (current_Total_level_of_treatment or 0), 2) if current_total_surface_water_with_discharge is not None else "NA",
                            "previous_surface_water_with_discharge":round((previous_total_surface_water_with_discharge or 0) + (previous_Total_level_of_treatment or 0), 2) if previous_total_surface_water_with_discharge is not None else "NA"
                        }],
                        "EI4_B1": [{
                            
                           "current_ground_water_without_discharge": round(current_total_ground_water_without_discharge, 2) if current_total_ground_water_without_discharge is not None else "NA",
                           "previous_ground_water_without_discharge": round(previous_total_ground_water_without_discharge, 2) if previous_total_ground_water_without_discharge is not None else "NA"
                        }],
                        "EI4_B2": [{
                           "current_B2": round((current_total_ground_water_with_discharge or 0) + (current_Total_level_of_treatment or 0), 2) if current_total_ground_water_with_discharge is not None else "NA",
                           "previous_B2": round((previous_total_ground_water_with_discharge or 0) + (previous_Total_level_of_treatment or 0), 2) if previous_total_ground_water_with_discharge is not None else "NA"
                        }],
                        "EI4_C1": [{
                            "current_seawater_without_discharge":round(current_total_seawater_without_discharge, 2) if current_total_seawater_without_discharge is not None else "NA",
                            "previous_seawater_without_discharge":round(previous_total_seawater_without_discharge, 2) if previous_total_seawater_without_discharge is not None else "NA"
                        }],
                        "EI4_C2": [{
                            "current_seawater_with_discharge": round((current_total_seawater_with_discharge or 0) + (current_Total_level_of_treatment or 0), 2) if current_total_seawater_with_discharge is not None else "NA",
                            "previous_seawater_with_discharge":round((previous_total_seawater_with_discharge or 0) + (previous_Total_level_of_treatment or 0), 2) if previous_total_seawater_with_discharge is not None else "NA"
                        }],
                        "EI4_D1": [{
                           "current_third_party_water_without_discharge":round(current_total_third_party_water_without_discharge, 2) if current_total_third_party_water_without_discharge is not None else "NA",
                           "previous_third_party_water_without_discharge":round(previous_total_third_party_water_without_discharge, 2) if previous_total_third_party_water_without_discharge is not None else "NA"
                        }],
                        "EI4_D2": [{
                            "current_total_third_party_water_with_discharge":round((current_total_third_party_water_with_discharge or 0) + (current_Total_level_of_treatment or 0), 2) if current_total_third_party_water_with_discharge is not None else "NA",
                            "previous_total_third_party_water_with_discharge":round((previous_total_third_party_water_with_discharge or 0) + (previous_Total_level_of_treatment or 0), 2) if previous_total_third_party_water_with_discharge is not None else "NA"
                        }],
                        "EI4_E1": [{
                            "current_without_discharge":round((current_total_other_without_discharge or 0) + (current_Total_level_of_treatment or 0), 2) if current_total_other_without_discharge is not None else "NA",
                            "previous_without_discharge":round((previous_total_other_without_discharge or 0) + (previous_Total_level_of_treatment or 0), 2) if previous_total_other_without_discharge is not None else "NA"
                       } ],
                        "EI4_E2": [{
                            "current_with_discharge":round((current_total_other_with_discharge or 0) + (current_Total_level_of_treatment or 0), 2) if current_total_other_with_discharge is not None else "NA",
                            "previous_with_discharge":round((previous_total_other_with_discharge or 0) + (previous_Total_level_of_treatment or 0), 2) if previous_total_other_with_discharge is not None else "NA"
                        }],
                        "EI4_F": [{
                            "Total_current_F":Total_current_F if Total_current_F is not None else "NA",
                            "Total_pervious_F":Total_pervious_F if Total_pervious_F is not None else "NA"
                       } ],

                        "EI4_Ans" : EI4_Ans,
                        
                        "EI5_Ans" :[{"description_zero_liquid_discharge":description_zero_liquid_discharge}],
                        
                        'EI6_A': {"EI6_A":ei6_totals.get('EI6_A', "NA") or "NA"},
                        'EI6_B': {"EI6_B":ei6_totals.get('EI6_B', "NA") or "NA"},
                        'EI6_C': {"EI6_C":ei6_totals.get('EI6_C', "NA") or "NA"},
                        'EI6_D': {"EI6_D":ei6_totals.get('EI6_D', "NA") or "NA"},
                        'EI6_E': {"EI6_E":ei6_totals.get('EI6_E', "NA") or "NA"},
                        'EI6_F': {"EI6_F":ei6_totals.get('EI6_F', "NA") or "NA"},
                        'EI6_G': {"EI6_G":ei6_totals.get('EI6_G', "NA") or "NA"},
                        "EI6_Ans" : EI4_Ans,

                        "EI7_A" :[{"scope1A_emissions":"Metric tons of CO2 equivalent",
                                  "current_total_scope1_emissions":round(current_total_scope1_emissions,2), 
                                   "previous_total_scope1_emissions":round(previous_total_scope1_emissions, 2)}],
                        "EI7_B" :[{"scope1B_emissions":"Metric tons of CO2 equivalent",
                                   "current_total_scope2_emissions":round(current_total_scope2_emissions,2),
                                  "previous_total_scope2_emissions":round(previous_total_scope2_emissions,2)}],

                        "Total_scope1_and_scope2_emission" :[{'unit': "Metric tons of CO2 equivalent",
                                                              "current_total_emissions": round((current_total_scope1_emissions+current_total_scope2_emissions),2),
                                                                "previous_total_emissions" :round((previous_total_scope1_emissions+previous_total_scope2_emissions),2)
                                                              }],

                        "EI7_C": [{
                            "no_data15":"-",
                            "intensity_current":round((((current_total_scope1_emissions + current_total_scope2_emissions) / total_intensity_current))/10, 2) if total_intensity_current != 0 else 0,
                            "intensity_previous":round((((previous_total_scope1_emissions + previous_total_scope2_emissions) / total_intensity_previous))/10, 2) if total_intensity_previous != 0 else 0
                        }],
                        "EI7_D" :[{"no_data":"-", 
                            "EI7_D_current_total_scope1_emissions":round((((current_total_scope1_emissions + current_total_scope2_emissions) / total_intensity_current)*22.4/10), 2) if total_intensity_current != 0 else 0,
                            "EI7_D_previous_total_scope1_emissions":round((((previous_total_scope1_emissions + previous_total_scope2_emissions) / total_intensity_previous)*22.4/10), 2) if total_intensity_previous != 0 else 0
                        }],
                        "EI7_E" :[{"no_data16":"-",
                                  "no_data17":"-",
                                  "no_data18":"-"}],
                        "EI7_F" :[{"no_data19":"-",
                                   "no_data20":"-",
                                   "no_data21":"-"}],
                        
                        "EI7_Ans":EI7_Ans,
                        "EI8_Ans":[{"description_green_house":description_green_house}],
                        "EI9_A": [{"current_total_plastic_waste":round(current_total_plastic_waste,3), 
                                   "previous_total_plastic_waste":round(previous_total_plastic_waste,3)}],
                        "EI9_B": [{"current_total_e_waste":round(current_total_e_waste,3), 
                                  "previous_total_e_waste":round(previous_total_e_waste,3)}],
                        "EI9_C": [{"current_total_bio_medical_waste":round(current_total_bio_medical_waste,3), 
                                  "previous_total_bio_medical_waste":round(previous_total_bio_medical_waste,3)}],
                        "EI9_D": [{"current_total_construction_waste":round(current_total_construction_waste,3), 
                                   "previous_total_construction_waste":round(previous_total_construction_waste,3)}],
                        "EI9_E": [{"current_total_battery_waste":round(current_total_battery_waste,3), 
                                   "previous_total_battery_waste":round(previous_total_battery_waste,3)}],
                        "EI9_F": [{"current_total_radioactive_waste":round(current_total_radioactive_waste,3), 
                                  "previous_total_radioactive_waste":round(previous_total_radioactive_waste,3)}],
                        "EI9_G": [{"current_total_other_hazardous_waste":round(current_total_other_hazardous_waste,3), 
                                  "previous_total_other_hazardous_waste":round(previous_total_other_hazardous_waste,3)}],
                        "EI9_H": [{"current_total_other_non_hazardous_waste":round(current_total_other_non_hazardous_waste,3), 
                                  "previous_total_other_non_hazardous_waste":round(previous_total_other_non_hazardous_waste,3)}],
                        "EI9_ABCDEFGH" :[{
                                       "current_waste":round((current_total_plastic_waste + current_total_e_waste +current_total_bio_medical_waste + current_total_construction_waste +current_total_battery_waste + current_total_radioactive_waste +current_total_other_hazardous_waste + current_total_other_non_hazardous_waste),3),
                                       "previous_waste":round((previous_total_plastic_waste + previous_total_e_waste + previous_total_bio_medical_waste + previous_total_construction_waste + previous_total_battery_waste + previous_total_radioactive_waste + previous_total_other_hazardous_waste + previous_total_other_non_hazardous_waste),3)
                                     }   ],

                    
                        "EI9_O": [{
                            "current_total_o":round(((current_sum_abcdefgh / total_intensity_current)/10), 3) if total_intensity_current != 0 else 0,
                            "previous_total_o":round(((previous_sum_abcdefgh / total_intensity_previous)/10), 3) if total_intensity_previous != 0 else 0
                        }],
                        "EI9_P":[ {
                            "current_P":round(((current_sum_abcdefgh / total_intensity_current)*22.4/10), 3) if total_intensity_current != 0 else 0,
                            "previous_P":round(((previous_sum_abcdefgh / total_intensity_previous)*22.4/10), 3) if total_intensity_previous != 0 else 0
                            }],
                        "EI9_Q":[{"EI9_Q1":0,
                                  "EI9_Q2":0}],
                        "EI9_R":[{"EI9_R1":0,
                                  "EI9_R2":0}],


                        "EI9_I": [{"current_total_recycled":round(current_total_recycled,3), 
                                  "previous_total_recycled":round(previous_total_recycled,3)}],
                        "EI9_J": [{"current_total_reused":round(current_total_reused,3), 
                                   "previous_total_reused":round(previous_total_reused,3)}],
                        "EI9_K": [{"current_total_other_recovery":round(current_total_other_recovery,3),
                                   "previous_total_other_recovery":round( previous_total_other_recovery,3)}],
                        "EI9_IJK": [{"total_current_recovered":round(total_current_recovered,3), 
                                     "total_previous_recovered":round(total_previous_recovered,3)}],
                        "EI9_L": [{"current_total_incineration":round(current_total_incineration,3), 
                                  "previous_total_incineration":round(previous_total_incineration,3)}],
                        "EI9_M": [{"current_total_landfilling":round(current_total_landfilling,3),
                                   "previous_total_landfilling":round(previous_total_landfilling,3)}],
                        "EI9_N": [{"current_total_other_disposal":round(current_total_other_disposal,3),
                                   "previous_total_other_disposal":round(previous_total_other_disposal,3)}],
                        "EI9_LMN": [{"total_current_disposed":round(total_current_disposed,3), 
                                    "total_previous_disposed":round(total_previous_disposed,3)}],
                        "EI9_Ans":EI9_Ans,

                        "EI10_Ans":[{"description_waste_management":description_waste_management}],
                        "EI11_Ans" : {"records_list_Q_11":records_list_Q_11},
                        "EI12_Ans" : [{"records_list_Q_12":records_list_Q_12 if records_list_Q_12 else "-"}],
                        "EI13_Ans" : [{"records_list_Q_13":records_list_Q_13 if records_list_Q_13 else "-"}],

                        "LI1_1": [{"records_list_Q1_1_2":records_list_Q1_1_2 if records_list_Q1_1_2 else "-"}],
                        "LI1_2": [{"records_list_Q1_1_2":records_list_Q1_1_2 if records_list_Q1_1_2 else "-"}],
                        
                        "LI1_A_A1": [{"current_sw":round(current_year_data["Surface Water"],2), 
                                      "previous_sw":round(previous_year_data["Surface Water"],2)}],
                        "LI1_A_A2": [{"current_gw":round(current_year_data["Ground Water"],2),
                                     "previous_gw":round(previous_year_data["Ground Water"],2)}],
                        "LI1_A_A3": [{"current_party": round(current_year_data["Third Party Water"],2), 
                                     "previous_party":round(previous_year_data["Third Party Water"],2)}],
                        
                        "LI1_A_A4": [{"current_sea":round(current_year_data["Sea Water"],2), 
                                     "previous_sea":round(previous_year_data["Sea Water"],2)}],
                        "LI1_A_A5": [{"current_others":round(current_year_data["Others"],2), 
                                    "previous_others":round(previous_year_data["Others"],2)}],
                        
                        "LI1_A_Total": [{"LI1_A_Total1":round((sum(current_year_data.values())),2), 
                                        "LI1_A_Total2":round((sum(previous_year_data.values())),2)}] ,
                        
                        "LI1_B" :[{"LI1_B1":round(current_total_consumption,2),
                                  "LI1_B2":round(previous_total_consumption,2)}],
                        
                        "LI1_C": [{"current_LI1_C":round((current_total_water_consumption / total_intensity_current)/10, 2) if total_intensity_current != 0 else 0,
                                "previous_LI1_C":round((previous_total_water_consumption / total_intensity_previous)/10, 2) if total_intensity_previous != 0 else 0}],
                        
                        "LI1_D":[{"no_data22":"-",
                                  "no_data23":"-"}],

                        "LI1_E_E1A": [{"current_LI1_E_E1A":round(current_year_discharge_without_treatment["Surface Water"],2), 
                                      "previous_LI1_E_E1A":round(previous_year_discharge_without_treatment["Surface Water"],2)}],
                        
                        "LI1_E_E1B": [{"current_surface_water":round(current_year_discharge_with_treatment["Surface Water"],2), 
                                      "previous_surface_water":round(previous_year_discharge_with_treatment["Surface Water"],2)}],
                        
                        "LI1_E_E2A": [{"current_ground_water":round(current_year_discharge_without_treatment["Ground Water"],2), 
                                      "previous_ground_water":round(previous_year_discharge_without_treatment["Ground Water"],2)}],
                        
                        "LI1_E_E2B": [{"current_ground_water_with":round(current_year_discharge_with_treatment["Ground Water"],2), 
                                      "previous_ground_water_with":round(previous_year_discharge_with_treatment["Ground Water"],2)}],
                        
                        "LI1_E_E3A": [{"current_year_discharge_without_treatment_sea_water":round(current_year_discharge_without_treatment["Sea Water"],2), 
                                      "previous_year_discharge_without_treatment_sea_water":round(previous_year_discharge_without_treatment["Sea Water"],2)}],   
                        
                        "LI1_E_E3B": [{"current_year_discharge_with_treatment_sea_water":round(current_year_discharge_with_treatment["Sea Water"],2), 
                                      "previous_year_discharge_with_treatment_sea_water":round(previous_year_discharge_with_treatment["Sea Water"],2)}],
                           
                        "LI1_E_E4A": [{"current_year_discharge_without_treatment_third_party":round(current_year_discharge_without_treatment["Third Party Water"],2), 
                                      "previous_year_discharge_without_treatment_third_party":round(previous_year_discharge_without_treatment["Third Party Water"],2)}],
                        
                        "LI1_E_E4B": [{"current_year_discharge_with_treatment_third_party":round(current_year_discharge_with_treatment["Third Party Water"],2), 
                                      "previous_year_discharge_with_treatment_third_party":round(previous_year_discharge_with_treatment["Third Party Water"],2)}],
                        
                        "LI1_E_E5A": [{"current_year_discharge_without_treatment_other":round(current_year_discharge_without_treatment["Others"],2),
                                      "previous_year_discharge_without_treatment_other":round(previous_year_discharge_without_treatment["Others"],2)}],
                        
                        "LI1_E_E5B": [{"current_year_discharge_with_treatment_others":round(current_year_discharge_with_treatment["Others"],2), 
                                      "previous_year_discharge_with_treatment":round(previous_year_discharge_with_treatment["Others"],2)}],
                        
                        "LI1_AllTotal":[{"current_all_total":round(current_year_total_discharge,2), 
                                        "previous_all_total":round(previous_year_total_discharge,2)}],

                        "LI1_Ans" : LI1_Ans,

                                                
                        "LI2_A" : [{"unit":"Metric tons of CO2 equivalent",
                                  "current_total_scope3_emission_by_facilities": round(current_total_scope3_emission_by_facilities,3) ,
                                  "previous_total_scope3_emission_by_facilities": round(previous_total_scope3_emission_by_facilities,3)}],
                        "LI2_B" : [{"unit1":"Metric tons of CO2 equivalent",
                                   "current_total_scope3_intensity":round(current_total_scope3_intensity,2) ,
                                   "previous_total_scope3_intensity":round(previous_total_scope3_intensity,2)} ],
                        
                        "LI2_C" : [{"units":"Metric tons of CO2 equivalent",
                                   "no_data24":"-",
                                   "no_data25":"-"}],
                        "LI2_Ans" : LI2_Ans2,

                        "LI3_Ans" : [{"description_Q_3":description_Q_3 if description_Q_3 else "-"}],
                        "LI4_Ans" : 
                         [{"description_Q_4":description_Q_4 if description_Q_4 else "-"}],
                        
                        "LI5_Ans" : [{"description_Q_5":description_Q_5 if description_Q_5 else "-"}],
                        "LI6_Ans" : [{"description_Q_6":description_Q_6 if description_Q_6 else "-"}],
                        "LI7_Ans" :[{"description_Q_7":description_Q_7 if description_Q_7 else "-"}],
                    

                    }
                }
                Brs_log = {
                "Financial_Year":financial_year,
                "Section":"Principle 6",
                "User_Name":f"{request.user.firstname} {request.user.lastname}" 
                }
                            
                brs_log_serializer = BRS_Report_LogSerializer(data=Brs_log)
                if brs_log_serializer.is_valid():
                    brs_log_serializer.save()
                    return Response(response_data, status=status.HTTP_200_OK)

            else:
                return Response({ "error": "This data can only accessed by Plant Operations or ESG Lead." }, status=status.HTTP_403_FORBIDDEN,)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Data Not Available in Principle_6"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except APIException as e:
            return Response(
                {"error": f"APIException in Principle_6: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TypeError as e:
            return Response(
                {"error": f"TypeError in Principle_6: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            error_type = type(e).__name__
            error_traceback = traceback.format_exc()
            return Response(
                {
                    "error": f"Unknown error in Principle_6: {error_type}",
                    "details": error_traceback,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class Principle7View(APIView):
    def get(self, request):
        try:
            response_data = {}

            financial_year = request.query_params.get("financial_year", None)

            if financial_year is None:
                return Response(
                    {"error": "financial_year parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract the starting year from the financial year string
            try:
                start_year = int(
                    financial_year.split("-")[0][2:]
                )  # Extract '2023' from 'FY2023-2024'
                previous_financial_year = (
                    f"FY{start_year-1}-{start_year}"  # 'FY2022-2023'
                )
            except (ValueError, IndexError):
                return Response(
                    {
                        "error": 'Invalid financial_year format. Expected format: "FY2023-2024"'
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                affiliation = Number_Of_Affiliations.objects.values_list(
                    "Number_Of_Affiliations_With_Trade_And_Industry_Chambers", flat=True
                )
                data_affiliation = list(affiliation) if affiliation else ["-"]
            except Exception:
                data_affiliation = ["-"]

            try:
                chambers = Top_10_Trade_And_Industry_Chambers.objects.all().values()
                data_chambers = list(chambers) if chambers else [ {
                    "Sr_No":"-",
                    "Name_Of_The_Trade_And_Industry_Chambers": "-",
                    "Reach_Of_Trade_And_Industry_Chambers": "-"
                }]
            except Exception:
                data_chambers =[ {
                    "Sr_No":"-",
                    "Name_Of_The_Trade_And_Industry_Chambers": "-",
                    "Reach_Of_Trade_And_Industry_Chambers": "-"
                }]

            # Fetch authority details, defaulting to empty list if no data
            try:
                authority = (
                    Details_Of_Any_Issues_Related_To_Anti_Competitive_Conduct_By_The_Entity.objects.all().values()
                )
                data_auth = list(authority) if authority else [
                    {
                        "Name_OF_Authority": "-",
                        "Brief_Of_The_Case": "-",
                        "Corrective_Action_Taken": "-"
                    }]
            except Exception:
                data_auth =[ {
                        "Name_OF_Authority": "-",
                        "Brief_Of_The_Case": "-",
                        "Corrective_Action_Taken": "-"
                    }]

            try:
                public_policy = Details_Of_Public_Policy_Positions_Advocated_By_The_Entity.objects.get(
                    Financial_Year=financial_year
                )
                if public_policy:
                    # Check if only Description_Details has a value
                    if public_policy.Description_Details and not any(
                        [
                            public_policy.Public_Policy_Advocated,
                            public_policy.Method_Resorted_For_Such_Advocacy,
                            public_policy.Information_Available_In_Public_Domain,
                            public_policy.Frequency_Of_Engagement,
                            public_policy.Web_Link,
                        ]
                    ):
                        # If only Description_Details has a value, keep it, and set the rest to "-"
                        financial_year_value = public_policy_advocated = (
                            method_resorted
                        ) = info_in_public_domain = engagement_frequency = web_link = (
                            "-"
                        )
                        description_details = public_policy.Description_Details
                    else:
                        # Fetch values with fallback to "-"
                        financial_year_value = public_policy.Financial_Year or "-"
                        public_policy_advocated = (
                            public_policy.Public_Policy_Advocated or "-"
                        )
                        method_resorted = (
                            public_policy.Method_Resorted_For_Such_Advocacy or "-"
                        )
                        info_in_public_domain = (
                            public_policy.Information_Available_In_Public_Domain or "-"
                        )
                        engagement_frequency = (
                            public_policy.Frequency_Of_Engagement or "-"
                        )
                        web_link = public_policy.Web_Link or "-"
                        description_details = public_policy.Description_Details or "-"
                else:
                    financial_year_value = public_policy_advocated = method_resorted = (
                        info_in_public_domain
                    ) = "-"
                    engagement_frequency = web_link = description_details = "-"
            except (
                Details_Of_Public_Policy_Positions_Advocated_By_The_Entity.DoesNotExist
            ):
                # Handle case where no record is found for the given financial year
                financial_year_value = public_policy_advocated = method_resorted = (
                    info_in_public_domain
                ) = "-"
                engagement_frequency = web_link = description_details = "-"

            response_data = {
                "Section_C_P7": {
                    "Principle_7_EI_1a": [{"data_affiliation": data_affiliation[0]}],
                    "Principle_7_EI_1b": data_chambers,
                    "Principle_7_EI_2": data_auth,
                    "Principle_7_LI_1": {
                        "Financial_Year": financial_year_value,
                        "Public_Policy_Advocated": public_policy_advocated,
                        "Method_Resorted_For_Such_Advocacy": method_resorted,
                        "Information_Available_In_Public_Domain": info_in_public_domain,
                        "Frequency_Of_Engagement": engagement_frequency,
                        "Web_Link": web_link,
                        "Description_Details": description_details,
                    },
                }
            }
            Brs_log = {
                "Financial_Year":financial_year,
                "Section":"Principle 7",
                "User_Name":f"{request.user.firstname} {request.user.lastname}"
               
            }
                            
            brs_log_serializer = BRS_Report_LogSerializer(data=Brs_log)
            if brs_log_serializer.is_valid():
                brs_log_serializer.save()


            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Data Not Available in Principle_7"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except APIException as e:
            return Response(
                {"error": f"APIException in Principle_7: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TypeError as e:
            return Response(
                {"error": f"TypeError in Principle_7: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Unknown error in Principle_7: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class Principle8View(APIView):
    def get(self, request):
        try:
            response_data = {}

            financial_year = request.query_params.get("financial_year", None)

            if financial_year is None:
                return Response(
                    {"error": "financial_year parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                start_year = int(
                    financial_year.split("-")[0][2:]
                )  # Extract '2023' from 'FY2023-2024'
                previous_financial_year = (
                    f"FY{start_year-1}-{start_year}"  # 'FY2022-2023'
                )
            except (ValueError, IndexError):
                return Response(
                    {
                        "error": 'Invalid financial_year format. Expected format: "FY2023-2024"'
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                social_impact_records = (
                    Details_Of_Social_Impact_Assessments.objects.values(
                        "Name_And_Brief_Details_Of_Project",
                        "SIA_Notification_No",
                        "Date_Of_Notification",
                        "Relevant_Web_Link",
                        "Conducted_By_Independent_External_Agency",
                        "Results_Communicated_In_Public_Domain",
                        "Description_Details",
                        "Whether_available_public_domain",
                    )
                )

                # Check if there are no records, return default values
                if not social_impact_records:
                    principle_8_data = [
                        {
                            "Name_And_Brief_Details_Of_Project": "-",
                            "SIA_Notification_No": "-",
                            "Date_Of_Notification": "-",
                            "Relevant_Web_Link": "-",
                            "Conducted_By_Independent_External_Agency": "-",
                            "Results_Communicated_In_Public_Domain": "-",
                            "Description_Details": "-",
                            "Whether_available_public_domain": "-",
                        }
                    ]
                else:
                    principle_8_data = []
                    for item in social_impact_records:
                        data_item = {}
                        # Process each field with error handling
                        for field in [
                            "Name_And_Brief_Details_Of_Project",
                            "SIA_Notification_No",
                            "Date_Of_Notification",
                            "Relevant_Web_Link",
                            "Conducted_By_Independent_External_Agency",
                            "Results_Communicated_In_Public_Domain",
                            "Description_Details",
                            "Whether_available_public_domain",
                        ]:
                            try:
                                # Convert to string to handle unexpected types gracefully
                                data_item[field] = (
                                    str(item.get(field, "-"))
                                    if item.get(field)
                                    else "-"
                                )
                            except (ZeroDivisionError, ValueError, TypeError) as e:
                                data_item[field] = (
                                    f"Error in {field} from Details_Of_Social_Impact_Assessments: {e}"
                                )
                        principle_8_data.append(data_item)

            except Exception as e:
                # If there is a broader exception, return a default entry
                principle_8_data = [
                    {
                        "Name_And_Brief_Details_Of_Project": "-",
                        "SIA_Notification_No": "-",
                        "Date_Of_Notification": "-",
                        "Relevant_Web_Link": "-",
                        "Conducted_By_Independent_External_Agency": "-",
                        "Results_Communicated_In_Public_Domain": "-",
                        "Description_Details": "-",
                        "Whether_available_public_domain": "-",
                    }
                ]

            ongoing = Ongoing_Rehabilitation_And_Resettlement.objects.values(
                "Name_Of_Project",
                "State",
                "District",
                "No_Of_PAFs",
                "Percentage_Of_PAFs_Covered_By_R_R",
                "Amounts_Paid_To_PAFs",
                "Description_Ongoing",
            )

            principle_8a_data = []
            for entry in ongoing:
                # Check if the Name_Of_Project is "Not Applicable"
                if entry["Name_Of_Project"] == "Not Applicable":
                    principle_8a_data.append(
                        {
                            "Name_Of_Project": "Not Applicable",
                            "State": "-",
                            "District": "-",
                            "No_Of_PAFs": "-",
                            "Percentage_Of_PAFs_Covered_By_R_R": "-",
                            "Amounts_Paid_To_PAFs": "-",
                            "Description_Ongoing": "-",
                        }
                    )
                else:
                    # Convert Decimal or Decimal128 to string and handle empty values
                    for key, value in entry.items():
                        if isinstance(value, (Decimal, Decimal128)):
                            entry[key] = str(value)

                    # Append formatted data with fallback for empty fields
                    principle_8a_data.append(
                        {
                            "Name_Of_Project": (
                                entry["Name_Of_Project"]
                                if entry["Name_Of_Project"]
                                else "-"
                            ),
                            "State": entry["State"] if entry["State"] else "-",
                            "District": entry["District"] if entry["District"] else "-",
                            "No_Of_PAFs": (
                                entry["No_Of_PAFs"] if entry["No_Of_PAFs"] else "-"
                            ),
                            "Percentage_Of_PAFs_Covered_By_R_R": (
                                f"{entry['Percentage_Of_PAFs_Covered_By_R_R']}%" 
                                if entry["Percentage_Of_PAFs_Covered_By_R_R"]
                                else "-"
                            ),
                            "Amounts_Paid_To_PAFs": (
                                f"{entry['Amounts_Paid_To_PAFs']}₹"
                                if entry["Amounts_Paid_To_PAFs"]
                                else "-"
                            ),
                            "Description_Ongoing": (
                                entry["Description_Ongoing"]
                                if entry["Description_Ongoing"]
                                else "-"
                            ),
                        }
                    )

            # If ongoing is empty, add a default entry with "-" values
            if not ongoing:
                principle_8a_data = [
                    {
                        "Name_Of_Project": "-",
                        "State": "-",
                        "District": "-",
                        "No_Of_PAFs": "-",
                        "Percentage_Of_PAFs_Covered_By_R_R": "-",
                        "Amounts_Paid_To_PAFs": "-",
                        "Description_Ongoing": "-",
                    }
                ]

            description_obj_griev = Society_Details.objects.filter(
                Model_Name_Society="Grievances of the community"
            ).first()

            current_records_material = Percentage_Of_Input_Material.objects.filter(
                Financial_Year=financial_year
            )
            previous_records_material = Percentage_Of_Input_Material.objects.filter(
                Financial_Year=previous_financial_year
            )
            current_total_record = sum(
                Decimal(str(record.Directly_Sourced_From_MSMEs_Small_Producers.to_decimal()))
                for record in current_records_material
            )

            previous_total_record = sum(
                Decimal(str(record.Directly_Sourced_From_MSMEs_Small_Producers.to_decimal()))
                for record in previous_records_material
            )

            directly_from_india_current_total_record = sum(
                Decimal(str(record.Sourced_Directly_Within_The_District_And_Neighbouring_Districts.to_decimal()))
                for record in current_records_material
            )

            directly_from_india_previous_total_record = sum(
                Decimal(str(record.Sourced_Directly_Within_The_District_And_Neighbouring_Districts.to_decimal()))
                for record in previous_records_material
            )
            
            social_impact_detail = Details_Of_Actions_Taken_To_Mitigate.objects.values(
                "Detail_of_Negative_Impact_Identified", "Corrective_Action_Taken"
            )

            if not social_impact_detail:  # If social_impact_detail is empty
                social_impact_detail_data = [
                    {
                        "Detail_of_Negative_Impact_Identified": "-",
                        "Corrective_Action_Taken": "-",
                    }
                ]
            else:
                social_impact_detail_data = [
                    {
                        "Detail_of_Negative_Impact_Identified": (
                            item["Detail_of_Negative_Impact_Identified"]
                            if item["Detail_of_Negative_Impact_Identified"]
                            else "-"
                        ),
                        "Corrective_Action_Taken": (
                            item["Corrective_Action_Taken"]
                            if item["Corrective_Action_Taken"]
                            else "-"
                        ),
                    }
                    for item in social_impact_detail
                ]

            carporate = Information_on_CSR_Projects.objects.values(
                "State", "Aspirational_District", "Amount_Spent", "Description_CSR"
            )

            if not carporate:  # If carporate is empty
                carporate_data = [
                    {
                        "State": "-",
                        "Aspirational_District": "-",
                        "Amount_Spent": "-",
                        "Description_CSR": "-",
                    }
                ]
            else:
                carporate_data = [
                    {
                        "State": item["State"] if item["State"] else "-",
                        "Aspirational_District": (
                            item["Aspirational_District"]
                            if item["Aspirational_District"]
                            else "-"
                        ),
                        "Amount_Spent": (
                             f'{item["Amount_Spent"]}₹'  if item["Amount_Spent"] else "-"
                        ),
                        "Description_CSR": (
                            item["Description_CSR"] if item["Description_CSR"] else "-"
                        ),
                    }
                    for item in carporate
                ]

            description_obj = Corporate_Social_Responsibility_Details.objects.filter(
                Model_Name_Corporate="Preferential Procurement"
            ).first()

            description_obj_corporate = (
                Corporate_Social_Responsibility_Details.objects.filter(
                    Model_Name_Corporate="Marginalized"
                ).first()
            )

            description_obj_procurement = (
                Corporate_Social_Responsibility_Details.objects.filter(
                    Model_Name_Corporate="Procurement"
                ).first()
            )

            carporate_benefit = (
                Benefits_Derived_And_Shared_From_Intellectual_Property.objects.values(
                    "IP",
                    "Owned",
                    "Benefit_Shared",
                    "Basis_of_Calculating_Benefit_Share",
                )
            )

            if not carporate_benefit:  # If carporate_benefit is empty
                carporate_benefit_data = [
                    {
                        "IP": "-",
                        "Owned": "-",
                        "Benefit_Shared": "-",
                        "Basis_of_Calculating_Benefit_Share": "-",
                    }
                ]
            else:
                carporate_benefit_data = [
                    {
                        "IP": item["IP"] if item["IP"] else "-",
                        "Owned": item["Owned"] if item["Owned"] else "-",
                        "Benefit_Shared": (
                            item["Benefit_Shared"] if item["Benefit_Shared"] else "-"
                        ),
                        "Basis_of_Calculating_Benefit_Share": (
                            item["Basis_of_Calculating_Benefit_Share"]
                            if item["Basis_of_Calculating_Benefit_Share"]
                            else "-"
                        ),
                    }
                    for item in carporate_benefit
                ]

            IP = Details_Of_Intellectual_Property_Related_Disputes.objects.values(
                "Name_of_Authority", "Brief_of_The_case", "Corrective_Actions_Taken"
            )

            if not IP:  # If IP is empty
                IP_data = [
                    {
                        "Name_of_Authority": "-",
                        "Brief_of_The_case": "-",
                        "Corrective_Actions_Taken": "-",
                    }
                ]
            else:
                IP_data = [
                    {
                        "Name_of_Authority": (
                            item["Name_of_Authority"]
                            if item["Name_of_Authority"]
                            else "-"
                        ),
                        "Brief_of_The_case": (
                            item["Brief_of_The_case"]
                            if item["Brief_of_The_case"]
                            else "-"
                        ),
                        "Corrective_Actions_Taken": (
                            item["Corrective_Actions_Taken"]
                            if item["Corrective_Actions_Taken"]
                            else "-"
                        ),
                    }
                    for item in IP
                ]

            csr = Details_Of_Beneficiaries_Of_CSR_Projects.objects.values(
                "CSR_Project",
                "NO_Of_Persons_Benefitted_From_CSR_Projects",
                "Percent_of_Beneficiaries_From_Vulnerable_And_Merginalized_Groups",
            )

            if not csr:  # If csr is empty
                csr_data = [
                    {
                        "CSR_Project": "-",
                        "NO_Of_Persons_Benefitted_From_CSR_Projects": "-",
                        "Percent_of_Beneficiaries_From_Vulnerable_And_Merginalized_Groups": "-",
                    }
                ]
            else:
                csr_data = [
                    {
                        "CSR_Project": (
                            item["CSR_Project"] if item["CSR_Project"] else "-"
                        ),
                        "NO_Of_Persons_Benefitted_From_CSR_Projects": (
                            item["NO_Of_Persons_Benefitted_From_CSR_Projects"]
                            if item["NO_Of_Persons_Benefitted_From_CSR_Projects"]
                            else "-"
                        ),
                        "Percent_of_Beneficiaries_From_Vulnerable_And_Merginalized_Groups": (
                            f'{item["Percent_of_Beneficiaries_From_Vulnerable_And_Merginalized_Groups"]}%' 
                            if item[
                                "Percent_of_Beneficiaries_From_Vulnerable_And_Merginalized_Groups"
                            ]
                            else "-"
                        ),
                    }
                    for item in csr
                ]

            current_year_record = Gross_Wages_Paid.objects.filter(
                Financial_Year=financial_year
            ).first()
            previous_year_record = Gross_Wages_Paid.objects.filter(
                Financial_Year=previous_financial_year
            ).first()

            # Fetching values or setting to "-" if no record is found
            current_year_rural = (
                conversion(current_year_record.Rural) if current_year_record else "-"
            )
            previous_year_rural = (
                conversion(previous_year_record.Rural) if previous_year_record else "-"
            )

            current_year_semi_urban = (
                conversion(current_year_record.Semi_Urban)
                if current_year_record
                else "-"
            )
            previous_year_semi_urban = (
                conversion(previous_year_record.Semi_Urban)
                if previous_year_record
                else "-"
            )

            current_year_urban = (
                conversion(current_year_record.Urban) if current_year_record else "-"
            )
            previous_year_urban = (
                conversion(previous_year_record.Urban) if previous_year_record else "-"
            )

            current_year_metropolitan = (
                conversion(current_year_record.Metropolitan)
                if current_year_record
                else "-"
            )
            previous_year_metropolitan = (
                conversion(previous_year_record.Metropolitan)
                if previous_year_record
                else "-"
            )

            response_data = {
                "Section_C_P8": {
                    "Principle_8_EI_1": principle_8_data,
                    "Principle_8_EI_2": principle_8a_data,
                    "Principle_8_EI_3": [
                        {
                            "description_obj_griev": (
                                description_obj_griev.Description
                                if description_obj_griev
                                else "-"
                            )
                        }
                    ],
                    "Principle_8_EI_4_MSME": [
                        {
                            "current_total_record": (
                                current_total_record if current_total_record else "-"
                            ),
                            "previous_total_record": (
                                previous_total_record if previous_total_record else "-"
                            ),
                        }
                    ],
                    "Principle_8_EI_4_INDIA": [
                        {
                            "directly_from_india_current_total_record": (
                                directly_from_india_current_total_record
                                if directly_from_india_current_total_record
                                else "-"
                            ),
                            "directly_from_india_previous_total_record": (
                                directly_from_india_previous_total_record
                                if directly_from_india_previous_total_record
                                else "-"
                            ),
                        }
                    ],
                    "Principle_8_EI_5_Rural": [
                        {
                            "current_year_rural": current_year_rural,
                            "previous_year_rural": previous_year_rural,
                        }
                    ],
                    "Principle_8_EI_5_Semi_urban": [
                        {
                            "current_year_semi_urban": current_year_semi_urban,
                            "previous_year_semi_urban": previous_year_semi_urban,
                        }
                    ],
                    "Principle_8_EI_5_Urban": [
                        {
                            "current_year_urban": current_year_urban,
                            "previous_year_urban": previous_year_urban,
                        }
                    ],
                    "Principle_8_EI_5_Metropolitan": [
                        {
                            "current_year_metropolitan": current_year_metropolitan,
                            "previous_year_metropolitan": previous_year_metropolitan,
                        }
                    ],
                    "Principle_8_LI_1": (
                        social_impact_detail_data if social_impact_detail_data else "-"
                    ),
                    "Principle_8_LI_2": carporate_data if carporate_data else "-",
                    "Principle_8_LI_3a": [
                        {
                            "description_obj": (
                                description_obj.Description if description_obj else "-"
                            )
                        }
                    ],
                    "Principle_8_LI_3b": [
                        {
                            "description_obj_corporate": (
                                description_obj_corporate.Description
                                if description_obj_corporate
                                else "-"
                            )
                        }
                    ],
                    "Principle_8_LI_3c": [
                        {
                            "description_obj_procurement": (
                                description_obj_procurement.Description
                                if description_obj_procurement
                                else "-"
                            )
                        }
                    ],
                    "Principle_8_LI_4": (
                        carporate_benefit_data if carporate_benefit_data else "-"
                    ),
                    "Principle_8_LI_5": IP_data if IP_data else "-",
                    "Principle_8_LI_6": csr_data if csr_data else "-",
                }
            }

            Brs_log = {
                "Financial_Year":financial_year,
                "Section":"Principle 8",
                "User_Name":f"{request.user.firstname} {request.user.lastname}"
            }
                            
            brs_log_serializer = BRS_Report_LogSerializer(data=Brs_log)
            if brs_log_serializer.is_valid():
                brs_log_serializer.save()
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Data Not Available in Principle_8"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except APIException as e:
            return Response(
                {"error": f"APIException in Principle_8: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TypeError as e:
            return Response(
                {"error": f"TypeError in Principle_8: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Unknown error in Principle_8: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class Principle9View(APIView):

    def get(self, request):
        try:
            response_data = {}

            financial_year = request.query_params.get("financial_year", None)

            if financial_year is None:
                return Response(
                    {"error": "financial_year parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract the starting year from the financial year string
            try:
                start_year = int(
                    financial_year.split("-")[0][2:]
                )  # Extract '2023' from 'FY2023-2024'
                previous_financial_year = (
                    f"FY{start_year-1}-{start_year}"  # 'FY2022-2023'
                )
            except (ValueError, IndexError):
                return Response(
                    {
                        "error": 'Invalid financial_year format. Expected format: "FY2023-2024"'
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            current_records_turnover = (
                Turnover_Of_Products_As_A_Percentage_Of_Turnover.objects.filter(
                    Financial_Year=financial_year
                )
            )

            environment = str(current_records_turnover[0].Environment_Parameters) if current_records_turnover else "-"
            safe_usage = str(current_records_turnover[0].Safe_Usage) if current_records_turnover else "-"
            recycling_Disposal = str(current_records_turnover[0].Recycling_Disposal) if current_records_turnover else "-"

            
                 

            current_year_Data_Privacy = Number_of_Consumer_Complaints.objects.filter(
                Financial_Year=financial_year, Type="Data Privacy"
            ).first()

            # Fetch data for the previous financial year
            previous_year_Data_Privacy = Number_of_Consumer_Complaints.objects.filter(
                Financial_Year=previous_financial_year, Type="Data Privacy"
            ).first()

            current_year_Advertising = Number_of_Consumer_Complaints.objects.filter(
                Financial_Year=financial_year, Type="Advertising"
            ).first()

            # Fetch data for the previous financial year
            previous_year_Advertising = Number_of_Consumer_Complaints.objects.filter(
                Financial_Year=previous_financial_year, Type="Advertising"
            ).first()

            current_year_Cyber_Security = Number_of_Consumer_Complaints.objects.filter(
                Financial_Year=financial_year, Type="Cyber-Security"
            ).first()

            # Fetch data for the previous financial year
            previous_year_Cyber_Security = Number_of_Consumer_Complaints.objects.filter(
                Financial_Year=previous_financial_year, Type="Cyber-Security"
            ).first()

            current_year_Delivery_of_Essential_Services = (
                Number_of_Consumer_Complaints.objects.filter(
                    Financial_Year=financial_year, Type="Delivery of Essential Services"
                ).first()
            )

            # Fetch data for the previous financial year
            previous_year_Delivery_of_Essential_Services = (
                Number_of_Consumer_Complaints.objects.filter(
                    Financial_Year=previous_financial_year,
                    Type="Delivery of Essential Services",
                ).first()
            )

            current_year_Restrictive_Trade_Practices = (
                Number_of_Consumer_Complaints.objects.filter(
                    Financial_Year=financial_year, Type="Restrictive Trade Practices"
                ).first()
            )

            # Fetch data for the previous financial year
            previous_year_Restrictive_Trade_Practices = (
                Number_of_Consumer_Complaints.objects.filter(
                    Financial_Year=previous_financial_year,
                    Type="Restrictive Trade Practices",
                ).first()
            )

            current_year_Unfair_Trade_Practices = (
                Number_of_Consumer_Complaints.objects.filter(
                    Financial_Year=financial_year, Type="Unfair Trade Practices"
                ).first()
            )

            # Fetch data for the previous financial year
            previous_year_Unfair_Trade_Practices = (
                Number_of_Consumer_Complaints.objects.filter(
                    Financial_Year=previous_financial_year,
                    Type="Unfair Trade Practices",
                ).first()
            )

            current_year_Other = Number_of_Consumer_Complaints.objects.filter(
                Financial_Year=financial_year, Type="Other"
            ).first()

            # Fetch data for the previous financial year
            previous_year_Other = Number_of_Consumer_Complaints.objects.filter(
                Financial_Year=previous_financial_year, Type="Other"
            ).first()

            Volunatry_Recalls = Details_Of_Instances_Of_Product_Recalls.objects.filter(
                Financial_Year=financial_year, Recall_Type="Volunatry Recalls"
            ).first()

            Forced_Recalls = Details_Of_Instances_Of_Product_Recalls.objects.filter(
                Financial_Year=financial_year, Recall_Type="Forced Recalls"
            ).first()

            description_obj_consumer = Consumer_Details.objects.filter(
                Model_Name_Consumer="Describe the mechanisms"
            ).first()
            description_obj_cd = Consumer_Details.objects.filter(
                Model_Name_Consumer="Data privacy"
            ).first()
            description_obj_cd1 = Consumer_Details.objects.filter(
                Model_Name_Consumer="Details of any corrective actions"
            ).first()
            description_obj_lcd1 = Consumer_Details.objects.filter(
                Model_Name_Consumer="Information on Products"
            ).first()
            description_obj_lcd2 = Consumer_Details.objects.filter(
                Model_Name_Consumer="Inform and Educate Consumers"
            ).first()
            description_obj_lcd3 = Consumer_Details.objects.filter(
                Model_Name_Consumer="Discontinuation of Essential Services"
            ).first()
            description_obj_lcd4 = Consumer_Details.objects.filter(
                Model_Name_Consumer="Display Product Information"
            ).first()
            description_obj_lcd5 = Consumer_Details.objects.filter(
                Model_Name_Consumer="Survey"
            ).first()

            ########################## p9 EI-7#######################
            data_breach = Number_Of_Instance_Of_Data_Breache.objects.filter(
                Financial_Year=financial_year
            ).first()

            if data_breach:
                Number_Of_Instances_Of_Data_Breaches = float(
                    data_breach.Number_Of_Instances_Of_Data_Breaches.to_decimal()
                )
                Percent_Of_Customers_Affected_By_Data_Breaches = float(
                    data_breach.Percent_Of_Customers_Affected_By_Data_Breaches.to_decimal()
                )
                impact = data_breach.Impact

                if Number_Of_Instances_Of_Data_Breaches == 0:
                    Number_Of_Instances_Of_Data_Breaches = (
                        f"No data breaches were recorded in {financial_year}."
                    )

                if Percent_Of_Customers_Affected_By_Data_Breaches == 0:
                    Percent_Of_Customers_Affected_By_Data_Breaches = (
                        f"No data breaches were recorded in {financial_year}."
                    )

                # if impact == "NA":
                #     impact = f"No data breaches were recorded in {financial_year}."
            else:
                Number_Of_Instances_Of_Data_Breaches = "-"
                Percent_Of_Customers_Affected_By_Data_Breaches = "-"
                impact = "-"

            #############################################################################
            response_data["Section_C_P9"] = {}
            # Merge with existing response_data to keep Principle_9_EI_3 data

            response_data["Section_C_P9"].update({
            "Principle_9_EI_1": [{"description_obj_consumer":description_obj_consumer.Description_consumer if description_obj_consumer else "-"}],
            "Principle_9_EI_2_ENV": [{
                "environment":environment if environment else "-",
            }],
            "Principle_9_EI_2_Safe": [{
                "safe_usage":safe_usage if safe_usage else "-",
            }],
            "Principle_9_EI_2_Recycling": [{
                "recycling_Disposal":recycling_Disposal if recycling_Disposal else "-",
            }],
            "Principle_9_EI_3_DP":[{
                           "Received_During_The_Year_DP_current": current_year_Data_Privacy.Received_During_The_Year if current_year_Data_Privacy else 0,
                           "Pending_Resolution_At_End_Of_The_Year_DP_current": current_year_Data_Privacy.Pending_Resolution_At_End_Of_The_Year if current_year_Data_Privacy else 0,
                           "Remarks_DP_current":current_year_Data_Privacy.Remarks if current_year_Data_Privacy  and current_year_Data_Privacy.Remarks else "NA",
                          

                          "Received_During_The_Year_DP_previous": previous_year_Data_Privacy.Received_During_The_Year if previous_year_Data_Privacy else 0,
                          "Pending_Resolution_At_End_Of_The_Year_DP_previous": previous_year_Data_Privacy.Pending_Resolution_At_End_Of_The_Year if previous_year_Data_Privacy else 0,
                          "Remarks_DP_previous": previous_year_Data_Privacy.Remarks if previous_year_Data_Privacy  and  previous_year_Data_Privacy.Remarks else "NA",
                                                             
           }],
            
            # Data for Cyber-Security
            "Principle_9_EI_3_CS": [{
                            "Received_During_The_Year_cs_current":current_year_Cyber_Security.Received_During_The_Year if current_year_Cyber_Security else 0,
                            "Pending_Resolution_At_End_Of_The_Year_cs_current":current_year_Cyber_Security.Pending_Resolution_At_End_Of_The_Year if current_year_Cyber_Security else 0,
                            "Remarks_cs_current":current_year_Cyber_Security.Remarks if current_year_Cyber_Security and current_year_Cyber_Security.Remarks  else "NA",

                            "Received_During_The_Year_cs_previous":previous_year_Cyber_Security.Received_During_The_Year if previous_year_Cyber_Security else 0,
                            "Pending_Resolution_At_End_Of_The_Year_cs_previous":previous_year_Cyber_Security.Pending_Resolution_At_End_Of_The_Year if previous_year_Cyber_Security else 0,
                            "Remarks_cs_previous":previous_year_Cyber_Security.Remarks if previous_year_Cyber_Security and  previous_year_Cyber_Security.Remarks else "NA",
                        }],

            # Data for Advertising
            "Principle_9_EI_3_AD": [{
                            "Received_During_The_Year_ad_current":current_year_Advertising.Received_During_The_Year if current_year_Advertising else 0,
                            "Pending_Resolution_At_End_Of_The_Year_ad_current": current_year_Advertising.Pending_Resolution_At_End_Of_The_Year if current_year_Advertising else 0,
                            "Remarks_ad_current":current_year_Advertising.Remarks if current_year_Advertising and  current_year_Advertising.Remarks else "NA",

                            "Received_During_The_Year_ad_previous": previous_year_Advertising.Received_During_The_Year if previous_year_Advertising else 0,
                            "Pending_Resolution_At_End_Of_The_Year_ad_previous":previous_year_Advertising.Pending_Resolution_At_End_Of_The_Year if previous_year_Advertising else 0,
                            "Remarks_ad_previous":previous_year_Advertising.Remarks if previous_year_Advertising and previous_year_Advertising.Remarks else "NA",
                       } ],

            # Data for Delivery of Essential Services
            "Principle_9_EI_3_DES": [{
                            "Received_During_The_Year_des_current":current_year_Delivery_of_Essential_Services.Received_During_The_Year if current_year_Delivery_of_Essential_Services else 0,
                            "Pending_Resolution_At_End_Of_The_Year_des_current":current_year_Delivery_of_Essential_Services.Pending_Resolution_At_End_Of_The_Year if current_year_Delivery_of_Essential_Services else 0,
                            "Remarks_des_current":current_year_Delivery_of_Essential_Services.Remarks if current_year_Delivery_of_Essential_Services and current_year_Delivery_of_Essential_Services.Remarks else "NA",

                            "Received_During_The_Year_des_previous":previous_year_Delivery_of_Essential_Services.Received_During_The_Year if previous_year_Delivery_of_Essential_Services else 0,
                            "Pending_Resolution_At_End_Of_The_Year_des_previous":previous_year_Delivery_of_Essential_Services.Pending_Resolution_At_End_Of_The_Year if previous_year_Delivery_of_Essential_Services else 0,
                            "Remarks_des_previous":previous_year_Delivery_of_Essential_Services.Remarks if  previous_year_Delivery_of_Essential_Services and previous_year_Delivery_of_Essential_Services.Remarks else "NA",
                        }],

            # Data for Restrictive Trade Practices
            "Principle_9_EI_3_RTP": [{
                            "Received_During_The_Year_rtp_current":current_year_Restrictive_Trade_Practices.Received_During_The_Year if current_year_Restrictive_Trade_Practices else 0,
                            "Pending_Resolution_At_End_Of_The_Year_rtp_current":current_year_Restrictive_Trade_Practices.Pending_Resolution_At_End_Of_The_Year if current_year_Restrictive_Trade_Practices else 0,
                            "Remarks_rtp_current":current_year_Restrictive_Trade_Practices.Remarks if current_year_Restrictive_Trade_Practices and current_year_Restrictive_Trade_Practices.Remarks else "NA",

                            "Received_During_The_Year_rtp_previous":previous_year_Restrictive_Trade_Practices.Received_During_The_Year if previous_year_Restrictive_Trade_Practices else 0,
                            "Pending_Resolution_At_End_Of_The_Year_rtp_previous":previous_year_Restrictive_Trade_Practices.Pending_Resolution_At_End_Of_The_Year if previous_year_Restrictive_Trade_Practices else 0,
                            "Remarks_rtp_previous":previous_year_Restrictive_Trade_Practices.Remarks if previous_year_Restrictive_Trade_Practices and  previous_year_Restrictive_Trade_Practices.Remarks else "NA",
                       } ],

            # Data for Unfair Trade Practices
            "Principle_9_EI_3_UTP": [{
                            "Received_During_The_Year_utp_current": current_year_Unfair_Trade_Practices.Received_During_The_Year if current_year_Unfair_Trade_Practices else 0,
                            "Pending_Resolution_At_End_Of_The_Year_utp_current":current_year_Unfair_Trade_Practices.Pending_Resolution_At_End_Of_The_Year if current_year_Unfair_Trade_Practices else 0,
                            "Remarks_utp_current":current_year_Unfair_Trade_Practices.Remarks if current_year_Unfair_Trade_Practices and  current_year_Unfair_Trade_Practices.Remarks  else "NA",

                            "Received_During_The_Year_utp_previous":previous_year_Unfair_Trade_Practices.Received_During_The_Year if previous_year_Unfair_Trade_Practices else 0,
                            "Pending_Resolution_At_End_Of_The_Year_utp_previous": previous_year_Unfair_Trade_Practices.Pending_Resolution_At_End_Of_The_Year if previous_year_Unfair_Trade_Practices else 0,
                            "Remarks_utp_previous":previous_year_Unfair_Trade_Practices.Remarks if previous_year_Unfair_Trade_Practices and previous_year_Unfair_Trade_Practices.Remarks else "NA",
                        }],

            # Data for Other
            "Principle_9_EI_3_Other": [{
                            "Received_During_The_Year_other_current":current_year_Other.Received_During_The_Year if current_year_Other else 0,
                            "Pending_Resolution_At_End_Of_The_Year_other_current":current_year_Other.Pending_Resolution_At_End_Of_The_Year if current_year_Other else 0,
                            "Remarks_other_current":current_year_Other.Remarks if current_year_Other and  current_year_Other.Remarks else "NA",

                            "Received_During_The_Year_other_previous":previous_year_Other.Received_During_The_Year if previous_year_Other else 0,
                            "Pending_Resolution_At_End_Of_The_Year_other_previous":previous_year_Other.Pending_Resolution_At_End_Of_The_Year if previous_year_Other else 0,
                            "Remarks_other_previous":previous_year_Other.Remarks if previous_year_Other and previous_year_Other.Remarks else "NA",
                        }],

            
            
            
            "Principle_9_EI_4_VR": [{
                "Number":Volunatry_Recalls.Number if Volunatry_Recalls else 0,
                "Reasons_For_Recall":Volunatry_Recalls.Reasons_For_Recall if Volunatry_Recalls else 0,
                                 
            }],
            
            "Principle_9_EI_4_FR": [{
               "Forced_Recalls_Numbers": Forced_Recalls.Number if Forced_Recalls else 0,
               "Forced_Recalls_Reasons": Forced_Recalls.Reasons_For_Recall if Forced_Recalls else 0,
                    
               
            }],
            "Principle_9_EI_5": [{
                "Is_Verified_EI_5":description_obj_cd.Is_Verified if description_obj_cd else "-",
                "Description_consumer_EI_5":description_obj_cd.Description_consumer if description_obj_cd else "-",
            }],
            "Principle_9_EI_6": [{"description_obj_cd1":description_obj_cd1.Description_consumer if description_obj_cd1 else "-"}],
            
            "Principle_9_EI_7a": [{"Number_Of_Instances_Of_Data_Breaches":Number_Of_Instances_Of_Data_Breaches}],
            "Principle_9_EI_7b": [{"Percent_Of_Customers_Affected_By_Data_Breaches":Percent_Of_Customers_Affected_By_Data_Breaches}],
            "Principle_9_EI_7c": [{"impact":impact}],
        
            "Principle_9_LI_1": [{"description_obj_lcd1":description_obj_lcd1.Description_consumer if description_obj_lcd1 else "-"}],
            "Principle_9_LI_2": [{"description_obj_lcd2":description_obj_lcd2.Description_consumer if description_obj_lcd2 else "-"}],
            "Principle_9_LI_3": [{"description_obj_lcd3":description_obj_lcd3.Description_consumer if description_obj_lcd3 else "-"}],
            "Principle_9_LI_4a": [{
                "Is_Verified_LI_4a":description_obj_lcd4.Is_Verified if description_obj_lcd4 else "-",
                "Description_consumer_LI_4a":description_obj_lcd4.Description_consumer if description_obj_lcd4 else "-",
            }],
            "Principle_9_LI_4B": [{
               "Is_Verified_LI_4B": description_obj_lcd5.Is_Verified if description_obj_lcd5 else "-",
                "Description_consumer_LI_4B":description_obj_lcd5.Description_consumer if description_obj_lcd5 else "-",
            }]
            
        })

            Brs_log = {
                "Financial_Year":financial_year,
                "Section":"Principle 9",
                "User_Name":f"{request.user.firstname} {request.user.lastname}"
               
            }
                            
            brs_log_serializer = BRS_Report_LogSerializer(data=Brs_log)
            if brs_log_serializer.is_valid():
                brs_log_serializer.save()
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Data Not Available in Principle_9"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except APIException as e:
            return Response(
                {"error": f"APIException in Principle_9: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TypeError as e:
            return Response(
                {"error": f"TypeError in Principle_9: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Unknown error in Principle_9: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
