from Workplace.models import *
from django.db.models import Count, Avg, F
from Environment.models import Air_Emissions_Other_Than_GHG_Emissions, Concerns_and_Action, End_of_Life_of_Product, Percentage_Of_R_and_D_and_Capex_Investments, Reclaimed_Products_and_Packaging
from Environment.models import *

import decimal

from decimal import Decimal
from django.db.models import Sum
from datetime import datetime 

def calculate_air_emissions_totals(financial_year, previous_financial_year):
    parameters = [
        "Nox", 
        "Sox", 
        "Particular Matter", 
        "Persistent Organic Pollutants", 
        "Volatile Organic Compounds", 
        "Hazardous Air Pollutant", 
        "Others"
    ]

    parameter_keys = {
        "Nox": "EI6_A",
        "Sox": "EI6_B",
        "Particular Matter": "EI6_C",
        "Persistent Organic Pollutants": "EI6_D",
        "Volatile Organic Compounds": "EI6_E",
        "Hazardous Air Pollutant": "EI6_F",
        "Others": "EI6_G"
    }

    air_emissions_unit = {
        "Nox": "mg/NM³",
        "Sox": "Kg/day",
        "Particular Matter": "mg/NM³",
        "Persistent Organic Pollutants": "mg/NM³",
        "Volatile Organic Compounds": "mg/NM³",
        "Hazardous Air Pollutant": "mg/NM³",
        "Others": "NA"
    }

    ei6_totals = {}

    for parameter in parameters:
        current_year_records = Air_Emissions_Other_Than_GHG_Emissions.objects.filter(
            Financial_Year=financial_year,
            Parameter=parameter
        )
        previous_year_records = Air_Emissions_Other_Than_GHG_Emissions.objects.filter(
            Financial_Year=previous_financial_year,
            Parameter=parameter
        )
        
        current_total = sum(float(record.Total_Air_Emission.to_decimal()) for record in current_year_records)
        previous_total = sum(float(record.Total_Air_Emission.to_decimal()) for record in previous_year_records)

        current_total_rounded = round(current_total, 2)
        previous_total_rounded = round(previous_total, 2)       
        
        key = parameter_keys.get(parameter)
        unit = air_emissions_unit.get(parameter)
        if key:
            ei6_totals[key] = [unit, current_total_rounded if current_total_rounded else "NA",
                               previous_total_rounded if previous_total_rounded else "NA"]

    return ei6_totals


def calculate_section_A_20_a_employees_data(financial_year):
    try:
        employee_summary_json = {}
        employee_summary_obj = EmployeeSummary.objects.filter(Financial_Year=financial_year)

        if employee_summary_obj.count() > 0:
            male_permanent = Decimal(0)
            male_non_permanent = Decimal(0)
            female_permanent = Decimal(0)
            female_non_permanent = Decimal(0)

            for obj in employee_summary_obj:
                male_permanent += obj.Male_Permanent.to_decimal()
                male_non_permanent += obj.Male_Non_Permanent.to_decimal()
                female_permanent += obj.Female_Permanent.to_decimal()
                female_non_permanent += obj.Female_Non_Permanent.to_decimal()

            # Round all the values to 2 decimal places before adding them to the JSON
            employee_summary_json["male_permanent"] = round(float(male_permanent), 2)
            employee_summary_json["male_non_permanent"] = round(float(male_non_permanent), 2)
            employee_summary_json["female_permanent"] = round(float(female_permanent), 2)
            employee_summary_json["female_non_permanent"] = round(float(female_non_permanent), 2)

            total_permanent = male_permanent + female_permanent
            total_non_permanent = male_non_permanent + female_non_permanent
            total_employees = total_permanent + total_non_permanent

            employee_summary_json["total_permanent"] = round(float(total_permanent), 2)
            employee_summary_json["total_non_permanent"] = round(float(total_non_permanent), 2)
            employee_summary_json["total_employees"] = round(float(total_employees), 2)

            total_male = male_permanent + male_non_permanent
            employee_summary_json["total_male"] = round(float(total_male), 2)

            employee_summary_json["male_permanent_percent"] = round(float(male_permanent / total_permanent) * 100, 2) if total_permanent else 0
            employee_summary_json["male_non_permanent_percent"] = round(float(male_non_permanent / total_non_permanent) * 100, 2) if total_non_permanent else 0
            # if total_permanent > 0:
            #     employee_summary_json["male_permanent_percent"] = round(float(male_permanent / total_permanent) * 100, 2)
            #     employee_summary_json["male_non_permanent_percent"] = round(float(male_non_permanent / total_non_permanent) * 100, 2)
            # else:
            #     employee_summary_json["male_permanent_percent"] = 0.00
            #     employee_summary_json["male_non_permanent_percent"] = 0.00

            if total_employees > 0:
                employee_summary_json["male_total_percent"] = round(float(total_male / total_employees) * 100, 2)
            else:
                employee_summary_json["male_total_percent"] = 0.00

            total_female = female_permanent + female_non_permanent
            employee_summary_json["total_female"] = round(float(total_female), 2)
            employee_summary_json["female_permanent_percent"] = round(float(female_permanent / total_permanent) * 100, 2) if total_permanent else 0
            employee_summary_json["female_non_permanent_percent"] = round(float(female_non_permanent / total_non_permanent) * 100, 2) if total_non_permanent else 0
            # if total_permanent > 0:
            #     employee_summary_json["female_permanent_percent"] = round(float(female_permanent / total_permanent) * 100, 2)
            #     employee_summary_json["female_non_permanent_percent"] = round(float(female_non_permanent / total_non_permanent) * 100, 2)
            # else:
            #     employee_summary_json["female_permanent_percent"] = 0.00
            #     employee_summary_json["female_non_permanent_percent"] = 0.00
            employee_summary_json["female_total_percent"] = round(float(total_female / total_employees) * 100, 2) if total_employees else 0

            # if total_employees > 0:
            #     employee_summary_json["female_total_percent"] = round(float(total_female / total_employees) * 100, 2)
            # else:
            #     employee_summary_json["female_total_percent"] = 0.00
        else:
            employee_summary_json = {'male_permanent': 0.00, 
                                     'male_non_permanent': 0.00, 
                                     'female_permanent': 0.00, 
                                     'female_non_permanent': 0.00, 
                                     'total_permanent': 0.00, 
                                     'total_non_permanent': 0.00, 
                                     'total_employees': 0.00, 
                                     'total_male': 0.00, 
                                     'male_permanent_percent': 0.00, 
                                     'male_non_permanent_percent': 0.00, 
                                     'male_total_percent': 0.00, 
                                     'total_female': 0.00, 
                                     'female_permanent_percent': 0.00, 
                                     'female_non_permanent_percent': 0.00, 
                                     'female_total_percent': 0.00}

        return employee_summary_json

    except Exception as e:
                print(f"An error occurred: {str(e)}")



