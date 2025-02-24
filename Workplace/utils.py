from decimal import Decimal
import logging
from bson import Decimal128  # Import Decimal128 for MongoDB
from bson.decimal128 import Decimal128
from rest_framework.response import Response
from rest_framework import status
from .models import Employees,EmployeeSummary, Workers, WorkerSummary
from .serializers import EmployeesSerializer,Differently_Abled_EmployeesSerializer,EmployeeSummarySerializer, WorkerSummarySerializer
logger = logging.getLogger(__name__)

def sum_monthly_employees(queryset):
    try:
        # import pdb;pdb.set_trace()
        total_sum = Decimal('0.00')

        # List of fields to sum
        fields_to_sum = [
            'Employees_Apr', 'Employees_May', 'Employees_Jun',
            'Employees_Jul', 'Employees_Aug', 'Employees_Sep',
            'Employees_Oct', 'Employees_Nov', 'Employees_Dec',
            'Employees_Jan', 'Employees_Feb', 'Employees_Mar',
        ]

        for doc in queryset.values():
            for field in fields_to_sum:
                if field in doc and doc[field] is not None:
                    value = doc[field]

                    # Convert Decimal128 to Decimal if needed
                    if isinstance(value, Decimal128):
                        value = Decimal(value.to_decimal())

                    # Convert other numeric types to Decimal
                    elif isinstance(value, (int, float)):
                        value = Decimal(str(value))
                   
                    total_sum += Decimal(value)

                else:
                    logger.warning(f"Field '{field}' not found or is None in document: {doc}")

        logger.debug(f"Total sum calculated: {total_sum}")
        return total_sum

    except Exception as e:
        logger.error(f"Error in sum_monthly_employees: {str(e)}")
        return Decimal('0.00')


def save_employee_summary(financial_year, facility):
    try:
        # Filter the employees queryset by the given financial year and facility
        employees = Employees.objects.filter(Financial_Year=financial_year, Facility=facility)

        total_male_permanent = sum_monthly_employees(employees.filter(Gender='Male', Type='Permanent'))
        total_male_non_permanent = sum_monthly_employees(employees.filter(Gender='Male', Type='Non-Permanent'))
        total_female_permanent = sum_monthly_employees(employees.filter(Gender='Female', Type='Permanent'))
        total_female_non_permanent =sum_monthly_employees(employees.filter(Gender='Female', Type='Non-Permanent'))

        total_male = total_male_permanent + total_male_non_permanent
        total_female = total_female_permanent + total_female_non_permanent
        total = total_male + total_female

        percentage_male = (total_male / total * 100) if total != 0 else 0
        percentage_female = (total_female / total * 100) if total != 0 else 0

        summary_data = {
            'financial_year': financial_year,
            'facility': facility,
            'total_male_permanent': total_male_permanent,
            'total_male_non_permanent': total_male_non_permanent,
            'total_female_permanent': total_female_permanent,
            'total_female_non_permanent': total_female_non_permanent,
            'total_male': total_male,
            'total_female': total_female,
            'percentage_male': percentage_male,
            'percentage_female': percentage_female,
        }
        # Save the summary data
        summary_serializer = EmployeeSummarySerializer(data=summary_data)
        if summary_serializer.is_valid():
            summary_serializer.save()
            logger.info('Employee summary data saved successfully')
        else:
            logger.error(f"Summary serializer errors: {summary_serializer.errors}")
    except Exception as e:
        logger.error(f"Exception in saving employee summary: {e}")



def convert_decimal128_to_float(value):
    """Helper function to convert Decimal128 to float and round to 2 decimal places."""
    if isinstance(value, Decimal128):
        return round(float(value.to_decimal()), 2)
    return round(float(value or 0), 2)


