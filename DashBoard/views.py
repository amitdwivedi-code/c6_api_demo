from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from CompanyDetails.models import *
from django.db import DatabaseError
from decimal import Decimal
from bson.decimal128 import Decimal128
from .utils import *

class Companydetails_Dashboard(APIView):
    def get(self, request):
        try:
            # Step 1: Get the financial year from the request
            financial_year = request.GET.get('financial_year')
            if not financial_year:
                return Response({"error": "Financial year is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Step 2: Fetch Networth and Turnover data for the given financial year
            networth_data = Networth.objects.filter(Financial_Year=financial_year).first()
            turnover_data = Turnover.objects.filter(Financial_Year=financial_year).first()


            # Step 6: Calculate turnover and networth for each quarter and their ratio
            Q1_turn = sum([safe_decimal(getattr(turnover_data, f"Turnover_{m}")) for m in ["Apr", "May", "Jun"]])
            Q1_net = sum([safe_decimal(getattr(networth_data, f"Networth_{m}")) for m in ["Apr", "May", "Jun"]])
            Q1 = ratio(Q1_turn, Q1_net)

            Q2_turn = sum([safe_decimal(getattr(turnover_data, f"Turnover_{m}")) for m in ["Jul", "Aug", "Sep"]])
            Q2_net = sum([safe_decimal(getattr(networth_data, f"Networth_{m}")) for m in ["Jul", "Aug", "Sep"]])
            Q2 = ratio(Q2_turn, Q2_net)

            Q3_turn = sum([safe_decimal(getattr(turnover_data, f"Turnover_{m}")) for m in ["Oct", "Nov", "Dec"]])
            Q3_net = sum([safe_decimal(getattr(networth_data, f"Networth_{m}")) for m in ["Oct", "Nov", "Dec"]])
            Q3 = ratio(Q3_turn, Q3_net)

            Q4_turn = sum([safe_decimal(getattr(turnover_data, f"Turnover_{m}")) for m in ["Jan", "Feb", "Mar"]])
            Q4_net = sum([safe_decimal(getattr(networth_data, f"Networth_{m}")) for m in ["Jan", "Feb", "Mar"]])
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
            return Response({"error": "An unexpected error occurred", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)