def calculate_section_A_20_a_workers_data(financial_year):
    try:
        worker_summary_json = {}
        worker_summary_obj = WorkerSummary.objects.filter(Financial_Year=financial_year)

        if worker_summary_obj.count() > 0:
            male_permanent = Decimal(0)
            male_non_permanent = Decimal(0)
            female_permanent = Decimal(0)
            female_non_permanent = Decimal(0)

            for obj in worker_summary_obj:
                male_permanent += obj.Male_Permanent.to_decimal()
                male_non_permanent += obj.Male_Non_Permanent.to_decimal()
                female_permanent += obj.Female_Permanent.to_decimal()
                female_non_permanent += obj.Female_Non_Permanent.to_decimal()

            # Round all the values to 2 decimal places before adding them to the JSON
            worker_summary_json["male_permanent"] = round(float(male_permanent), 2)
            worker_summary_json["male_non_permanent"] = round(float(male_non_permanent), 2)
            worker_summary_json["female_permanent"] = round(float(female_permanent), 2)
            worker_summary_json["female_non_permanent"] = round(float(female_non_permanent), 2)

            total_permanent = male_permanent + female_permanent
            total_non_permanent = male_non_permanent + female_non_permanent
            total_employees = total_permanent + total_non_permanent

            worker_summary_json["total_permanent"] = round(float(total_permanent), 2)
            worker_summary_json["total_non_permanent"] = round(float(total_non_permanent), 2)
            worker_summary_json["total_workers"] = round(float(total_employees), 2)

            total_male = male_permanent + male_non_permanent
            worker_summary_json["total_male"] = round(float(total_male), 2)

            worker_summary_json["male_permanent_percent"] = round(float(male_permanent / total_permanent) * 100, 2) if total_permanent else 0
            worker_summary_json["male_non_permanent_percent"] = round(float(male_non_permanent / total_non_permanent) * 100, 2) if total_non_permanent else 0
            
            # if total_permanent > 0:
            #     worker_summary_json["male_permanent_percent"] = round(float(male_permanent / total_permanent) * 100, 2)
            #     worker_summary_json["male_non_permanent_percent"] = round(float(male_non_permanent / total_non_permanent) * 100, 2)
            # else:
            #     worker_summary_json["male_permanent_percent"] = 0.00
            #     worker_summary_json["male_non_permanent_percent"] = 0.00

            worker_summary_json["male_total_percent"] = round(float(total_male / total_employees) * 100, 2) if total_employees else 0
            # if total_employees > 0:
            #     worker_summary_json["male_total_percent"] = round(float(total_male / total_employees) * 100, 2)
            # else:
            #     worker_summary_json["male_total_percent"] = 0.00

            total_female = female_permanent + female_non_permanent
            worker_summary_json["total_female"] = round(float(total_female), 2)

            worker_summary_json["female_permanent_percent"] = round(float(female_permanent / total_permanent) * 100, 2) if total_permanent else 0
            worker_summary_json["female_non_permanent_percent"] = round(float(female_non_permanent / total_non_permanent) * 100, 2) if total_non_permanent else 0
            
            # if total_permanent > 0:
            #     worker_summary_json["female_permanent_percent"] = round(float(female_permanent / total_permanent) * 100, 2)
            #     worker_summary_json["female_non_permanent_percent"] = round(float(female_non_permanent / total_non_permanent) * 100, 2)
            # else:
            #     worker_summary_json["female_permanent_percent"] = 0.00
            #     worker_summary_json["female_non_permanent_percent"] = 0.00

            worker_summary_json["female_total_percent"] = round(float(total_female / total_employees) * 100, 2) if total_employees else 0
            # if total_employees > 0:
            #     worker_summary_json["female_total_percent"] = round(float(total_female / total_employees) * 100, 2)
            # else:
            #     worker_summary_json["female_total_percent"] = 0.00
        else:
            worker_summary_json = {'male_permanent': 0.00, 
                                     'male_non_permanent': 0.00, 
                                     'female_permanent': 0.00, 
                                     'female_non_permanent': 0.00, 
                                     'total_permanent': 0.00, 
                                     'total_non_permanent': 0.00, 
                                     'total_workers': 0.00, 
                                     'total_male': 0.00, 
                                     'male_permanent_percent': 0.00, 
                                     'male_non_permanent_percent': 0.00, 
                                     'male_total_percent': 0.00, 
                                     'total_female': 0.00, 
                                     'female_permanent_percent': 0.00, 
                                     'female_non_permanent_percent': 0.00, 
                                     'female_total_percent': 0.00}

        return worker_summary_json
    except Exception as e:
                print(f"An error occurred: {str(e)}")



def calculate_section_A_20_b_differently_abled_employees_data(financial_year):
    def get_total_diff_abled_employees(financial_year, type, gender):
        diff_abled_employees_obj = Differently_Abled_Employees.objects.filter(Financial_Year=financial_year, Type=type, Gender=gender)
        total = Decimal(0)
        for obj in diff_abled_employees_obj:
            total += obj.Total_Differently_Abled_Employees.to_decimal()
        return float(total)
    
    # Calculate totals
    permanent_male = get_total_diff_abled_employees(financial_year, "Permanent", "Male")
    non_permanent_male = get_total_diff_abled_employees(financial_year, "Non-Permanent", "Male")
    permanent_female = get_total_diff_abled_employees(financial_year, "Permanent", "Female")
    non_permanent_female = get_total_diff_abled_employees(financial_year, "Non-Permanent", "Female")

    total_permanent = permanent_male + permanent_female
    total_non_permanent = non_permanent_male + non_permanent_female
    total_employees = total_permanent + total_non_permanent
    total_male = permanent_male + non_permanent_male
    total_female = permanent_female + non_permanent_female

    # Calculate percentages
    permanent_male_percent = round(permanent_male / total_permanent * 100, 2) if total_permanent else 0
    non_permanent_male_percent = round(non_permanent_male / total_non_permanent * 100, 2) if total_non_permanent else 0
    total_male_percent = round(total_male / total_employees* 100, 2) if total_employees else 0

    permanent_female_percent = round(permanent_female / total_permanent * 100, 2) if total_permanent else 0
    non_permanent_female_percent = round(non_permanent_female / total_non_permanent * 100, 2) if total_non_permanent else 0
    total_female_percent = round(total_female / total_employees* 100, 2) if total_employees else 0

    # Construct the JSON response
    employee_json = {
        "Total_Permanent": round(total_permanent, 2) if total_permanent else 0,
        "Total_Non_Permanent": round(total_non_permanent, 2) if total_non_permanent else 0,
        "Total_Employees": round(total_employees, 2) if total_employees else 0,
        "Permanent_Male": round(permanent_male, 2) if permanent_male else 0,
        "Non_Permanent_Male": round(non_permanent_male, 2) if non_permanent_male else 0,
        "Total_Male": round(total_male, 2) if total_male else 0,
        "Permanent_Male_Percent": permanent_male_percent,
        "Non_Permanent_Male_Percent": non_permanent_male_percent,
        "Total_Male_Percent": total_male_percent,
        "Permanent_Female": round(permanent_female, 2) if permanent_female else 0,
        "Non_Permanent_Female": round(non_permanent_female, 2) if non_permanent_female else 0,
        "Total_Female": round(total_female, 2) if total_female else 0,
        "Permanent_Female_Percent": permanent_female_percent,
        "Non_Permanent_Female_Percent": non_permanent_female_percent,
        "Total_Female_Percent": total_female_percent,
    }

    return employee_json



def calculate_section_A_20_b_differently_abled_workers_data(financial_year):
    def get_total_diff_abled_workers(financial_year, type, gender):
        diff_abled_workers_obj = Differently_Abled_Workers.objects.filter(Financial_Year=financial_year, Type=type, Gender=gender)
        total = Decimal(0)
        for obj in diff_abled_workers_obj:
            total += obj.Total_Differently_Abled_Workers.to_decimal()
        return float(total)
    
    # Calculate totals
    permanent_male = get_total_diff_abled_workers(financial_year, "Permanent", "Male")
    non_permanent_male = get_total_diff_abled_workers(financial_year, "Non-Permanent", "Male")
    permanent_female = get_total_diff_abled_workers(financial_year, "Permanent", "Female")
    non_permanent_female = get_total_diff_abled_workers(financial_year, "Non-Permanent", "Female")

    total_permanent = permanent_male + permanent_female
    total_non_permanent = non_permanent_male + non_permanent_female
    total_employees = total_permanent + total_non_permanent
    total_male = permanent_male + non_permanent_male
    total_female = permanent_female + non_permanent_female

    # Calculate percentages
    permanent_male_percent = round(permanent_male / total_permanent * 100, 2) if total_permanent else 0
    non_permanent_male_percent = round(non_permanent_male / total_non_permanent * 100, 2) if total_non_permanent else 0
    total_male_percent = round(total_male / total_employees* 100, 2) if total_employees else 0

    permanent_female_percent = round(permanent_female / total_permanent * 100, 2) if total_permanent else 0
    non_permanent_female_percent = round(non_permanent_female / total_non_permanent * 100, 2) if total_non_permanent else 0
    total_female_percent = round(total_female / total_employees* 100, 2) if total_employees else 0

    # Construct the JSON response
    worker_json = {
        "Total_Permanent": round(total_permanent, 2) if total_permanent else 0,
        "Total_Non_Permanent": round(total_non_permanent, 2) if total_non_permanent else 0,
        "Total_Employees": round(total_employees, 2) if total_employees else 0,

        "Permanent_Male": round(permanent_male, 2) if permanent_male else 0,
        "Non_Permanent_Male": round(non_permanent_male, 2) if non_permanent_male else 0,
        "Total_Male": round(total_male, 2) if total_male else 0,

        "Permanent_Male_Percent": permanent_male_percent if permanent_male_percent else 0,
        "Non_Permanent_Male_Percent": non_permanent_male_percent,
        "Total_Male_Percent": total_male_percent,
        
        "Permanent_Female": round(permanent_female, 2) if permanent_female else 0,
        "Non_Permanent_Female": round(non_permanent_female, 2) if non_permanent_female else 0,
        "Total_Female": round(total_female, 2) if total_female else 0,
        
        "Permanent_Female_Percent": permanent_female_percent,
        "Non_Permanent_Female_Percent": non_permanent_female_percent,
        "Total_Female_Percent": total_female_percent
    }

    return worker_json