def calculate_total_employees():
    result = []
    distinct_combinations = Employees.objects.values('Financial_Year', 'Facility').distinct()

    for comb in distinct_combinations:
        record_json = {
            "Financial_Year": comb["Financial_Year"],
            "Facility": comb["Facility"],
            "Female_Permanent": 0.0,
            "Female_Non_Permanent": 0.0,
            "Male_Permanent": 0.0,
            "Male_Non_Permanent": 0.0,
            "Total_Male": 0.0,
            "Total_Female": 0.0,
            "Percentage_Male": 0.0,
            "Percentage_Female": 0.0
        }

        filtered_documents = Employees.objects.filter(Financial_Year=comb["Financial_Year"], Facility=comb["Facility"])

        for doc in filtered_documents:
            total_employees = convert_decimal128_to_float(doc.Total_Employees)
            if doc.Type == "Permanent" and doc.Gender == "Male":
                record_json["Male_Permanent"] = total_employees
            elif doc.Type == "Non-Permanent" and doc.Gender == "Male":
                record_json["Male_Non_Permanent"] = total_employees
            elif doc.Type == "Permanent" and doc.Gender == "Female":
                record_json["Female_Permanent"] = total_employees
            elif doc.Type == "Non-Permanent" and doc.Gender == "Female":
                record_json["Female_Non_Permanent"] = total_employees

        # Calculate totals
        record_json["Total_Male"] = round(record_json["Male_Permanent"] + record_json["Male_Non_Permanent"], 2)
        record_json["Total_Female"] = round(record_json["Female_Permanent"] + record_json["Female_Non_Permanent"], 2)

        # Only calculate percentages if the total number of employees is not zero
        total_employees = record_json["Total_Male"] + record_json["Total_Female"]
        if total_employees > 0:
            record_json["Percentage_Male"] = round(record_json["Total_Male"] / total_employees * 100, 2)
            record_json["Percentage_Female"] = round(record_json["Total_Female"] / total_employees * 100, 2)
        else:
            record_json["Percentage_Male"] = 0.0
            record_json["Percentage_Female"] = 0.0
        
        result.append(record_json)

    return result




def calculate_employees_percent_covered(facility, financial_year, permanent_males, permanent_females):
    try:
        permanent_males = int(permanent_males)
        permanent_females = int(permanent_females)
        filtered_documents = EmployeeSummary.objects.filter(
            Financial_Year=financial_year,
            Facility=facility
        )

        percent_male_covered = 0
        percent_female_covered = 0

        if filtered_documents:
            for document in filtered_documents:
                total_male_permanent_employees = convert_decimal128_to_float(document.Male_Permanent)
                total_female_permanent_employees = convert_decimal128_to_float(document.Female_Permanent)

                if total_male_permanent_employees > 0:
                    percent_male_covered = round((permanent_males / total_male_permanent_employees) * 100, 2)
                if total_female_permanent_employees > 0:
                    percent_female_covered = round((permanent_females / total_female_permanent_employees) * 100, 2)

        return percent_male_covered, percent_female_covered 
    except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        




