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

    # def get(self, request):
    #     try:
    #         financial_year = request.query_params.get('financial_year')
    #         facility = request.query_params.get('facility')

    #         # Querysets with filters
    #         elec_qs = Electricity_Consumption_GJ.objects.all()
    #         fuel_qs = Fuel_Consumption_Onsite_Combustion_GJ.objects.all()

    #         if financial_year:
    #             elec_qs = elec_qs.filter(Financial_Year=financial_year)
    #             fuel_qs = fuel_qs.filter(Financial_Year=financial_year)
    #         if facility:
    #             elec_qs = elec_qs.filter(Facility=facility)
    #             fuel_qs = fuel_qs.filter(Facility=facility)

    #         # Facility-wise grouping
    #         elec_data = defaultdict(Decimal)
    #         fuel_data = defaultdict(Decimal)

    #         # Electricity aggregation
    #         for obj in elec_qs:
    #             fac = obj.Facility or "Unknown"
    #             value = obj.Total_Electricity_Consumption
    #             value = value.to_decimal() if hasattr(value, "to_decimal") else (value or Decimal("0.00"))
    #             elec_data[fac] += value

    #         # Fuel aggregation
    #         for obj in fuel_qs:
    #             fac = obj.Facility or "Unknown"
    #             value = obj.Total_Fuel_Consumption
    #             value = value.to_decimal() if hasattr(value, "to_decimal") else (value or Decimal("0.00"))
    #             fuel_data[fac] += value

    #         total_elec = sum(elec_data.values()) or Decimal("0.00")
    #         total_fuel = sum(fuel_data.values()) or Decimal("0.00")

    #         # Union of all facilities found
    #         all_facilities = set(elec_data.keys()) | set(fuel_data.keys())

    #         result = []
    #         for fac in all_facilities:
    #             elec = elec_data.get(fac, Decimal("0.00"))
    #             fuel = fuel_data.get(fac, Decimal("0.00"))
    #             elec_pct = (elec / total_elec * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if total_elec else Decimal("0.00")
    #             fuel_pct = (fuel / total_fuel * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if total_fuel else Decimal("0.00")

    #             result.append({
    #                 "Facility": fac,
    #                 "Total_Electricity_Consumption": float(elec),
    #                 "Electricity_Percentage": float(elec_pct),
    #                 "Total_Fuel_Consumption": float(fuel),
    #                 "Fuel_Percentage": float(fuel_pct)
    #             })

    #         return Response(result, status=status.HTTP_200_OK)

    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
                        "fuel_type": fuel_type,
                        "Total_Fuel_Consumption": float(total),
                         "Percentage": float(percentage)
                    })
                elif financial_year:
                    fuel_type, = key
                    result.append({
                        "Financial_Year": financial_year,
                        "fuel_type": fuel_type,
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
                        "fuel_type": fuel_type,
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
            year_queryset = Scope1_Emissions_by_Facilities.objects.all()
            if facility and not financial_year:
                year_queryset = year_queryset.filter(Facility=facility)
            elif financial_year and not facility:
                year_queryset = year_queryset.filter(Financial_Year=financial_year)
            elif financial_year and facility:
                year_queryset = year_queryset.filter(Financial_Year=financial_year, Facility=facility)

            yearly_grouped = defaultdict(Decimal)
            for record in year_queryset:
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

                result[f"{label}_year"] = year
                result[f"{label}_year_month_wise_data"] = {
                    month: float(val) for month, val in month_data.items()
                }

            return Response(result)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