def calculate_section_A_21_Management(financial_year):
    # Calculate total board of directors
    board_of_directors_obj = Management_Board_of_Directors.objects.filter(Financial_Year=financial_year)
    total_board_of_directors = sum(obj.Total_Board_of_Directors.to_decimal() for obj in board_of_directors_obj)

    # Calculate total female board of directors
    board_of_directors_female_obj = Management_Board_of_Directors.objects.filter(Financial_Year=financial_year, Gender="Female")
    total_board_of_directors_female = sum(obj.Total_Board_of_Directors.to_decimal() for obj in board_of_directors_female_obj)

    # Calculate percentage of females on the board
    percent_board_of_directors_females = (float(total_board_of_directors_female) / float(total_board_of_directors)) * 100 if total_board_of_directors else 0


    # Calculate total key management personnel
    key_management_personnel_obj = Key_Management_Personnel.objects.filter(Financial_Year=financial_year)
    total_key_management_personnel = sum(obj.Total_Key_Management_Personnel.to_decimal() for obj in key_management_personnel_obj)

    # Calculate total female key management personnel
    key_management_personnel_female_obj = Key_Management_Personnel.objects.filter(Financial_Year=financial_year, Gender="Female")
    total_key_management_personnel_female = sum(obj.Total_Key_Management_Personnel.to_decimal() for obj in key_management_personnel_female_obj)

    # Calculate percentage of females
    percent_key_management_personnel_females = (float(total_key_management_personnel_female) / float(total_key_management_personnel)) * 100 if total_key_management_personnel else 0

    record_json = {}
    record_json["Total_Board_of_Directors"] = round(float(total_board_of_directors), 2)
    record_json["Board_of_Directors_Female"] = round(float(total_board_of_directors_female), 2)
    record_json["Percent_Board_of_Directors_Females"] = round(float(percent_board_of_directors_females), 2)

    record_json["Total_Key_Management_Personnel"] = round(float(total_key_management_personnel), 2)
    record_json["Key_Management_Personnel_Female"] = round(float(total_key_management_personnel_female), 2)
    record_json["Percent_Key_Management_Personnel_Females"] = round(float(percent_key_management_personnel_females), 2)

    return record_json
    


def calculate_section_C_EI_3(financial_year):
    record_json = {}
    try:
        details_of_appeal_obj = Details_of_the_appeal.objects.filter(Financial_Year=financial_year).first()
        if details_of_appeal_obj:
            record_json["Case_Details"] = details_of_appeal_obj.Case_details or "-"
            record_json["Name_of_Agencies"] = details_of_appeal_obj.Name_of_agency or "-"
        else:
            record_json["Case_Details"] = "-"
            record_json["Name_of_Agencies"] = "-"
    except Exception:
        record_json["Case_Details"] = "-"
        record_json["Name_of_Agencies"] = "-"
    return record_json



def calculate_section_C_EI_5(financial_year, previous_financial_year):
    record_json = {}
    
    try:
        disciplinary_action_obj1 = Disciplinary_Action_Against_For_curruption.objects.filter(
            Financial_Year=financial_year
        ).first()

        current_year_directors = disciplinary_action_obj1.BOD if disciplinary_action_obj1 else 0
        current_year_kmp = disciplinary_action_obj1.KMPs if disciplinary_action_obj1 else 0
        current_year_employees = disciplinary_action_obj1.EMPLOYEES if disciplinary_action_obj1 else 0
        current_year_workers = disciplinary_action_obj1.WORKERS if disciplinary_action_obj1 else 0
    except Exception:
        current_year_directors = 0
        current_year_kmp = 0
        current_year_employees = 0
        current_year_workers = 0

    try:
        disciplinary_action_obj2 = Disciplinary_Action_Against_For_curruption.objects.filter(
            Financial_Year=previous_financial_year
        ).first()

        previous_year_directors = disciplinary_action_obj2.BOD if disciplinary_action_obj2 else 0
        previous_year_kmp = disciplinary_action_obj2.KMPs if disciplinary_action_obj2 else 0
        previous_year_employees = disciplinary_action_obj2.EMPLOYEES if disciplinary_action_obj2 else 0
        previous_year_workers = disciplinary_action_obj2.WORKERS if disciplinary_action_obj2 else 0
    except Exception:
        previous_year_directors = 0
        previous_year_kmp = 0
        previous_year_employees = 0
        previous_year_workers = 0

    record_json["Current_Year_Directors"] = current_year_directors
    record_json["Current_Year_KMPs"] = current_year_kmp
    record_json["Current_Year_Employees"] = current_year_employees
    record_json["Current_Year_Workers"] = current_year_workers
    record_json["Previous_Year_Directors"] = previous_year_directors
    record_json["Previous_Year_KMPs"] = previous_year_kmp
    record_json["Previous_Year_Employees"] = previous_year_employees
    record_json["Previous_Year_Workers"] = previous_year_workers

    return record_json



def calculate_principle_2_LI_1(financial_year):
    obj1 = Life_Cycle_Perspective_Assessments.objects.filter(Year_of_Assessment=financial_year).first()
    record_json = {}
    if obj1:
        nic_code = obj1.NIC_Code
        name_of_product_service = obj1.Product_Service
        percent_total_turnover = obj1.Percent_of_Turnover_Contributed
        boundary_for_assessment = obj1.Boundary_for_Assessment
        conducted_by_external_agency = obj1.Conducted_by_External_Agency
        url_of_published_results = obj1.URL_of_Published_Results
        description_assessment = obj1.Description_Assessment
    else:
        nic_code = "-"
        name_of_product_service = "-"
        percent_total_turnover = "-"
        boundary_for_assessment = "-"
        conducted_by_external_agency = "-"
        url_of_published_results = "-"
        description_assessment = "-"

    record_json["NIC_Code"] = nic_code
    record_json["Name_of_Product_Service"] = name_of_product_service
    record_json["Percent_of_Turnover_Contributed"] = percent_total_turnover
    record_json["Boundary_for_Assessment"] = boundary_for_assessment
    record_json["Conducted_by_External_Agency"] = conducted_by_external_agency
    record_json["URL_of_Published_Results"] = url_of_published_results
    record_json["Description_Assessment"] = description_assessment


    return record_json


def calculate_principle_2_LI_2(financial_year):
    concerns_and_actions_obj = Concerns_and_Action.objects.filter(Financial_Year=financial_year).first()
    if concerns_and_actions_obj:
        name_of_product_service = concerns_and_actions_obj.Product_Service
        description = concerns_and_actions_obj.Risk_Concern_in_Assessment
        action_taken = concerns_and_actions_obj.Corrective_Action_Taken
        description_action = concerns_and_actions_obj.Description_Concern
    else:
        name_of_product_service = "-"
        description = "-"
        action_taken = "-"
        description_action = "-"

    record_json = {}
    record_json["Name_of_Product_Service"] = name_of_product_service
    record_json["Description"] = description
    record_json["Action_Taken"] = action_taken
    record_json["Description_Concern"] = description_action

    return record_json