def calculate_total_workers():

    result = []
    distinct_combinations = Workers.objects.values('Financial_Year', 'Facility').distinct()

    # Convert the result to a list if needed
    distinct_combinations_list = list(distinct_combinations)

    for comb in distinct_combinations_list:
        record_json = {}
        record_json["Financial_Year"] = comb["Financial_Year"]
        record_json["Facility"] = comb["Facility"]
        record_json["Female_Permanent"] = 0.0
        record_json["Female_Non_Permanent"] = 0.0
        record_json["Male_Permanent"] = 0.0
        record_json["Male_Non_Permanent"] = 0.0
        record_json["Total_Male"] = 0.0
        record_json["Total_Female"] = 0.0
        record_json["Percentage_Male"] = 0.0
        record_json["Percentage_Female"] = 0.0

        filtered_documents = Workers.objects.filter(Financial_Year=comb["Financial_Year"], Facility=comb["Facility"])

        for doc in filtered_documents:
            if doc.Type == "Permanent" and doc.Gender == "Male":
                record_json["Male_Permanent"] = convert_decimal128_to_float(doc.Total_Differently_Abled_Workers)
            elif doc.Type == "Non-Permanent" and doc.Gender == "Male":
                record_json["Male_Non_Permanent"] = convert_decimal128_to_float(doc.Total_Differently_Abled_Workers)
            elif doc.Type == "Permanent" and doc.Gender == "Female":
                record_json["Female_Permanent"] = convert_decimal128_to_float(doc.Total_Differently_Abled_Workers)
            elif doc.Type == "Non-Permanent" and doc.Gender == "Female":
                record_json["Female_Non_Permanent"] = convert_decimal128_to_float(doc.Total_Differently_Abled_Workers)

        record_json["Total_Male"] = round(record_json["Male_Permanent"] + record_json["Male_Non_Permanent"], 2)
        record_json["Total_Female"] = round(record_json["Female_Permanent"] + record_json["Female_Non_Permanent"], 2)

        # record_json["Percentage_Male"] = round(record_json["Total_Male"] / (record_json["Total_Male"] + record_json["Total_Female"]) * 100, 2)
        # record_json["Percentage_Female"] = round(record_json["Total_Female"] / (record_json["Total_Male"] + record_json["Total_Female"]) * 100, 2)
        
        total_male_female = record_json["Total_Male"] + record_json["Total_Female"]
        
        if total_male_female:
            record_json["Percentage_Male"] = round(record_json["Total_Male"] / total_male_female * 100, 2)
            record_json["Percentage_Female"] = round(record_json["Total_Female"] / total_male_female * 100, 2)
        else:
            record_json["Percentage_Male"] = 0
            record_json["Percentage_Female"] = 0

        result.append(record_json)

    return result




def calculate_workers_percent_covered(facility, financial_year, permanent_males, permanent_females):
    try:
        permanent_males = int(permanent_males)
        permanent_females = int(permanent_females)

        filtered_documents = WorkerSummary.objects.filter(
            Financial_Year=financial_year,
            Facility=facility
        )

        percent_male_covered = 0
        percent_female_covered = 0

        if filtered_documents:
            for document in filtered_documents:
                total_male_permanent_employees = convert_decimal128_to_float(document.Male_Permanent)
                total_female_permanent_employees = convert_decimal128_to_float(document.Female_Permanent)

                if total_male_permanent_employees > 0:
                    percent_male_covered = round((permanent_males / total_male_permanent_employees) * 100, 2)
                if total_female_permanent_employees > 0:
                    percent_female_covered = round((permanent_females / total_female_permanent_employees) * 100, 2)

        return percent_male_covered, percent_female_covered
    except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



def calculate_percent_males(financial_year,segment,type,Male_wages):
    
    filtered_documents = {}
    if segment == "Employees":
        filtered_documents = EmployeeSummary.objects.filter(Financial_Year=financial_year)
    if segment == "Workers":
        filtered_documents = WorkerSummary.objects.filter(Financial_Year=financial_year)
    
    male_count = 0
    for doc in filtered_documents:

        if type == "Permanent":
            male_count += Decimal(doc.Male_Permanent.to_decimal())
        elif type == "Non-Permanent":
            male_count += Decimal(doc.Male_Non_Permanent.to_decimal())

    percent_males = 0 if male_count == 0 else round((Male_wages / male_count) * 100, 2)

    return percent_males



def calculate_percent_females(financial_year,segment,type,Female_wages):
    
    filtered_documents = {}
    if segment == "Employees":
        filtered_documents = EmployeeSummary.objects.filter(Financial_Year=financial_year)
    if segment == "Workers":
        filtered_documents = WorkerSummary.objects.filter(Financial_Year=financial_year)
    
    female_count = 0
    for doc in filtered_documents:
        if type == "Permanent":
            female_count += Decimal(doc.Female_Permanent.to_decimal())
        elif type == "Non-Permanent":
            female_count += Decimal(doc.Female_Non_Permanent.to_decimal())

    percent_females = 0 if female_count == 0 else round((Female_wages / female_count) * 100, 2)

    return percent_females