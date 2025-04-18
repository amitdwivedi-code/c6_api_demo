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

            # Base Queryset
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

            # Case 1: No filter → group by Facility
            if not financial_year and not facility:
                grouped = defaultdict(lambda: {month: Decimal('0.00') for month in months})
                for record in queryset:
                    fac = record.Facility or "Unknown"
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            grouped[fac][month] += val.to_decimal()
                response_data = {
                    facility: {month: float(val) for month, val in data.items()}
                    for facility, data in grouped.items()
                }

            # Case 2: Only financial year OR only facility → sum month-wise
            elif financial_year and not facility:
                result = {month: Decimal('0.00') for month in months}
                for record in queryset:
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            result[month] += val.to_decimal()
                response_data = {month: float(val) for month, val in result.items()}

            elif facility and not financial_year:
                result = {month: Decimal('0.00') for month in months}
                for record in queryset:
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            result[month] += val.to_decimal()
                response_data = {month: float(val) for month, val in result.items()}

            # Case 3: Both filters → single facility & year
            else:
                result = {month: Decimal('0.00') for month in months}
                for record in queryset:
                    for month in months:
                        val = getattr(record, month)
                        if val:
                            result[month] += val.to_decimal()
                response_data = {month: float(val) for month, val in result.items()}

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