def calculate_principle_2_LI_4_OLD(financial_year, previous_financial_year):
    end_of_life_of_product_obj1 = End_of_Life_of_Product.objects.filter(Financial_Year=financial_year).first()
    if end_of_life_of_product_obj1:
        current_year_plastic_reused = end_of_life_of_product_obj1.Plastic_Reused
        current_year_plastic_recycled = end_of_life_of_product_obj1.Plastic_Recycled
        current_year_plastic_disposed = end_of_life_of_product_obj1.Plastic_Disposed
        current_year_e_waste_reused = end_of_life_of_product_obj1.E_Waste_Reused
        current_year_e_waste_recycled = end_of_life_of_product_obj1.E_Waste_Recycled
        current_year_e_waste_disposed = end_of_life_of_product_obj1.E_Waste_Disposed
        current_year_hazardous_waste_reused = end_of_life_of_product_obj1.Hazardous_Waste_Reused
        current_year_hazardous_waste_recycled = end_of_life_of_product_obj1.Hazardous_Waste_Recycled
        current_year_hazardous_waste_disposed = end_of_life_of_product_obj1.Hazardous_Waste_Disposed
        current_year_other_waste_reused = end_of_life_of_product_obj1.Other_Waste_Reused
        current_year_other_waste_recycled = end_of_life_of_product_obj1.Other_Waste_Recycled
        current_year_other_waste_disposed = end_of_life_of_product_obj1.Other_Waste_Disposed
    else:
        current_year_plastic_reused = "-"
        current_year_plastic_recycled = "-"
        current_year_plastic_disposed = "-"
        current_year_e_waste_reused = "-"
        current_year_e_waste_recycled = "-"
        current_year_e_waste_disposed = "-"
        current_year_hazardous_waste_reused = "-"
        current_year_hazardous_waste_recycled = "-"
        current_year_hazardous_waste_disposed = "-"
        current_year_other_waste_reused = "-"
        current_year_other_waste_recycled = "-"
        current_year_other_waste_disposed = "-"

    end_of_life_of_product_obj2 = End_of_Life_of_Product.objects.filter(Financial_Year=previous_financial_year).first()
    if end_of_life_of_product_obj2:
        previous_year_plastic_reused = end_of_life_of_product_obj2.Plastic_Reused
        previous_year_plastic_recycled = end_of_life_of_product_obj2.Plastic_Recycled
        previous_year_plastic_disposed = end_of_life_of_product_obj2.Plastic_Disposed
        previous_year_e_waste_reused = end_of_life_of_product_obj2.E_Waste_Reused
        previous_year_e_waste_recycled = end_of_life_of_product_obj2.E_Waste_Recycled
        previous_year_e_waste_disposed = end_of_life_of_product_obj2.E_Waste_Disposed
        previous_year_hazardous_waste_reused = end_of_life_of_product_obj2.Hazardous_Waste_Reused
        previous_year_hazardous_waste_recycled = end_of_life_of_product_obj2.Hazardous_Waste_Recycled
        previous_year_hazardous_waste_disposed = end_of_life_of_product_obj2.Hazardous_Waste_Disposed
        previous_year_other_waste_reused = end_of_life_of_product_obj2.Other_Waste_Reused
        previous_year_other_waste_recycled = end_of_life_of_product_obj2.Other_Waste_Recycled
        previous_year_other_waste_disposed = end_of_life_of_product_obj2.Other_Waste_Disposed
    else:
        previous_year_plastic_reused = "-"
        previous_year_plastic_recycled = "-"
        previous_year_plastic_disposed = "-"
        previous_year_e_waste_reused = "-"
        previous_year_e_waste_recycled = "-"
        previous_year_e_waste_disposed = "-"
        previous_year_hazardous_waste_reused = "-"
        previous_year_hazardous_waste_recycled = "-"
        previous_year_hazardous_waste_disposed = "-"
        previous_year_other_waste_reused = "-"
        previous_year_other_waste_recycled = "-"
        previous_year_other_waste_disposed = "-"


    record_json = {}
    record_json["Current_Year_Plastic_Reused"] = current_year_plastic_reused
    record_json["Current_Year_Plastic_Recycled"] = current_year_plastic_recycled
    record_json["Current_Year_Plastic_Disposed"] = current_year_plastic_disposed
    record_json["Current_Year_E_Waste_Reused"] = current_year_e_waste_reused
    record_json["Current_Year_E_Waste_Recycled"] = current_year_e_waste_recycled
    record_json["Current_Year_E_Waste_Disposed"] = current_year_e_waste_disposed
    record_json["Current_Year_Hazardous_Waste_Reused"] = current_year_hazardous_waste_reused
    record_json["Current_Year_Hazardous_Waste_Recycled"] = current_year_hazardous_waste_recycled
    record_json["Current_Year_Hazardous_Waste_Disposed"] = current_year_hazardous_waste_disposed
    record_json["Current_Year_Other_Waste_Reused"] = current_year_other_waste_reused
    record_json["Current_Year_Other_Waste_Recycled"] = current_year_other_waste_recycled
    record_json["Current_Year_Other_Waste_Disposed"] = current_year_other_waste_disposed
    
    record_json["Previous_Year_Plastic_Reused"] = previous_year_plastic_reused
    record_json["Previous_Year_Plastic_Recycled"] = previous_year_plastic_recycled
    record_json["Previous_Year_Plastic_Disposed"] = previous_year_plastic_disposed
    record_json["Previous_Year_E_Waste_Reused"] = previous_year_e_waste_reused
    record_json["Previous_Year_E_Waste_Recycled"] = previous_year_e_waste_recycled
    record_json["Previous_Year_E_Waste_Disposed"] = previous_year_e_waste_disposed
    record_json["Previous_Year_Hazardous_Waste_Reused"] = previous_year_hazardous_waste_reused
    record_json["Previous_Year_Hazardous_Waste_Recycled"] = previous_year_hazardous_waste_recycled
    record_json["Previous_Year_Hazardous_Waste_Disposed"] = previous_year_hazardous_waste_disposed
    record_json["Previous_Year_Other_Waste_Reused"] = previous_year_other_waste_reused
    record_json["Previous_Year_Other_Waste_Recycled"] = previous_year_other_waste_recycled
    record_json["Previous_Year_Other_Waste_Disposed"] = previous_year_other_waste_disposed

    return record_json


def calculate_principle_2_LI_4(financial_year, previous_financial_year):
    def get_values_or_default(obj, fields):
        """Helper function to get float values or default to '-'."""
        return {field: float(getattr(obj, field).to_decimal()) if obj and getattr(obj, field) is not None else "-" for field in fields}

    fields = [
        "Plastic_Reused", "Plastic_Recycled", "Plastic_Disposed",
        "E_Waste_Reused", "E_Waste_Recycled", "E_Waste_Disposed",
        "Hazardous_Waste_Reused", "Hazardous_Waste_Recycled", "Hazardous_Waste_Disposed",
        "Other_Waste_Reused", "Other_Waste_Recycled", "Other_Waste_Disposed"
    ]

    # Fetching the current year's data
    end_of_life_of_product_obj1 = End_of_Life_of_Product.objects.filter(Financial_Year=financial_year).first()
    current_year_data = get_values_or_default(end_of_life_of_product_obj1, fields)

    # Fetching the previous year's data
    end_of_life_of_product_obj2 = End_of_Life_of_Product.objects.filter(Financial_Year=previous_financial_year).first()
    previous_year_data = get_values_or_default(end_of_life_of_product_obj2, fields)

    # Combining current and previous year data into a single dictionary
    record_json = {
        f"Current_Year_{field}": current_year_data[field] for field in fields
    }
    record_json.update({
        f"Previous_Year_{field}": previous_year_data[field] for field in fields
    })

    return record_json



def calculate_principle_2_LI_5(financial_year):
    # Fetch the first object that matches the financial year
    obj = Reclaimed_Products_and_Packaging.objects.filter(Financial_Year=financial_year).first()
    
    # Initialize the dictionary with default values
    record_json = {
        "Product_Category": "-",
        "Percent_of_Reclaimed": "-"
    }
    
    # If the object exists, update the dictionary with actual values
    if obj:
        record_json["Product_Category"] = obj.Product_Category
        record_json["Percent_of_Reclaimed"] = float(obj.Percent_of_Reclaimed.to_decimal()) if obj.Percent_of_Reclaimed is not None else "-"

    return record_json


def calculate_section_C_Principle_1_LI_1(financial_year):
    # Query to get all awareness programmes for the given financial year
    awareness_programmes_qs = Awareness_Programmes_On_ESG.objects.filter(Financial_Year=financial_year)

    # Initialize the JSON response dictionary
    awareness_programmes_json = {
        "Topics_and_Percent_Age": [],
        "Total_Number_of_Programmes_Held": 0
    }

    # Iterate through each programme and accumulate data
    for programme in awareness_programmes_qs:
        # Append each programme's details to the result list
        awareness_programmes_json["Topics_and_Percent_Age"].append({
            "Topics_Covered": programme.Topics_Covered,
            "Percentage_Of_Persons": float(programme.Percentage_Of_Persons.to_decimal())
        })

        # Increment the total number of programmes held
        awareness_programmes_json["Total_Number_of_Programmes_Held"] += programme.Total_No_Of_Programmes_Held

    return awareness_programmes_json


