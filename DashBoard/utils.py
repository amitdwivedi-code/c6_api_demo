from decimal import Decimal
from bson.decimal128 import Decimal128
from Workplace.models import *
from datetime import datetime

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

    # Step 1: Get all records from EmployeeSummary
    summaries = EmployeeSummary.objects.all()

    for summary in summaries:
        male_perm = convert_decimal128_to_float(summary.Male_Permanent)
        male_non_perm = convert_decimal128_to_float(summary.Male_Non_Permanent)
        female_perm = convert_decimal128_to_float(summary.Female_Permanent)
        female_non_perm = convert_decimal128_to_float(summary.Female_Non_Permanent)

        total_male = round(male_perm + male_non_perm, 2)
        total_female = round(female_perm + female_non_perm, 2)
        total = total_male + total_female

        record_json = {
            "Financial_Year": summary.Financial_Year,
            "Facility": summary.Facility,
            "Female_Permanent": female_perm,
            "Female_Non_Permanent": female_non_perm,
            "Male_Permanent": male_perm,
            "Male_Non_Permanent": male_non_perm,
            "Total_Male": total_male,
            "Total_Female": total_female,
            "Percentage_Male": round((total_male / total) * 100, 2) if total > 0 else 0.0,
            "Percentage_Female": round((total_female / total) * 100, 2) if total > 0 else 0.0
        }

        result.append(record_json)

    return result


def calculate_total_workers():
    result = []
    summaries = WorkerSummary.objects.all()

    for summary in summaries:
        male_perm = convert_decimal128_to_float(summary.Male_Permanent)
        male_non_perm = convert_decimal128_to_float(summary.Male_Non_Permanent)
        female_perm = convert_decimal128_to_float(summary.Female_Permanent)
        female_non_perm = convert_decimal128_to_float(summary.Female_Non_Permanent)

        total_male = round(male_perm + male_non_perm, 2)
        total_female = round(female_perm + female_non_perm, 2)
        total = total_male + total_female

        result.append({
            "Financial_Year": summary.Financial_Year,
            "Facility": summary.Facility,
            "Female_Permanent": female_perm,
            "Female_Non_Permanent": female_non_perm,
            "Male_Permanent": male_perm,
            "Male_Non_Permanent": male_non_perm,
            "Total_Male": total_male,
            "Total_Female": total_female,
            "Percentage_Male": round((total_male / total) * 100, 2) if total > 0 else 0.0,
            "Percentage_Female": round((total_female / total) * 100, 2) if total > 0 else 0.0
        })

    return result


