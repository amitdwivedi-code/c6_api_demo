from decimal import Decimal
from bson.decimal128 import Decimal128
from Workplace.models import *


# Step 3: Function to safely convert database values to floats
def safe_decimal(value):
    if value is None:
        return 0.0
    if isinstance(value, Decimal128):
        return float(value.to_decimal())
    if isinstance(value, Decimal):
        return float(value)
    return float(str(value))

# Step 4: Calculate ratio (turnover / networth)
def ratio(turnover, networth):
    net = safe_decimal(networth)
    turn = safe_decimal(turnover)
    return round(turn / net, 2) if net != 0 else 0.0

# Step 5: Calculate change and percent change between consecutive quarters
def get_change(prev, curr):
    change = round(curr - prev, 2)
    percent = round((change / prev) * 100, 2) if prev != 0 else 0.0
    return {"change": change, "percent": percent}

def safe_decimal_to_float(val):
        if isinstance(val, Decimal128):
            return float(val.to_decimal())
        elif val is not None:
            return float(val)
        return 0.0

def convert_decimal128_to_float(value):
    """Helper function to convert Decimal128 to float and round to 2 decimal places."""
    if isinstance(value, Decimal128):
        return round(float(value.to_decimal()), 2)
    return round(float(value or 0), 2)

from itertools import chain

def calculate_total_employees():
    result = []

    # Step 1: Get all unique (Financial_Year, Facility) from both models
    dae_combinations = Differently_Abled_Employees.objects.values_list(
        'Financial_Year', 'Facility'
    ).distinct()
    emp_combinations = Employees.objects.values_list(
        'Financial_Year', 'Facility'
    ).distinct()

    # Combine and deduplicate
    all_combinations = set(chain(dae_combinations, emp_combinations))

    for financial_year, facility in all_combinations:
        record_json = {
            "Financial_Year": financial_year,
            "Facility": facility,
            "Female_Permanent": 0.0,
            "Female_Non_Permanent": 0.0,
            "Male_Permanent": 0.0,
            "Male_Non_Permanent": 0.0,
            "Total_Male": 0.0,
            "Total_Female": 0.0,
            "Percentage_Male": 0.0,
            "Percentage_Female": 0.0
        }

        # Step 2: From Differently_Abled_Employees
        dae_docs = Differently_Abled_Employees.objects.filter(
            Financial_Year=financial_year, Facility=facility
        )
        for doc in dae_docs:
            total = convert_decimal128_to_float(doc.Total_Differently_Abled_Employees)
            if doc.Type == "Permanent" and doc.Gender == "Male":
                record_json["Male_Permanent"] += total
            elif doc.Type == "Non-Permanent" and doc.Gender == "Male":
                record_json["Male_Non_Permanent"] += total
            elif doc.Type == "Permanent" and doc.Gender == "Female":
                record_json["Female_Permanent"] += total
            elif doc.Type == "Non-Permanent" and doc.Gender == "Female":
                record_json["Female_Non_Permanent"] += total

        # Step 3: From Employees
        emp_docs = Employees.objects.filter(
            Financial_Year=financial_year, Facility=facility
        )
        for doc in emp_docs:
            total = convert_decimal128_to_float(doc.Total_Employees)
            if doc.Type == "Permanent" and doc.Gender == "Male":
                record_json["Male_Permanent"] += total
            elif doc.Type == "Non-Permanent" and doc.Gender == "Male":
                record_json["Male_Non_Permanent"] += total
            elif doc.Type == "Permanent" and doc.Gender == "Female":
                record_json["Female_Permanent"] += total
            elif doc.Type == "Non-Permanent" and doc.Gender == "Female":
                record_json["Female_Non_Permanent"] += total

        # Step 4: Totals and Percentages
        record_json["Total_Male"] = round(record_json["Male_Permanent"] + record_json["Male_Non_Permanent"], 2)
        record_json["Total_Female"] = round(record_json["Female_Permanent"] + record_json["Female_Non_Permanent"], 2)
        total_employees = record_json["Total_Male"] + record_json["Total_Female"]
        if total_employees > 0:
            record_json["Percentage_Male"] = round((record_json["Total_Male"] / total_employees) * 100, 2)
            record_json["Percentage_Female"] = round((record_json["Total_Female"] / total_employees) * 100, 2)

        result.append(record_json)

    return result