def get_totals(financial_year, segment, emp_type):
    # Initialize totals for employees
    total_male_permanent_employees = 0
    total_female_permanent_employees = 0
    total_male_non_permanent_employees = 0
    total_female_non_permanent_employees = 0

    # Initialize totals for workers
    total_male_permanent_worker = 0
    total_female_permanent_worker = 0
    total_male_non_permanent_worker = 0
    total_female_non_permanent_worker = 0
    
    # Initialize wellbeing measures totals
    total_males_health_insurance = 0
    total_females_health_insurance = 0
    total_males_accident_insurance = 0
    total_females_accident_insurance = 0
    total_males_maternity_benefits = 0
    total_females_maternity_benefits = 0
    total_males_paternity_benefits = 0
    total_females_paternity_benefits = 0
    total_males_day_care_facilities = 0
    total_females_day_care_facilities = 0

    response=""
    # Check the segment type
    if segment == "Employees":
        employee_records = EmployeeSummary.objects.filter(Financial_Year=financial_year)

        # Calculate total number of male and female employees
        total_male_permanent_employees = sum(float(record.Male_Permanent.to_decimal() or 0) for record in employee_records)
        total_female_permanent_employees = sum(float(record.Female_Permanent.to_decimal() or 0) for record in employee_records)
        total_male_non_permanent_employees = sum(float(record.Male_Non_Permanent.to_decimal() or 0) for record in employee_records)
        total_female_non_permanent_employees = sum(float(record.Female_Non_Permanent.to_decimal() or 0) for record in employee_records)


        # Filter records for wellbeing measures
        filtered_records = Percentage_Covered_In_Wellbeing_Measures.objects.filter(
            Financial_Year=financial_year,
            Segment=segment,
            Type=emp_type  
        )

        # Calculate wellbeing measures totals
        for record in filtered_records:
            if emp_type == "Permanent":
                total_males_health_insurance += record.Health_Insurance_No_Of_Male or 0
                total_females_health_insurance += record.Health_Insurance_No_Of_Female or 0
                total_males_accident_insurance += record.Accident_Insurance_No_Of_Male or 0
                total_females_accident_insurance += record.Accident_Insurance_No_Of_Female or 0
                total_males_maternity_benefits += record.Maternity_Benefits_No_Of_Male or 0
                total_females_maternity_benefits += record.Maternity_Benefits_No_Of_Female or 0
                total_males_paternity_benefits += record.Paternity_Benefits_No_Of_Male or 0
                total_females_paternity_benefits += record.Paternity_Benefits_No_Of_Female or 0
                total_males_day_care_facilities += record.Day_Care_Facilities_No_Of_Male or 0
                total_females_day_care_facilities += record.Day_Care_Facilities_No_Of_Female or 0

            elif emp_type == "Non-Permanent":
                total_males_health_insurance += record.Health_Insurance_No_Of_Male or 0
                total_females_health_insurance += record.Health_Insurance_No_Of_Female or 0
                total_males_accident_insurance += record.Accident_Insurance_No_Of_Male or 0
                total_females_accident_insurance += record.Accident_Insurance_No_Of_Female or 0
                total_males_maternity_benefits += record.Maternity_Benefits_No_Of_Male or 0
                total_females_maternity_benefits += record.Maternity_Benefits_No_Of_Female or 0
                total_males_paternity_benefits += record.Paternity_Benefits_No_Of_Male or 0
                total_females_paternity_benefits += record.Paternity_Benefits_No_Of_Female or 0
                total_males_day_care_facilities += record.Day_Care_Facilities_No_Of_Male or 0
                total_females_day_care_facilities += record.Day_Care_Facilities_No_Of_Female or 0

        # Return structured data for employees
        if emp_type == "Permanent":
                
            response = {
                "Principle_3_EI_1a_Permanent_Male_EMP":[{
                    "males_permanent_employees" :  total_male_permanent_employees,
                    "males_health_insurance":  total_males_health_insurance,
                    "males_health_insurance_ratio":  round(total_males_health_insurance / total_male_permanent_employees*100, 2) if total_male_permanent_employees > 0 else 0,
                    "males_accident_insurance":  total_males_accident_insurance,
                    "males_accident_insurance_ratio":  round(total_males_accident_insurance / total_male_permanent_employees*100, 2) if total_male_permanent_employees > 0 else 0,
                    "males_maternity_benefits":  total_males_maternity_benefits,
                    "males_maternity_benefits_ratio":  round(total_males_maternity_benefits / total_male_permanent_employees*100, 2) if total_male_permanent_employees > 0 else 0, 
                    "males_paternity_benefits":  total_males_paternity_benefits,
                    "males_paternity_benefits_ratio":  round(total_males_paternity_benefits / total_male_permanent_employees*100, 2) if total_male_permanent_employees > 0 else 0,
                    "males_day_care_facilities":  total_males_day_care_facilities,
                    "males_day_care_facilities_ratio":  round(total_males_day_care_facilities / total_male_permanent_employees*100, 2) if total_male_permanent_employees > 0 else 0,
                        }],
                "Principle_3_EI_1a_Permanent_Female_EMP":[{
                    "females_permanent_employees":    total_female_permanent_employees,
                    "females_health_insurance":   total_females_health_insurance,
                    "females_health_insurance_ratio":   round(total_females_health_insurance / total_female_permanent_employees*100, 2) if total_female_permanent_employees > 0 else 0,
                    "females_accident_insurance":       total_females_accident_insurance,
                    "females_accident_insurance_ratio":   round(total_females_accident_insurance / total_female_permanent_employees*100, 2) if total_female_permanent_employees > 0 else 0,
                    "females_maternity_benefits":   total_females_maternity_benefits,
                    "females_maternity_benefits_ratio":   round(total_females_maternity_benefits / total_female_permanent_employees*100, 2) if total_female_permanent_employees > 0 else 0,
                    "females_paternity_benefits":  total_females_paternity_benefits,
                    "females_paternity_benefits_ratio":  round(total_females_paternity_benefits / total_female_permanent_employees*100, 2) if total_female_permanent_employees > 0 else 0,
                    "females_day_care_facilities":   total_females_day_care_facilities,
                    "females_day_care_facilities_ratio":   round(total_females_day_care_facilities / total_female_permanent_employees*100, 2) if total_female_permanent_employees > 0 else 0,
                
                    }],
                "Principle_3_EI_1a_Permanent_Total_EMP":[{
                   "total_permanent_employees":round(total_male_permanent_employees + total_female_permanent_employees, 2),
                    "total_health_insurance":   total_males_health_insurance + total_females_health_insurance,
                    "total_health_insurance_ratio":   round((total_males_health_insurance + total_females_health_insurance) / (total_male_permanent_employees + total_female_permanent_employees)*100, 2) if (total_male_permanent_employees + total_female_permanent_employees) > 0 else 0, 
                    "total_accident_insurance":   total_males_accident_insurance + total_females_accident_insurance,
                    "total_accident_insurance_ratio": round((total_males_accident_insurance + total_females_accident_insurance) / (total_male_permanent_employees + total_female_permanent_employees)*100, 2) if (total_male_permanent_employees + total_female_permanent_employees) > 0 else 0, 
                    "total_maternity_benefits":   total_males_maternity_benefits + total_females_maternity_benefits, 
                    "total_maternity_benefits_ratio":   round((total_males_maternity_benefits + total_females_maternity_benefits) / (total_male_permanent_employees + total_female_permanent_employees)*100, 2) if (total_male_permanent_employees + total_female_permanent_employees) > 0 else 0,
                    "total_paternity_benefits":       total_males_paternity_benefits + total_females_paternity_benefits,
                    "total_paternity_benefits_ratio":   round((total_males_paternity_benefits + total_females_paternity_benefits) / (total_male_permanent_employees + total_female_permanent_employees)*100, 2) if (total_male_permanent_employees + total_female_permanent_employees) > 0 else 0,
                    "total_day_care_facilities":       total_males_day_care_facilities + total_females_day_care_facilities,
                    "total_day_care_facilities_ratio":       round((total_males_day_care_facilities + total_females_day_care_facilities) / (total_male_permanent_employees + total_female_permanent_employees)*100, 2) if (total_male_permanent_employees + total_female_permanent_employees) > 0 else 0,
                }],
            }


        if emp_type == "Non-Permanent":
                
            response = {
                "Principle_3_EI_1a_Non_Permanent_Male_EMP":[{        
                        "males_non_permanent_employees" : total_male_non_permanent_employees,
                        "males_health_insurance":   total_males_health_insurance,
                        "males_health_insurance_ratio":   round(total_males_health_insurance / total_male_non_permanent_employees * 100, 2) if total_male_non_permanent_employees > 0 else 0,
                        "males_accident_insurance":   total_males_accident_insurance,
                        "males_accident_insurance_ratio":   round(total_males_accident_insurance / total_male_non_permanent_employees * 100, 2) if total_male_non_permanent_employees > 0 else 0,
                        "males_maternity_benefits":   total_males_maternity_benefits,
                        "males_maternity_benefits_ratio":   round(total_males_maternity_benefits / total_male_non_permanent_employees * 100, 2) if total_male_non_permanent_employees > 0 else 0,
                        "males_paternity_benefits":   total_males_paternity_benefits,
                        "males_paternity_benefits_ratio":       round(total_males_paternity_benefits / total_male_non_permanent_employees * 100, 2) if total_male_non_permanent_employees > 0 else 0,
                        "males_day_care_facilities":   total_males_day_care_facilities,
                        "males_day_care_facilities_ratio":   round(total_males_day_care_facilities / total_male_non_permanent_employees * 100, 2) if total_male_non_permanent_employees > 0 else 0,
                    }],
                "Principle_3_EI_1a_Non_Permanent_Female_EMP":[{
                    "females_non_permanent_employees": total_female_non_permanent_employees,
                    "females_health_insurance": total_females_health_insurance,
                    "females_health_insurance_ratio":  round(total_females_health_insurance / total_female_non_permanent_employees * 100, 2) if total_female_non_permanent_employees > 0 else 0,
                    "females_accident_insurance": total_females_accident_insurance,
                    "females_accident_insurance_ratio": round(total_females_accident_insurance / total_female_non_permanent_employees * 100, 2) if total_female_non_permanent_employees > 0 else 0,
                    "females_maternity_benefits": total_females_maternity_benefits,
                    "females_maternity_benefits_ratio": round(total_females_maternity_benefits / total_female_non_permanent_employees * 100, 2) if total_female_non_permanent_employees > 0 else 0,
                    "females_paternity_benefits": total_females_paternity_benefits,
                    "females_paternity_benefits_ratio": round(total_females_paternity_benefits / total_female_non_permanent_employees * 100, 2) if total_female_non_permanent_employees > 0 else 0,
                    "females_day_care_facilities": total_females_day_care_facilities,
                    "females_day_care_facilities_ratio": round(total_females_day_care_facilities / total_female_non_permanent_employees * 100, 2) if total_female_non_permanent_employees > 0 else 0,

                    }],
                "Principle_3_EI_1a_Non_Permanent_Total_EMP":[{
                    "total_non_permanent_employees":    round(total_male_non_permanent_employees + total_female_non_permanent_employees, 2),
                    "total_health_insurance":    total_males_health_insurance + total_females_health_insurance,
                    "total_health_insurance_ratio":    round((total_males_health_insurance + total_females_health_insurance) / (total_male_non_permanent_employees + total_female_non_permanent_employees)*100, 2) if (total_male_non_permanent_employees + total_female_non_permanent_employees) > 0 else 0,
                    "total_accident_insurance":    total_males_accident_insurance + total_females_accident_insurance,
                    "total_accident_insurance_ratio":    round((total_males_accident_insurance + total_females_accident_insurance) / (total_male_non_permanent_employees + total_female_non_permanent_employees)*100, 2) if (total_male_non_permanent_employees + total_female_non_permanent_employees) > 0 else 0,
                    "total_maternity_benefits":    total_males_maternity_benefits + total_females_maternity_benefits,
                    "total_maternity_benefits_ratio":    round((total_males_maternity_benefits + total_females_maternity_benefits) / (total_male_non_permanent_employees + total_female_non_permanent_employees)*100, 2) if (total_male_non_permanent_employees + total_female_non_permanent_employees) > 0 else 0,
                    "total_paternity_benefits":    total_males_paternity_benefits + total_females_paternity_benefits,
                    "total_paternity_benefits_ratio":    round((total_males_paternity_benefits + total_females_paternity_benefits) / (total_male_non_permanent_employees + total_female_non_permanent_employees)*100, 2) if (total_male_non_permanent_employees + total_female_non_permanent_employees) > 0 else 0,
                    "total_day_care_facilities":    total_males_day_care_facilities + total_females_day_care_facilities,
                    "total_day_care_facilities_ratio":    round((total_males_day_care_facilities + total_females_day_care_facilities) / (total_male_non_permanent_employees + total_female_non_permanent_employees)*100, 2) if (total_male_non_permanent_employees + total_female_non_permanent_employees) > 0 else 0,
            }]
            }



    elif segment == "Workers":
        
        worker_records = WorkerSummary.objects.filter(Financial_Year=financial_year)

        # Calculate total number of male and female workers
        total_male_permanent_worker = sum(float(record.Male_Permanent.to_decimal() or 0) for record in worker_records)
        total_female_permanent_worker = sum(float(record.Female_Permanent.to_decimal() or 0) for record in worker_records)
        total_male_non_permanent_worker = sum(float(record.Male_Non_Permanent.to_decimal() or 0) for record in worker_records)
        total_female_non_permanent_worker = sum(float(record.Female_Non_Permanent.to_decimal() or 0) for record in worker_records)

         # Filter records for wellbeing measures
        filtered_records = Percentage_Covered_In_Wellbeing_Measures.objects.filter(
            Financial_Year=financial_year,
            Segment=segment,
            Type=emp_type  
        )

        # Calculate wellbeing measures totals
        for record in filtered_records:
            if emp_type == "Permanent":
                total_males_health_insurance += record.Health_Insurance_No_Of_Male or 0
                total_females_health_insurance += record.Health_Insurance_No_Of_Female or 0
                total_males_accident_insurance += record.Accident_Insurance_No_Of_Male or 0
                total_females_accident_insurance += record.Accident_Insurance_No_Of_Female or 0
                total_males_maternity_benefits += record.Maternity_Benefits_No_Of_Male or 0
                total_females_maternity_benefits += record.Maternity_Benefits_No_Of_Female or 0
                total_males_paternity_benefits += record.Paternity_Benefits_No_Of_Male or 0
                total_females_paternity_benefits += record.Paternity_Benefits_No_Of_Female or 0
                total_males_day_care_facilities += record.Day_Care_Facilities_No_Of_Male or 0
                total_females_day_care_facilities += record.Day_Care_Facilities_No_Of_Female or 0
            elif emp_type == "Non-Permanent":
                total_males_health_insurance += record.Health_Insurance_No_Of_Male or 0
                total_females_health_insurance += record.Health_Insurance_No_Of_Female or 0
                total_males_accident_insurance += record.Accident_Insurance_No_Of_Male or 0
                total_females_accident_insurance += record.Accident_Insurance_No_Of_Female or 0
                total_males_maternity_benefits += record.Maternity_Benefits_No_Of_Male or 0
                total_females_maternity_benefits += record.Maternity_Benefits_No_Of_Female or 0
                total_males_paternity_benefits += record.Paternity_Benefits_No_Of_Male or 0
                total_females_paternity_benefits += record.Paternity_Benefits_No_Of_Female or 0
                total_males_day_care_facilities += record.Day_Care_Facilities_No_Of_Male or 0
                total_females_day_care_facilities += record.Day_Care_Facilities_No_Of_Female or 0

        # Return structured data for workers
        if emp_type == "Permanent":
                
            response = {
                "Principle_3_EI_1b_Permanent_Male_WRK":[{
                    "males_permanent_workers" :     total_male_permanent_worker,
                    "males_health_insurance":   total_males_health_insurance,
                    "males_health_insurance_ratio":   round(total_males_health_insurance / total_male_permanent_worker*100, 2) if total_male_permanent_worker > 0 else 0,
                    "males_accident_insurance":   total_males_accident_insurance,
                    "males_accident_insurance_ratio":   round(total_males_accident_insurance / total_male_permanent_worker*100, 2) if total_male_permanent_worker > 0 else 0,
                    "males_maternity_benefits":   total_males_maternity_benefits,
                    "males_maternity_benefits_ratio":   round(total_males_maternity_benefits / total_male_permanent_worker*100, 2) if total_male_permanent_worker > 0 else 0, 
                    "males_paternity_benefits":   total_males_paternity_benefits,
                    "males_paternity_benefits_ratio":   round(total_males_paternity_benefits / total_male_permanent_worker*100, 2) if total_male_permanent_worker > 0 else 0,
                    "males_day_care_facilities":   total_males_day_care_facilities,
                    "males_day_care_facilities_ratio":   round(total_males_day_care_facilities / total_male_permanent_worker*100, 2) if total_male_permanent_worker > 0 else 0,
                }],
                "Principle_3_EI_1b_Permanent_Female_WRK":[{
                    "females_permanent_workers":  total_female_permanent_worker,
                    "females_health_insurance":   total_females_health_insurance,
                    "females_health_insurance_ratio":   round(total_females_health_insurance / total_female_permanent_worker*100, 2) if total_female_permanent_worker > 0 else 0,
                    "females_accident_insurance":    total_females_accident_insurance,
                    "females_accident_insurance_ratio":    round(total_females_accident_insurance / total_female_permanent_worker*100, 2) if total_female_permanent_worker > 0 else 0,
                    "females_maternity_benefits":    total_females_maternity_benefits,
                    "females_maternity_benefits_ratio":    round(total_females_maternity_benefits / total_female_permanent_worker*100, 2) if total_female_permanent_worker > 0 else 0,
                    "females_paternity_benefits":     total_females_paternity_benefits,
                    "females_paternity_benefits_ratio":     round(total_females_paternity_benefits / total_female_permanent_worker*100, 2) if total_female_permanent_worker > 0 else 0,
                    "females_day_care_facilities":   total_females_day_care_facilities,
                    "females_day_care_facilities_ratio":    round(total_females_day_care_facilities / total_female_permanent_worker*100, 2) if total_female_permanent_worker > 0 else 0,
                        }],
                
                "Principle_3_EI_1b_Permanent_Total_WRK":[{
                        "total_permanent_workers":  round(total_male_permanent_worker + total_female_permanent_worker, 2),
                        "total_health_insurance":  total_males_health_insurance + total_females_health_insurance,
                        "total_health_insurance_ratio":  round((total_males_health_insurance + total_females_health_insurance) / (total_male_permanent_worker + total_female_permanent_worker)*100, 2) if (total_male_permanent_worker + total_female_permanent_worker) > 0 else 0, 
                        "total_accident_insurance":  total_males_accident_insurance + total_females_accident_insurance,
                        "total_accident_insurance_ratio":  round((total_males_accident_insurance + total_females_accident_insurance) / (total_male_permanent_worker + total_female_permanent_worker)*100, 2) if (total_male_permanent_worker + total_female_permanent_worker) > 0 else 0, 
                        "total_maternity_benefits":  total_males_maternity_benefits + total_females_maternity_benefits, 
                        "total_maternity_benefits_ratio":  round((total_males_maternity_benefits + total_females_maternity_benefits) / (total_male_permanent_worker + total_female_permanent_worker)*100, 2) if (total_male_permanent_worker + total_female_permanent_worker) > 0 else 0,
                        "total_paternity_benefits":  total_males_paternity_benefits + total_females_paternity_benefits,
                        "total_paternity_benefits_ratio":  round((total_males_paternity_benefits + total_females_paternity_benefits) / (total_male_permanent_worker + total_female_permanent_worker)*100, 2) if (total_male_permanent_worker + total_female_permanent_worker) > 0 else 0,
                        "total_day_care_facilities":  total_males_day_care_facilities + total_females_day_care_facilities,
                        "total_day_care_facilities_ratio":   round((total_males_day_care_facilities + total_females_day_care_facilities) / (total_male_permanent_worker + total_female_permanent_worker)*100, 2) if (total_male_permanent_worker + total_female_permanent_worker) > 0 else 0,
            }],
                
            }
        elif emp_type == "Non-Permanent":
            response = {
                "Principle_3_EI_1b_Non_Permanent_Male_WRK":[{
                    "males_non_permanent_workers":   total_male_non_permanent_worker,
                    "males_health_insurance":   total_males_health_insurance,
                    "males_health_insurance_ratio":   round(total_males_health_insurance / total_male_non_permanent_worker*100, 2) if total_male_non_permanent_worker > 0 else 0,
                    "males_accident_insurance":   total_males_accident_insurance,
                    "males_accident_insurance_ratio":   round(total_males_accident_insurance / total_male_non_permanent_worker*100, 2) if total_male_non_permanent_worker > 0 else 0,
                    "males_maternity_benefits":   total_males_maternity_benefits,
                    "males_maternity_benefits_ratio":   round(total_males_maternity_benefits / total_male_non_permanent_worker*100, 2) if total_male_non_permanent_worker > 0 else 0,
                    "males_paternity_benefits":   total_males_paternity_benefits,
                    "males_paternity_benefits_ratio":   round(total_males_paternity_benefits / total_male_non_permanent_worker*100, 2) if total_male_non_permanent_worker > 0 else 0,
                    "males_day_care_facilities":   total_males_day_care_facilities,
                    "males_day_care_facilities_ratio":   round(total_males_day_care_facilities / total_male_non_permanent_worker*100, 2) if total_male_non_permanent_worker > 0 else 0,
                    }],

                "Principle_3_EI_1_1b_Non_Permanent_Female_WRK":[{
                        "females_non_permanent_workers":  total_female_non_permanent_worker,
                        "females_health_insurance":  total_females_health_insurance,
                        "females_health_insurance_ratio":  round(total_females_health_insurance / total_female_non_permanent_worker*100, 2) if total_female_non_permanent_worker > 0 else 0,
                        "females_accident_insurance":  total_females_accident_insurance,
                        "females_accident_insurance_ratio":  round(total_females_accident_insurance / total_female_non_permanent_worker*100, 2) if total_female_non_permanent_worker > 0 else 0,
                        "females_maternity_benefits":  total_females_maternity_benefits,
                        "females_maternity_benefits_ratio":  round(total_females_maternity_benefits/ total_female_non_permanent_worker*100, 2) if total_female_non_permanent_worker > 0 else 0,
                        "females_paternity_benefits":  total_females_paternity_benefits,
                        "females_paternity_benefits_ratio":  round(total_females_paternity_benefits / total_female_non_permanent_worker*100, 2) if total_female_non_permanent_worker > 0 else 0,
                        "females_day_care_facilities":   total_females_day_care_facilities,
                        "females_day_care_facilities_ratio":   round(total_females_day_care_facilities / total_female_non_permanent_worker*100, 2) if total_female_non_permanent_worker > 0 else 0,
                    }],
               
                "Principle_3_EI_1b_Non_Permanent_Total_WRK":[{
                        "total_non_permanent_workers":   round(total_male_non_permanent_worker + total_female_non_permanent_worker, 2),
                        "total_health_insurance":   total_males_health_insurance + total_females_health_insurance,
                        "total_health_insurance_ratio":   round((total_males_health_insurance + total_females_health_insurance) / (total_male_non_permanent_worker + total_female_non_permanent_worker)*100, 2) if (total_male_non_permanent_worker + total_female_non_permanent_worker) > 0 else 0,
                        "total_accident_insurance":   total_males_accident_insurance + total_females_accident_insurance,
                        "total_accident_insurance_ratio":   round((total_males_accident_insurance + total_females_accident_insurance) / (total_male_non_permanent_worker + total_female_non_permanent_worker)*100, 2) if (total_male_non_permanent_worker + total_female_non_permanent_worker) > 0 else 0,
                        "total_maternity_benefits":   total_males_maternity_benefits + total_females_maternity_benefits,
                        "total_maternity_benefits_ratio":   round((total_males_maternity_benefits + total_females_maternity_benefits) / (total_male_non_permanent_worker + total_female_non_permanent_worker)*100, 2) if (total_male_non_permanent_worker + total_female_non_permanent_worker) > 0 else 0,
                        "total_paternity_benefits":   total_males_paternity_benefits + total_females_paternity_benefits,
                        "total_paternity_benefits_ratio":   round((total_males_paternity_benefits + total_females_paternity_benefits) / (total_male_non_permanent_worker + total_female_non_permanent_worker)*100, 2) if (total_male_non_permanent_worker + total_female_non_permanent_worker) > 0 else 0,
                        "total_day_care_facilities":   total_males_day_care_facilities + total_females_day_care_facilities,
                        "total_day_care_facilities_ratio":   round((total_males_day_care_facilities + total_females_day_care_facilities) / (total_male_non_permanent_worker + total_female_non_permanent_worker)*100, 2) if (total_male_non_permanent_worker + total_female_non_permanent_worker) > 0 else 0,
                    }]   

             }

   
    return response  # Return None if segment doesn't match