def get_new_hires_summary(fy=None, facility=None, gender=None, emp_type=None):
    # import pdb;pdb.set_trace()
    if not fy:
        fy = f"FY{datetime.now().year}-{datetime.now().year + 1}"

    emp_qs = EmployeeSummary.objects.filter(Financial_Year=fy)
    worker_qs = WorkerSummary.objects.filter(Financial_Year=fy)

    if facility:
        emp_qs = emp_qs.filter(Facility=facility)
        worker_qs = worker_qs.filter(Facility=facility)

    total_new_hires = 0.0

    for emp in emp_qs:
        if gender == "male":
            if emp_type == "permanent":
                total_new_hires += convert_decimal128_to_float(emp.Male_Permanent)
            elif emp_type == "non_permanent":
                total_new_hires += convert_decimal128_to_float(emp.Male_Non_Permanent)
            else:
                total_new_hires += convert_decimal128_to_float(emp.Male_Permanent) + convert_decimal128_to_float(emp.Male_Non_Permanent)
        elif gender == "female":
            if emp_type == "permanent":
                total_new_hires += convert_decimal128_to_float(emp.Female_Permanent)
            elif emp_type == "non_permanent":
                total_new_hires += convert_decimal128_to_float(emp.Female_Non_Permanent)
            else:
                total_new_hires += convert_decimal128_to_float(emp.Female_Permanent) + convert_decimal128_to_float(emp.Female_Non_Permanent)
        else:
            total_new_hires += (convert_decimal128_to_float(
                emp.Male_Permanent) + convert_decimal128_to_float(emp.Male_Non_Permanent) +
                convert_decimal128_to_float(emp.Female_Permanent) + convert_decimal128_to_float(emp.Female_Non_Permanent)
            )

    for worker in worker_qs:
        if gender == "male":
            if emp_type == "permanent":
                total_new_hires += convert_decimal128_to_float(worker.Male_Permanent)
            elif emp_type == "non_permanent":
                total_new_hires += convert_decimal128_to_float(worker.Male_Non_Permanent)
            else:
                total_new_hires += convert_decimal128_to_float(worker.Male_Permanent) + convert_decimal128_to_float(worker.Male_Non_Permanent)
        elif gender == "female":
            if emp_type == "permanent":
                total_new_hires += convert_decimal128_to_float(worker.Female_Permanent)
            elif emp_type == "non_permanent":
                total_new_hires += convert_decimal128_to_float(worker.Female_Non_Permanent)
            else:
                total_new_hires += convert_decimal128_to_float(worker.Female_Permanent) + convert_decimal128_to_float(worker.Female_Non_Permanent)
        else:
            total_new_hires += (convert_decimal128_to_float(worker.Male_Permanent) + convert_decimal128_to_float(worker.Male_Non_Permanent) +
                convert_decimal128_to_float(worker.Female_Permanent) + convert_decimal128_to_float(worker.Female_Non_Permanent))
            

    return round(total_new_hires, 2)


def get_worker_new_hires_summary(fy=None, facility=None, gender=None, emp_type=None):
    if not fy:
        fy = f"FY{datetime.now().year}-{datetime.now().year + 1}"

    qs = WorkerSummary.objects.filter(Financial_Year=fy)

    if facility:
        qs = qs.filter(Facility=facility)

    total_new_hires = 0.0

    for worker in qs:
        # Gender filter logic (worker model does not have a Gender field)
        # So this check is skipped

        if emp_type == "permanent":
            total_new_hires += convert_decimal128_to_float(worker.Male_Permanent)
            total_new_hires += convert_decimal128_to_float(worker.Female_Permanent)
        elif emp_type == "non_permanent":
            total_new_hires += convert_decimal128_to_float(worker.Male_Non_Permanent)
            total_new_hires += convert_decimal128_to_float(worker.Female_Non_Permanent)
        else:
            total_new_hires += (
                convert_decimal128_to_float(worker.Male_Permanent) +
                convert_decimal128_to_float(worker.Male_Non_Permanent) +
                convert_decimal128_to_float(worker.Female_Permanent) +
                convert_decimal128_to_float(worker.Female_Non_Permanent)
            )

    return round(total_new_hires, 2)


def get_employess_new_hires_summary(fy=None, facility=None, gender=None, emp_type=None):
    if not fy:
        fy = f"FY{datetime.now().year}-{datetime.now().year + 1}"

    qs = EmployeeSummary.objects.filter(Financial_Year=fy)

    if facility:
        qs = qs.filter(Facility=facility)

    total_new_hires = 0.0

    for worker in qs:
        # Gender filter logic (worker model does not have a Gender field)
        # So this check is skipped

        if emp_type == "permanent":
            total_new_hires += convert_decimal128_to_float(worker.Male_Permanent)
            total_new_hires += convert_decimal128_to_float(worker.Female_Permanent)
        elif emp_type == "non_permanent":
            total_new_hires += convert_decimal128_to_float(worker.Male_Non_Permanent)
            total_new_hires += convert_decimal128_to_float(worker.Female_Non_Permanent)
        else:
            total_new_hires += (
                convert_decimal128_to_float(worker.Male_Permanent) +
                convert_decimal128_to_float(worker.Male_Non_Permanent) +
                convert_decimal128_to_float(worker.Female_Permanent) +
                convert_decimal128_to_float(worker.Female_Non_Permanent)
            )

    return round(total_new_hires, 2)

