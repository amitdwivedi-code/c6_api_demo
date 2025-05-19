from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from CompanyDetails.models import *
from Environment.models import *
from django.db import DatabaseError
from decimal import Decimal
from bson.decimal128 import Decimal128
from .utils import *
from django.db.models import Sum, F, FloatField, DecimalField, ExpressionWrapper
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
from django.db.models.functions import Coalesce
from Workplace.models import *

class Companydetails_Dashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Step 1: Get the financial year from the request
            financial_year = request.GET.get('financial_year')
            if not financial_year:
                return Response({"error": "Financial year is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Step 2: Fetch Networth and Turnover data for the given financial year
            networth_data = Networth.objects.filter(Financial_Year=financial_year).first()
            turnover_data = Turnover.objects.filter(Financial_Year=financial_year).first()

            if not networth_data and not turnover_data:
            # Return default values with 0 if any data is missing
                return Response({
                    "financial_year": financial_year,
                    "Q1": 0.0,
                    "Q1_to_Q2": {
                        "change": 0.0,
                        "percent": 0.0
                    },
                    "Q2": 0.0,
                    "Q2_to_Q3": {
                        "change": 0.0,
                        "percent": 0.0
                    },
                    "Q3": 0.0,
                    "Q3_to_Q4": {
                        "change": 0.0,
                        "percent": 0.0
                    },
                    "Q4": 0.0
                }, status=status.HTTP_200_OK)

            Q1_turn = sum([safe_decimal(getattr(turnover_data, f"Turnover_{m}", 0)) for m in ["Apr", "May", "Jun"]])
            Q1_net = sum([safe_decimal(getattr(networth_data, f"Networth_{m}", 0)) for m in ["Apr", "May", "Jun"]])
            Q1 = ratio(Q1_turn, Q1_net)

            Q2_turn = sum([safe_decimal(getattr(turnover_data, f"Turnover_{m}", 0)) for m in ["Jul", "Aug", "Sep"]])
            Q2_net = sum([safe_decimal(getattr(networth_data, f"Networth_{m}", 0)) for m in ["Jul", "Aug", "Sep"]])
            Q2 = ratio(Q2_turn, Q2_net)

            Q3_turn = sum([safe_decimal(getattr(turnover_data, f"Turnover_{m}", 0)) for m in ["Oct", "Nov", "Dec"]])
            Q3_net = sum([safe_decimal(getattr(networth_data, f"Networth_{m}", 0)) for m in ["Oct", "Nov", "Dec"]])
            Q3 = ratio(Q3_turn, Q3_net)

            Q4_turn = sum([safe_decimal(getattr(turnover_data, f"Turnover_{m}", 0)) for m in ["Jan", "Feb", "Mar"]])
            Q4_net = sum([safe_decimal(getattr(networth_data, f"Networth_{m}", 0)) for m in ["Jan", "Feb", "Mar"]])
            Q4 = ratio(Q4_turn, Q4_net)

            # Step 7: Construct the response with change percentages between quarters
            response_data = {
                "financial_year": financial_year,
                "Q1": Q1,
                "Q1_to_Q2": get_change(Q1, Q2),
                "Q2": Q2,
                "Q2_to_Q3": get_change(Q2, Q3),
                "Q3": Q3,
                "Q3_to_Q4": get_change(Q3, Q4),
                "Q4": Q4
            }

            # Step 8: Return the response with the calculated data
            return Response(response_data, status=status.HTTP_200_OK)

        except DatabaseError as db_err:
            return Response({"error": "Database error occurred", "details": str(db_err)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EnergyConsumptionBreakdown_Dashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
            try:
                financial_year = request.query_params.get('financial_year')
                facility = request.query_params.get('facility')

                # Filtered querysets
                elec_qs = Electricity_Consumption_GJ.objects.all()
                fuel_qs = Fuel_Consumption_Onsite_Combustion_GJ.objects.all()

                if financial_year:
                    elec_qs = elec_qs.filter(Financial_Year=financial_year)
                    fuel_qs = fuel_qs.filter(Financial_Year=financial_year)
                if facility:
                    elec_qs = elec_qs.filter(Facility=facility)
                    fuel_qs = fuel_qs.filter(Facility=facility)

                # Structure: {facility: {source: total_value}}
                elec_grouped = defaultdict(lambda: defaultdict(Decimal))
                fuel_grouped = defaultdict(lambda: defaultdict(Decimal))

                for obj in elec_qs:
                    fac = obj.Facility or "Unknown"
                    src = obj.Source or "Unknown"
                    value = obj.Total_Electricity_Consumption
                    value = value.to_decimal() if hasattr(value, "to_decimal") else (value or Decimal("0.00"))
                    elec_grouped[fac][src] += value

                for obj in fuel_qs:
                    fac = obj.Facility or "Unknown"
                    ftype = obj.Fuel_Type or "Unknown"
                    value = obj.Total_Fuel_Consumption
                    value = value.to_decimal() if hasattr(value, "to_decimal") else (value or Decimal("0.00"))
                    fuel_grouped[fac][ftype] += value

                # All facilities
                all_facilities = set(elec_grouped.keys()) | set(fuel_grouped.keys())

                result = []

                for fac in all_facilities:
                    elec_sources = elec_grouped.get(fac, {})
                    fuel_types = fuel_grouped.get(fac, {})

                    total_elec = sum(elec_sources.values()) or Decimal("0.00")
                    total_fuel = sum(fuel_types.values()) or Decimal("0.00")

                    elec_detail = [
                        {
                            "Source": src,
                            "Consumption": float(val),
                            "Percentage": float((val / total_elec * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) if total_elec else 0.0
                        }
                        for src, val in elec_sources.items()
                    ]

                    fuel_detail = [
                        {
                            "Fuel_Type": ft,
                            "Consumption": float(val),
                            "Percentage": float((val / total_fuel * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) if total_fuel else 0.0
                        }
                        for ft, val in fuel_types.items()
                    ]

                    result.append({
                        "Facility": fac,
                        "Total_Electricity_Consumption": float(total_elec),
                        "Electricity_Details": elec_detail,
                        "Total_Fuel_Consumption": float(total_fuel),
                        "Fuel_Details": fuel_detail,
                    })

                return Response(result, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Electricity_Distribution_Dashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            financial_year = request.query_params.get('financial_year')
            facility = request.query_params.get('facility')

            queryset = Electricity_Consumption_GJ.objects.all()

            # Apply filters
            if financial_year:
                queryset = queryset.filter(Financial_Year=financial_year)
            if facility:
                queryset = queryset.filter(Facility=facility)

            grouped = defaultdict(Decimal)

            for obj in queryset:
                consumption = obj.Total_Electricity_Consumption
                if consumption is None:
                    consumption = Decimal('0.00')
                else:
                    consumption = consumption.to_decimal()

                # Decide grouping key
                if financial_year and facility:
                    key = (obj.Financial_Year, obj.Facility, obj.Source)
                elif financial_year:
                    key = (obj.Source,)
                elif facility:
                    key = (obj.Facility, obj.Source)
                else:
                    # No filters — group only by source
                    key = (obj.Source,)

                grouped[key] += consumption
            
            total_sum = sum(grouped.values())

            # Prepare result
            result = []
            for key, total in grouped.items():
                percentage = (total / total_sum * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if financial_year and facility:
                    year, fac, source = key
                    result.append({
                        "Financial_Year": year,
                        "Facility": fac,
                        "Source": source,
                        "Total_Electricity_Consumption": float(total),
                         "Percentage": float(percentage)
                    })
                elif financial_year:
                    source, = key
                    result.append({
                        "Financial_Year": financial_year,
                        "Source": source,
                        "Total_Electricity_Consumption": float(total),
                         "Percentage": float(percentage)
                    })
                elif facility:
                    fac, source = key
                    result.append({
                        "Facility": fac,
                        "Source": source,
                        "Total_Electricity_Consumption": float(total),
                         "Percentage": float(percentage)
                    })
                else:
                    source, = key
                    result.append({
                        "Source": source,
                        "Total_Electricity_Consumption": float(total),
                         "Percentage": float(percentage)
                    })

            return Response(result)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Water_Consumption_Dashboard(APIView):
    permission_classes= [IsAuthenticated]
    def get(self, request):
        try:
            financial_year = request.query_params.get('financial_year')
            facility = request.query_params.get('facility')

            queryset = Water_Consumption.objects.all()

            if financial_year:
                queryset = queryset.filter(Financial_Year=financial_year)
            if facility:
                queryset = queryset.filter(Facility=facility)

            months = [
                'Water_Consumption_Apr', 'Water_Consumption_May', 'Water_Consumption_Jun',
                'Water_Consumption_Jul', 'Water_Consumption_Aug', 'Water_Consumption_Sep',
                'Water_Consumption_Oct', 'Water_Consumption_Nov', 'Water_Consumption_Dec',
                'Water_Consumption_Jan', 'Water_Consumption_Feb', 'Water_Consumption_Mar'
            ]

            response_data = []

            # Case 1: No filters → group by Facility
            if not financial_year and not facility:
                grouped = defaultdict(lambda: {month: Decimal('0.00') for month in months})
                for record in queryset:
                    fac = record.Facility or "Unknown"
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            grouped[fac][month] += val.to_decimal()
                for fac, data in grouped.items():
                    response_data.append({
                        "Facility": fac,
                        "Financial_Year": "All",
                        **{month: float(val) for month, val in data.items()}
                    })

            # Case 2: Only financial year → group by Facility
            elif financial_year and not facility:
                grouped = defaultdict(lambda: {month: Decimal('0.00') for month in months})
                for record in queryset:
                    fac = record.Facility or "Unknown"
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            grouped[fac][month] += val.to_decimal()
                for fac, data in grouped.items():
                    response_data.append({
                        "Facility": fac,
                        "Financial_Year": financial_year,
                        **{month: float(val) for month, val in data.items()}
                    })

            # Case 3: Only facility → aggregate for all years
            elif facility and not financial_year:
                result = {month: Decimal('0.00') for month in months}
                for record in queryset:
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            result[month] += val.to_decimal()
                response_data.append({
                    "Facility": facility,
                    "Financial_Year": "All",
                    **{month: float(val) for month, val in result.items()}
                })

            # Case 4: Both filters → single facility & year
            else:
                result = {month: Decimal('0.00') for month in months}
                for record in queryset:
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            result[month] += val.to_decimal()
                response_data.append({
                    "Facility": facility,
                    "Financial_Year": financial_year,
                    **{month: float(val) for month, val in result.items()}
                })

            return Response(response_data)

        except Exception as e:
            return Response({"error": str(e)}, status=500)



class Scope1_Emission_Dashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            financial_year = request.query_params.get('financial_year')
            facility = request.query_params.get('facility')

            queryset = Scope1_Emissions_by_Facilities.objects.all()

            if financial_year:
                queryset = queryset.filter(Financial_Year=financial_year)
            if facility:
                queryset = queryset.filter(Facility=facility)

            months = [
                'Emission_Apr', 'Emission_May', 'Emission_Jun', 'Emission_Jul',
                'Emission_Aug', 'Emission_Sep', 'Emission_Oct', 'Emission_Nov',
                'Emission_Dec', 'Emission_Jan', 'Emission_Feb', 'Emission_Mar'
            ]

            # Case 1: No filters — group by Facility
            if not financial_year and not facility:
                grouped = defaultdict(lambda: {
                    'Financial_Year': 'All',
                    'data': {month: Decimal('0.00') for month in months},
                    'Total_Emission': Decimal('0.00')
                })

                for record in queryset:
                    fac = record.Facility or "Unknown"
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            grouped[fac]['data'][month] += val.to_decimal()

                    total = record.Total_Emission
                    if total:
                        grouped[fac]['Total_Emission'] += total.to_decimal()

                response_data = []
                for fac, data in grouped.items():
                    entry = {
                        'Facility': fac,
                        'Financial_Year': 'All',
                        'Total_Emission': float(data['Total_Emission']),
                        **{month: float(v) for month, v in data['data'].items()}
                    }
                    response_data.append(entry)

            # Case 2: Only year — group by facility for that year
            elif financial_year and not facility:
                grouped = defaultdict(lambda: {
                    'Financial_Year': financial_year,
                    'data': {month: Decimal('0.00') for month in months},
                    'Total_Emission': Decimal('0.00')
                })

                for record in queryset:
                    fac = record.Facility or "Unknown"
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            grouped[fac]['data'][month] += val.to_decimal()

                    total = record.Total_Emission
                    if total:
                        grouped[fac]['Total_Emission'] += total.to_decimal()

                response_data = []
                for fac, data in grouped.items():
                    entry = {
                        'Facility': fac,
                        'Financial_Year': financial_year,
                        'Total_Emission': float(data['Total_Emission']),
                        **{month: float(v) for month, v in data['data'].items()}
                    }
                    response_data.append(entry)

            # Case 3: only facility - group by all year
            elif facility and not financial_year:
                result = {
                    month: Decimal('0.00') for month in months
                }
                total_sum = Decimal('0.00')

                for record in queryset:
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            result[month] += val.to_decimal()

                    total = record.Total_Emission
                    if total:
                        total_sum += total.to_decimal()
                        
                response_data = {
                        'Facility': facility,
                        'Financial_Year': 'All',  # <-- fixed here
                        'Total_Emission': float(total_sum),
                        **{month: float(v) for month, v in result.items()}
                    }
            # Case 4: Both filters — exact match
            else:
                result = {month: Decimal('0.00') for month in months}
                total_sum = Decimal('0.00')
                for record in queryset:
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            result[month] += val.to_decimal()
                    total = record.Total_Emission
                    if total:
                        total_sum += total.to_decimal()

                response_data = {
                    'Facility': facility,
                    'Financial_Year': financial_year,
                    'Total_Emission': float(total_sum),
                    **{month: float(v) for month, v in result.items()}
                }

            return Response(response_data)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

class Fuel_Distribution_Dashboard(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            
            financial_year = request.query_params.get('financial_year')
            facility = request.query_params.get('facility')

            queryset = Fuel_Consumption_Onsite_Combustion_GJ.objects.all()

            # Apply filters
            if financial_year:
                queryset = queryset.filter(Financial_Year=financial_year)
            if facility:
                queryset = queryset.filter(Facility=facility)

            grouped = defaultdict(Decimal)

            for obj in queryset:
                consumption = obj.Total_Fuel_Consumption
                if consumption is None:
                    consumption = Decimal('0.00')
                else:
                    consumption = consumption.to_decimal()

                # Decide grouping key
                if financial_year and facility:
                    key = (obj.Financial_Year, obj.Facility, obj.Fuel_Type)
                elif financial_year:
                    key = (obj.Fuel_Type,)
                elif facility:
                    key = (obj.Facility, obj.Fuel_Type)
                else:
                    # No filters — group only by fuel_type
                    key = (obj.Fuel_Type,)

                grouped[key] += consumption
            
            total_sum = sum(grouped.values())

            # Prepare result
            result = []
            for key, total in grouped.items():
                percentage = (total / total_sum * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if financial_year and facility:
                    year, fac, fuel_type = key
                    result.append({
                        "Financial_Year": year,
                        "Facility": fac,
                        "Fuel_Type": fuel_type,
                        "Total_Fuel_Consumption": float(total),
                         "Percentage": float(percentage)
                    })
                elif financial_year:
                    fuel_type, = key
                    result.append({
                        "Financial_Year": financial_year,
                        "Fuel_Type": fuel_type,
                        "Total_Fuel_Consumption": float(total),
                         "Percentage": float(percentage)
                    })
                elif facility:
                    fac, fuel_type = key
                    result.append({
                        "Facility": fac,
                        "Fuel_Type": fuel_type,
                        "Total_Fuel_Consumption": float(total),
                         "Percentage": float(percentage)
                    })
                else:
                    fuel_type, = key
                    result.append({
                        "Fuel_Type": fuel_type,
                        "Total_Fuel_Consumption": float(total),
                         "Percentage": float(percentage)
                    })

            return Response(result)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Scope2_Emission_Dashboard(APIView):
    permission_classes = [IsAuthenticated]

    
    def get(self, request):
        try:
            financial_year = request.query_params.get('financial_year')
            facility = request.query_params.get('facility')

            queryset = Scope2_Emissions_by_Facilities.objects.all()

            if financial_year:
                queryset = queryset.filter(Financial_Year=financial_year)
            if facility:
                queryset = queryset.filter(Facility=facility)

            grouped = defaultdict(Decimal)

            for obj in queryset:
                total = obj.Total_Emission 
                if total is None:
                    total = Decimal('0.00')
                else:
                    total = total.to_decimal()  

                if financial_year and facility:
                    key = (facility, financial_year)
                elif financial_year:
                    key = (obj.Facility or "Unknown", financial_year)
                elif facility:
                    key = (facility, "All")
                else:
                    key = (obj.Facility or "Unknown", "All")

                grouped[key] += total

            total_sum = sum(grouped.values()) or Decimal('1.00')  # prevent division by zero

            result = []
            for (fac, year), total in grouped.items():
                percentage = (total / total_sum * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                result.append({
                    "Facility": fac,
                    "Financial_Year": year,
                    "Total_Emission": float(total),
                    "Percentage": float(percentage)
                })

            return Response(result)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Combined_Fuel_Consumption_Dashboard(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            financial_year = request.query_params.get('financial_year')
            facility = request.query_params.get('facility')

            queryset = Fuel_Consumption_Onsite_Combustion_GJ.objects.all()

            if financial_year:
                queryset = queryset.filter(Financial_Year=financial_year)
            if facility:
                queryset = queryset.filter(Facility=facility)

            # 1. Monthly Consumption Grouped by Fuel_Type
            months = [
                'Fuel_Consumption_Apr', 'Fuel_Consumption_May', 'Fuel_Consumption_Jun', 'Fuel_Consumption_Jul',
                'Fuel_Consumption_Aug', 'Fuel_Consumption_Sep', 'Fuel_Consumption_Oct', 'Fuel_Consumption_Nov',
                'Fuel_Consumption_Dec', 'Fuel_Consumption_Jan', 'Fuel_Consumption_Feb', 'Fuel_Consumption_Mar'
            ]

            monthly_grouped = defaultdict(lambda: {
                'data': {month: Decimal('0.00') for month in months},
                'Total_Fuel_Consumption': Decimal('0.00'),
                'Facility': facility or 'All',
                'Financial_Year': financial_year or 'All'
            })

            for record in queryset:
                fuel_type = record.Fuel_Type or 'Unknown'
                for month in months:
                    val = getattr(record, month)
                    if val:
                        monthly_grouped[fuel_type]['data'][month] += val.to_decimal()

                total = record.Total_Fuel_Consumption
                if total:
                    monthly_grouped[fuel_type]['Total_Fuel_Consumption'] += total.to_decimal()

            monthly_response = []
            for fuel_type, data in monthly_grouped.items():
                entry = {
                    'Fuel_Type': fuel_type,
                    'Facility': data['Facility'],
                    'Financial_Year': data['Financial_Year'],
                    'Total_Fuel_Consumption': float(data['Total_Fuel_Consumption']),
                    **{month: float(v) for month, v in data['data'].items()}
                }
                monthly_response.append(entry)

            # 2. Distribution Calculation (Percentage)
            distribution_grouped = defaultdict(Decimal)
            for obj in queryset:
                consumption = obj.Total_Fuel_Consumption
                if consumption is None:
                    consumption = Decimal('0.00')
                else:
                    consumption = consumption.to_decimal()

                # Grouping keys
                if financial_year and facility:
                    key = (obj.Financial_Year, obj.Facility, obj.Fuel_Type)
                elif financial_year:
                    key = (obj.Fuel_Type,)
                elif facility:
                    key = (obj.Facility, obj.Fuel_Type)
                else:
                    key = (obj.Fuel_Type,)

                distribution_grouped[key] += consumption

            total_sum = sum(distribution_grouped.values())

            distribution_response = []
            for key, total in distribution_grouped.items():
                percentage = (total / total_sum * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                if financial_year and facility:
                    year, fac, fuel_type = key
                    distribution_response.append({
                        "Financial_Year": year,
                        "Facility": fac,
                        "Fuel_Type": fuel_type,
                        "Total_Fuel_Consumption": float(total),
                        "Percentage": float(percentage)
                    })
                elif financial_year:
                    fuel_type, = key
                    distribution_response.append({
                        "Financial_Year": financial_year,
                        "Fuel_Type": fuel_type,
                        "Total_Fuel_Consumption": float(total),
                        "Percentage": float(percentage)
                    })
                elif facility:
                    fac, fuel_type = key
                    distribution_response.append({
                        "Facility": fac,
                        "Fuel_Type": fuel_type,
                        "Total_Fuel_Consumption": float(total),
                        "Percentage": float(percentage)
                    })
                else:
                    fuel_type, = key
                    distribution_response.append({
                        "Fuel_Type": fuel_type,
                        "Total_Fuel_Consumption": float(total),
                        "Percentage": float(percentage)
                    })
                    
             # ---------- YEAR WISE TOTAL Fuel ----------
            yearly_grouped = defaultdict(Decimal)
            for record in queryset:
                fy = record.Financial_Year or "Unknown"
                total = record.Total_Fuel_Consumption.to_decimal() if record.Total_Fuel_Consumption else Decimal('0.00')
                yearly_grouped[fy] += total

            def extract_year(fy_str):
                try:
                    return int(fy_str[2:6])
                except:
                    return 0

            year_wise_data = []
            for fy, total in sorted(yearly_grouped.items(), key=lambda x: extract_year(x[0]), reverse=True):
                year_wise_data.append({
                    "Financial_Year": fy,
                    "Total_Fuel_Consumption": float(total)
                })
            return Response({
                "monthly_consumption": monthly_response,
                "fuel_distribution": distribution_response,
                "year_wise_data": year_wise_data
            })

        except Exception as e:
            return Response({'error': str(e)}, status=500)


class Combined_Electricity_Consumption_Dashboard(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            financial_year = request.query_params.get('financial_year')
            facility = request.query_params.get('facility')

            queryset = Electricity_Consumption_GJ.objects.all()

            if financial_year:
                queryset = queryset.filter(Financial_Year=financial_year)
            if facility:
                queryset = queryset.filter(Facility=facility)

            # -------- 1. Monthly Grouping ----------
            months = [
                'Electricity_Consumption_Apr', 'Electricity_Consumption_May', 'Electricity_Consumption_Jun', 'Electricity_Consumption_Jul',
                'Electricity_Consumption_Aug', 'Electricity_Consumption_Sep', 'Electricity_Consumption_Oct', 'Electricity_Consumption_Nov',
                'Electricity_Consumption_Dec', 'Electricity_Consumption_Jan', 'Electricity_Consumption_Feb', 'Electricity_Consumption_Mar'
            ]

            monthly_grouped = defaultdict(lambda: {
                'data': {month: Decimal('0.00') for month in months},
                'Total_Electricity_Consumption': Decimal('0.00'),
                'Facility': facility or 'All',
                'Financial_Year': financial_year or 'All'
            })

            for record in queryset:
                source = record.Source or 'Unknown'
                for month in months:
                    val = getattr(record, month)
                    if val:
                        monthly_grouped[source]['data'][month] += val.to_decimal()

                total = record.Total_Electricity_Consumption
                if total:
                    monthly_grouped[source]['Total_Electricity_Consumption'] += total.to_decimal()

            monthly_response = []
            for source, data in monthly_grouped.items():
                entry = {
                    'Source': source,
                    'Facility': data['Facility'],
                    'Financial_Year': data['Financial_Year'],
                    'Total_Electricity_Consumption': float(data['Total_Electricity_Consumption']),
                    **{month: float(v) for month, v in data['data'].items()}
                }
                monthly_response.append(entry)

            # -------- 2. Distribution with Percentages ----------
            distribution_grouped = defaultdict(Decimal)

            for obj in queryset:
                consumption = obj.Total_Electricity_Consumption
                if consumption is None:
                    consumption = Decimal('0.00')
                else:
                    consumption = consumption.to_decimal()

                if financial_year and facility:
                    key = (obj.Financial_Year, obj.Facility, obj.Source)
                elif financial_year:
                    key = (obj.Source,)
                elif facility:
                    key = (obj.Facility, obj.Source)
                else:
                    key = (obj.Source,)

                distribution_grouped[key] += consumption

            total_sum = sum(distribution_grouped.values())

            distribution_response = []
            for key, total in distribution_grouped.items():
                percentage = (total / total_sum * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                if financial_year and facility:
                    year, fac, source = key
                    distribution_response.append({
                        "Financial_Year": year,
                        "Facility": fac,
                        "Source": source,
                        "Total_Electricity_Consumption": float(total),
                        "Percentage": float(percentage)
                    })
                elif financial_year:
                    source, = key
                    distribution_response.append({
                        "Financial_Year": financial_year,
                        "Source": source,
                        "Total_Electricity_Consumption": float(total),
                        "Percentage": float(percentage)
                    })
                elif facility:
                    fac, source = key
                    distribution_response.append({
                        "Facility": fac,
                        "Source": source,
                        "Total_Electricity_Consumption": float(total),
                        "Percentage": float(percentage)
                    })
                else:
                    source, = key
                    distribution_response.append({
                        "Source": source,
                        "Total_Electricity_Consumption": float(total),
                        "Percentage": float(percentage)
                    })


            # -------- 3. Year Wise  Total Electricity ----------
            yearly_grouped = defaultdict(Decimal)
            for record in queryset:
                fy = record.Financial_Year or "Unknown"
                total = record.Total_Electricity_Consumption.to_decimal() if record.Total_Electricity_Consumption else Decimal('0.00')
                yearly_grouped[fy] += total

            def extract_year(fy_str):
                try:
                    return int(fy_str[2:6])
                except:
                    return 0

            year_wise_data = []
            for fy, total in sorted(yearly_grouped.items(), key=lambda x: extract_year(x[0]), reverse=True):
                year_wise_data.append({
                    "Financial_Year": fy,
                    "Total_Electricity_Consumption": float(total)
                })

            # -------- Final Response ----------
            return Response({
                "monthly_consumption": monthly_response,
                "electricity_distribution": distribution_response,
                "year_wise_data" : year_wise_data
            })

        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
 
class Waste_Generated_Dashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            financial_year = request.query_params.get('financial_year')
            facility = request.query_params.get('facility')

            queryset = Waste_Generated.objects.all()
            if financial_year:
                queryset = queryset.filter(Financial_Year=financial_year)
            if facility:
                queryset = queryset.filter(Facility=facility)

            months = [
                'Waste_Generated_Apr', 'Waste_Generated_May', 'Waste_Generated_Jun', 'Waste_Generated_Jul',
                'Waste_Generated_Aug', 'Waste_Generated_Sep', 'Waste_Generated_Oct', 'Waste_Generated_Nov',
                'Waste_Generated_Dec', 'Waste_Generated_Jan', 'Waste_Generated_Feb', 'Waste_Generated_Mar'
            ]

            # ---------- MONTH-WISE DATA ----------
            grouped = defaultdict(lambda: {
                'data': {month: Decimal('0.00') for month in months},
                'Waste_Generated_Total': Decimal('0.00')
            })

            for record in queryset:
                waste_type = record.Type or 'Unknown'
                for month in months:
                    val = getattr(record, month)
                    if val:
                        grouped[waste_type]['data'][month] += val.to_decimal()

                total = record.Waste_Generated_Total
                if total:
                    grouped[waste_type]['Waste_Generated_Total'] += total.to_decimal()

            month_wise_data = []
            for waste_type, data in grouped.items():
                entry = {
                    'Waste_Type': waste_type,
                    'Facility': facility if facility else 'All',
                    'Financial_Year': financial_year if financial_year else 'All',
                    'Waste_Generated_Total': float(data['Waste_Generated_Total']),
                    **{month: float(val) for month, val in data['data'].items()}
                }
                month_wise_data.append(entry)

            # ---------- YEAR-WISE DATA ----------
            yearly_grouped = defaultdict(Decimal)
            for record in queryset:  # Reuse already-filtered queryset
                fy = record.Financial_Year or "Unknown"
                total = record.Waste_Generated_Total
                if total:
                    yearly_grouped[fy] += total.to_decimal()

            def extract_year(fy_str):
                try:
                    return int(fy_str[2:6])
                except:
                    return 0

            year_wise_data = []
            for fy, total in sorted(yearly_grouped.items(), key=lambda x: extract_year(x[0]), reverse=True):
                year_wise_data.append({
                    "Financial_Year": fy,
                    "Total_Waste_Generated": float(total)
                })

            return Response({
                "month_wise_data": month_wise_data,
                "year_wise_data": year_wise_data
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

      
class Waste_Recovered_Dashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            financial_year = request.query_params.get('financial_year')
            facility = request.query_params.get('facility')

            queryset = Waste_Recovered.objects.all()
            if financial_year:
                queryset = queryset.filter(Financial_Year=financial_year)
            if facility:
                queryset = queryset.filter(Facility=facility)

            months = [
                'Waste_Recovered_Apr', 'Waste_Recovered_May', 'Waste_Recovered_Jun', 'Waste_Recovered_Jul',
                'Waste_Recovered_Aug', 'Waste_Recovered_Sep', 'Waste_Recovered_Oct', 'Waste_Recovered_Nov',
                'Waste_Recovered_Dec', 'Waste_Recovered_Jan', 'Waste_Recovered_Feb', 'Waste_Recovered_Mar'
            ]

            # ---------- MONTH-WISE DATA ----------
            grouped = defaultdict(lambda: {
                'data': {month: Decimal('0.00') for month in months},
                'Waste_Recovered_Total': Decimal('0.00')
            })

            for record in queryset:
                waste_type = record.Waste_Recovered_Category or 'Unknown'
                for month in months:
                    val = getattr(record, month)
                    if val:
                        grouped[waste_type]['data'][month] += val.to_decimal()
                total = record.Waste_Recovered_Total
                if total:
                    grouped[waste_type]['Waste_Recovered_Total'] += total.to_decimal()

            month_wise_data = []
            for waste_type, data in grouped.items():
                entry = {
                    'Waste_Type': waste_type,
                    'Facility': facility if facility else 'All',
                    'Financial_Year': financial_year if financial_year else 'All',
                    'Waste_Recovered_Total': float(data['Waste_Recovered_Total']),
                    **{month: float(val) for month, val in data['data'].items()}
                }
                month_wise_data.append(entry)

            # ---------- YEAR-WISE RECYCLED & REUSED ----------
            recycled_yearly = defaultdict(Decimal)
            reused_yearly = defaultdict(Decimal)

            # Re-filtered base data for grouping without monthly totals
           
            for record in queryset:
                fy = record.Financial_Year or "Unknown"
                category = (record.Waste_Recovered_Category or "").strip().lower()
                total = record.Waste_Recovered_Total or Decimal('0.00')

                if category == "recycled":
                    recycled_yearly[fy] += total.to_decimal()
                elif category == "re-used":
                    reused_yearly[fy] += total.to_decimal()

            def extract_year(fy_str):
                try:
                    return int(fy_str[2:6])
                except:
                    return 0

            year_wise_recycled_data = [
                {"Financial_Year": fy, "Waste_Recycled_Total": float(total)}
                for fy, total in sorted(recycled_yearly.items(), key=lambda x: extract_year(x[0]), reverse=True)
            ]

            year_wise_reused_data = [
                {"Financial_Year": fy, "Waste_Reused_Total": float(total)}
                for fy, total in sorted(reused_yearly.items(), key=lambda x: extract_year(x[0]), reverse=True)
            ]

            return Response({
                "month_wise_data": month_wise_data,
                "year_wise_recycled_data": year_wise_recycled_data,
                "year_wise_reused_data": year_wise_reused_data
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

class Waste_Disposed_Dashboard(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            financial_year = request.query_params.get('financial_year')
            facility = request.query_params.get('facility')

            queryset = Waste_Disposed.objects.all()
            if financial_year:
                queryset = queryset.filter(Financial_Year=financial_year)
            if facility:
                queryset = queryset.filter(Facility=facility)

            months = [
                'Waste_Disposed_Apr', 'Waste_Disposed_May', 'Waste_Disposed_Jun', 'Waste_Disposed_Jul',
                'Waste_Disposed_Aug', 'Waste_Disposed_Sep', 'Waste_Disposed_Oct', 'Waste_Disposed_Nov',
                'Waste_Disposed_Dec', 'Waste_Disposed_Jan', 'Waste_Disposed_Feb', 'Waste_Disposed_Mar'
            ]

            # ---------- MONTH-WISE DATA ----------
            grouped = defaultdict(lambda: {
                'data': {month: Decimal('0.00') for month in months},
                'Waste_Disposed_Total': Decimal('0.00')
            })

            for record in queryset:
                waste_type = record.Waste_Disposed_Category or 'Unknown'

                for month in months:
                    val = getattr(record, month)
                    if val:
                        grouped[waste_type]['data'][month] += val.to_decimal()

                total = record.Waste_Disposed_Total
                if total:
                    grouped[waste_type]['Waste_Disposed_Total'] += total.to_decimal()

            month_wise_data = []
            for waste_type, data in grouped.items():
                entry = {
                    'Waste_Type': waste_type,
                    'Facility': facility if facility else 'All',
                    'Financial_Year': financial_year if financial_year else 'All',
                    'Waste_Disposed_Total': float(data['Waste_Disposed_Total']),
                    **{month: float(val) for month, val in data['data'].items()}
                }
                month_wise_data.append(entry)

            # ---------- YEAR-WISE DATA (Incineration & Landfilling) ----------
            incineration_yearly = defaultdict(Decimal)
            landfilling_yearly = defaultdict(Decimal)

            yearly_queryset = Waste_Disposed.objects.all()
            if financial_year:
                yearly_queryset = yearly_queryset.filter(Financial_Year=financial_year)
            if facility:
                yearly_queryset = yearly_queryset.filter(Facility=facility)

            for record in yearly_queryset:
                fy = record.Financial_Year or "Unknown"
                category = (record.Waste_Disposed_Category or "").strip().lower()
                total = record.Waste_Disposed_Total or Decimal('0.00')

                if category == "incineration":
                    incineration_yearly[fy] += total.to_decimal()
                elif category == "landfilling":
                    landfilling_yearly[fy] += total.to_decimal()

            def extract_year(fy_str):
                try:
                    return int(fy_str[2:6])
                except:
                    return 0

            year_wise_incinerated_data = [
                {"Financial_Year": fy, "Waste_Incinerated_Total": float(total)}
                for fy, total in sorted(incineration_yearly.items(), key=lambda x: extract_year(x[0]), reverse=True)
            ]

            year_wise_landfilling_data = [
                {"Financial_Year": fy, "Waste_Landfilled_Total": float(total)}
                for fy, total in sorted(landfilling_yearly.items(), key=lambda x: extract_year(x[0]), reverse=True)
            ]

            return Response({
                "month_wise_data": month_wise_data,
                "year_wise_incinerated_data": year_wise_incinerated_data,
                "year_wise_landfilling_data": year_wise_landfilling_data
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)
class Combined_Scope1_Emission_Dashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            financial_year = request.query_params.get('financial_year')
            facility = request.query_params.get('facility')

            months = [
                'Emission_Apr', 'Emission_May', 'Emission_Jun', 'Emission_Jul',
                'Emission_Aug', 'Emission_Sep', 'Emission_Oct', 'Emission_Nov',
                'Emission_Dec', 'Emission_Jan', 'Emission_Feb', 'Emission_Mar'
            ]

            # ---------- FACILITY-WISE DATA ----------
            queryset = Scope1_Emissions_by_Facilities.objects.all()
            if financial_year:
                queryset = queryset.filter(Financial_Year=financial_year)
            if facility:
                queryset = queryset.filter(Facility=facility)

            facility_data = []

            if not financial_year and not facility:
                grouped = defaultdict(lambda: {
                    'Financial_Year': 'All',
                    'data': {month: Decimal('0.00') for month in months},
                    'Total_Emission': Decimal('0.00')
                })
                for record in queryset:
                    fac = record.Facility or "Unknown"
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            grouped[fac]['data'][month] += val.to_decimal()
                    if record.Total_Emission:
                        grouped[fac]['Total_Emission'] += record.Total_Emission.to_decimal()

                for fac, data in grouped.items():
                    entry = {
                        'Facility': fac,
                        'Financial_Year': data['Financial_Year'],
                        'Total_Emission': float(data['Total_Emission']),
                        **{month: float(v) for month, v in data['data'].items()}
                    }
                    facility_data.append(entry)

            elif financial_year and not facility:
                grouped = defaultdict(lambda: {
                    'Financial_Year': financial_year,
                    'data': {month: Decimal('0.00') for month in months},
                    'Total_Emission': Decimal('0.00')
                })
                for record in queryset:
                    fac = record.Facility or "Unknown"
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            grouped[fac]['data'][month] += val.to_decimal()
                    if record.Total_Emission:
                        grouped[fac]['Total_Emission'] += record.Total_Emission.to_decimal()

                for fac, data in grouped.items():
                    entry = {
                        'Facility': fac,
                        'Financial_Year': financial_year,
                        'Total_Emission': float(data['Total_Emission']),
                        **{month: float(v) for month, v in data['data'].items()}
                    }
                    facility_data.append(entry)

            elif facility and not financial_year:
                result = {month: Decimal('0.00') for month in months}
                total_sum = Decimal('0.00')
                for record in queryset:
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            result[month] += val.to_decimal()
                    if record.Total_Emission:
                        total_sum += record.Total_Emission.to_decimal()

                facility_data = [{
                    'Facility': facility,
                    'Financial_Year': 'All',
                    'Total_Emission': float(total_sum),
                    **{month: float(v) for month, v in result.items()}
                }]

            else:
                result = {month: Decimal('0.00') for month in months}
                total_sum = Decimal('0.00')
                for record in queryset:
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            result[month] += val.to_decimal()
                    if record.Total_Emission:
                        total_sum += record.Total_Emission.to_decimal()

                facility_data = [{
                    'Facility': facility,
                    'Financial_Year': financial_year,
                    'Total_Emission': float(total_sum),
                    **{month: float(v) for month, v in result.items()}
                }]

            # ---------- FUEL TYPE PERCENTAGE DATA ----------
            fuel_queryset = Scope1_Emissions_by_Fuel.objects.all()
            if financial_year:
                fuel_queryset = fuel_queryset.filter(Financial_Year=financial_year)

            fuel_grouped = defaultdict(Decimal)
            for record in fuel_queryset:
                fuel = record.Fuel_Type or "Unknown"
                total = record.Total_Emission.to_decimal() if record.Total_Emission else Decimal('0.00')
                fuel_grouped[fuel] += total

            total_fuel_emission = sum(fuel_grouped.values()) or Decimal('1.00')
            fuel_data = []
            for fuel_type, total in fuel_grouped.items():
                percentage = (total / total_fuel_emission * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                fuel_data.append({
                    "Fuel_Type": fuel_type,
                    "Total_Emission": float(total),
                    "Percentage": float(percentage),
                    "Financial_Year": financial_year or "All"
                })

           # ---------- YEAR WISE TOTAL EMISSION ----------
            
            yearly_grouped = defaultdict(Decimal)
            for record in queryset:
                fy = record.Financial_Year or "Unknown"
                total = record.Total_Emission.to_decimal() if record.Total_Emission else Decimal('0.00')
                yearly_grouped[fy] += total

            def extract_year(fy_str):
                try:
                    return int(fy_str[2:6])
                except:
                    return 0

            year_wise_data = []
            for fy, total in sorted(yearly_grouped.items(), key=lambda x: extract_year(x[0]), reverse=True):
                year_wise_data.append({
                    "Financial_Year": fy,
                    "Total_Emission": float(total)
                })

            return Response({
                "facility_emission_data": facility_data,
                "fuel_type_percentage_data": fuel_data,
                "year_wise_emission_data": year_wise_data
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class Combined_Scope2_Emission_Dashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            financial_year = request.query_params.get('financial_year')
            facility = request.query_params.get('facility')

            months = [
                'Emission_Apr', 'Emission_May', 'Emission_Jun', 'Emission_Jul',
                'Emission_Aug', 'Emission_Sep', 'Emission_Oct', 'Emission_Nov',
                'Emission_Dec', 'Emission_Jan', 'Emission_Feb', 'Emission_Mar'
            ]

            # ---------- FACILITY-WISE DATA ----------
            queryset = Scope2_Emissions_by_Facilities.objects.all()
            if financial_year:
                queryset = queryset.filter(Financial_Year=financial_year)
            if facility:
                queryset = queryset.filter(Facility=facility)

            facility_data = []
            yearly_grouped = defaultdict(Decimal)

            if not financial_year and not facility:
                grouped = defaultdict(lambda: {
                    'Financial_Year': 'All',
                    'data': {month: Decimal('0.00') for month in months},
                    'Total_Emission': Decimal('0.00')
                })
                for record in queryset:
                    fac = record.Facility or "Unknown"
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            grouped[fac]['data'][month] += val.to_decimal()
                    if record.Total_Emission:
                        grouped[fac]['Total_Emission'] += record.Total_Emission.to_decimal()

                for fac, data in grouped.items():
                    entry = {
                        'Facility': fac,
                        'Financial_Year': data['Financial_Year'],
                        'Total_Emission': float(data['Total_Emission']),
                        **{month: float(v) for month, v in data['data'].items()}
                    }
                    facility_data.append(entry)

            elif financial_year and not facility:
                grouped = defaultdict(lambda: {
                    'Financial_Year': financial_year,
                    'data': {month: Decimal('0.00') for month in months},
                    'Total_Emission': Decimal('0.00')
                })
                for record in queryset:
                    fac = record.Facility or "Unknown"
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            grouped[fac]['data'][month] += val.to_decimal()
                    if record.Total_Emission:
                        grouped[fac]['Total_Emission'] += record.Total_Emission.to_decimal()

                for fac, data in grouped.items():
                    entry = {
                        'Facility': fac,
                        'Financial_Year': financial_year,
                        'Total_Emission': float(data['Total_Emission']),
                        **{month: float(v) for month, v in data['data'].items()}
                    }
                    facility_data.append(entry)

            elif facility and not financial_year:
                result = {month: Decimal('0.00') for month in months}
                total_sum = Decimal('0.00')
                for record in queryset:
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            result[month] += val.to_decimal()
                    if record.Total_Emission:
                        total_sum += record.Total_Emission.to_decimal()

                facility_data = [{
                    'Facility': facility,
                    'Financial_Year': 'All',
                    'Total_Emission': float(total_sum),
                    **{month: float(v) for month, v in result.items()}
                }]

            else:
                result = {month: Decimal('0.00') for month in months}
                total_sum = Decimal('0.00')
                for record in queryset:
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            result[month] += val.to_decimal()
                    if record.Total_Emission:
                        total_sum += record.Total_Emission.to_decimal()

                facility_data = [{
                    'Facility': facility,
                    'Financial_Year': financial_year,
                    'Total_Emission': float(total_sum),
                    **{month: float(v) for month, v in result.items()}
                }]

            # ---------- FUEL TYPE PERCENTAGE DATA ----------
            percentage_grouped = defaultdict(Decimal)

            for obj in queryset:
                total = obj.Total_Emission 
                if total is None:
                    total = Decimal('0.00')
                else:
                    total = total.to_decimal()  

                if financial_year and facility:
                    key = (facility, financial_year)
                elif financial_year:
                    key = (obj.Facility or "Unknown", financial_year)
                elif facility:
                    key = (facility, "All")
                else:
                    key = (obj.Facility or "Unknown", "All")

                percentage_grouped[key] += total

            total_sum = sum(percentage_grouped.values()) or Decimal('1.00')  # avoid division by zero

            facility_percentage_data = []
            for (fac, year), total in percentage_grouped.items():
                percentage = (total / total_sum * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                facility_percentage_data.append({
                    "Facility": fac,
                    "Financial_Year": year,
                    "Total_Emission": float(total),
                    "Percentage": float(percentage)
                })
            # ---------- YEAR WISE TOTAL EMISSION ----------
           
            yearly_grouped = defaultdict(Decimal)
            for record in queryset:
                fy = record.Financial_Year or "Unknown"
                total = record.Total_Emission.to_decimal() if record.Total_Emission else Decimal('0.00')
                yearly_grouped[fy] += total

            def extract_year(fy_str):
                try:
                    return int(fy_str[2:6])
                except:
                    return 0

            year_wise_data = []
            for fy, total in sorted(yearly_grouped.items(), key=lambda x: extract_year(x[0]), reverse=True):
                year_wise_data.append({
                    "Financial_Year": fy,
                    "Total_Emission": float(total)
                })

            return Response({
                "monthly_facility_data": facility_data,
                "Facility_percentage_data": facility_percentage_data,
                "year_wise_emission_data": year_wise_data
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)
  

class Total_Waste_Generated_Dashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            financial_year = request.query_params.get('financial_year')
            facility = request.query_params.get('facility')

            months = [
                'Waste_Generated_Apr', 'Waste_Generated_May', 'Waste_Generated_Jun', 'Waste_Generated_Jul',
                'Waste_Generated_Aug', 'Waste_Generated_Sep', 'Waste_Generated_Oct', 'Waste_Generated_Nov',
                'Waste_Generated_Dec', 'Waste_Generated_Jan', 'Waste_Generated_Feb', 'Waste_Generated_Mar'
            ]

            # Define a helper to get queryset based on filters
            def get_queryset(year=None, fac=None):
                q = Waste_Generated.objects.all()
                if year:
                    q = q.filter(Financial_Year=year)
                if fac:
                    q = q.filter(Facility=fac)
                return q

            # Get current and previous financial years
            if financial_year:
                current_year = financial_year
                try:
                    start_year = int(financial_year[2:6])
                    prev_year = f"FY{start_year - 1}-{start_year}"
                except:
                    prev_year = "Unknown"
            else:
                # If no FY is given, use all unique years from the DB
                all_years = Waste_Generated.objects.values_list("Financial_Year", flat=True).distinct()
                sorted_years = sorted([y for y in all_years if y and y.startswith("FY")], reverse=True)
                current_year = sorted_years[0] if sorted_years else "Unknown"
                try:
                    start_year = int(current_year[2:6])
                    prev_year = f"FY{start_year - 1}-{start_year}"
                except:
                    prev_year = "Unknown"

            result = {}

            for label, year in [("current", current_year), ("previous", prev_year)]:
                queryset = get_queryset(year, facility)

                month_data = defaultdict(lambda: Decimal('0.00'))

                for record in queryset:
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            month_data[month] += val.to_decimal()

               
                result[f"{label}_year_month_wise_data"] = {
                    month: float(val) for month, val in month_data.items()
                }

            return Response(result)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class PlantWiseDistributionDashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            financial_year = request.query_params.get('financial_year')
            facility_filter = request.query_params.get('facility')
            gender = request.query_params.get('gender')  # "male" or "female"
            emp_type = request.query_params.get('type')  # "permanent" or "non_permanent"

            employee_data = calculate_total_employees()
            worker_data = calculate_total_workers()

            def get_combined_plant_wise_distribution(employee_data, worker_data):
                combined_grouped = defaultdict(float)

                for record in employee_data + worker_data:
                    if financial_year and record["Financial_Year"] != financial_year:
                        continue
                    if facility_filter and record["Facility"] != facility_filter:
                        continue

                    total = record.get("Total_Male", 0.0) + record.get("Total_Female", 0.0)
                    combined_grouped[record["Facility"]] += total

                results = []
                total_all = sum(combined_grouped.values())

                for facility, total in combined_grouped.items():
                    percentage = (total / total_all) * 100 if total_all else 0
                    results.append({
                        "Facility": facility,
                        "Total_Employees": round(total, 2),
                        "Percentage": f"{percentage:.2f}%"
                    })

                return results

            # Now, get month-wise data
            def get_monthwise_data_employees(filters):
                months = [
                    "Employees_Apr", "Employees_May", "Employees_Jun", "Employees_Jul",
                    "Employees_Aug", "Employees_Sep", "Employees_Oct", "Employees_Nov",
                    "Employees_Dec", "Employees_Jan", "Employees_Feb", "Employees_Mar"
                ]
                result = {month: 0.0 for month in months}

                for obj in Employees.objects.filter(**filters):
                    for month in months:
                        value = getattr(obj, month, 0)
                        result[month] += convert_decimal128_to_float(value)
                return result

            def get_monthwise_data_workers(filters):
                months = [
                    "Differently_Abled_Workers_Apr", "Differently_Abled_Workers_May", "Differently_Abled_Workers_Jun",
                    "Differently_Abled_Workers_Jul", "Differently_Abled_Workers_Aug", "Differently_Abled_Workers_Sep",
                    "Differently_Abled_Workers_Oct", "Differently_Abled_Workers_Nov", "Differently_Abled_Workers_Dec",
                    "Differently_Abled_Workers_Jan", "Differently_Abled_Workers_Feb", "Differently_Abled_Workers_Mar"
                ]
                result = {month: 0.0 for month in months}

                for obj in Workers.objects.filter(**filters):
                    for month in months:
                        value = getattr(obj, month, 0)
                        result[month] += convert_decimal128_to_float(value)
                return result

            # Filters for the month-wise data
            filters = {}
            if financial_year:
                filters["Financial_Year"] = financial_year
            if facility_filter:
                filters["Facility"] = facility_filter
            # if gender:
            #     filters["Gender"] = gender
            # if emp_type:
            #     filters["Type"] = emp_type

            emp_month_wise = get_monthwise_data_employees(filters)
            worker_month_wise = get_monthwise_data_workers(filters)

            return Response({
                "plant_wise_distribution": get_combined_plant_wise_distribution(employee_data, worker_data),
                "month_wise": {
                    "employees": emp_month_wise,
                    "workers": worker_month_wise
                }
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class CombinedEmployeeWorkerDashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            fy = request.query_params.get("financial_year")
            facility_filter = request.query_params.get("facility")
            gender = request.query_params.get("gender")
            emp_type = request.query_params.get("type")

            employee_data = calculate_total_employees()
            worker_data = calculate_total_workers()

            def process_data(data_list, label):
                grouped = defaultdict(lambda: {
                    "Male_Permanent": 0.0,
                    "Male_Non_Permanent": 0.0,
                    "Female_Permanent": 0.0,
                    "Female_Non_Permanent": 0.0,
                    "Total_Male": 0.0,
                    "Total_Female": 0.0,
                })

                for record in data_list:
                    if fy and record["Financial_Year"] != fy:
                        continue
                    if facility_filter and record["Facility"] != facility_filter:
                        continue

                    if fy and not facility_filter:
                        key = record["Financial_Year"]
                    elif not fy and facility_filter:
                        key = "combined"
                    elif fy and facility_filter:
                        key = "filtered"
                    else:
                        key = "combined"

                    grouped[key]["Male_Permanent"] += record["Male_Permanent"]
                    grouped[key]["Male_Non_Permanent"] += record["Male_Non_Permanent"]
                    grouped[key]["Female_Permanent"] += record["Female_Permanent"]
                    grouped[key]["Female_Non_Permanent"] += record["Female_Non_Permanent"]
                    grouped[key]["Total_Male"] += record["Total_Male"]
                    grouped[key]["Total_Female"] += record["Total_Female"]

                formatted = []
                for key, group in grouped.items():
                    entry = {}
                    if fy and not facility_filter:
                        entry["Financial_Year"] = key
                    elif fy and facility_filter:
                        entry["Financial_Year"] = fy
                        entry["Facility"] = facility_filter
                    elif not fy and facility_filter:
                        entry["Facility"] = facility_filter

                    total_male = group["Total_Male"]
                    total_female = group["Total_Female"]
                    total = total_male + total_female

                    if not gender and not emp_type:
                        entry.update({
                            "Male_Permanent": group["Male_Permanent"],
                            "Male_Non_Permanent": group["Male_Non_Permanent"],
                            "Female_Permanent": group["Female_Permanent"],
                            "Female_Non_Permanent": group["Female_Non_Permanent"],
                            "Total_Male": group["Total_Male"],
                            "Total_Female": group["Total_Female"],
                            "Male_Percentage": f"{(total_male / total * 100):.2f}%" if total else "0.00%",
                            "Female_Percentage": f"{(total_female / total * 100):.2f}%" if total else "0.00%",
                        })
                    else:
                        if gender == "male":
                            if emp_type == "permanent":
                                total_permanent = group["Male_Permanent"] + group["Female_Permanent"]
                                entry["Male_Permanent"] = group["Male_Permanent"]
                                entry["Male_Percentage"] = (
                                    f"{(group['Male_Permanent'] / total_permanent * 100):.2f}%"
                                    if total_permanent else "0.00%"
                                )
                            elif emp_type == "non_permanent":
                                total_non_permanent = group["Male_Non_Permanent"] + group["Female_Non_Permanent"]
                                entry["Male_Non_Permanent"] = group["Male_Non_Permanent"]
                                entry["Male_Percentage"] = (
                                    f"{(group['Male_Non_Permanent'] / total_non_permanent * 100):.2f}%"
                                    if total_non_permanent else "0.00%"
                                )
                            else:
                                total = group["Total_Male"] + group["Total_Female"]
                                entry.update({
                                    "Male_Permanent": group["Male_Permanent"],
                                    "Male_Non_Permanent": group["Male_Non_Permanent"],
                                    "Total_Male": group["Total_Male"],
                                    "Male_Percentage": f"{(group['Total_Male'] / total * 100):.2f}%" if total else "0.00%"
                                })
                        elif gender == "female":
                            if emp_type == "permanent":
                                total_permanent = group["Male_Permanent"] + group["Female_Permanent"]
                                entry["Female_Permanent"] = group["Female_Permanent"]
                                entry["Female_Percentage"] = (
                                    f"{(group['Female_Permanent'] / total_permanent * 100):.2f}%"
                                    if total_permanent else "0.00%"
                                )
                            elif emp_type == "non_permanent":
                                total_non_permanent = group["Male_Non_Permanent"] + group["Female_Non_Permanent"]
                                entry["Female_Non_Permanent"] = group["Female_Non_Permanent"]
                                entry["Female_Percentage"] = (
                                        f"{(group['Female_Non_Permanent'] / total_non_permanent * 100):.2f}%"
                                        if total_non_permanent else "0.00%"
                                )
                            else:
                                total = group["Total_Male"] + group["Total_Female"]
                                entry.update({
                                    
                                    "Female_Permanent": group["Female_Permanent"],
                                    "Female_Non_Permanent": group["Female_Non_Permanent"],
                                    "Total_Female": group["Total_Female"],
                                     "Female_Percentage": f"{(group['Total_Female'] / total * 100):.2f}%" if total else "0.00%"
                                })

                    formatted.append(entry)

                return formatted

            def calculate_permanent_vs_nonpermanent(emp_data, worker_data):
                result = {
                    "Permanent": 0.0,
                    "Non_Permanent": 0.0
                }

                for record in emp_data + worker_data:
                    if fy and record["Financial_Year"] != fy:
                        continue
                    if facility_filter and record["Facility"] != facility_filter:
                        continue

                    result["Permanent"] += record.get("Male_Permanent", 0.0) + record.get("Female_Permanent", 0.0)
                    result["Non_Permanent"] += record.get("Male_Non_Permanent", 0.0) + record.get("Female_Non_Permanent", 0.0)

                return [
                    {"Type": "Permanent", "Total": result["Permanent"]},
                    {"Type": "Non-Permanent", "Total": result["Non_Permanent"]},
                ]

            total_new_hires = get_new_hires_summary(
                fy=fy,
                facility=facility_filter,
                gender=gender,
                emp_type=emp_type,
            )
            total_wokers_hires = get_worker_new_hires_summary(
                fy=fy,
                facility=facility_filter,
                gender=gender,
                emp_type=emp_type,
            )
            total_employees_hires = get_employess_new_hires_summary(
                fy=fy,
                facility=facility_filter,
                gender=gender,
                emp_type=emp_type,
            )

            # Calculate Permanent vs Non-Permanent totals
            permanent_total = 0.0
            non_permanent_total = 0.0

            # Combine data from employee and worker data
            combined_data = employee_data + worker_data

            for record in combined_data:
                if fy and record["Financial_Year"] != fy:
                    continue
                if facility_filter and record["Facility"] != facility_filter:
                    continue

                permanent_total += record.get("Male_Permanent", 0.0) + record.get("Female_Permanent", 0.0)
                non_permanent_total += record.get("Male_Non_Permanent", 0.0) + record.get("Female_Non_Permanent", 0.0)






            response = {
                "employees": process_data(employee_data, "employees"),
                "workers": process_data(worker_data, "workers"),
                "permanent_vs_non_permanent": [
                    {
                        "permanent_total": permanent_total,
                        "non_permanent_total": non_permanent_total
                    }
                ],
                "total_new_hires": total_new_hires,
                "total_wokers_hires": total_wokers_hires,
                "total_employees_hires": total_employees_hires
            }

            return Response(response)

        except Exception as e:
            return Response({"error": str(e)}, status=500)




class FemaleDistributionDashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            fy = request.query_params.get("financial_year")
            financial_year_label = fy if fy else "All"

            def get_employee_female_percentage():
                qs = EmployeeSummary.objects.all()
                if fy:
                    qs = qs.filter(Financial_Year=fy)

                total_female = 0.0
                total_all = 0.0
                for obj in qs:
                    female_perm = convert_decimal128_to_float(obj.Female_Permanent)
                    female_non_perm = convert_decimal128_to_float(obj.Female_Non_Permanent)
                    male_perm = convert_decimal128_to_float(obj.Male_Permanent)
                    male_non_perm = convert_decimal128_to_float(obj.Male_Non_Permanent)

                    total_female += female_perm + female_non_perm
                    total_all += female_perm + female_non_perm + male_perm + male_non_perm

                percentage = round((total_female / total_all) * 100, 2) if total_all > 0 else 0.0
                return round(total_female, 2), percentage

            def get_worker_female_percentage():
                qs = WorkerSummary.objects.all()
                if fy:
                    qs = qs.filter(Financial_Year=fy)

                total_female = 0.0
                total_all = 0.0
                for obj in qs:
                    female_perm = convert_decimal128_to_float(obj.Female_Permanent)
                    female_non_perm = convert_decimal128_to_float(obj.Female_Non_Permanent)
                    male_perm = convert_decimal128_to_float(obj.Male_Permanent)
                    male_non_perm = convert_decimal128_to_float(obj.Male_Non_Permanent)

                    total_female += female_perm + female_non_perm
                    total_all += female_perm + female_non_perm + male_perm + male_non_perm

                percentage = round((total_female / total_all) * 100, 2) if total_all > 0 else 0.0
                return round(total_female, 2), percentage

            def get_female_total_from_model(model, total_field_name):
                qs = model.objects.all()
                if fy:
                    qs = qs.filter(Financial_Year=fy)

                female_total = 0.0
                overall_total = 0.0

                for obj in qs:
                    value = convert_decimal128_to_float(getattr(obj, total_field_name, 0))
                    overall_total += value
                    if obj.Gender and obj.Gender.lower() == "female":
                        female_total += value

                percentage = round((female_total / overall_total) * 100, 2) if overall_total > 0 else 0.0
                return round(female_total, 2), percentage

            # Build the final response list
            response_data = []

            employee_female, emp_pct = get_employee_female_percentage()
            response_data.append({
                "Financial_Year": financial_year_label,
                "Segment": "Employees",
                "Total_female": employee_female,
                "Female_Percentage": emp_pct
            })

            worker_female, worker_pct = get_worker_female_percentage()
            response_data.append({
                "Financial_Year": financial_year_label,
                "Segment": "Workers",
                "Total_female": worker_female,
                "Female_Percentage": worker_pct
            })

            board_female, board_pct = get_female_total_from_model(Management_Board_of_Directors, "Total_Board_of_Directors")
            response_data.append({
                "Financial_Year": financial_year_label,
                "Segment": "BoardOfDirectors",
                "Total_female": board_female,
                "Female_Percentage": board_pct
            })

            key_female, key_pct = get_female_total_from_model(Key_Management_Personnel, "Total_Key_Management_Personnel")
            response_data.append({
                "Financial_Year": financial_year_label,
                "Segment": "KeyManagementPersonnel",
                "Total_female": key_female,
                "Female_Percentage": key_pct
            })

            return Response({"female_distribution": response_data})

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class TotalProgrammesHeldByFacilityDashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            fy = request.query_params.get("financial_year")
            facility = request.query_params.get("facility")
            segment = request.query_params.get("segment")

            qs = Awareness_Programmes_On_ESG.objects.all()

            if fy:
                qs = qs.filter(Financial_Year=fy)
            if facility:
                qs = qs.filter(Facility=facility)
            if segment:
                qs = qs.filter(Segment=segment)

            total_topics_covered = 0
            grouped_data = defaultdict(lambda: defaultdict(int))
            

            for record in qs:
                fac = record.Facility or "Unknown"
                seg = record.Segment or "Unknown"
                grouped_data[fac][seg] += record.Total_No_Of_Programmes_Held or 0
                total_topics_covered += int(record.Topics_Covered) or 0

                  

            response = []
            for fac, segments in grouped_data.items():
                for seg, total in segments.items():
                    response.append({
                        "Facility": fac,
                        "Segment": seg,
                        "Total_No_Of_Programmes_Held": total
                        
                    })

            response.append({
                "Topics_Covered_Count": total_topics_covered
            })


            return Response(response)

        except Exception as e:
            return Response({"error": str(e)}, status=500)   
        
class SkillUpgradtionTraningDashborad(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            fy = request.query_params.get("financial_year")
            facility = request.query_params.get("facility")
            segment = request.query_params.get("segment")
            gender = request.query_params.get("gender")  # "Male" or "Female"

            qs = On_Skill_Upgradation.objects.all()

            if fy:
                qs = qs.filter(Financial_Year=fy)
            if facility:
                qs = qs.filter(Facility=facility)
            if segment:
                qs = qs.filter(Segment=segment)

            data = defaultdict(lambda: {"male": 0, "female": 0})

            for record in qs:
                fac = record.Facility or "Unknown"
                if gender in ["male", None]:
                    data[fac]["male"] += record.No_Of_Male or 0
                if gender in ["female", None]:
                    data[fac]["female"] += record.No_Of_Female or 0

            response = []
            for fac, values in data.items():
                if gender == "male":
                    response.append({
                        "Facility": fac,
                        "Gender": "male",
                        "Total_Gender": values["male"]
                    })
                elif gender == "female":
                    response.append({
                        "Facility": fac,
                        "Gender": "female",
                        "Total_Gender": values["female"]
                    })
                else:
                    response.extend([
                        {
                            "Facility": fac,
                            "Gender": "male",
                            "Total_Gender": values["male"]
                        },
                        {
                            "Facility": fac,
                            "Gender": "female",
                            "Total_Gender": values["female"]
                        }
                    ])

            return Response(response)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class TraningIngeneralByMonthDashborad(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            fy = request.query_params.get("financial_year")
            facility = request.query_params.get("facility")
            segment = request.query_params.get("segment")

            qs = Ingeneral.objects.all()

            # Apply filters
            if fy:
                qs = qs.filter(Financial_Year=fy)
            if facility:
                qs = qs.filter(Facility=facility)
            if segment:
                qs = qs.filter(Segment=segment)

            # Month field mapping
            month_fields = {
                "Apr": "Ingeneral_Consumption_Apr",
                "May": "Ingeneral_Consumption_May",
                "Jun": "Ingeneral_Consumption_Jun",
                "Jul": "Ingeneral_Consumption_Jul",
                "Aug": "Ingeneral_Consumption_Aug",
                "Sep": "Ingeneral_Consumption_Sep",
                "Oct": "Ingeneral_Consumption_Oct",
                "Nov": "Ingeneral_Consumption_Nov",
                "Dec": "Ingeneral_Consumption_Dec",
                "Jan": "Ingeneral_Consumption_Jan",
                "Feb": "Ingeneral_Consumption_Feb",
                "Mar": "Ingeneral_Consumption_Mar",
            }

            # Initialize month totals
            month_totals = {month: 0 for month in month_fields}

            for record in qs:
                for month, field in month_fields.items():
                    value = getattr(record, field) or 0
                    value = float(str(value)) if value is not None else 0
                    month_totals[month] += float(value)

            # Format response
            response = [
                {"Month": month, "Value": round(value, 2)}
                for month, value in month_totals.items()
            ]

            return Response(response)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

class HumanRightsTrainingDashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            fy = request.query_params.get("financial_year")
            facility = request.query_params.get("facility")

            queryset = On_Human_Rights_Issues_And_Policies.objects.all()

            if fy:
                queryset = queryset.filter(Financial_Year=fy)
            if facility:
                queryset = queryset.filter(Facility=facility)

            result = {}
            total_human_rights_training = 0 

            for entry in queryset:
                segment = entry.Segment or "Unknown"
                if segment not in result:
                    result[segment] = {
                        "Permanent": 0,
                        "Non-Permanent": 0
                    }

                permanent = int(entry.Total_Permanent_Covered or 0)
                non_permanent = int(entry.Total_Non_Permanent_Covered or 0)

                result[segment]["Permanent"] += permanent
                result[segment]["Non-Permanent"] += non_permanent
                total_human_rights_training += permanent + non_permanent

            # Convert result into list for frontend
            data = []
            for segment, values in result.items():
                data.append({
                    "Segment": segment,
                    "Type": "Permanent",
                    "Total": values["Permanent"]
                })
                data.append({
                    "Segment": segment,
                    "Type": "Non-Permanent",
                    "Total": values["Non-Permanent"]
                })

            return Response({  
                "data": data,
                "Total_human_rights_training": total_human_rights_training,
            })

            return Response(data)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class HealthSafetyTrainingByGender(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            fy = request.query_params.get("financial_year")
            facility = request.query_params.get("facility")

            queryset = On_Health_And_Safety_Measures.objects.all()

            if fy:
                queryset = queryset.filter(Financial_Year=fy)
            if facility:
                queryset = queryset.filter(Facility=facility)

            result = {}
            total_training_health_and_safety = 0

            for entry in queryset:
                fac = entry.Facility or "Unknown"
                if fac not in result:
                    result[fac] = {"male": 0, "female": 0}
                result[fac]["male"] += entry.No_Of_Male or 0
                result[fac]["female"] += entry.No_Of_Female or 0
                total = entry.Total_Male_And_Female or 0
                total_training_health_and_safety += total

            data = []
            for fac, gender_counts in result.items():
                data.append({
                    "Facility": fac,
                    "Gender": "male",
                    "Total": gender_counts["male"]
                })
                data.append({
                    "Facility": fac,
                    "Gender": "female",
                    "Total": gender_counts["female"]
                })
            return Response({
            "data": data,
            "total_training_health_and_safety": total_training_health_and_safety
            })
            

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

class TrainingIngeneralBySegment(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            fy = request.query_params.get("financial_year")
            facility = request.query_params.get("facility")

            queryset = Ingeneral.objects.all()
            if fy:
                queryset = queryset.filter(Financial_Year=fy)
            if facility:
                queryset = queryset.filter(Facility=facility)

            # Manual aggregation
            segment_totals = defaultdict(float)

            for record in queryset:
                segment = record.Segment or "Unknown"
                value = record.Total_Ingeneral_Consumption

                if isinstance(value, Decimal128):
                    value = float(value.to_decimal())
                elif value is None:
                    value = 0.0
                else:
                    value = float(value)

                segment_totals[segment] += value

            result = [
                {"Segment": segment, "Total_Ingeneral_Consumption": round(total, 2)}
                for segment, total in segment_totals.items()
            ]

            return Response(result)

        except Exception as e:
            return Response({"error": str(e)}, status=500)