# def calculate_totals(current_year, previous_year):
#     # Fetch records for current year and previous year
#     records_current = Retirement_Benefits.objects.filter(
#         Financial_Year=current_year, Segment="Employees"
#     )
#     records_previous = Retirement_Benefits.objects.filter(
#         Financial_Year=previous_year, Segment="Employees"
#     )
    
#     records_wrk_current = Retirement_Benefits.objects.filter(
#         Financial_Year=current_year, Segment="Workers"
#     )
#     records_wrk_previous = Retirement_Benefits.objects.filter(
#         Financial_Year=previous_year, Segment="Workers"
#     )

#     # Initialize totals for current year
#     total_pf_employees_current = 0
#     total_pf_wrk_current = 0

#     total_gratuity_employees_current = 0
#     total_gratuity_wrk_current = 0

#     total_esi_employees_current = 0
#     total_esi_wrk_current = 0

#     total_other_employees_current = 0
#     total_other_wrk_current = 0

#     total_deducted_pf_employees_current = ""
#     total_deducted_and_deposited_gratuity_employees_current = ""
#     total_deducted_and_deposited_esi_employees_current = ""
#     total_deducted_and_deposited_other_employees_current = ""

#     # Initialize totals for previous year
#     total_pf_employees_previous = 0
#     total_pf_wrk_previous = 0

#     total_gratuity_employees_previous = 0
#     total_gratuity_wrk_previous = 0

#     total_esi_employees_previous = 0
#     total_esi_wrk_previous = 0

#     total_other_employees_previous = 0
#     total_other_wrk_previous = 0

#     total_deducted_pf_employees_previous = ""
#     total_deducted_and_deposited_gratuity_employees_previous = ""
#     total_deducted_and_deposited_esi_employees_previous = ""
#     total_deducted_and_deposited_other_employees_previous = ""

#     # Helper function to safely convert Decimal128 to float
#     def to_float(value):
#         if isinstance(value, Decimal):
#             return float(value)
#         return float(str(value or 0))

#     # Calculate totals for current year
#     for record in records_current:
#         total_pf_employees_current += to_float(record.Total_Covered_PF)
#         total_gratuity_employees_current += to_float(record.Total_Covered_Gratuity)
#         total_esi_employees_current += to_float(record.Total_Covered_ESI)
#         total_other_employees_current += to_float(record.Total_Covered_Other)
       
#         total_deducted_pf_employees_current = record.Deducted_And_Deposited_PF or ""
#         total_deducted_and_deposited_gratuity_employees_current = record.Deducted_And_Deposited_Gratuity or ""
#         total_deducted_and_deposited_esi_employees_current = record.Deducted_And_Deposited_ESI or ""
#         total_deducted_and_deposited_other_employees_current = record.Deducted_And_Deposited_Other or ""

#     for record in records_wrk_current:
#         total_pf_wrk_current += to_float(record.Total_Covered_PF)
#         total_gratuity_wrk_current += to_float(record.Total_Covered_Gratuity)
#         total_esi_wrk_current += to_float(record.Total_Covered_ESI)
#         total_other_wrk_current += to_float(record.Total_Covered_Other)

#     # Calculate totals for previous year
#     for record in records_previous:
#         total_pf_employees_previous += to_float(record.Total_Covered_PF)
#         total_gratuity_employees_previous += to_float(record.Total_Covered_Gratuity)
#         total_esi_employees_previous += to_float(record.Total_Covered_ESI)
#         total_other_employees_previous += to_float(record.Total_Covered_Other)
        
#         total_deducted_pf_employees_previous = record.Deducted_And_Deposited_PF or ""
#         total_deducted_and_deposited_gratuity_employees_previous = record.Deducted_And_Deposited_Gratuity or ""
#         total_deducted_and_deposited_esi_employees_previous = record.Deducted_And_Deposited_ESI or ""
#         total_deducted_and_deposited_other_employees_previous = record.Deducted_And_Deposited_Other or ""

#     for record in records_wrk_previous:
#         total_pf_wrk_previous += to_float(record.Total_Covered_PF)
#         total_gratuity_wrk_previous += to_float(record.Total_Covered_Gratuity)
#         total_esi_wrk_previous += to_float(record.Total_Covered_ESI)
#         total_other_wrk_previous += to_float(record.Total_Covered_Other)

#     # Return the totals for both years
#     return {
#         # Current year totals
#         "Total_Covered_PF_emp_current_yr": total_pf_employees_current,
#         "Total_Covered_PF_wrk_current_yr": total_pf_wrk_current,
#         "Total_Deducted_PF_current_yr": total_deducted_pf_employees_current,

#         # Previous year totals
#         "Total_Covered_PF_emp_previous_yr": total_pf_employees_previous,
#         "Total_Covered_PF_wrk_previous_yr": total_pf_wrk_previous,
#         "Total_Deducted_PF_previous_yr": total_deducted_pf_employees_previous,
#     }


def calculate_section_C_EI_6(financial_year, previous_financial_year):
    def get_conflict_data(year, segment):
        try:
            conflict_obj = Conflict_of_interest_complaints.objects.filter(
                Financial_Year=year, Segment=segment
            ).first()
            if conflict_obj:
                return conflict_obj.No_of_complaints, conflict_obj.Remark
            return 0, "NA"
        except Exception:
            return 0, "NA"

    try:
        # Get conflict data for the current financial year
        current_year_no_of_conflicts_director, current_year_remarks_director = get_conflict_data(financial_year, "Director")
        current_year_no_of_conflicts_kmp, current_year_remarks_kmp = get_conflict_data(financial_year, "KMP")
        
        # Get conflict data for the previous financial year
        previous_year_no_of_conflicts_director, previous_year_remarks_director = get_conflict_data(previous_financial_year, "Director")
        previous_year_no_of_conflicts_kmp, previous_year_remarks_kmp = get_conflict_data(previous_financial_year, "KMP")

        # Construct the result JSON
        record_json = {
            "Current_Year_No_of_Conflicts_Director": current_year_no_of_conflicts_director,
            "Current_Year_Remarks_Director": current_year_remarks_director,
            "Current_Year_No_of_Conflicts_KMP": current_year_no_of_conflicts_kmp,
            "Current_Year_Remarks_KMP": current_year_remarks_kmp,
            "Previous_Year_No_of_Conflicts_Director": previous_year_no_of_conflicts_director,
            "Previous_Year_Remarks_Director": previous_year_remarks_director,
            "Previous_Year_No_of_Conflicts_KMP": previous_year_no_of_conflicts_kmp,
            "Previous_Year_Remarks_KMP": previous_year_remarks_kmp
        }
    except Exception:
        # Return default values if an error occurs
        record_json = {
            "Current_Year_No_of_Conflicts_Director": 0,
            "Current_Year_Remarks_Director": "NA",
            "Current_Year_No_of_Conflicts_KMP": 0,
            "Current_Year_Remarks_KMP": "NA",
            "Previous_Year_No_of_Conflicts_Director": 0,
            "Previous_Year_Remarks_Director": "NA",
            "Previous_Year_No_of_Conflicts_KMP": 0,
            "Previous_Year_Remarks_KMP": "NA"
        }

    return record_json



def calculate_principle_2_EI_1(financial_year, previous_financial_year):
    # Fetch data for the current financial year
    current_data = Percentage_Of_R_and_D_and_Capex_Investments.objects.filter(Financial_Year=financial_year).first()
    
    # Fetch data for the previous financial year
    previous_data = Percentage_Of_R_and_D_and_Capex_Investments.objects.filter(Financial_Year=previous_financial_year).first()
    
    # Prepare the response dictionary with conditional values
    record_json = {
        "Current_Year_R_and_D_Investments": current_data.Percentage_of_R_and_D_investments if current_data and current_data.Percentage_of_R_and_D_investments else 0,
        "Previous_Year_R_and_D_Investments": previous_data.Percentage_of_R_and_D_investments if previous_data and previous_data.Percentage_of_R_and_D_investments else 0,
        "R_and_D_Investment_Details": current_data.Details_investment if current_data and current_data.Details_investment else "-",
        "Current_Year_Capex": current_data.Percent_of_capex if current_data and current_data.Percent_of_capex else 0,
        "Previous_Year_Capex": previous_data.Percent_of_capex if previous_data and previous_data.Percent_of_capex else 0,
        "Capex_Investment_Details": current_data.Details_capex if current_data and current_data.Details_capex else "-",
    }

    return record_json


def convert_to_float(value):
    """
    This function converts Decimal128 or Decimal objects to float.
    If the value is already an int or float, it returns the value directly.
    If the value is "-", it returns it as is.
    """
    if value is None or value == "-":  # Handle the case where data is not available
        return "-"
    
    if isinstance(value, Decimal128):
        # Convert Decimal128 to float
        return float(value.to_decimal())
    elif isinstance(value, Decimal):  # For Decimal fields
        return float(value)
    elif isinstance(value, (int, float)):
        return value
    else:
        return value







from bson.decimal128 import Decimal128
from decimal import Decimal
def convert_decimal(value):
            if isinstance(value, Decimal128):
                return float(value.to_decimal())
            elif isinstance(value, Decimal):
                return float(value)
            return value
        
        
def decimal_from_decimal128(value):
    if isinstance(value, Decimal):
        return value
    try:
        # Attempt to convert directly to Decimal
        return Decimal(value)
    except (TypeError, ValueError):
        # Handle cases where conversion fails
        return Decimal('0.0')      
    
    
    import decimal
def safe_divide(numerator, denominator):
    # Convert both numerator and denominator to float if they are decimal.Decimal
    if isinstance(numerator, decimal.Decimal):
        numerator = float(numerator)
    if isinstance(denominator, decimal.Decimal):
        denominator = float(denominator)
    # Perform division with protection against division by zero
    return round((numerator / denominator)*100, 2) if denominator != 0 else 0


def safe_decimal_to_float(value):
    """Convert Decimal128 to float or return 'NA' if None."""
    if value is None:
        return "NA"
    try:
        return float(value)  # Convert Decimal128 to float
    except (TypeError, ValueError):
        return str(value)  # Fallback to string conversion if float fails

from decimal import Decimal, InvalidOperation
def convert_decimal(value): 
    if value is None:
        return Decimal('0.00')
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(value)
    

def conversion(value):
    """Convert Decimal128 to float or return 0 if None."""
    if value is None:
        return 0.0
    try:
        if isinstance(value, (int, float, Decimal)):
            return float(value)
        elif isinstance(value, Decimal128):
            return float(Decimal(value.to_decimal()))
    except (TypeError, ValueError):
        pass  
    return 0.0  
    
def generate_fiscal_years(financial_year, num_years=3):
    start_year = int(financial_year[2:6])
    
    financial_years = [
        f"FY{year}-{year + 1}" for year in range(start_year, start_year - num_years, -1)
    ]
    
    return financial_years

def calculate_section_A_22_Management(financial_year):
    current_year = datetime.now().year
    financial_years = generate_fiscal_years(financial_year)
    result_dict = {"male": [], "female": [], "total": []}
    for year in financial_years:
        permanent_employees_queryset = Employee_Turnover_Rate.objects.filter(Financial_Year=year, Type="Permanent")
        male_count = sum(
            float(entry['Total_Employee_Turnover_Rate'].to_decimal())
            for entry in permanent_employees_queryset.filter(Gender="Male").values('Total_Employee_Turnover_Rate')
            if isinstance(entry['Total_Employee_Turnover_Rate'], Decimal128)
        )
        female_count = sum(
            float(entry['Total_Employee_Turnover_Rate'].to_decimal())
            for entry in permanent_employees_queryset.filter(Gender="Female").values('Total_Employee_Turnover_Rate')
            if isinstance(entry['Total_Employee_Turnover_Rate'], Decimal128)
        )
        total_count = (male_count + female_count) / 2
        # Append values to the respective keys
        result_dict["male"].append(f"{male_count}%" if male_count >= 0 else "-")
        result_dict["female"].append(f"{female_count}%" if female_count >= 0 else "-")
        result_dict["total"].append(f"{total_count}%" if total_count >= 0 else "-")
    # Wrap result_dict in a list before returning
    return [result_dict]

def generate_fiscal_years(financial_year, num_years=3):
    start_year = int(financial_year[2:6])
    
    financial_years = [
        f"FY{year}-{year + 1}" for year in range(start_year, start_year - num_years, -1)
    ]
    
    return financial_years

def calculate_section_A_22_Worker(financial_year):
    current_year = datetime.now().year
    financial_years = generate_fiscal_years(financial_year)
    result_dict = {"male": [], "female": [], "total": []}
    for year in financial_years:
        permanent_employees_queryset = Workers_Turnover_Rate.objects.filter(Financial_Year=year, Type="Permanent")
        male_count = sum(
            float(entry['Total_Workers_Turnover_Rate'].to_decimal())
            for entry in permanent_employees_queryset.filter(Gender="Male").values('Total_Workers_Turnover_Rate')
            if isinstance(entry['Total_Workers_Turnover_Rate'], Decimal128)
        )
        female_count = sum(
            float(entry['Total_Workers_Turnover_Rate'].to_decimal())
            for entry in permanent_employees_queryset.filter(Gender="Female").values('Total_Workers_Turnover_Rate')
            if isinstance(entry['Total_Workers_Turnover_Rate'], Decimal128)
        )
        total_count = (male_count + female_count) / 2
        # Append values to the respective keys
        result_dict["male"].append(f"{male_count}%" if male_count >= 0 else "-")
        result_dict["female"].append(f"{female_count}%" if female_count >= 0 else "-")
        result_dict["total"].append(f"{total_count}%" if total_count >= 0 else "-")
    # Wrap result_dict in a list before returning
    return [result_dict]

def format_value(value,records):
    """Return the value if records exist, otherwise return '-'."""
    return value if records.exists() else "-"
