from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Environment.models import *
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
# from EmissionFactors.models import EmissionFactors
from rest_framework.permissions import IsAuthenticated 
import logging

from Activity_Log.serializers import ActivityLogSerializer
logger = logging.getLogger(__name__)
from . import serializers
from .choices import *
from .models import *
from .utils  import *
from .serializers import *


from django.db.models import Max, Sum

from decimal import Decimal


from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import APIException
from Activity_Log.models import *
from Activity_Log.serializers import *

# Create your views here.

class AgencyTypeList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            agency_type_list = AGENCY_TYPE

            if not agency_type_list:
                return Response({'error': 'Agency Type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(agency_type_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Agency Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Energy_Assessment_by_External_Agency_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            assessment_by_external_agency = Energy_Assessment_by_External_Agency.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(assessment_by_external_agency, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = EnergyAssessmentbyExternalAgencySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            type = request.data.get('Agency_Type')
            count = Energy_Assessment_by_External_Agency.objects.filter(Financial_Year=year, Agency_Type=type).count()
            if count > 0:
                return Response({'error':'Entry for this Financial Year  and Agency_Type already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Energy_Assessment_by_External_Agency.objects.count() == 0:
                id = 1
            else:
                id = Energy_Assessment_by_External_Agency.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            
            serializer = EnergyAssessmentbyExternalAgencySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Assessment by External Agency"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    assessment_by_external_agency_instance = Energy_Assessment_by_External_Agency.objects.get(id=id)
                    serializer = EnergyAssessmentbyExternalAgencySerializer(assessment_by_external_agency_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Assessment by External Agency"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    assessment_by_external_agency = Energy_Assessment_by_External_Agency.objects.get(id=id)
                    assessment_by_external_agency.delete()

                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Deleted information in table - Assessment by External Agency"}
                                        
                    activity_log_serializer = EnergyAssessmentbyExternalAgencySerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Energy_Assessment_by_External_Agency.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        


class Electricity_Consumption_mwh_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":
               
            electricity_consumption_mwh = Electricity_Consumption_mwh.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(electricity_consumption_mwh, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = ElectricityConsumptionmwhSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            financial_year = request.data.get('Financial_Year')
            facility =  request.data.get('Facility')
            source =  request.data.get('Source')
            
            # Check if an entry for this financial year already exists
            if Electricity_Consumption_mwh.objects.filter(Financial_Year=financial_year,Facility=facility,Source=source).count() > 0:
                return Response({'error': 'Entry for this Financial Year, Facility and Source already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            if Electricity_Consumption_mwh.objects.count() == 0:
                id = 1
            else:
                id = Electricity_Consumption_mwh.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            total_electricity_consumption = request.data.get('Electricity_Consumption_Apr', 0) + request.data.get('Electricity_Consumption_May', 0)  + request.data.get('Electricity_Consumption_Jun', 0) + request.data.get('Electricity_Consumption_Jul', 0) + request.data.get('Electricity_Consumption_Aug', 0) + request.data.get('Electricity_Consumption_Sep', 0) + request.data.get('Electricity_Consumption_Oct', 0) + request.data.get('Electricity_Consumption_Nov', 0) + request.data.get('Electricity_Consumption_Dec', 0) + request.data.get('Electricity_Consumption_Jan', 0) + request.data.get('Electricity_Consumption_Feb', 0) + request.data.get('Electricity_Consumption_Mar', 0)
            request.data["Total_Electricity_Consumption"] = round(total_electricity_consumption, 2)

            Electricity_Consumption_GJ = {}
            Electricity_Consumption_GJ["id"] = id
            Electricity_Consumption_GJ["Financial_Year"] = request.data.get('Financial_Year')
            Electricity_Consumption_GJ["Facility"] = request.data.get('Facility')
            Electricity_Consumption_GJ["Source"] = request.data.get('Source')
            Electricity_Consumption_GJ["Unit"] = "Giga Joules"
            Electricity_Consumption_GJ["Electricity_Consumption_Apr"] = round(request.data.get('Electricity_Consumption_Apr', 0) * 3.6, 2)
            Electricity_Consumption_GJ["Electricity_Consumption_May"] = round(request.data.get('Electricity_Consumption_May', 0) * 3.6, 2)
            Electricity_Consumption_GJ["Electricity_Consumption_Jun"] = round(request.data.get('Electricity_Consumption_Jun', 0) * 3.6, 2)
            Electricity_Consumption_GJ["Electricity_Consumption_Jul"] = round(request.data.get('Electricity_Consumption_Jul', 0) * 3.6, 2)
            Electricity_Consumption_GJ["Electricity_Consumption_Aug"] = round(request.data.get('Electricity_Consumption_Aug', 0) * 3.6, 2)
            Electricity_Consumption_GJ["Electricity_Consumption_Sep"] = round(request.data.get('Electricity_Consumption_Sep', 0) * 3.6, 2)
            Electricity_Consumption_GJ["Electricity_Consumption_Oct"] = round(request.data.get('Electricity_Consumption_Oct', 0) * 3.6, 2)
            Electricity_Consumption_GJ["Electricity_Consumption_Nov"] = round(request.data.get('Electricity_Consumption_Nov', 0) * 3.6, 2)
            Electricity_Consumption_GJ["Electricity_Consumption_Dec"] = round(request.data.get('Electricity_Consumption_Dec', 0) * 3.6, 2)
            Electricity_Consumption_GJ["Electricity_Consumption_Jan"] = round(request.data.get('Electricity_Consumption_Jan', 0) * 3.6, 2)
            Electricity_Consumption_GJ["Electricity_Consumption_Feb"] = round(request.data.get('Electricity_Consumption_Feb', 0) * 3.6, 2)
            Electricity_Consumption_GJ["Electricity_Consumption_Mar"] = round(request.data.get('Electricity_Consumption_Mar', 0) * 3.6, 2)

            Electricity_Consumption_GJ["Total_Electricity_Consumption"] = round(Electricity_Consumption_GJ["Electricity_Consumption_Apr"] + Electricity_Consumption_GJ["Electricity_Consumption_May"] + Electricity_Consumption_GJ["Electricity_Consumption_Jun"] + Electricity_Consumption_GJ["Electricity_Consumption_Jul"] + Electricity_Consumption_GJ["Electricity_Consumption_Aug"] + Electricity_Consumption_GJ["Electricity_Consumption_Sep"] + Electricity_Consumption_GJ["Electricity_Consumption_Oct"] + Electricity_Consumption_GJ["Electricity_Consumption_Nov"] + Electricity_Consumption_GJ["Electricity_Consumption_Dec"] + Electricity_Consumption_GJ["Electricity_Consumption_Jan"] + Electricity_Consumption_GJ["Electricity_Consumption_Feb"] + Electricity_Consumption_GJ["Electricity_Consumption_Mar"], 2)

            energy_intensity = calculate_energy_intensity()
            
            serializer = ElectricityConsumptionmwhSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

            serializer1 = ElectricityConsumptionGJSerializer(data=Electricity_Consumption_GJ)
            if serializer1.is_valid():
                serializer1.save()

                Energy_Intensity.objects.all().delete()
                for i in energy_intensity:
                    serializer2 = EnergyIntensitySerializer(data=i)
                    if serializer2.is_valid():
                        serializer2.save()


                energy_intensity_for_production = calculate_energy_intensity_for_production()
                Energy_Intensity_for_Production.objects.all().delete()
                for i in energy_intensity_for_production:
                    serializer3 = EnergyIntensityforProductionSerializer(data=i)
                    if serializer3.is_valid():
                        serializer3.save()
                
                scope2_emission_by_facilities = calculate_scope2_emission_by_facilities()
                Scope2_Emissions_by_Facilities.objects.all().delete()
                for i in scope2_emission_by_facilities:
                    serializer4 = Scope2EmissionsbyFacilitiesSerializer(data=i)
                    if serializer4.is_valid():
                        serializer4.save()

                scope2_emission_by_fuel = calculate_scope2_emissions_by_fuel()
                Scope2_Emissions_by_Fuel.objects.all().delete()
                for i in scope2_emission_by_fuel:
                    serializer5 = Scope2EmissionsbyFuelSerializer(data=i)
                    if serializer5.is_valid():
                        serializer5.save()

                scope2_emission_by_ghg_type = calculate_scope2_emissions_by_ghg_type()
                Scope2_Emissions_by_GHG_Type.objects.all().delete()
                for i in scope2_emission_by_ghg_type:
                    serializer6 = Scope2EmissionsbyGHGTypeSerializer(data=i)
                    if serializer6.is_valid():
                        serializer6.save()

                scope2_intensity = calculate_scope_2_intensity()
                Scope2_Intensity.objects.all().delete()
                for i in scope2_intensity:
                    serializer7 = Scope2IntensitySerializer(data=i)
                    if serializer7.is_valid():
                        serializer7.save()


                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Electricity Consumption (mWh)"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            # import pdb; pdb.set_trace()
            if id is not None:
                try:
                    total_electricity_consumption = request.data.get('Electricity_Consumption_Apr', 0) + request.data.get('Electricity_Consumption_May', 0)  + request.data.get('Electricity_Consumption_Jun', 0) + request.data.get('Electricity_Consumption_Jul', 0) + request.data.get('Electricity_Consumption_Aug', 0) + request.data.get('Electricity_Consumption_Sep', 0) + request.data.get('Electricity_Consumption_Oct', 0) + request.data.get('Electricity_Consumption_Nov', 0) + request.data.get('Electricity_Consumption_Dec', 0) + request.data.get('Electricity_Consumption_Jan', 0) + request.data.get('Electricity_Consumption_Feb', 0) + request.data.get('Electricity_Consumption_Mar', 0)
                    request.data["Total_Electricity_Consumption"] = round(total_electricity_consumption, 2)

                    electricity_consumption_instance = Electricity_Consumption_mwh.objects.get(id=id)
                    serializer = ElectricityConsumptionmwhSerializer(electricity_consumption_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                    my_dict = {}
                    my_dict["id"] = id
                    my_dict["Financial_Year"] = request.data.get('Financial_Year')
                    my_dict["Facility"] = request.data.get('Facility')
                    my_dict["Source"] = request.data.get('Source')
                    my_dict["Unit"] = "Giga Joules"
                    my_dict["Electricity_Consumption_Apr"] = round(request.data.get('Electricity_Consumption_Apr', 0) * 3.6, 2)
                    my_dict["Electricity_Consumption_May"] = round(request.data.get('Electricity_Consumption_May', 0) * 3.6, 2)
                    my_dict["Electricity_Consumption_Jun"] = round(request.data.get('Electricity_Consumption_Jun', 0) * 3.6, 2)
                    my_dict["Electricity_Consumption_Jul"] = round(request.data.get('Electricity_Consumption_Jul', 0) * 3.6, 2)
                    my_dict["Electricity_Consumption_Aug"] = round(request.data.get('Electricity_Consumption_Aug', 0) * 3.6, 2)
                    my_dict["Electricity_Consumption_Sep"] = round(request.data.get('Electricity_Consumption_Sep', 0) * 3.6, 2)
                    my_dict["Electricity_Consumption_Oct"] = round(request.data.get('Electricity_Consumption_Oct', 0) * 3.6, 2)
                    my_dict["Electricity_Consumption_Nov"] = round(request.data.get('Electricity_Consumption_Nov', 0) * 3.6, 2)
                    my_dict["Electricity_Consumption_Dec"] = round(request.data.get('Electricity_Consumption_Dec', 0) * 3.6, 2)
                    my_dict["Electricity_Consumption_Jan"] = round(request.data.get('Electricity_Consumption_Jan', 0) * 3.6, 2)
                    my_dict["Electricity_Consumption_Feb"] = round(request.data.get('Electricity_Consumption_Feb', 0) * 3.6, 2)
                    my_dict["Electricity_Consumption_Mar"] = round(request.data.get('Electricity_Consumption_Mar', 0) * 3.6, 2)

                    my_dict["Total_Electricity_Consumption"] = round(my_dict["Electricity_Consumption_Apr"] + my_dict["Electricity_Consumption_May"] + my_dict["Electricity_Consumption_Jun"] + my_dict["Electricity_Consumption_Jul"] + my_dict["Electricity_Consumption_Aug"] + my_dict["Electricity_Consumption_Sep"] + my_dict["Electricity_Consumption_Oct"] + my_dict["Electricity_Consumption_Nov"] + my_dict["Electricity_Consumption_Dec"] + my_dict["Electricity_Consumption_Jan"] + my_dict["Electricity_Consumption_Feb"] + my_dict["Electricity_Consumption_Mar"], 2)

                    electricity_consumption_instance1 = Electricity_Consumption_GJ.objects.get(id=id)

                    serializer1 = ElectricityConsumptionGJSerializer(electricity_consumption_instance1, data=my_dict, partial = True)
                    if serializer1.is_valid():
                        serializer1.save()

                        energy_intensity = calculate_energy_intensity()
                        Energy_Intensity.objects.all().delete()
                        for i in energy_intensity:
                            serializer2 = EnergyIntensitySerializer(data=i)
                            if serializer2.is_valid():
                                serializer2.save()

                        
                        energy_intensity_for_production = calculate_energy_intensity_for_production()
                        Energy_Intensity_for_Production.objects.all().delete()
                        for i in energy_intensity_for_production:
                            serializer3 = EnergyIntensityforProductionSerializer(data=i)
                            if serializer3.is_valid():
                                serializer3.save()

                        scope2_emission_by_facilities = calculate_scope2_emission_by_facilities()
                        Scope2_Emissions_by_Facilities.objects.all().delete()
                        for i in scope2_emission_by_facilities:
                            serializer4 = Scope2EmissionsbyFacilitiesSerializer(data=i)
                            if serializer4.is_valid():
                                serializer4.save()

                        scope2_emission_by_fuel = calculate_scope2_emissions_by_fuel()
                        Scope2_Emissions_by_Fuel.objects.all().delete()
                        for i in scope2_emission_by_fuel:
                            serializer5 = Scope2EmissionsbyFuelSerializer(data=i)
                            if serializer5.is_valid():
                                serializer5.save()
  
                        scope2_emission_by_ghg_type = calculate_scope2_emissions_by_ghg_type()
                        Scope2_Emissions_by_GHG_Type.objects.all().delete()
                        for i in scope2_emission_by_ghg_type:
                            serializer6 = Scope2EmissionsbyGHGTypeSerializer(data=i)
                            if serializer6.is_valid():
                                serializer6.save()
    
                        scope2_intensity = calculate_scope_2_intensity()
                        Scope2_Intensity.objects.all().delete()
                        for i in scope2_intensity:
                            serializer7 = Scope2IntensitySerializer(data=i)
                            if serializer7.is_valid():
                                serializer7.save()
             
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Electricity Consumption (mWh)"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()


                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    electricity_consumption_mwh = Electricity_Consumption_mwh.objects.get(id=id)
                    electricity_consumption_mwh.delete()

                    electricity_consumption_GJ = Electricity_Consumption_GJ.objects.get(id=id)
                    electricity_consumption_GJ.delete()

                    energy_intensity = calculate_energy_intensity()
                    Energy_Intensity.objects.all().delete()
                    for i in energy_intensity:
                        serializer2 = EnergyIntensitySerializer(data=i)
                        if serializer2.is_valid():
                            serializer2.save()

                    energy_intensity_for_production = calculate_energy_intensity_for_production()
                    Energy_Intensity_for_Production.objects.all().delete()
                    for i in energy_intensity_for_production:
                        serializer3 = EnergyIntensityforProductionSerializer(data=i)
                        if serializer3.is_valid():
                            serializer3.save()


                    scope2_emission_by_facilities = calculate_scope2_emission_by_facilities()
                    Scope2_Emissions_by_Facilities.objects.all().delete()
                    for i in scope2_emission_by_facilities:
                        serializer4 = Scope2EmissionsbyFacilitiesSerializer(data=i)
                        if serializer4.is_valid():
                            serializer4.save()

                    scope2_emission_by_fuel = calculate_scope2_emissions_by_fuel()
                    Scope2_Emissions_by_Fuel.objects.all().delete()
                    for i in scope2_emission_by_fuel:
                        serializer5 = Scope2EmissionsbyFuelSerializer(data=i)
                        if serializer5.is_valid():
                            serializer5.save()

                    scope2_emission_by_ghg_type = calculate_scope2_emissions_by_ghg_type()
                    Scope2_Emissions_by_GHG_Type.objects.all().delete()
                    for i in scope2_emission_by_ghg_type:
                        serializer6 = Scope2EmissionsbyGHGTypeSerializer(data=i)
                        if serializer6.is_valid():
                            serializer6.save()


                    scope2_intensity = calculate_scope_2_intensity()
                    Scope2_Intensity.objects.all().delete()
                    for i in scope2_intensity:
                        serializer7 = Scope2IntensitySerializer(data=i)
                        if serializer7.is_valid():
                            serializer7.save()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Electricity Consumption (mWh)"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Electricity_Consumption_mwh.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        


class Electricity_Consumption_mwh_Filter_View(APIView):
    permission_classes = [IsAuthenticated]

   
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            production = Electricity_Consumption_mwh.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ElectricityConsumptionmwhSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        


class Electricity_Consumption_GJ_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            electricity_consumption_gj = Electricity_Consumption_GJ.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(electricity_consumption_gj, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ElectricityConsumptionGJSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Electricity_Consumption_GJ_Filter_View(APIView):
    permission_classes = [IsAuthenticated]

   
    def get(self,request):
        try:

            facility = request.query_params.get('facility')

            production = Electricity_Consumption_GJ.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ElectricityConsumptionGJSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FuelTypeList_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            fuel_types = EmissionFactors.objects.filter(Type_of_Emission='Fuel').values_list('Fuel', flat=True).distinct()
            sorted_list = sorted(fuel_types)
            return Response(sorted_list, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class FuelUnitList_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            fuel_type = request.query_params.get('fuel_type', None)
           
            if fuel_type is None or not fuel_type.strip():
                return Response({'error': 'Fuel type parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

            fuel_type = fuel_type.strip()
            fuel_units = EmissionFactors.objects.filter(Type_of_Emission='Fuel', Fuel=fuel_type).values_list('Unit', flat=True)

            return Response(list(fuel_units), status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        


class Fuel_Consumption_Onsite_Combustion_General_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":
               
            fuel_consumption_general = Fuel_Consumption_Onsite_Combustion_General.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(fuel_consumption_general, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = FuelConsumptionOnsiteCombustionGeneralSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            if Fuel_Consumption_Onsite_Combustion_General.objects.count() == 0:
                id = 1
            else:
                id = Fuel_Consumption_Onsite_Combustion_General.objects.aggregate(Max('id'))['id__max'] + 1


            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            Unit = request.data.get('Unit')
            Fuel_Type = request.data.get('Fuel_Type')

            # Check if an entry already exists for the given facility and financial year
            if Fuel_Consumption_Onsite_Combustion_General.objects.filter(Facility=Facility, Fuel_Type=Fuel_Type, Financial_Year=Financial_Year, Unit=Unit).count() > 0:
                return Response({'error': 'Entry for this Unit, Fuel_Type, facility and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
            request.data['id'] = id

            total_fuel_consumption = request.data.get('Fuel_Consumption_Apr', 0) + request.data.get('Fuel_Consumption_May', 0)  + request.data.get('Fuel_Consumption_Jun', 0) + request.data.get('Fuel_Consumption_Jul', 0) + request.data.get('Fuel_Consumption_Aug', 0) + request.data.get('Fuel_Consumption_Sep', 0) + request.data.get('Fuel_Consumption_Oct', 0) + request.data.get('Fuel_Consumption_Nov', 0) + request.data.get('Fuel_Consumption_Dec', 0) + request.data.get('Fuel_Consumption_Jan', 0) + request.data.get('Fuel_Consumption_Feb', 0) + request.data.get('Fuel_Consumption_Mar', 0)
            request.data["Total_Fuel_Consumption"] = round(total_fuel_consumption, 2)

            fuel_type = request.data.get("Fuel_Type")
            unit = request.data.get("Unit")

            conversion_factor = get_conversion_factor(fuel_type, unit)

            Fuel_Consumption_GJ = {}
            Fuel_Consumption_GJ["id"] = id
            Fuel_Consumption_GJ["Financial_Year"] = request.data.get('Financial_Year')
            Fuel_Consumption_GJ["Facility"] = request.data.get('Facility')
            Fuel_Consumption_GJ["Fuel_Type"] = request.data.get('Fuel_Type')
            Fuel_Consumption_GJ["Unit"] = "Giga Joules"
            Fuel_Consumption_GJ["Fuel_Consumption_Apr"] = round(request.data.get('Fuel_Consumption_Apr', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_May"] = round(request.data.get('Fuel_Consumption_May', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Jun"] = round(request.data.get('Fuel_Consumption_Jun', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Jul"] = round(request.data.get('Fuel_Consumption_Jul', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Aug"] = round(request.data.get('Fuel_Consumption_Aug', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Sep"] = round(request.data.get('Fuel_Consumption_Sep', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Oct"] = round(request.data.get('Fuel_Consumption_Oct', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Nov"] = round(request.data.get('Fuel_Consumption_Nov', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Dec"] = round(request.data.get('Fuel_Consumption_Dec', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Jan"] = round(request.data.get('Fuel_Consumption_Jan', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Feb"] = round(request.data.get('Fuel_Consumption_Feb', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Mar"] = round(request.data.get('Fuel_Consumption_Mar', 0) * conversion_factor, 2)

            Fuel_Consumption_GJ["Total_Fuel_Consumption"] = round(Fuel_Consumption_GJ["Fuel_Consumption_Apr"] + Fuel_Consumption_GJ["Fuel_Consumption_May"] + Fuel_Consumption_GJ["Fuel_Consumption_Jun"] + Fuel_Consumption_GJ["Fuel_Consumption_Jul"] + Fuel_Consumption_GJ["Fuel_Consumption_Aug"] + Fuel_Consumption_GJ["Fuel_Consumption_Sep"] + Fuel_Consumption_GJ["Fuel_Consumption_Oct"] + Fuel_Consumption_GJ["Fuel_Consumption_Nov"] + Fuel_Consumption_GJ["Fuel_Consumption_Dec"] + Fuel_Consumption_GJ["Fuel_Consumption_Jan"] + Fuel_Consumption_GJ["Fuel_Consumption_Feb"] + Fuel_Consumption_GJ["Fuel_Consumption_Mar"], 2)

            serializer = FuelConsumptionOnsiteCombustionGeneralSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

            serializer1 = FuelConsumptionOnsiteCombustionGJSerializer(data=Fuel_Consumption_GJ)
            if serializer1.is_valid():
                serializer1.save()

                energy_intensity = calculate_energy_intensity()
                Energy_Intensity.objects.all().delete()
                for i in energy_intensity:
                    serializer2 = EnergyIntensitySerializer(data=i)
                    if serializer2.is_valid():
                        serializer2.save()

                energy_intensity_for_production = calculate_energy_intensity_for_production()
                Energy_Intensity_for_Production.objects.all().delete()
                for i in energy_intensity_for_production:
                    serializer3 = EnergyIntensityforProductionSerializer(data=i)
                    if serializer3.is_valid():
                        serializer3.save()


                scope_1_emissions_by_facilities = calculate_scope_1_emissions_by_facilities()
                Scope1_Emissions_by_Facilities.objects.all().delete()
                for i in scope_1_emissions_by_facilities:
                    serializer3 = Scope1EmissionsbyFacilitiesSerializer(data=i)
                    if serializer3.is_valid():
                        serializer3.save()

                scope_1_emissions_by_fuel = calculate_scope_1_emissions_by_fuel()
                Scope1_Emissions_by_Fuel.objects.all().delete()
                for i in scope_1_emissions_by_fuel:
                    serializer4 = Scope1EmissionsbyFuelSerializer(data=i)
                    if serializer4.is_valid():
                        serializer4.save()


                scope_1_emissions_by_ghg_type = calculate_scope_1_emissions_by_ghg_type()
                Scope1_Emissions_by_GHG_Type.objects.all().delete()
                for i in scope_1_emissions_by_ghg_type:
                    serializer5 = Scope1EmissionsbyGHGTypeSerializer(data=i)
                    if serializer5.is_valid():
                        serializer5.save()
                    else:
                        print("Error",i)


                scope_1_intensity = calculate_scope_1_intensity()
                Scope1_Intensity.objects.all().delete()
                for i in scope_1_intensity:
                    serializer6 = Scope1IntensitySerializer(data=i)
                    if serializer6.is_valid():
                        serializer6.save()
                    else:
                        print("Error",i)

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Fuel Consumption by on-site Combustion (Unit)"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            # import pdb;pdb.set_trace()
            id= kwargs.get('id')
            # import pdb; pdb.set_trace()
            if id is not None:
                try:
                    total_fuel_consumption = request.data.get('Fuel_Consumption_Apr', 0) + request.data.get('Fuel_Consumption_May', 0)  + request.data.get('Fuel_Consumption_Jun', 0) + request.data.get('Fuel_Consumption_Jul', 0) + request.data.get('Fuel_Consumption_Aug', 0) + request.data.get('Fuel_Consumption_Sep', 0) + request.data.get('Fuel_Consumption_Oct', 0) + request.data.get('Fuel_Consumption_Nov', 0) + request.data.get('Fuel_Consumption_Dec', 0) + request.data.get('Fuel_Consumption_Jan', 0) + request.data.get('Fuel_Consumption_Feb', 0) + request.data.get('Fuel_Consumption_Mar', 0)
                    request.data["Total_Fuel_Consumption"] = round(total_fuel_consumption, 2)

                    fuel_consumption_instance = Fuel_Consumption_Onsite_Combustion_General.objects.get(id=id)
                    serializer = FuelConsumptionOnsiteCombustionGeneralSerializer(fuel_consumption_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                    fuel_type = request.data.get("Fuel_Type")
                    unit = request.data.get("Unit")

                    conversion_factor = get_conversion_factor(fuel_type, unit)

                    Fuel_Consumption_GJ = {}
                    Fuel_Consumption_GJ["id"] = id
                    Fuel_Consumption_GJ["Financial_Year"] = request.data.get('Financial_Year')
                    Fuel_Consumption_GJ["Facility"] = request.data.get('Facility')
                    Fuel_Consumption_GJ["Fuel_Type"] = request.data.get('Fuel_Type')
                    Fuel_Consumption_GJ["Unit"] = "Giga Joules"
                    Fuel_Consumption_GJ["Fuel_Consumption_Apr"] = round(request.data.get('Fuel_Consumption_Apr', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_May"] = round(request.data.get('Fuel_Consumption_May', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Jun"] = round(request.data.get('Fuel_Consumption_Jun', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Jul"] = round(request.data.get('Fuel_Consumption_Jul', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Aug"] = round(request.data.get('Fuel_Consumption_Aug', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Sep"] = round(request.data.get('Fuel_Consumption_Sep', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Oct"] = round(request.data.get('Fuel_Consumption_Oct', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Nov"] = round(request.data.get('Fuel_Consumption_Nov', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Dec"] = round(request.data.get('Fuel_Consumption_Dec', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Jan"] = round(request.data.get('Fuel_Consumption_Jan', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Feb"] = round(request.data.get('Fuel_Consumption_Feb', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Mar"] = round(request.data.get('Fuel_Consumption_Mar', 0) * conversion_factor, 2)

                    Fuel_Consumption_GJ["Total_Fuel_Consumption"] = round(Fuel_Consumption_GJ["Fuel_Consumption_Apr"] + Fuel_Consumption_GJ["Fuel_Consumption_May"] + Fuel_Consumption_GJ["Fuel_Consumption_Jun"] + Fuel_Consumption_GJ["Fuel_Consumption_Jul"] + Fuel_Consumption_GJ["Fuel_Consumption_Aug"] + Fuel_Consumption_GJ["Fuel_Consumption_Sep"] + Fuel_Consumption_GJ["Fuel_Consumption_Oct"] + Fuel_Consumption_GJ["Fuel_Consumption_Nov"] + Fuel_Consumption_GJ["Fuel_Consumption_Dec"] + Fuel_Consumption_GJ["Fuel_Consumption_Jan"] + Fuel_Consumption_GJ["Fuel_Consumption_Feb"] + Fuel_Consumption_GJ["Fuel_Consumption_Mar"], 2)

                    fuel_consumption_instance1 = Fuel_Consumption_Onsite_Combustion_GJ.objects.get(id=id)

                    serializer1 = FuelConsumptionOnsiteCombustionGJSerializer(fuel_consumption_instance1, data=Fuel_Consumption_GJ, partial = True)
                    if serializer1.is_valid():
                        serializer1.save()

                        energy_intensity = calculate_energy_intensity()
                        Energy_Intensity.objects.all().delete()
                        for i in energy_intensity:
                            serializer2 = EnergyIntensitySerializer(data=i)
                            if serializer2.is_valid():
                                serializer2.save()

                        energy_intensity_for_production = calculate_energy_intensity_for_production()
                        Energy_Intensity_for_Production.objects.all().delete()
                        for i in energy_intensity_for_production:
                            serializer3 = EnergyIntensityforProductionSerializer(data=i)
                            if serializer3.is_valid():
                                serializer3.save()


                        scope_1_emissions_by_facilities = calculate_scope_1_emissions_by_facilities()
                        Scope1_Emissions_by_Facilities.objects.all().delete()
                        for i in scope_1_emissions_by_facilities:
                            serializer3 = Scope1EmissionsbyFacilitiesSerializer(data=i)
                            if serializer3.is_valid():
                                serializer3.save()

                        scope_1_emissions_by_fuel = calculate_scope_1_emissions_by_fuel()
                        Scope1_Emissions_by_Fuel.objects.all().delete()
                        for i in scope_1_emissions_by_fuel:
                            serializer4 = Scope1EmissionsbyFuelSerializer(data=i)
                            if serializer4.is_valid():
                                serializer4.save()
                            
                        scope_1_emissions_by_ghg_type = calculate_scope_1_emissions_by_ghg_type()
                        Scope1_Emissions_by_GHG_Type.objects.all().delete()
                        for i in scope_1_emissions_by_ghg_type:
                            serializer5 = Scope1EmissionsbyGHGTypeSerializer(data=i)
                            if serializer5.is_valid():
                                serializer5.save()
                            else:
                                print("Error",i) 


                        scope_1_intensity = calculate_scope_1_intensity()
                        Scope1_Intensity.objects.all().delete()
                        for i in scope_1_intensity:
                            serializer6 = Scope1IntensitySerializer(data=i)
                            if serializer6.is_valid():
                                serializer6.save()
                            else:
                                print("Error",i)   

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Fuel Consumption by on-site Combustion (Unit)"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Fuel_Consumption_Onsite_Combustion_General.DoesNotExist:
                    return Response({'error': 'Fuel Consumption record not found'}, status=status.HTTP_404_NOT_FOUND)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'id is required'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    fuel_consumption = Fuel_Consumption_Onsite_Combustion_General.objects.get(id=id)
                    fuel_consumption.delete()

                    fuel_consumption_GJ = Fuel_Consumption_Onsite_Combustion_GJ.objects.get(id=id)
                    fuel_consumption_GJ.delete()

                    energy_intensity = calculate_energy_intensity()
                    Energy_Intensity.objects.all().delete()
                    for i in energy_intensity:
                        serializer2 = EnergyIntensitySerializer(data=i)
                        if serializer2.is_valid():
                            serializer2.save()

                    energy_intensity_for_production = calculate_energy_intensity_for_production()
                    Energy_Intensity_for_Production.objects.all().delete()
                    for i in energy_intensity_for_production:
                        serializer3 = EnergyIntensityforProductionSerializer(data=i)
                        if serializer3.is_valid():
                            serializer3.save()

                    scope_1_emissions_by_facilities = calculate_scope_1_emissions_by_facilities()
                    Scope1_Emissions_by_Facilities.objects.all().delete()
                    for i in scope_1_emissions_by_facilities:
                        serializer3 = Scope1EmissionsbyFacilitiesSerializer(data=i)
                        if serializer3.is_valid():
                            serializer3.save()

                    scope_1_emissions_by_fuel = calculate_scope_1_emissions_by_fuel()
                    Scope1_Emissions_by_Fuel.objects.all().delete()
                    for i in scope_1_emissions_by_fuel:
                        serializer4 = Scope1EmissionsbyFuelSerializer(data=i)
                        if serializer4.is_valid():
                            serializer4.save()

                    scope_1_emissions_by_ghg_type = calculate_scope_1_emissions_by_ghg_type()
                    Scope1_Emissions_by_GHG_Type.objects.all().delete()
                    for i in scope_1_emissions_by_ghg_type:
                        serializer5 = Scope1EmissionsbyGHGTypeSerializer(data=i)
                        if serializer5.is_valid():
                            serializer5.save()
                        else:
                            print("Error",i)


                    scope_1_intensity = calculate_scope_1_intensity()
                    Scope1_Intensity.objects.all().delete()
                    for i in scope_1_intensity:
                        serializer6 = Scope1IntensitySerializer(data=i)
                        if serializer6.is_valid():
                            serializer6.save()
                        else:
                            print("Error",i)

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Fuel Consumption by on-site Combustion (Unit)"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()


                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Electricity_Consumption_mwh.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 



class Fuel_Consumption_Onsite_Combustion_GJ_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            fuel_consumption = Fuel_Consumption_Onsite_Combustion_GJ.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(fuel_consumption, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = FuelConsumptionOnsiteCombustionGeneralSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Fuel_Consumption_Onsite_Combustion_GJ_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:

            facility = request.query_params.get('facility')

            production = Fuel_Consumption_Onsite_Combustion_GJ.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = FuelConsumptionOnsiteCombustionGeneralSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Onsite_Vehicles_OwnershipList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            ownership_list = FUEL_ONSITE_VEHICLES_SCOPE

            if not ownership_list:
                return Response({'error': 'Ownership list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(ownership_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Ownership list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Fuel_Consumption_Onsite_Vehicles_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            fuel_consumption_general = Fuel_Consumption_Onsite_Vehicles_General.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(fuel_consumption_general, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = FuelConsumptionOnsiteVehiclesGeneralSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            Unit = request.data.get('Unit')
            Ownership = request.data.get('Ownership')
            Fuel_Type = request.data.get('Fuel_Type')

            # Check if an entry already exists for the given facility and financial year
            if Fuel_Consumption_Onsite_Vehicles_General.objects.filter(Facility=Facility, Fuel_Type=Fuel_Type, Ownership=Ownership, Financial_Year=Financial_Year, Unit=Unit).count() > 0:
                return Response({'error': 'Entry for this Unit, Ownership, Fuel_Type, facility and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)


            if Fuel_Consumption_Onsite_Vehicles_General.objects.count() == 0:
                id = 1
            else:
                id = Fuel_Consumption_Onsite_Vehicles_General.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            total_fuel_consumption = request.data.get('Fuel_Consumption_Apr', 0) + request.data.get('Fuel_Consumption_May', 0)  + request.data.get('Fuel_Consumption_Jun', 0) + request.data.get('Fuel_Consumption_Jul', 0) + request.data.get('Fuel_Consumption_Aug', 0) + request.data.get('Fuel_Consumption_Sep', 0) + request.data.get('Fuel_Consumption_Oct', 0) + request.data.get('Fuel_Consumption_Nov', 0) + request.data.get('Fuel_Consumption_Dec', 0) + request.data.get('Fuel_Consumption_Jan', 0) + request.data.get('Fuel_Consumption_Feb', 0) + request.data.get('Fuel_Consumption_Mar', 0)
            request.data["Total_Fuel_Consumption"] = round(total_fuel_consumption, 2)

            fuel_type = request.data.get("Fuel_Type")
            unit = request.data.get("Unit")

            conversion_factor = get_conversion_factor(fuel_type, unit)

            Fuel_Consumption_GJ = {}
            Fuel_Consumption_GJ["id"] = id
            Fuel_Consumption_GJ["Financial_Year"] = request.data.get('Financial_Year')
            Fuel_Consumption_GJ["Facility"] = request.data.get('Facility')
            Fuel_Consumption_GJ["Fuel_Type"] = request.data.get('Fuel_Type')
            Fuel_Consumption_GJ["Ownership"] = request.data.get('Ownership')
            Fuel_Consumption_GJ["Unit"] = "Giga Joules"
            Fuel_Consumption_GJ["Fuel_Consumption_Apr"] = round(request.data.get('Fuel_Consumption_Apr', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_May"] = round(request.data.get('Fuel_Consumption_May', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Jun"] = round(request.data.get('Fuel_Consumption_Jun', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Jul"] = round(request.data.get('Fuel_Consumption_Jul', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Aug"] = round(request.data.get('Fuel_Consumption_Aug', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Sep"] = round(request.data.get('Fuel_Consumption_Sep', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Oct"] = round(request.data.get('Fuel_Consumption_Oct', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Nov"] = round(request.data.get('Fuel_Consumption_Nov', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Dec"] = round(request.data.get('Fuel_Consumption_Dec', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Jan"] = round(request.data.get('Fuel_Consumption_Jan', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Feb"] = round(request.data.get('Fuel_Consumption_Feb', 0) * conversion_factor, 2)
            Fuel_Consumption_GJ["Fuel_Consumption_Mar"] = round(request.data.get('Fuel_Consumption_Mar', 0) * conversion_factor, 2)

            Fuel_Consumption_GJ["Total_Fuel_Consumption"] = round(Fuel_Consumption_GJ["Fuel_Consumption_Apr"] + Fuel_Consumption_GJ["Fuel_Consumption_May"] + Fuel_Consumption_GJ["Fuel_Consumption_Jun"] + Fuel_Consumption_GJ["Fuel_Consumption_Jul"] + Fuel_Consumption_GJ["Fuel_Consumption_Aug"] + Fuel_Consumption_GJ["Fuel_Consumption_Sep"] + Fuel_Consumption_GJ["Fuel_Consumption_Oct"] + Fuel_Consumption_GJ["Fuel_Consumption_Nov"] + Fuel_Consumption_GJ["Fuel_Consumption_Dec"] + Fuel_Consumption_GJ["Fuel_Consumption_Jan"] + Fuel_Consumption_GJ["Fuel_Consumption_Feb"] + Fuel_Consumption_GJ["Fuel_Consumption_Mar"], 2)

            serializer = FuelConsumptionOnsiteVehiclesGeneralSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

            serializer1 = FuelConsumptionOnsiteVehiclesGJSerializer(data=Fuel_Consumption_GJ)
            if serializer1.is_valid():
                serializer1.save()

                scope_1_emissions_by_facilities = calculate_scope_1_emissions_by_facilities()
                Scope1_Emissions_by_Facilities.objects.all().delete()
                for i in scope_1_emissions_by_facilities:
                    serializer3 = Scope1EmissionsbyFacilitiesSerializer(data=i)
                    if serializer3.is_valid():
                        serializer3.save()

                scope_1_emissions_by_fuel = calculate_scope_1_emissions_by_fuel()
                Scope1_Emissions_by_Fuel.objects.all().delete()
                for i in scope_1_emissions_by_fuel:
                    serializer4 = Scope1EmissionsbyFuelSerializer(data=i)
                    if serializer4.is_valid():
                        serializer4.save()

                scope_1_emissions_by_ghg_type = calculate_scope_1_emissions_by_ghg_type()
                Scope1_Emissions_by_GHG_Type.objects.all().delete()
                for i in scope_1_emissions_by_ghg_type:
                    serializer5 = Scope1EmissionsbyGHGTypeSerializer(data=i)
                    if serializer5.is_valid():
                        serializer5.save()
                    else:
                        print("Error",i)

                scope_1_intensity = calculate_scope_1_intensity()
                Scope1_Intensity.objects.all().delete()
                for i in scope_1_intensity:
                    serializer6 = Scope1IntensitySerializer(data=i)
                    if serializer6.is_valid():
                        serializer6.save()
                    else:
                        print("Error",i)

                
                scope_3_emissions_by_facilities = calculate_scope_3_emissions_by_facilities()
                Scope3_Emissions_by_Facilities.objects.all().delete()
                for i in scope_3_emissions_by_facilities:
                    serializer7 = Scope3EmissionsbyFacilitiesSerializer(data=i)
                    if serializer7.is_valid():
                        serializer7.save()


                scope_3_emissions_by_activity = calculate_scope_3_emissions_by_activity()
                Scope3_Emissions_by_Activity.objects.all().delete()
                for i in scope_3_emissions_by_activity:
                    serializer8 = Scope3EmissionsbyActivitySerializer(data=i)
                    if serializer8.is_valid():
                        serializer8.save()


                scope_3_emissions_by_ghg_type = calculate_scope_3_emissions_by_ghg_type()
                Scope3_Emissions_by_GHG_Type.objects.all().delete()
                for i in scope_3_emissions_by_ghg_type:
                    serializer = Scope3EmissionsbyGHGTypeSerializer(data=i)
                    if serializer.is_valid():
                        serializer.save()

                
                scope_3_intensity = calculate_scope_3_intensity()
                Scope3_Intensity.objects.all().delete()
                for i in scope_3_intensity:
                    serializer = Scope3IntensitySerializer(data=i)
                    if serializer.is_valid():
                        serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Fuel Consumption by on-site Vehicles (Unit)"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
           
            if id is not None:
                try:

                    total_fuel_consumption = request.data.get('Fuel_Consumption_Apr', 0) + request.data.get('Fuel_Consumption_May', 0)  + request.data.get('Fuel_Consumption_Jun', 0) + request.data.get('Fuel_Consumption_Jul', 0) + request.data.get('Fuel_Consumption_Aug', 0) + request.data.get('Fuel_Consumption_Sep', 0) + request.data.get('Fuel_Consumption_Oct', 0) + request.data.get('Fuel_Consumption_Nov', 0) + request.data.get('Fuel_Consumption_Dec', 0) + request.data.get('Fuel_Consumption_Jan', 0) + request.data.get('Fuel_Consumption_Feb', 0) + request.data.get('Fuel_Consumption_Mar', 0)
                    request.data["Total_Fuel_Consumption"] = round(total_fuel_consumption, 2)

                    fuel_consumption_instance = Fuel_Consumption_Onsite_Vehicles_General.objects.get(id=id)
                    serializer = FuelConsumptionOnsiteVehiclesGeneralSerializer(fuel_consumption_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                    fuel_type = request.data.get("Fuel_Type")
                    unit = request.data.get("Unit")

                    conversion_factor = get_conversion_factor(fuel_type, unit)

                    Fuel_Consumption_GJ = {}
                    Fuel_Consumption_GJ["id"] = id
                    Fuel_Consumption_GJ["Financial_Year"] = request.data.get('Financial_Year')
                    Fuel_Consumption_GJ["Facility"] = request.data.get('Facility')
                    Fuel_Consumption_GJ["Fuel_Type"] = request.data.get('Fuel_Type')
                    Fuel_Consumption_GJ["Ownership"] = request.data.get('Ownership')
                    Fuel_Consumption_GJ["Unit"] = "Giga Joules"
                    Fuel_Consumption_GJ["Fuel_Consumption_Apr"] = round(request.data.get('Fuel_Consumption_Apr', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_May"] = round(request.data.get('Fuel_Consumption_May', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Jun"] = round(request.data.get('Fuel_Consumption_Jun', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Jul"] = round(request.data.get('Fuel_Consumption_Jul', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Aug"] = round(request.data.get('Fuel_Consumption_Aug', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Sep"] = round(request.data.get('Fuel_Consumption_Sep', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Oct"] = round(request.data.get('Fuel_Consumption_Oct', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Nov"] = round(request.data.get('Fuel_Consumption_Nov', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Dec"] = round(request.data.get('Fuel_Consumption_Dec', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Jan"] = round(request.data.get('Fuel_Consumption_Jan', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Feb"] = round(request.data.get('Fuel_Consumption_Feb', 0) * conversion_factor, 2)
                    Fuel_Consumption_GJ["Fuel_Consumption_Mar"] = round(request.data.get('Fuel_Consumption_Mar', 0) * conversion_factor, 2)

                    Fuel_Consumption_GJ["Total_Fuel_Consumption"] = round(Fuel_Consumption_GJ["Fuel_Consumption_Apr"] + Fuel_Consumption_GJ["Fuel_Consumption_May"] + Fuel_Consumption_GJ["Fuel_Consumption_Jun"] + Fuel_Consumption_GJ["Fuel_Consumption_Jul"] + Fuel_Consumption_GJ["Fuel_Consumption_Aug"] + Fuel_Consumption_GJ["Fuel_Consumption_Sep"] + Fuel_Consumption_GJ["Fuel_Consumption_Oct"] + Fuel_Consumption_GJ["Fuel_Consumption_Nov"] + Fuel_Consumption_GJ["Fuel_Consumption_Dec"] + Fuel_Consumption_GJ["Fuel_Consumption_Jan"] + Fuel_Consumption_GJ["Fuel_Consumption_Feb"] + Fuel_Consumption_GJ["Fuel_Consumption_Mar"], 2)

                    fuel_consumption_instance1 = Fuel_Consumption_Onsite_Vehicles_GJ.objects.get(id=id)

                    serializer1 = FuelConsumptionOnsiteVehiclesGJSerializer(fuel_consumption_instance1, data=Fuel_Consumption_GJ, partial = True)
                    if serializer1.is_valid():
                        serializer1.save()

                        scope_1_emissions_by_facilities = calculate_scope_1_emissions_by_facilities()
                        Scope1_Emissions_by_Facilities.objects.all().delete()
                        for i in scope_1_emissions_by_facilities:
                            serializer3 = Scope1EmissionsbyFacilitiesSerializer(data=i)
                            if serializer3.is_valid():
                                serializer3.save()


                        scope_1_emissions_by_fuel = calculate_scope_1_emissions_by_fuel()
                        Scope1_Emissions_by_Fuel.objects.all().delete()
                        for i in scope_1_emissions_by_fuel:
                            serializer4 = Scope1EmissionsbyFuelSerializer(data=i)
                            if serializer4.is_valid():
                                serializer4.save()

                        scope_1_emissions_by_ghg_type = calculate_scope_1_emissions_by_ghg_type()
                        Scope1_Emissions_by_GHG_Type.objects.all().delete()
                        for i in scope_1_emissions_by_ghg_type:
                            serializer5 = Scope1EmissionsbyGHGTypeSerializer(data=i)
                            if serializer5.is_valid():
                                serializer5.save()
                            else:
                                print("ERROR",i)

                        scope_1_intensity = calculate_scope_1_intensity()
                        Scope1_Intensity.objects.all().delete()
                        for i in scope_1_intensity:
                            serializer6 = Scope1IntensitySerializer(data=i)
                            if serializer6.is_valid():
                                serializer6.save()
                            else:
                                print("Error",i)


                        scope_3_emissions_by_facilities = calculate_scope_3_emissions_by_facilities()
                        Scope3_Emissions_by_Facilities.objects.all().delete()
                        for i in scope_3_emissions_by_facilities:
                            serializer7 = Scope3EmissionsbyFacilitiesSerializer(data=i)
                            if serializer7.is_valid():
                                serializer7.save()

                        scope_3_emissions_by_activity = calculate_scope_3_emissions_by_activity()
                        Scope3_Emissions_by_Activity.objects.all().delete()
                        for i in scope_3_emissions_by_activity:
                            serializer8 = Scope3EmissionsbyActivitySerializer(data=i)
                            if serializer8.is_valid():
                                serializer8.save()

                        
                        scope_3_emissions_by_ghg_type = calculate_scope_3_emissions_by_ghg_type()
                        Scope3_Emissions_by_GHG_Type.objects.all().delete()
                        for i in scope_3_emissions_by_ghg_type:
                            serializer = Scope3EmissionsbyGHGTypeSerializer(data=i)
                            if serializer.is_valid():
                                serializer.save()


                        scope_3_intensity = calculate_scope_3_intensity()
                        Scope3_Intensity.objects.all().delete()
                        for i in scope_3_intensity:
                            serializer = Scope3IntensitySerializer(data=i)
                            if serializer.is_valid():
                                serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Fuel Consumption by on-site Vehicles (Unit)"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()


                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
       
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    fuel_consumption = Fuel_Consumption_Onsite_Vehicles_General.objects.get(id=id)
                    fuel_consumption.delete()

                    fuel_consumption_GJ = Fuel_Consumption_Onsite_Vehicles_GJ.objects.get(id=id)
                    fuel_consumption_GJ.delete()

                    scope_1_emissions_by_facilities = calculate_scope_1_emissions_by_facilities()
                    Scope1_Emissions_by_Facilities.objects.all().delete()
                    for i in scope_1_emissions_by_facilities:
                        serializer3 = Scope1EmissionsbyFacilitiesSerializer(data=i)
                        if serializer3.is_valid():
                            serializer3.save()

                    scope_1_emissions_by_fuel = calculate_scope_1_emissions_by_fuel()
                    Scope1_Emissions_by_Fuel.objects.all().delete()
                    for i in scope_1_emissions_by_fuel:
                        serializer4 = Scope1EmissionsbyFuelSerializer(data=i)
                        if serializer4.is_valid():
                            serializer4.save()

                    scope_1_emissions_by_ghg_type = calculate_scope_1_emissions_by_ghg_type()
                    Scope1_Emissions_by_GHG_Type.objects.all().delete()
                    for i in scope_1_emissions_by_ghg_type:
                        serializer5 = Scope1EmissionsbyGHGTypeSerializer(data=i)
                        if serializer5.is_valid():
                            serializer5.save()
                        else:
                            print("Error",i)

                    scope_1_intensity = calculate_scope_1_intensity()
                    Scope1_Intensity.objects.all().delete()
                    for i in scope_1_intensity:
                        serializer6 = Scope1IntensitySerializer(data=i)
                        if serializer6.is_valid():
                            serializer6.save()
                        else:
                            print("Error",i)


                    scope_3_emissions_by_facilities = calculate_scope_3_emissions_by_facilities()
                    Scope3_Emissions_by_Facilities.objects.all().delete()
                    for i in scope_3_emissions_by_facilities:
                        serializer7 = Scope3EmissionsbyFacilitiesSerializer(data=i)
                        if serializer7.is_valid():
                            serializer7.save()


                    scope_3_emissions_by_activity = calculate_scope_3_emissions_by_activity()
                    Scope3_Emissions_by_Activity.objects.all().delete()
                    for i in scope_3_emissions_by_activity:
                        serializer8 = Scope3EmissionsbyActivitySerializer(data=i)
                        if serializer8.is_valid():
                            serializer8.save()

                    scope_3_emissions_by_ghg_type = calculate_scope_3_emissions_by_ghg_type()
                    Scope3_Emissions_by_GHG_Type.objects.all().delete()
                    for i in scope_3_emissions_by_ghg_type:
                        serializer = Scope3EmissionsbyGHGTypeSerializer(data=i)
                        if serializer.is_valid():
                            serializer.save()

                    
                    scope_3_intensity = calculate_scope_3_intensity()
                    Scope3_Intensity.objects.all().delete()
                    for i in scope_3_intensity:
                        serializer = Scope3IntensitySerializer(data=i)
                        if serializer.is_valid():
                            serializer.save()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Fuel Consumption by on-site Vehicles (Unit)"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()


                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Fuel_Consumption_Onsite_Vehicles_General.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Fuel_Consumption_Onsite_Vehicles_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')

            production = Fuel_Consumption_Onsite_Vehicles_General.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = FuelConsumptionOnsiteVehiclesGeneralSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #         return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class OnsiteVehiclesFuelTypeList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            fuel_type_list = ONSITE_VEHICLES_FUEL_TYPE

            if not fuel_type_list:
                return Response({'error': 'Fuel Type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(fuel_type_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Fuel Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Fuel_Consumption_Onsite_Vehicles_GJ_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            fuel_consumption_gj = Fuel_Consumption_Onsite_Vehicles_GJ.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(fuel_consumption_gj, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = FuelConsumptionOnsiteVehiclesGJSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Fuel_Consumption_Onsite_Vehicles_GJ_filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')

            production = Fuel_Consumption_Onsite_Vehicles_GJ.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = FuelConsumptionOnsiteVehiclesGJSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Fuel_Consumption_Onsite_Combustion_General_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            facility = request.query_params.get('facility')

            production = Fuel_Consumption_Onsite_Combustion_General.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = FuelConsumptionOnsiteCombustionGeneralSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class Logistics_Fuel_Type_List_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            logistics_fuel_type_list = LOGISTICS_FUEL_TYPE

            if not logistics_fuel_type_list:
                return Response({'error': 'Logistics Fuel Type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(logistics_fuel_type_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Logistics Fuel Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Inbound_Logistics_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            inbound_logistics = Inbound_Logistics.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(inbound_logistics, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = InboundLogisticsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            Unit = request.data.get('Unit')
            Ownership = request.data.get('Ownership')
            Fuel_Type = request.data.get('Fuel_Type')

            # Check if an entry already exists for the given facility and financial year
            if Inbound_Logistics.objects.filter(Facility=Facility, Fuel_Type=Fuel_Type, Ownership=Ownership, Financial_Year=Financial_Year, Unit=Unit).count() > 0:
                return Response({'error': 'Entry for this Unit,Ownership, Fuel_Type, facility and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            if Inbound_Logistics.objects.count() == 0:
                id = 1
            else:
                id = Inbound_Logistics.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            total_fuel_consumption = request.data.get('Fuel_Consumption_Apr', 0) + request.data.get('Fuel_Consumption_May', 0)  + request.data.get('Fuel_Consumption_Jun', 0) + request.data.get('Fuel_Consumption_Jul', 0) + request.data.get('Fuel_Consumption_Aug', 0) + request.data.get('Fuel_Consumption_Sep', 0) + request.data.get('Fuel_Consumption_Oct', 0) + request.data.get('Fuel_Consumption_Nov', 0) + request.data.get('Fuel_Consumption_Dec', 0) + request.data.get('Fuel_Consumption_Jan', 0) + request.data.get('Fuel_Consumption_Feb', 0) + request.data.get('Fuel_Consumption_Mar', 0)
            request.data["Total_Fuel_Consumption"] = round(total_fuel_consumption, 2)

            serializer = InboundLogisticsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                scope_3_emissions_by_facilities = calculate_scope_3_emissions_by_facilities()
                Scope3_Emissions_by_Facilities.objects.all().delete()
                for i in scope_3_emissions_by_facilities:
                    serializer1 = Scope3EmissionsbyFacilitiesSerializer(data=i)
                    if serializer1.is_valid():
                        serializer1.save()

                scope_3_emissions_by_activity = calculate_scope_3_emissions_by_activity()
                Scope3_Emissions_by_Activity.objects.all().delete()
                for i in scope_3_emissions_by_activity:
                    serializer2 = Scope3EmissionsbyActivitySerializer(data=i)
                    if serializer2.is_valid():
                        serializer2.save()

                
                scope_3_emissions_by_ghg_type = calculate_scope_3_emissions_by_ghg_type()
                Scope3_Emissions_by_GHG_Type.objects.all().delete()
                for i in scope_3_emissions_by_ghg_type:
                    serializer = Scope3EmissionsbyGHGTypeSerializer(data=i)
                    if serializer.is_valid():
                        serializer.save()

                
                scope_3_intensity = calculate_scope_3_intensity()
                Scope3_Intensity.objects.all().delete()
                for i in scope_3_intensity:
                    serializer = Scope3IntensitySerializer(data=i)
                    if serializer.is_valid():
                        serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Fuel Consumption in In-bound Logistics"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            # import pdb; pdb.set_trace()
            if id is not None:
                try:
                    total_fuel_consumption = request.data.get('Fuel_Consumption_Apr', 0) + request.data.get('Fuel_Consumption_May', 0)  + request.data.get('Fuel_Consumption_Jun', 0) + request.data.get('Fuel_Consumption_Jul', 0) + request.data.get('Fuel_Consumption_Aug', 0) + request.data.get('Fuel_Consumption_Sep', 0) + request.data.get('Fuel_Consumption_Oct', 0) + request.data.get('Fuel_Consumption_Nov', 0) + request.data.get('Fuel_Consumption_Dec', 0) + request.data.get('Fuel_Consumption_Jan', 0) + request.data.get('Fuel_Consumption_Feb', 0) + request.data.get('Fuel_Consumption_Mar', 0)
                    request.data["Total_Fuel_Consumption"] = round(total_fuel_consumption, 2)

                    fuel_consumption_instance = Inbound_Logistics.objects.get(id=id)
                    serializer = InboundLogisticsSerializer(fuel_consumption_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        scope_3_emissions_by_facilities = calculate_scope_3_emissions_by_facilities()
                        Scope3_Emissions_by_Facilities.objects.all().delete()
                        for i in scope_3_emissions_by_facilities:
                            serializer1 = Scope3EmissionsbyFacilitiesSerializer(data=i)
                            if serializer1.is_valid():
                                serializer1.save()

                        scope_3_emissions_by_activity = calculate_scope_3_emissions_by_activity()
                        Scope3_Emissions_by_Activity.objects.all().delete()
                        for i in scope_3_emissions_by_activity:
                            serializer2 = Scope3EmissionsbyActivitySerializer(data=i)
                            if serializer2.is_valid():
                                serializer2.save()

                        scope_3_emissions_by_ghg_type = calculate_scope_3_emissions_by_ghg_type()
                        Scope3_Emissions_by_GHG_Type.objects.all().delete()
                        for i in scope_3_emissions_by_ghg_type:
                            serializer = Scope3EmissionsbyGHGTypeSerializer(data=i)
                            if serializer.is_valid():
                                serializer.save()

                        
                        scope_3_intensity = calculate_scope_3_intensity()
                        Scope3_Intensity.objects.all().delete()
                        for i in scope_3_intensity:
                            serializer = Scope3IntensitySerializer(data=i)
                            if serializer.is_valid():
                                serializer.save()


                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Fuel Consumption in In-bound Logistics"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    inbound_logistics = Inbound_Logistics.objects.get(id=id)
                    inbound_logistics.delete()

                    scope_3_emissions_by_facilities = calculate_scope_3_emissions_by_facilities()
                    Scope3_Emissions_by_Facilities.objects.all().delete()
                    for i in scope_3_emissions_by_facilities:
                        serializer1 = Scope3EmissionsbyFacilitiesSerializer(data=i)
                        if serializer1.is_valid():
                            serializer1.save()

                    scope_3_emissions_by_activity = calculate_scope_3_emissions_by_activity()
                    Scope3_Emissions_by_Activity.objects.all().delete()
                    for i in scope_3_emissions_by_activity:
                        serializer2 = Scope3EmissionsbyActivitySerializer(data=i)
                        if serializer2.is_valid():
                            serializer2.save()


                    scope_3_emissions_by_ghg_type = calculate_scope_3_emissions_by_ghg_type()
                    Scope3_Emissions_by_GHG_Type.objects.all().delete()
                    for i in scope_3_emissions_by_ghg_type:
                        serializer = Scope3EmissionsbyGHGTypeSerializer(data=i)
                        if serializer.is_valid():
                            serializer.save()

                    
                    scope_3_intensity = calculate_scope_3_intensity()
                    Scope3_Intensity.objects.all().delete()
                    for i in scope_3_intensity:
                        serializer = Scope3IntensitySerializer(data=i)
                        if serializer.is_valid():
                            serializer.save()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Fuel Consumption in In-bound Logistics"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()


                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Inbound_Logistics.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
class Inbound_Logistics_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')

            production = Inbound_Logistics.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = InboundLogisticsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Outbound_Logistics_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            outbound_logistics = Outbound_Logistics.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(outbound_logistics, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = OutboundLogisticsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            Unit = request.data.get('Unit')
            Ownership = request.data.get('Ownership')
            Fuel_Type = request.data.get('Fuel_Type')

            # Check if an entry already exists for the given facility and financial year
            if Outbound_Logistics.objects.filter(Facility=Facility, Fuel_Type=Fuel_Type, Ownership=Ownership, Financial_Year=Financial_Year, Unit=Unit).count() > 0:
                return Response({'error': 'Entry for this Unit, Ownership, Fuel_Type, facility and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Outbound_Logistics.objects.count() == 0:
                id = 1
            else:
                id = Outbound_Logistics.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            total_fuel_consumption = request.data.get('Fuel_Consumption_Apr', 0) + request.data.get('Fuel_Consumption_May', 0)  + request.data.get('Fuel_Consumption_Jun', 0) + request.data.get('Fuel_Consumption_Jul', 0) + request.data.get('Fuel_Consumption_Aug', 0) + request.data.get('Fuel_Consumption_Sep', 0) + request.data.get('Fuel_Consumption_Oct', 0) + request.data.get('Fuel_Consumption_Nov', 0) + request.data.get('Fuel_Consumption_Dec', 0) + request.data.get('Fuel_Consumption_Jan', 0) + request.data.get('Fuel_Consumption_Feb', 0) + request.data.get('Fuel_Consumption_Mar', 0)
            request.data["Total_Fuel_Consumption"] = round(total_fuel_consumption, 2)

            serializer = OutboundLogisticsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                scope_3_emissions_by_facilities = calculate_scope_3_emissions_by_facilities()
                Scope3_Emissions_by_Facilities.objects.all().delete()
                for i in scope_3_emissions_by_facilities:
                    serializer1 = Scope3EmissionsbyFacilitiesSerializer(data=i)
                    if serializer1.is_valid():
                        serializer1.save()

                
                scope_3_emissions_by_activity = calculate_scope_3_emissions_by_activity()
                Scope3_Emissions_by_Activity.objects.all().delete()
                for i in scope_3_emissions_by_activity:
                    serializer2 = Scope3EmissionsbyActivitySerializer(data=i)
                    if serializer2.is_valid():
                        serializer2.save()

                scope_3_emissions_by_ghg_type = calculate_scope_3_emissions_by_ghg_type()
                Scope3_Emissions_by_GHG_Type.objects.all().delete()
                for i in scope_3_emissions_by_ghg_type:
                    serializer = Scope3EmissionsbyGHGTypeSerializer(data=i)
                    if serializer.is_valid():
                        serializer.save()


                scope_3_intensity = calculate_scope_3_intensity()
                Scope3_Intensity.objects.all().delete()
                for i in scope_3_intensity:
                    serializer = Scope3IntensitySerializer(data=i)
                    if serializer.is_valid():
                        serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Fuel Consumption in Out-bound Logistics"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            # import pdb; pdb.set_trace()
            if id is not None:
                try:
                    total_fuel_consumption = request.data.get('Fuel_Consumption_Apr', 0) + request.data.get('Fuel_Consumption_May', 0)  + request.data.get('Fuel_Consumption_Jun', 0) + request.data.get('Fuel_Consumption_Jul', 0) + request.data.get('Fuel_Consumption_Aug', 0) + request.data.get('Fuel_Consumption_Sep', 0) + request.data.get('Fuel_Consumption_Oct', 0) + request.data.get('Fuel_Consumption_Nov', 0) + request.data.get('Fuel_Consumption_Dec', 0) + request.data.get('Fuel_Consumption_Jan', 0) + request.data.get('Fuel_Consumption_Feb', 0) + request.data.get('Fuel_Consumption_Mar', 0)
                    request.data["Total_Fuel_Consumption"] = round(total_fuel_consumption, 2)

                    fuel_consumption_instance = Outbound_Logistics.objects.get(id=id)
                    serializer = OutboundLogisticsSerializer(fuel_consumption_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        scope_3_emissions_by_facilities = calculate_scope_3_emissions_by_facilities()
                        Scope3_Emissions_by_Facilities.objects.all().delete()
                        for i in scope_3_emissions_by_facilities:
                            serializer1 = Scope3EmissionsbyFacilitiesSerializer(data=i)
                            if serializer1.is_valid():
                                serializer1.save()

                        scope_3_emissions_by_activity = calculate_scope_3_emissions_by_activity()
                        Scope3_Emissions_by_Activity.objects.all().delete()
                        for i in scope_3_emissions_by_activity:
                            serializer2 = Scope3EmissionsbyActivitySerializer(data=i)
                            if serializer2.is_valid():
                                serializer2.save()

                        
                        scope_3_emissions_by_ghg_type = calculate_scope_3_emissions_by_ghg_type()
                        Scope3_Emissions_by_GHG_Type.objects.all().delete()
                        for i in scope_3_emissions_by_ghg_type:
                            serializer = Scope3EmissionsbyGHGTypeSerializer(data=i)
                            if serializer.is_valid():
                                serializer.save()

                        
                        scope_3_intensity = calculate_scope_3_intensity()
                        Scope3_Intensity.objects.all().delete()
                        for i in scope_3_intensity:
                            serializer = Scope3IntensitySerializer(data=i)
                            if serializer.is_valid():
                                serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Fuel Consumption in Out-bound Logistics"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error': str(e)})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    outbound_logistics = Outbound_Logistics.objects.get(id=id)
                    outbound_logistics.delete()

                    scope_3_emissions_by_facilities = calculate_scope_3_emissions_by_facilities()
                    Scope3_Emissions_by_Facilities.objects.all().delete()
                    for i in scope_3_emissions_by_facilities:
                        serializer1 = Scope3EmissionsbyFacilitiesSerializer(data=i)
                        if serializer1.is_valid():
                            serializer1.save()

                    
                    scope_3_emissions_by_activity = calculate_scope_3_emissions_by_activity()
                    Scope3_Emissions_by_Activity.objects.all().delete()
                    for i in scope_3_emissions_by_activity:
                        serializer2 = Scope3EmissionsbyActivitySerializer(data=i)
                        if serializer2.is_valid():
                            serializer2.save()

                    
                    scope_3_emissions_by_ghg_type = calculate_scope_3_emissions_by_ghg_type()
                    Scope3_Emissions_by_GHG_Type.objects.all().delete()
                    for i in scope_3_emissions_by_ghg_type:
                        serializer = Scope3EmissionsbyGHGTypeSerializer(data=i)
                        if serializer.is_valid():
                            serializer.save()


                    scope_3_intensity = calculate_scope_3_intensity()
                    Scope3_Intensity.objects.all().delete()
                    for i in scope_3_intensity:
                        serializer = Scope3IntensitySerializer(data=i)
                        if serializer.is_valid():
                            serializer.save()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Fuel Consumption in Out-bound Logistics"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Outbound_Logistics.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
class Outbound_Logistics_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            production = Outbound_Logistics.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = OutboundLogisticsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Business_Travel_Mode_List_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            business_travel_mode_list = BUSINESS_TRAVEL_MODE

            if not business_travel_mode_list:
                return Response({'error': 'Business Travel Mode list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(business_travel_mode_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Business Travel Mode list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Business_Travel_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            business_travel = Business_Travel.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(business_travel, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = BusinessTravelSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            Mode = request.data.get('Mode')
            Unit = request.data.get('Unit')

            # Check if an entry already exists for the given facility and financial year
            if Business_Travel.objects.filter(Facility=Facility, Financial_Year=Financial_Year, Unit=Unit, Mode=Mode).count() > 0:
                return Response({'error': 'Entry for this financial year, Facility, Mode and Unit  already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            if Business_Travel.objects.count() == 0:
                id = 1
            else:
                id = Business_Travel.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            total_fuel_consumption = request.data.get('Fuel_Consumption_Apr', 0) + request.data.get('Fuel_Consumption_May', 0)  + request.data.get('Fuel_Consumption_Jun', 0) + request.data.get('Fuel_Consumption_Jul', 0) + request.data.get('Fuel_Consumption_Aug', 0) + request.data.get('Fuel_Consumption_Sep', 0) + request.data.get('Fuel_Consumption_Oct', 0) + request.data.get('Fuel_Consumption_Nov', 0) + request.data.get('Fuel_Consumption_Dec', 0) + request.data.get('Fuel_Consumption_Jan', 0) + request.data.get('Fuel_Consumption_Feb', 0) + request.data.get('Fuel_Consumption_Mar', 0)
            request.data["Total_Fuel_Consumption"] = round(total_fuel_consumption, 2)

            serializer = BusinessTravelSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                scope_3_emissions_by_facilities = calculate_scope_3_emissions_by_facilities()
                Scope3_Emissions_by_Facilities.objects.all().delete()
                for i in scope_3_emissions_by_facilities:
                    serializer1 = Scope3EmissionsbyFacilitiesSerializer(data=i)
                    if serializer1.is_valid():
                        serializer1.save()

                scope_3_emissions_by_activity = calculate_scope_3_emissions_by_activity()
                Scope3_Emissions_by_Activity.objects.all().delete()
                for i in scope_3_emissions_by_activity:
                    serializer2 = Scope3EmissionsbyActivitySerializer(data=i)
                    if serializer2.is_valid():
                        serializer2.save()

                
                scope_3_emissions_by_ghg_type = calculate_scope_3_emissions_by_ghg_type()
                Scope3_Emissions_by_GHG_Type.objects.all().delete()
                for i in scope_3_emissions_by_ghg_type:
                    serializer = Scope3EmissionsbyGHGTypeSerializer(data=i)
                    if serializer.is_valid():
                        serializer.save()


                scope_3_intensity = calculate_scope_3_intensity()
                Scope3_Intensity.objects.all().delete()
                for i in scope_3_intensity:
                    serializer = Scope3IntensitySerializer(data=i)
                    if serializer.is_valid():
                        serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Fuel Consumption in Business Travel"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            # import pdb; pdb.set_trace()
            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            Mode = request.data.get('Mode')
            Unit = request.data.get('Unit')

            # Check if an entry already exists for the given facility and financial year
            if Business_Travel.objects.filter(Facility=Facility, Financial_Year=Financial_Year, Unit=Unit, Mode=Mode).exclude(id=id).count() > 0:
                return Response({'error': 'Entry for this Facility Destination, Mode, Source, Unit and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            if id is not None:
                try:
                    total_fuel_consumption = request.data.get('Fuel_Consumption_Apr', 0) + request.data.get('Fuel_Consumption_May', 0)  + request.data.get('Fuel_Consumption_Jun', 0) + request.data.get('Fuel_Consumption_Jul', 0) + request.data.get('Fuel_Consumption_Aug', 0) + request.data.get('Fuel_Consumption_Sep', 0) + request.data.get('Fuel_Consumption_Oct', 0) + request.data.get('Fuel_Consumption_Nov', 0) + request.data.get('Fuel_Consumption_Dec', 0) + request.data.get('Fuel_Consumption_Jan', 0) + request.data.get('Fuel_Consumption_Feb', 0) + request.data.get('Fuel_Consumption_Mar', 0)
                    request.data["Total_Fuel_Consumption"] = round(total_fuel_consumption, 2)

                    fuel_consumption_instance = Business_Travel.objects.get(id=id)
                    serializer = BusinessTravelSerializer(fuel_consumption_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        scope_3_emissions_by_facilities = calculate_scope_3_emissions_by_facilities()
                        Scope3_Emissions_by_Facilities.objects.all().delete()
                        for i in scope_3_emissions_by_facilities:
                            serializer1 = Scope3EmissionsbyFacilitiesSerializer(data=i)
                            if serializer1.is_valid():
                                serializer1.save()

                        scope_3_emissions_by_activity = calculate_scope_3_emissions_by_activity()
                        Scope3_Emissions_by_Activity.objects.all().delete()
                        for i in scope_3_emissions_by_activity:
                            serializer2 = Scope3EmissionsbyActivitySerializer(data=i)
                            if serializer2.is_valid():
                                serializer2.save()


                        scope_3_emissions_by_ghg_type = calculate_scope_3_emissions_by_ghg_type()
                        Scope3_Emissions_by_GHG_Type.objects.all().delete()
                        for i in scope_3_emissions_by_ghg_type:
                            serializer = Scope3EmissionsbyGHGTypeSerializer(data=i)
                            if serializer.is_valid():
                                serializer.save()

                        
                        scope_3_intensity = calculate_scope_3_intensity()
                        Scope3_Intensity.objects.all().delete()
                        for i in scope_3_intensity:
                            serializer = Scope3IntensitySerializer(data=i)
                            if serializer.is_valid():
                                serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Fuel Consumption in Business Travel"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    business_travel = Business_Travel.objects.get(id=id)
                    business_travel.delete()

                    scope_3_emissions_by_facilities = calculate_scope_3_emissions_by_facilities()
                    Scope3_Emissions_by_Facilities.objects.all().delete()
                    for i in scope_3_emissions_by_facilities:
                        serializer1 = Scope3EmissionsbyFacilitiesSerializer(data=i)
                        if serializer1.is_valid():
                            serializer1.save()

                    
                    scope_3_emissions_by_activity = calculate_scope_3_emissions_by_activity()
                    Scope3_Emissions_by_Activity.objects.all().delete()
                    for i in scope_3_emissions_by_activity:
                        serializer2 = Scope3EmissionsbyActivitySerializer(data=i)
                        if serializer2.is_valid():
                            serializer2.save()


                    scope_3_emissions_by_ghg_type = calculate_scope_3_emissions_by_ghg_type()
                    Scope3_Emissions_by_GHG_Type.objects.all().delete()
                    for i in scope_3_emissions_by_ghg_type:
                        serializer = Scope3EmissionsbyGHGTypeSerializer(data=i)
                        if serializer.is_valid():
                            serializer.save()

                    
                    scope_3_intensity = calculate_scope_3_intensity()
                    Scope3_Intensity.objects.all().delete()
                    for i in scope_3_intensity:
                        serializer = Scope3IntensitySerializer(data=i)
                        if serializer.is_valid():
                            serializer.save()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Fuel Consumption in Business Travel"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Business_Travel.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
class Business_Travel_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            facility = request.query_params.get('facility')

            production = Business_Travel.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = BusinessTravelSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Employee_Commuting_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            employee_commuting = Employee_Commuting.objects.filter(Facility__in=user_location).order_by('-Financial_Year','-id')
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(employee_commuting, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = EmployeeCommutingSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            Unit = request.data.get('Unit')
            Commute_to_Work = request.data.get('Commute_to_Work')
            Type_of_Transport = request.data.get('Type_of_Transport')
            
            Vehicle_Type = request.data.get('Vehicle_Type')
            Fuel_Type = request.data.get('Fuel_Type')
            Company_Bus_Route = request.data.get('Company_Bus_Route')
            

            # Check if an entry already exists for the given facility and financial year
            if Employee_Commuting.objects.filter(Facility=Facility,Fuel_Type=Fuel_Type,Company_Bus_Route=Company_Bus_Route,Vehicle_Type=Vehicle_Type, Commute_to_Work=Commute_to_Work, Type_of_Transport=Type_of_Transport, Financial_Year=Financial_Year, Unit=Unit).count() > 0:
                return Response({'error': 'Entry for this Unit, Commute_to_Work, Vehicle_Type, Fuel_Type, Company_Bus_Route, facility and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)            
            
            if Employee_Commuting.objects.count() == 0:
                id = 1
            else:
                id = Employee_Commuting.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            total_fuel_consumption = request.data.get('Fuel_Consumption_Apr', 0) + request.data.get('Fuel_Consumption_May', 0)  + request.data.get('Fuel_Consumption_Jun', 0) + request.data.get('Fuel_Consumption_Jul', 0) + request.data.get('Fuel_Consumption_Aug', 0) + request.data.get('Fuel_Consumption_Sep', 0) + request.data.get('Fuel_Consumption_Oct', 0) + request.data.get('Fuel_Consumption_Nov', 0) + request.data.get('Fuel_Consumption_Dec', 0) + request.data.get('Fuel_Consumption_Jan', 0) + request.data.get('Fuel_Consumption_Feb', 0) + request.data.get('Fuel_Consumption_Mar', 0)
            request.data["Total_Fuel_Consumption"] = round(total_fuel_consumption, 2)

            serializer = EmployeeCommutingSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                scope_3_emissions_by_facilities = calculate_scope_3_emissions_by_facilities()
                Scope3_Emissions_by_Facilities.objects.all().delete()
                for i in scope_3_emissions_by_facilities:
                    serializer1 = Scope3EmissionsbyFacilitiesSerializer(data=i)
                    if serializer1.is_valid():
                        serializer1.save()


                scope_3_emissions_by_activity = calculate_scope_3_emissions_by_activity()
                Scope3_Emissions_by_Activity.objects.all().delete()
                for i in scope_3_emissions_by_activity:
                    serializer2 = Scope3EmissionsbyActivitySerializer(data=i)
                    if serializer2.is_valid():
                        serializer2.save()

                
                scope_3_emissions_by_ghg_type = calculate_scope_3_emissions_by_ghg_type()
                Scope3_Emissions_by_GHG_Type.objects.all().delete()
                for i in scope_3_emissions_by_ghg_type:
                    serializer = Scope3EmissionsbyGHGTypeSerializer(data=i)
                    if serializer.is_valid():
                        serializer.save()

                
                scope_3_intensity = calculate_scope_3_intensity()
                Scope3_Intensity.objects.all().delete()
                for i in scope_3_intensity:
                    serializer = Scope3IntensitySerializer(data=i)
                    if serializer.is_valid():
                        serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Fuel Consumption in Employee Commuting"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()


                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            # import pdb; pdb.set_trace()
            if id is not None:
                Facility = request.data.get('Facility')
                Financial_Year = request.data.get('Financial_Year')
                Unit = request.data.get('Unit')
                Commute_to_Work = request.data.get('Commute_to_Work')
                Type_of_Transport = request.data.get('Type_of_Transport')
                
                Vehicle_Type = request.data.get('Vehicle_Type')
                Fuel_Type = request.data.get('Fuel_Type')
                Company_Bus_Route = request.data.get('Company_Bus_Route')
                

                # Check if an entry already exists for the given facility and financial year
                if Employee_Commuting.objects.filter(Facility=Facility,Fuel_Type=Fuel_Type,Company_Bus_Route=Company_Bus_Route,Vehicle_Type=Vehicle_Type, Commute_to_Work=Commute_to_Work, Type_of_Transport=Type_of_Transport, Financial_Year=Financial_Year, Unit=Unit).exclude(id=id).count() > 0:
                    return Response({'error': 'Entry for this Unit, Commute_to_Work, Vehicle_Type, Fuel_Type, Company_Bus_Route, facility and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)            
            
                try:
                    total_fuel_consumption = request.data.get('Fuel_Consumption_Apr', 0) + request.data.get('Fuel_Consumption_May', 0)  + request.data.get('Fuel_Consumption_Jun', 0) + request.data.get('Fuel_Consumption_Jul', 0) + request.data.get('Fuel_Consumption_Aug', 0) + request.data.get('Fuel_Consumption_Sep', 0) + request.data.get('Fuel_Consumption_Oct', 0) + request.data.get('Fuel_Consumption_Nov', 0) + request.data.get('Fuel_Consumption_Dec', 0) + request.data.get('Fuel_Consumption_Jan', 0) + request.data.get('Fuel_Consumption_Feb', 0) + request.data.get('Fuel_Consumption_Mar', 0)
                    request.data["Total_Fuel_Consumption"] = round(total_fuel_consumption, 2)

                    fuel_consumption_instance = Employee_Commuting.objects.get(id=id)
                    serializer = EmployeeCommutingSerializer(fuel_consumption_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        scope_3_emissions_by_facilities = calculate_scope_3_emissions_by_facilities()
                        Scope3_Emissions_by_Facilities.objects.all().delete()
                        for i in scope_3_emissions_by_facilities:
                            serializer1 = Scope3EmissionsbyFacilitiesSerializer(data=i)
                            if serializer1.is_valid():
                                serializer1.save()

                        
                        scope_3_emissions_by_activity = calculate_scope_3_emissions_by_activity()
                        Scope3_Emissions_by_Activity.objects.all().delete()
                        for i in scope_3_emissions_by_activity:
                            serializer2 = Scope3EmissionsbyActivitySerializer(data=i)
                            if serializer2.is_valid():
                                serializer2.save()


                        scope_3_emissions_by_ghg_type = calculate_scope_3_emissions_by_ghg_type()
                        Scope3_Emissions_by_GHG_Type.objects.all().delete()
                        for i in scope_3_emissions_by_ghg_type:
                            serializer = Scope3EmissionsbyGHGTypeSerializer(data=i)
                            if serializer.is_valid():
                                serializer.save()

                        
                        scope_3_intensity = calculate_scope_3_intensity()
                        Scope3_Intensity.objects.all().delete()
                        for i in scope_3_intensity:
                            serializer = Scope3IntensitySerializer(data=i)
                            if serializer.is_valid():
                                serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Fuel Consumption in Employee Commuting"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    employee_commuting = Employee_Commuting.objects.get(id=id)
                    employee_commuting.delete()

                    scope_3_emissions_by_facilities = calculate_scope_3_emissions_by_facilities()
                    Scope3_Emissions_by_Facilities.objects.all().delete()
                    for i in scope_3_emissions_by_facilities:
                        serializer1 = Scope3EmissionsbyFacilitiesSerializer(data=i)
                        if serializer1.is_valid():
                            serializer1.save()

                    scope_3_emissions_by_activity = calculate_scope_3_emissions_by_activity()
                    Scope3_Emissions_by_Activity.objects.all().delete()
                    for i in scope_3_emissions_by_activity:
                        serializer2 = Scope3EmissionsbyActivitySerializer(data=i)
                        if serializer2.is_valid():
                            serializer2.save()

                    
                    scope_3_emissions_by_ghg_type = calculate_scope_3_emissions_by_ghg_type()
                    Scope3_Emissions_by_GHG_Type.objects.all().delete()
                    for i in scope_3_emissions_by_ghg_type:
                        serializer = Scope3EmissionsbyGHGTypeSerializer(data=i)
                        if serializer.is_valid():
                            serializer.save()

                    
                    scope_3_intensity = calculate_scope_3_intensity()
                    Scope3_Intensity.objects.all().delete()
                    for i in scope_3_intensity:
                        serializer = Scope3IntensitySerializer(data=i)
                        if serializer.is_valid():
                            serializer.save()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Fuel Consumption in Employee Commuting"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Employee_Commuting.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
class Employee_Commuting_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')

            production = Employee_Commuting.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = EmployeeCommutingSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Elecricity_SourceList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            source_list = SOURCE

            if not source_list:
                return Response({'error': 'Source list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(source_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Source list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Energy_Intensity_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            financial_Year =  request.query_params.get('financial_Year',None)
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            if financial_Year:
                energy_intensity = Energy_Intensity.objects.filter(Financial_Year=financial_Year)
            else:
                energy_intensity = Energy_Intensity.objects.order_by('-Financial_Year')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(energy_intensity, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = EnergyIntensitySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Energy_Intensity_for_Production_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            financial_Year =  request.query_params.get('financial_Year',None)
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            if financial_Year:
                energy_intensity = Energy_Intensity_for_Production.objects.filter(Financial_Year=financial_Year).order_by('-Financial_Year')
            else:
                energy_intensity = Energy_Intensity_for_Production.objects.order_by('-Financial_Year')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(energy_intensity, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = EnergyIntensityforProductionSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Energy_Consumption_Other_Sources_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            energy_consumption = Energy_Consumption_Other_Sources.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(energy_consumption, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = EnergyConsumptionOtherSourcesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            # source = request.data.get('Source')

            # Check if an entry already exists for the given facility and financial year
            if Energy_Consumption_Other_Sources.objects.filter(Facility=Facility, Financial_Year=Financial_Year).count() > 0:
                return Response({'error': 'Entry for this facility and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Energy_Consumption_Other_Sources.objects.count() == 0:
                id = 1
            else:
                id = Energy_Consumption_Other_Sources.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            total_energy_consumption = request.data.get('Energy_Consumption_Apr', 0) + request.data.get('Energy_Consumption_May', 0)  + request.data.get('Energy_Consumption_Jun', 0) + request.data.get('Energy_Consumption_Jul', 0) + request.data.get('Energy_Consumption_Aug', 0) + request.data.get('Energy_Consumption_Sep', 0) + request.data.get('Energy_Consumption_Oct', 0) + request.data.get('Energy_Consumption_Nov', 0) + request.data.get('Energy_Consumption_Dec', 0) + request.data.get('Energy_Consumption_Jan', 0) + request.data.get('Energy_Consumption_Feb', 0) + request.data.get('Energy_Consumption_Mar', 0)
            request.data["Total_Energy_Consumption"] = round(total_energy_consumption, 2)

            serializer = EnergyConsumptionOtherSourcesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Energy Consumption through other sources"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:

                    total_energy_consumption = request.data.get('Energy_Consumption_Apr', 0) + request.data.get('Energy_Consumption_May', 0)  + request.data.get('Energy_Consumption_Jun', 0) + request.data.get('Energy_Consumption_Jul', 0) + request.data.get('Energy_Consumption_Aug', 0) + request.data.get('Energy_Consumption_Sep', 0) + request.data.get('Energy_Consumption_Oct', 0) + request.data.get('Energy_Consumption_Nov', 0) + request.data.get('Energy_Consumption_Dec', 0) + request.data.get('Energy_Consumption_Jan', 0) + request.data.get('Energy_Consumption_Feb', 0) + request.data.get('Energy_Consumption_Mar', 0)
                    request.data["Total_Energy_Consumption"] = round(total_energy_consumption, 2)

                    energy_consumption_instance = Energy_Consumption_Other_Sources.objects.get(id=id)
                    serializer = EnergyConsumptionOtherSourcesSerializer(energy_consumption_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Energy Consumption through other sources"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    energy_consumption = Energy_Consumption_Other_Sources.objects.get(id=id)
                    energy_consumption.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Energy Consumption through other sources"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Energy_Consumption_Other_Sources.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
class Energy_Consumption_Other_Sources_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')

            production = Energy_Consumption_Other_Sources.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = EnergyConsumptionOtherSourcesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GasTypeList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            gas_type_list = PROCESS_EMISSIONS_GAS_TYPE

            if not gas_type_list:
                return Response({'error': 'Gas type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(gas_type_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Gas Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Process_Emissions_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            process_emissions = Process_Emissions.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(process_emissions, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ProcessEmissionsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        # else:
        #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            gas_type = request.data.get('Gas_Type')

            # Check if an entry already exists for the given facility and financial year
            if Process_Emissions.objects.filter(Facility=Facility, Financial_Year=Financial_Year, Gas_Type= gas_type).count() > 0:
                return Response({'error': 'Entry for this facility, financial year  and Gas Type already exists'}, status=status.HTTP_400_BAD_REQUEST)
            if Process_Emissions.objects.count() == 0:
                id = 1
            else:
                id = Process_Emissions.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            total_process_emissions = request.data.get('Process_Emissions_Apr', 0) + request.data.get('Process_Emissions_May', 0)  + request.data.get('Process_Emissions_Jun', 0) + request.data.get('Process_Emissions_Jul', 0) + request.data.get('Process_Emissions_Aug', 0) + request.data.get('Process_Emissions_Sep', 0) + request.data.get('Process_Emissions_Oct', 0) + request.data.get('Process_Emissions_Nov', 0) + request.data.get('Process_Emissions_Dec', 0) + request.data.get('Process_Emissions_Jan', 0) + request.data.get('Process_Emissions_Feb', 0) + request.data.get('Process_Emissions_Mar', 0)
            request.data["Total_Process_Emissions"] = round(total_process_emissions, 2)

            serializer = ProcessEmissionsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Process Emissions"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:

                    total_process_emissions = request.data.get('Process_Emissions_Apr', 0) + request.data.get('Process_Emissions_May', 0)  + request.data.get('Process_Emissions_Jun', 0) + request.data.get('Process_Emissions_Jul', 0) + request.data.get('Process_Emissions_Aug', 0) + request.data.get('Process_Emissions_Sep', 0) + request.data.get('Process_Emissions_Oct', 0) + request.data.get('Process_Emissions_Nov', 0) + request.data.get('Process_Emissions_Dec', 0) + request.data.get('Process_Emissions_Jan', 0) + request.data.get('Process_Emissions_Feb', 0) + request.data.get('Process_Emissions_Mar', 0)
                    request.data["Total_Process_Emissions"] = round(total_process_emissions, 2)

                    process_emissions_instance = Process_Emissions.objects.get(id=id)
                    serializer = ProcessEmissionsSerializer(process_emissions_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Process Emissions"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    process_emissions = Process_Emissions.objects.get(id=id)
                    process_emissions.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Process Emissions"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Process_Emissions.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

class Process_Emissions_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            production = Process_Emissions.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ProcessEmissionsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Refrigerant_Losses_Months_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            months_list = get_months()

            if not months_list:
                return Response({'error': 'Month list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(months_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Month list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Refrigerant_Losses_TypesList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            rl_type_list = REFRIGERANT_LOSSES_TYPE

            if not rl_type_list:
                return Response({'error': 'Type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(rl_type_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Refrigerant_Losses_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            refrigerant_losses = Refrigerant_Losses.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(refrigerant_losses, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = RefrigerantLossesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            type = request.data.get('Type')

            # Check if an entry already exists for the given facility and financial year
            if Refrigerant_Losses.objects.filter(Facility=Facility, Financial_Year=Financial_Year, Type=type).count() > 0:
                return Response({'error': 'Entry for this facility, financial year and type already exists'}, status=status.HTTP_400_BAD_REQUEST)

            
            if Refrigerant_Losses.objects.count() == 0:
                id = 1
            else:
                id = Refrigerant_Losses.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            
            serializer = RefrigerantLossesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Refrigerant Losses"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    refrigerant_losses_instance = Refrigerant_Losses.objects.get(id=id)
                    serializer = RefrigerantLossesSerializer(refrigerant_losses_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Refrigerant Losses"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    refrigerant_losses = Refrigerant_Losses.objects.get(id=id)
                    refrigerant_losses.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Refrigerant Losses"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Refrigerant_Losses.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        

class Refrigerant_Losses_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            facility = request.query_params.get('facility')

            production = Refrigerant_Losses.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = RefrigerantLossesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Employee_Commuting_Way_to_Commute_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            way_to_commute_list = WORK_COMMUTE_TYPE

            if not way_to_commute_list:
                return Response({'error': 'Way to commute list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(way_to_commute_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Way to commute list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Employee_Commuting_Type_of_Transport_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            way_to_commute = request.query_params.get('way_to_commute', None)

            if way_to_commute is None:
                return Response({'error': 'Way to commute parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if way_to_commute == "Public Transport":
                type_of_transport = PUBLIC_TRANSPORT_TYPE_OF_TRANSPORT
            elif way_to_commute == "Personal Vehicle":
                type_of_transport = PERSONAL_VEHICLE_TYPE_OF_TRANSPORT

            return Response(type_of_transport, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Type of transport list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Employee_Commuting_Vehicle_Type_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            type_of_transport = request.query_params.get('type_of_transport', None)

            if type_of_transport is None:
                
                return Response({'error': 'Type of Transport parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if type_of_transport == "By Road":
                
                vehicle_type = BY_ROAD_VEHICLE_TYPE
            
            elif type_of_transport == "2W - 2 Wheeler":
                
                vehicle_type = TWO_WHEELER_VEHICLE_TYPE

            elif type_of_transport == "4W - 4 Wheeler":
                
                vehicle_type = FOUR_WHEELER_VEHICLE_TYPE

            return Response(vehicle_type, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Vehicle Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Employee_Commuting_Vehicle_Fuel_Type_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            type_of_transport = request.query_params.get('type_of_transport', None)

            if type_of_transport is None:
                
                return Response({'error': 'Type of Transport parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if type_of_transport == "2W - 2 Wheeler":
                
                vehicle_fuel_type = TWO_WHEELER_VEHICLE_FUEL_TYPE

            elif type_of_transport == "4W - 4 Wheeler":
                
                vehicle_fuel_type = FOUR_WHEELER_VEHICLE_FUEL_TYPE

            return Response(vehicle_fuel_type, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Vehicle Fuel Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Employee_Commuting_Company_Bus_Route_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            type_of_transport = request.query_params.get('type_of_transport', None)

            if type_of_transport is None:
                
                return Response({'error': 'Type of Transport parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if type_of_transport == "By Company Bus":
                
                company_bus_route = COMPANY_BUS_ROUTE

            return Response(company_bus_route, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Company Bus route list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
######################################## life cycle  #######################################

class Life_Cycle_Perspective_Assessments_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            life_cycle_perspective_assessments = Life_Cycle_Perspective_Assessments.objects.order_by('-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(life_cycle_perspective_assessments, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = LifeCyclePerspectiveAssessmentsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            year = request.data.get('Year_of_Assessment')
            count = Life_Cycle_Perspective_Assessments.objects.filter(Year_of_Assessment=year).count()
            if count > 0:
                return Response({'error': 'Entry for this Year of Assessment already exists'}, status=status.HTTP_400_BAD_REQUEST)

            id = 1 if Life_Cycle_Perspective_Assessments.objects.count() == 0 else Life_Cycle_Perspective_Assessments.objects.aggregate(Max('id'))['id__max'] + 1
            request.data['id'] = id

            year_of_assessment = request.data.get('Year_of_Assessment')
            product_service = request.data.get('Product_Service')

            try:
                document = Products_Services.objects.get(Financial_Year=year_of_assessment)
                print("Retrieved Document:", document)
                percent_turnover = None

                for item in document.Products_Services_and_Turnover:
                    if item.get('Product_Service') == product_service:
                        percent_turnover = item.get('Percent_Turnover')
                        break

                request.data['Percent_of_Turnover_Contributed'] = percent_turnover if percent_turnover is not None else 'NA'
            except Products_Services.DoesNotExist:
                print("No matching Products_Services document found.")
                # request.data['Percent_of_Turnover_Contributed'] = 'NA'

            try:
                product_obj = Products_Services_Details.objects.get(Name_of_Product_Service=product_service)
                request.data['NIC_Code'] = product_obj.NIC_Code
            except Products_Services_Details.DoesNotExist:
                print("No matching Products_Services_Details entry found.")
                # request.data['NIC_Code'] = "NA"

            serializer = LifeCyclePerspectiveAssessmentsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": f"{request.user.firstname} {request.user.lastname}",
                    "Activity": "Added information in table - Life Cycle Perspective/Assessments"
                }
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("Unexpected Error:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    life_cycle_perspective_and_assessments_instance = Life_Cycle_Perspective_Assessments.objects.get(id=id)
                    serializer = LifeCyclePerspectiveAssessmentsSerializer(life_cycle_perspective_and_assessments_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Life Cycle Perspective/Assessments"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    life_cycle_perspective_and_assessments = Life_Cycle_Perspective_Assessments.objects.get(id=id)
                    life_cycle_perspective_and_assessments.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Life Cycle Perspective/Assessments"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Life_Cycle_Perspective_Assessments.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        



class Concerns_and_Action_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            concerns_and_action = Concerns_and_Action.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(concerns_and_action, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ConcernsandActionSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            count = Concerns_and_Action.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error':'Entry for this Financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Concerns_and_Action.objects.count() == 0:
                id = 1
            else:
                id = Concerns_and_Action.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            serializer = ConcernsandActionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Concerns and Action"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    concerns_and_action_instance = Concerns_and_Action.objects.get(id=id)
                    serializer = ConcernsandActionSerializer(concerns_and_action_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Concerns and Action"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    concerns_and_action = Concerns_and_Action.objects.get(id=id)
                    concerns_and_action.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Concerns and Action"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Concerns_and_Action.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Material_Business_Conduct_Issue_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            material_business_conduct_issue = Material_Business_Conduct_Issue.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(material_business_conduct_issue, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = MaterialBusinessConductIssueSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:

            # financial_year = request.data.get('Financial_Year')
            # risk_or_opportunity = request.data.get('Risk_or_Opportunity')
            # if Material_Business_Conduct_Issue.objects.filter(Financial_Year=financial_year,Risk_or_Opportunity=risk_or_opportunity).count() > 0:
            #     return Response({'error': 'Entry for this Risk_or_Opportunity and Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Material_Business_Conduct_Issue.objects.count() == 0:
                id = 1
            else:
                id = Material_Business_Conduct_Issue.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            serializer = MaterialBusinessConductIssueSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Material responsible business conduct issue"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    material_business_conduct_issue_instance = Material_Business_Conduct_Issue.objects.get(id=id)
                    serializer = MaterialBusinessConductIssueSerializer(material_business_conduct_issue_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Material responsible business conduct issue"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    material_business_conduct_issue = Material_Business_Conduct_Issue.objects.get(id=id)
                    material_business_conduct_issue.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Material responsible business conduct issue"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Material_Business_Conduct_Issue.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Sustainable_Sourcing_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            sustainable_sourcing = Sustainable_Sourcing.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(sustainable_sourcing, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = SustainableSourcingSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
            if Sustainable_Sourcing.objects.filter(Financial_Year=year).count() > 0:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Generate unique ID
            last_id = Sustainable_Sourcing.objects.aggregate(Max('id'))['id__max'] or 0
            request.data['id'] = last_id + 1

            # Check and adjust 'Is_Verified' based on 'Total_Material_Input' value
            if request.data.get("Total_Material_Input") == "null":
                request.data["Is_Verified"] = "No"

            # Validate and save Sustainable Sourcing entry
            serializer = SustainableSourcingSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                # Log the activity
                activity_log = {
                    "Name": f"{request.user.firstname} {request.user.lastname}",
                    "Activity": "Added information in table - Sustainable Sourcing"
                }
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    sustainable_sourcing_instance = Sustainable_Sourcing.objects.get(id=id)
                    serializer = SustainableSourcingSerializer(sustainable_sourcing_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Sustainable Sourcing"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    sustainable_sourcing = Sustainable_Sourcing.objects.get(id=id)
                    sustainable_sourcing.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Sustainable Sourcing"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Sustainable_Sourcing.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



##############################
class Input_MaterialList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            material_list = Total_Material_Input

            if not material_list:
                return Response({'error': 'Material list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(material_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Material list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Recycled_or_Reused_Input_Material_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            recycled_or_reused_input_material = Recycled_or_Reused_Input_Material.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(recycled_or_reused_input_material, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = RecycledorReusedInputMaterialSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            input_material = request.data.get('Total_Material_Input')
            count = Recycled_or_Reused_Input_Material.objects.filter(Financial_Year=year,Total_Material_Input=input_material).count()
            if count > 0:
                return Response({'error':'Entry for this Financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Recycled_or_Reused_Input_Material.objects.count() == 0:
                id = 1
            else:
                id = Recycled_or_Reused_Input_Material.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            serializer = RecycledorReusedInputMaterialSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Recycled or reused input material"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    recycled_or_reused_input_material_instance = Recycled_or_Reused_Input_Material.objects.get(id=id)
                    serializer = RecycledorReusedInputMaterialSerializer(recycled_or_reused_input_material_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Recycled or reused input material"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    recycled_or_reused_input_material = Recycled_or_Reused_Input_Material.objects.get(id=id)
                    recycled_or_reused_input_material.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Recycled or reused input material"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Recycled_or_Reused_Input_Material.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class Production_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            production = Production.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ProductionSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            # Extract facility and financial year from the request data
            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')

            # Check if an entry already exists for the given facility and financial year
            if Production.objects.filter(Facility=Facility, Financial_Year=Financial_Year).count() > 0:
                return Response({'error': 'Entry for this facility and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Determine the new ID
            if Production.objects.count() == 0:
                id = 1
            else:
                id = Production.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            # Calculate total production
            total_production = sum(
                request.data.get(month, 0) for month in [
                    'Production_Apr', 'Production_May', 'Production_Jun', 'Production_Jul',
                    'Production_Aug', 'Production_Sep', 'Production_Oct', 'Production_Nov',
                    'Production_Dec', 'Production_Jan', 'Production_Feb', 'Production_Mar'
                ]
            )

            request.data["Total_Production"] = round(total_production)

            # Serialize and save the production data
            serializer = ProductionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                # Calculate and save energy intensity for production
                energy_intensity_for_production = calculate_energy_intensity_for_production()
                Energy_Intensity_for_Production.objects.all().delete()
                for i in energy_intensity_for_production:
                    serializer3 = EnergyIntensityforProductionSerializer(data=i)
                    if serializer3.is_valid():
                        serializer3.save()


                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Production"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    total_production = request.data.get('Production_Apr', 0) + request.data.get('Production_May', 0)  + request.data.get('Production_Jun', 0) + request.data.get('Production_Jul', 0) + request.data.get('Production_Aug', 0) + request.data.get('Production_Sep', 0) + request.data.get('Production_Oct', 0) + request.data.get('Production_Nov', 0) + request.data.get('Production_Dec', 0) + request.data.get('Production_Jan', 0) + request.data.get('Production_Feb', 0) + request.data.get('Production_Mar', 0)
                    request.data["Total_Production"] = round(total_production, 2)


                    production_instance = Production.objects.get(id=id)
                    serializer = ProductionSerializer(production_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        energy_intensity_for_production = calculate_energy_intensity_for_production()
                        Energy_Intensity_for_Production.objects.all().delete()
                        for i in energy_intensity_for_production:
                            serializer3 = EnergyIntensityforProductionSerializer(data=i)
                            if serializer3.is_valid():
                                serializer3.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Production"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    production = Production.objects.get(id=id)
                    production.delete()

                    energy_intensity_for_production = calculate_energy_intensity_for_production()
                    Energy_Intensity_for_Production.objects.all().delete()
                    for i in energy_intensity_for_production:
                        serializer3 = EnergyIntensityforProductionSerializer(data=i)
                        if serializer3.is_valid():
                            serializer3.save()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Production"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Production.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        


class End_of_Life_of_Product_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            end_of_life_of_product = End_of_Life_of_Product.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(end_of_life_of_product, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = EndofLifeofProductSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            count = End_of_Life_of_Product.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error':'Entry for this Financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if End_of_Life_of_Product.objects.count() == 0:
                id = 1
            else:
                id = End_of_Life_of_Product.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            serializer = EndofLifeofProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - End of Life of Product"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    end_of_life_of_product_instance = End_of_Life_of_Product.objects.get(id=id)
                    serializer = EndofLifeofProductSerializer(end_of_life_of_product_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - End of Life of Product"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    end_of_life_of_product = End_of_Life_of_Product.objects.get(id=id)
                    end_of_life_of_product.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - End of Life of Product"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except End_of_Life_of_Product.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        


class Reclaimed_Products_and_Packaging_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            reclaimed_products_and_packaging = Reclaimed_Products_and_Packaging.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(reclaimed_products_and_packaging, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ReclaimedProductsandPackagingSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            count = Reclaimed_Products_and_Packaging.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error':'Entry for this Financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)


            if Reclaimed_Products_and_Packaging.objects.count() == 0:
                id = 1
            else:
                id = Reclaimed_Products_and_Packaging.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            serializer = ReclaimedProductsandPackagingSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Reclaimed Products and packaging"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    reclaimed_products_and_packaging_instance = Reclaimed_Products_and_Packaging.objects.get(id=id)
                    serializer = ReclaimedProductsandPackagingSerializer(reclaimed_products_and_packaging_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Reclaimed Products and packaging"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    reclaimed_product_and_packaging = Reclaimed_Products_and_Packaging.objects.get(id=id)
                    reclaimed_product_and_packaging.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Reclaimed Products and packaging"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Reclaimed_Products_and_Packaging.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        


class MaterialList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            material_list = MATERIAL

            if not material_list:
                return Response({'error': 'Material list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(material_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Material list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class ReclaimTypeList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            reclaim_type_list = RECLAIM_TYPE

            if not reclaim_type_list:
                return Response({'error': 'Reclaim Type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(reclaim_type_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Reclaim Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Reclaim_Process_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            reclaim_process = Reclaim_Process.objects.all().order_by('-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(reclaim_process, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ReclaimProcessSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            material = request.data.get('Material')
            reclaim_Type = request.data.get('Reclaim_Type')
            is_exist = Reclaim_Process.objects.filter(Material=material, Reclaim_Type=reclaim_Type)

            if is_exist:
                return Response({'error': 'Entry for this Material, Reclaim Type already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Reclaim_Process.objects.count() == 0:
                id = 1
            else:
                id = Reclaim_Process.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            serializer = ReclaimProcessSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Reclaim Process"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:

                    reclaim_process_instance = Reclaim_Process.objects.get(id=id)
                    serializer = ReclaimProcessSerializer(reclaim_process_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Reclaim Process"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    reclaim_process = Reclaim_Process.objects.get(id=id)
                    reclaim_process.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Reclaim Process"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Reclaim_Process.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        



class Production_Filter(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')

            production = Production.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ProductionSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# ########################################   Water and Air  #####################################################

# Create your views here.
class Water_AgencyTypeList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            agency_type_list = WATER_AGENCY_TYPE

            if not agency_type_list:
                return Response({'error': 'Agency Type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(agency_type_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Agency Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Assessment_By_External_Agency_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead" :
            assessments = Water_Assessment_By_External_Agency.objects.all().order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(assessments, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = WaterAssessmentbyExternalAgencySerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #         return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            financial_year = request.data.get('Financial_Year')
            agency_type = request.data.get('Agency_Type')
            
            # Check if an entry for this financial year already exists
            if Water_Assessment_By_External_Agency.objects.filter(Financial_Year=financial_year,Agency_Type=agency_type).count() > 0:
                return Response({'error': 'Entry for this Financial Year and Agency_Type already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Water_Assessment_By_External_Agency.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Water_Assessment_By_External_Agency.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = WaterAssessmentbyExternalAgencySerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Assessment_By_External_Agency"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            

            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")
            assessment = Water_Assessment_By_External_Agency.objects.get(id=id)
            serializer = WaterAssessmentbyExternalAgencySerializer(assessment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table -  Assessment_By_External_Agency"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            assessment = Water_Assessment_By_External_Agency.objects.get(id=id)
            assessment.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Assessment_By_External_Agency"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Water_Intensity_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            if  user_location:
                water_intensity = Water_Intensity.objects.filter(Facility__in=user_location).order_by('-Financial_Year')
            else:
                water_intensity = Water_Intensity.objects.all().order_by('-Financial_Year')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(water_intensity, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = WaterIntensitySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'},status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            financial_year = request.data.get('Financial_Year')
            
            # Check if an entry for this financial year already exists
            if Water_Intensity.objects.filter(Financial_Year=financial_year).count() > 0:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Water_Intensity.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Water_Intensity.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = WaterIntensitySerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Water_Intensity"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#         except Exception as e:
#             logger.error(f"Exception: {e}")
#             return Response({'message': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")
            water_intensity = Water_Intensity.objects.get(id=id)
            serializer = WaterIntensitySerializer(water_intensity, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Water_Intensity"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            water_intensity = Water_Intensity.objects.get(id=id)
            water_intensity.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Water_Intensity"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class Water_Stress_Areas_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:  
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":
                
            if user_location:
                waterstress =  Water_Stress_Areas.objects.filter(Facility__in=user_location).order_by('-id')
            else:
                waterstress =  Water_Stress_Areas.objects.all().order_by('-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(waterstress, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = WaterStressAreasSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'},status=status.HTTP_403_FORBIDDEN)

            
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")
            facility = request.data.get('Facility')
            state = request.data.get('State')

            is_exist = Water_Stress_Areas.objects.filter(Facility=facility, State=state)

            if is_exist:
                return Response({'error': 'Entry for this facility and state  already exists'}, status=status.HTTP_400_BAD_REQUEST)


            # Get the count of existing objects
            if Water_Stress_Areas.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Water_Stress_Areas.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = WaterStressAreasSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Water_Stress_Areas"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                return Response({'success': 'Data added successfully.'})
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")
            waterstress = Water_Stress_Areas.objects.get(id=id)
            serializer = WaterStressAreasSerializer(waterstress, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Water_Stress_Areas"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            waterstress = Water_Stress_Areas.objects.get(id=id)
            waterstress.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Water_Stress_Areas"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    



class SourceList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            source_list = WATER_WITHDRAWAL_BY_SOURCE

            if not source_list:
                return Response({'error': 'Source list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(source_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Source list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Water_Withdrawal_By_Source_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
            try:
                user_role = request.user.role
                user_location = request.user.location
                # if user_role == "Plant Operations" or user_role == "ESG Lead":

                # facility = request.query_params.get('Facility', None)
                # filter_kwargs = {}
                # if facility:
                #     filter_kwargs['Facility'] = facility
                if user_location:
                    water_withdrawal = Water_withdrawal_By_Source.objects.filter(Facility__in=user_location).order_by('-id')
                else:
                    water_withdrawal = Water_withdrawal_By_Source.objects.all().order_by('-id')
                    
                page_size = request.query_params.get('page_size', 5)
                paginator = Paginator(water_withdrawal, page_size)
                page_number = request.query_params.get('page', 1)

                try:
                    paginated_queryset = paginator.page(page_number)
                except EmptyPage:
                    return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
                except PageNotAnInteger:
                    return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = WaterWithdrawalBySourceSerializer(paginated_queryset, many=True)
                response_data = {
                    'data': serializer.data,
                    'page': int(page_number),
                    'total_pages': paginator.num_pages,
                    'count': paginator.count,
                }
                return Response(response_data, status=status.HTTP_200_OK)
                # else:
                #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

            except ObjectDoesNotExist:
                logger.error("Object not found")
                return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
            except APIException as e:
                logger.error(f"APIException: {e}")
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Exception: {e}")
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self,request):
        try:
            logger.info(f"POST data: {request.data}")

            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            source = request.data.get("Source")
            # Check if an entry already exists for the given facility and financial year
            if Water_withdrawal_By_Source.objects.filter(Facility=Facility, Financial_Year=Financial_Year,Source=source).count() > 0:
                return Response({'error': 'Entry for this facility, source and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
            # Get the count of existing objects
            if Water_withdrawal_By_Source.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Water_withdrawal_By_Source.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            Total_Water_withdrawal = request.data.get('Water_withdrawal_Apr', 0) + request.data.get('Water_withdrawal_May', 0)  + request.data.get('Water_withdrawal_Jun', 0) + request.data.get('Water_withdrawal_Jul', 0) + request.data.get('Water_withdrawal_Aug', 0) + request.data.get('Water_withdrawal_Sep', 0) + request.data.get('Water_withdrawal_Oct', 0) + request.data.get('Water_withdrawal_Nov', 0) + request.data.get('Water_withdrawal_Dec', 0) + request.data.get('Water_withdrawal_Jan', 0) + request.data.get('Water_withdrawal_Feb', 0) + request.data.get('Water_withdrawal_Mar', 0)
            request.data["Total_Water_withdrawal"] = round(Total_Water_withdrawal ,2)


            # Serialize the data
            serializer =  WaterWithdrawalBySourceSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Water_withdrawal_By_Source"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data added successfully.'})
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def put(self, request, id):
        try:
            Total_Water_withdrawal = request.data.get('Water_withdrawal_Apr', 0) + request.data.get('Water_withdrawal_May', 0)  + request.data.get('Water_withdrawal_Jun', 0) + request.data.get('Water_withdrawal_Jul', 0) + request.data.get('Water_withdrawal_Aug', 0) + request.data.get('Water_withdrawal_Sep', 0) + request.data.get('Water_withdrawal_Oct', 0) + request.data.get('Water_withdrawal_Nov', 0) + request.data.get('Water_withdrawal_Dec', 0) + request.data.get('Water_withdrawal_Jan', 0) + request.data.get('Water_withdrawal_Feb', 0) + request.data.get('Water_withdrawal_Mar', 0)
            request.data["Total_Water_withdrawal"] = round(Total_Water_withdrawal ,2)

            logger.info(f"PUT data: {request.data}")
            water_withdrawal = Water_withdrawal_By_Source.objects.get(id=id)
            serializer = WaterWithdrawalBySourceSerializer(water_withdrawal, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Water_withdrawal_By_Source"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            water_withdrawal = Water_withdrawal_By_Source.objects.get(id=id)
            water_withdrawal.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Water_withdrawal_By_Source"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        





class Water_Consumption_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:    
            user_role = request.user.role
            user_location = request.user.location
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            # facility = request.query_params.get('Facility', None)
            # filter_kwargs = {}
            # if facility:
            #         filter_kwargs['Facility'] = facility
            if user_location:
                water_consumption = Water_Consumption.objects.filter(Facility__in=user_location).order_by('-id')
            else:
                water_consumption = Water_Consumption.objects.all().order_by('-id')
                

            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(water_consumption, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer =  WaterConsumptionSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self,request):
        try:
            logger.info(f"POST data: {request.data}")

            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')

            # Check if an entry already exists for the given facility and financial year
            if Water_Consumption.objects.filter(Facility=Facility, Financial_Year=Financial_Year).count() > 0:
                return Response({'error': 'Entry for this facility and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Water_Consumption.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Water_Consumption.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            Total_Consumption = request.data.get('Water_Consumption_Apr', 0) + request.data.get('Water_Consumption_May', 0)  + request.data.get('Water_Consumption_Jun', 0) + request.data.get('Water_Consumption_Jul', 0) + request.data.get('Water_Consumption_Aug', 0) + request.data.get('Water_Consumption_Sep', 0) + request.data.get('Water_Consumption_Oct', 0) + request.data.get('Water_Consumption_Nov', 0) + request.data.get('Water_Consumption_Dec', 0) + request.data.get('Water_Consumption_Jan', 0) + request.data.get('Water_Consumption_Feb', 0) + request.data.get('Water_Consumption_Mar', 0)
            request.data["Total_Consumption"] = round(Total_Consumption ,2)

            # Serialize the data
            serializer =  WaterConsumptionSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Water_Consumption"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                water_intensity = calculate_water_intensity()
                Water_Intensity.objects.all().delete()
                for i in water_intensity:
                    serializer1 = WaterIntensitySerializer(data=i)
                    if serializer1.is_valid():
                        serializer1.save()

                return Response({'success': 'Data added successfully.'})
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def put(self, request, id):
        try:

            Total_Consumption = request.data.get('Water_Consumption_Apr', 0) + request.data.get('Water_Consumption_May', 0)  + request.data.get('Water_Consumption_Jun', 0) + request.data.get('Water_Consumption_Jul', 0) + request.data.get('Water_Consumption_Aug', 0) + request.data.get('Water_Consumption_Sep', 0) + request.data.get('Water_Consumption_Oct', 0) + request.data.get('Water_Consumption_Nov', 0) + request.data.get('Water_Consumption_Dec', 0) + request.data.get('Water_Consumption_Jan', 0) + request.data.get('Water_Consumption_Feb', 0) + request.data.get('Water_Consumption_Mar', 0)
            request.data["Total_Consumption"] = round(Total_Consumption ,2)


            logger.info(f"PUT data: {request.data}")
            water_consumption = Water_Consumption.objects.get(id=id)
            serializer = WaterConsumptionSerializer(water_consumption, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Water_Consumption"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                water_intensity = calculate_water_intensity()
                Water_Intensity.objects.all().delete()
                for i in water_intensity:
                    serializer1 = WaterIntensitySerializer(data=i)
                    if serializer1.is_valid():
                        serializer1.save()
                        


                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            water_consumption = Water_Consumption.objects.get(id=id)
            water_consumption.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Water_Consumption"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()

            water_intensity = calculate_water_intensity()
            Water_Intensity.objects.all().delete()
            for i in water_intensity:
                serializer1 = WaterIntensitySerializer(data=i)
                if serializer1.is_valid():
                    serializer1.save()

            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Water_Consumption_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
   
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            facility = request.query_params.get('Facility')
            production = Water_Consumption.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = WaterConsumptionSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Water_Withdrawal_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            Facility = request.query_params.get('Facility')
            production = Water_withdrawal_By_Source.objects.filter(Facility=Facility).order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)
            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = WaterWithdrawalBySourceSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DestinationList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            destination_list = WATER_DISCHARGE_TO_DESTINATION_WITHOUT_TREATMENT

            if not destination_list:
                return Response({'error': 'Destination list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(destination_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Destination list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Water_Discharge_To_Destination_Without_Treatment_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            Facility = request.query_params.get('Facility')
            production = Water_Discharge_To_Destination_Without_Treatment.objects.filter(Facility=Facility).order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)
            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Water_Discharge_To_Destination_Without_TreatmentSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Water_Discharge_To_Destination_With_Treatment_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            Facility = request.query_params.get('Facility')
            production = Water_Discharge_To_Destination_With_Treatment.objects.filter(Facility=Facility).order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)
            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Water_Discharge_To_Destination_With_TreatmentSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Air_Emissions_Other_Than_GHG_Emissions_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            Facility = request.query_params.get('Facility')
            production = Air_Emissions_Other_Than_GHG_Emissions.objects.filter(Facility=Facility).order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)
            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Air_Emissions_Other_Than_GHG_EmissionsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








class Water_Discharge_To_Destination_Without_Treatment_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            user_role = request.user.role
            user_location = request.user.location
            
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            facility = request.query_params.get('Facility', None)
            
            # filter_kwargs = {}
            # if facility:
            #     filter_kwargs['Facility'] = facility
            if user_location:
                water_Discharge_Without_Treatment = Water_Discharge_To_Destination_Without_Treatment.objects.filter(Facility__in=user_location).order_by('-id')
            else :
                water_Discharge_Without_Treatment = Water_Discharge_To_Destination_Without_Treatment.objects.all().order_by('-id')
                
                
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(water_Discharge_Without_Treatment, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)  
            serializer = Water_Discharge_To_Destination_Without_TreatmentSerializer(paginated_queryset, many=True)
            response_data = {
            'data': serializer.data,
            'page': int(page_number),
            'total_pages': paginator.num_pages,
            'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self,request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            Destination = request.data.get('Destination')

            # Check if an entry already exists for the given facility and financial year
            if Water_Discharge_To_Destination_Without_Treatment.objects.filter(Facility=Facility, Financial_Year=Financial_Year,Destination=Destination).count() > 0:
                return Response({'error': 'Entry for this facility, Destination and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Water_Discharge_To_Destination_Without_Treatment.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Water_Discharge_To_Destination_Without_Treatment.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id


            Total_Water_Discharge_Without_Treatment = request.data.get('Water_Discharge_Without_Treatment_Apr', 0) + request.data.get('Water_Discharge_Without_Treatment_May', 0)  + request.data.get('Water_Discharge_Without_Treatment_Jun', 0) + request.data.get('Water_Discharge_Without_Treatment_Jul', 0) + request.data.get('Water_Discharge_Without_Treatment_Aug', 0) + request.data.get('Water_Discharge_Without_Treatment_Sep', 0) + request.data.get('Water_Discharge_Without_Treatment_Oct', 0) + request.data.get('Water_Discharge_Without_Treatment_Nov', 0) + request.data.get('Water_Discharge_Without_Treatment_Dec', 0) + request.data.get('Water_Discharge_Without_Treatment_Jan', 0) + request.data.get('Water_Discharge_Without_Treatment_Feb', 0) + request.data.get('Water_Discharge_Without_Treatment_Mar', 0)
            request.data["Total_Water_Discharge_Without_Treatment"] = round(Total_Water_Discharge_Without_Treatment ,2)




            # Serialize the data
            serializer =  Water_Discharge_To_Destination_Without_TreatmentSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Water_Discharge_To_Destination_Without_Treatment"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data added successfully.'})
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def put(self, request, id):
        try:
            Total_Water_Discharge_Without_Treatment = request.data.get('Water_Discharge_Without_Treatment_Apr', 0) + request.data.get('Water_Discharge_Without_Treatment_May', 0)  + request.data.get('Water_Discharge_Without_Treatment_Jun', 0) + request.data.get('Water_Discharge_Without_Treatment_Jul', 0) + request.data.get('Water_Discharge_Without_Treatment_Aug', 0) + request.data.get('Water_Discharge_Without_Treatment_Sep', 0) + request.data.get('Water_Discharge_Without_Treatment_Oct', 0) + request.data.get('Water_Discharge_Without_Treatment_Nov', 0) + request.data.get('Water_Discharge_Without_Treatment_Dec', 0) + request.data.get('Water_Discharge_Without_Treatment_Jan', 0) + request.data.get('Water_Discharge_Without_Treatment_Feb', 0) + request.data.get('Water_Discharge_Without_Treatment_Mar', 0)
            request.data["Total_Water_Discharge_Without_Treatment"] = round(Total_Water_Discharge_Without_Treatment ,2)



            logger.info(f"PUT data: {request.data}")
            water_Discharge_Without_Treatment = Water_Discharge_To_Destination_Without_Treatment.objects.get(id=id)
            serializer = Water_Discharge_To_Destination_Without_TreatmentSerializer(water_Discharge_Without_Treatment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Water_Discharge_To_Destination_Without_Treatment"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            water_Discharge_Without_Treatment = Water_Discharge_To_Destination_Without_Treatment.objects.get(id=id)
            water_Discharge_Without_Treatment.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Water_Discharge_To_Destination_Without_Treatment"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        

class DestinationListWithTreatment_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            destination_list = WATER_DISCHARGE_TO_DESTINATION_WITH_TREATMENT

            if not destination_list:
                return Response({'error': 'Destination list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(destination_list, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except NameError:
            return Response({'error': 'Destination list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class Water_Discharge_To_Destination_With_Treatment_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            user_role = request.user.role
            user_location = request.user.location
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            facility = request.query_params.get('Facility', None)
            
            # filter_kwargs = {}
            # if facility:
            #     filter_kwargs['Facility'] = facility
            if user_location:
                water_Discharge_With_Treatment = Water_Discharge_To_Destination_With_Treatment.objects.filter(Facility__in=user_location).order_by('-id')
            else:
                water_Discharge_With_Treatment = Water_Discharge_To_Destination_With_Treatment.objects.all().order_by('-id')
                
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(water_Discharge_With_Treatment, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)                
            serializer = Water_Discharge_To_Destination_With_TreatmentSerializer(paginated_queryset, many=True)
            response_data = {
            'data': serializer.data,
            'page': int(page_number),
            'total_pages': paginator.num_pages,
            'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self,request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            Destination = request.data.get('Destination')

            # Check if an entry already exists for the given facility and financial year
            if Water_Discharge_To_Destination_With_Treatment.objects.filter(Facility=Facility, Financial_Year=Financial_Year,Destination=Destination).count() > 0:
                return Response({'error': 'Entry for this facility, Destination and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Water_Discharge_To_Destination_With_Treatment.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Water_Discharge_To_Destination_With_Treatment.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id


            Total_Water_Discharge_With_Treatment = request.data.get('Water_Discharge_With_Treatment_Apr', 0) + request.data.get('Water_Discharge_With_Treatment_May', 0)  + request.data.get('Water_Discharge_With_Treatment_Jun', 0) + request.data.get('Water_Discharge_With_Treatment_Jul', 0) + request.data.get('Water_Discharge_With_Treatment_Aug', 0) + request.data.get('Water_Discharge_With_Treatment_Sep', 0) + request.data.get('Water_Discharge_With_Treatment_Oct', 0) + request.data.get('Water_Discharge_With_Treatment_Nov', 0) + request.data.get('Water_Discharge_With_Treatment_Dec', 0) + request.data.get('Water_Discharge_With_Treatment_Jan', 0) + request.data.get('Water_Discharge_With_Treatment_Feb', 0) + request.data.get('Water_Discharge_With_Treatment_Mar', 0)
            request.data["Total_Water_Discharge_With_Treatment"] = round(Total_Water_Discharge_With_Treatment ,2)

            # Serialize the data
            serializer =  Water_Discharge_To_Destination_With_TreatmentSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Water_Discharge_To_Destination_With_Treatment"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'})
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def put(self, request, id):
        try:
            Total_Water_Discharge_With_Treatment = request.data.get('Water_Discharge_With_Treatment_Apr', 0) + request.data.get('Water_Discharge_With_Treatment_May', 0)  + request.data.get('Water_Discharge_With_Treatment_Jun', 0) + request.data.get('Water_Discharge_With_Treatment_Jul', 0) + request.data.get('Water_Discharge_With_Treatment_Aug', 0) + request.data.get('Water_Discharge_With_Treatment_Sep', 0) + request.data.get('Water_Discharge_With_Treatment_Oct', 0) + request.data.get('Water_Discharge_With_Treatment_Nov', 0) + request.data.get('Water_Discharge_With_Treatment_Dec', 0) + request.data.get('Water_Discharge_With_Treatment_Jan', 0) + request.data.get('Water_Discharge_With_Treatment_Feb', 0) + request.data.get('Water_Discharge_With_Treatment_Mar', 0)
            request.data["Total_Water_Discharge_With_Treatment"] = round(Total_Water_Discharge_With_Treatment ,2)


            logger.info(f"PUT data: {request.data}")
            water_Discharge_With_Treatment = Water_Discharge_To_Destination_With_Treatment.objects.get(id=id)
            serializer = Water_Discharge_To_Destination_With_TreatmentSerializer(water_Discharge_With_Treatment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Water_Discharge_To_Destination_With_Treatment"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            water_Discharge_With_Treatment = Water_Discharge_To_Destination_With_Treatment.objects.get(id=id)
            water_Discharge_With_Treatment.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Water_Discharge_To_Destination_With_Treatment"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
                

class ParameterList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            parameter_list = AIR_EMISSIONS_PARAMETER

            if not parameter_list:
                return Response({'error': 'Parameter list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(parameter_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Parameter list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class UnitList_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Replace AIR_EMISSIONS_UNIT with your actual unit list source
            unit_list = AIR_EMISSIONS_UNIT
            parameter_list = AIR_EMISSIONS_PARAMETER
            if not unit_list:
                return Response({'error': 'Unit list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            # Get the 'parameter_list' query parameter
            parameter_params = request.query_params.get('parameter')
            for ind,parameter in enumerate(parameter_list):
                if parameter == parameter_params:
                    unit_data = [unit_list[ind]]
                    return Response(unit_data, status=status.HTTP_200_OK)
            if parameter_list:
                # Convert the comma-separated parameter list into a dictionary
                try:
                    parameters = dict(param.split('=') for param in parameter_list.split(','))
                except ValueError:
                    return Response({'error': 'Invalid parameter list format'}, status=status.HTTP_400_BAD_REQUEST)

                # Filter the unit list based on the parameters
                filtered_units = [unit for unit in unit_list if all(str(unit.get(key)) == value for key, value in parameters.items())]

            if not filtered_units:
                    return Response({'error': 'No units match the given parameters'}, status=status.HTTP_404_NOT_FOUND)

            return Response(filtered_units, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Unit list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class Air_Emissions_Other_Than_GHG_Emissions_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":

                # facility = request.query_params.get('Facility', None)
                # filter_kwargs = {}
                # if facility:
                #     filter_kwargs['Facility'] = facility
            if user_location:
                Air_emissions = Air_Emissions_Other_Than_GHG_Emissions.objects.filter(Facility__in=user_location).order_by('-id')
            else:
                Air_emissions = Air_Emissions_Other_Than_GHG_Emissions.objects.all().order_by('-id')
                
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(Air_emissions, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)                
            serializer = Air_Emissions_Other_Than_GHG_EmissionsSerializer(paginated_queryset, many=True)
            response_data = {
            'data': serializer.data,
            'page': int(page_number),
            'total_pages': paginator.num_pages,
            'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)              
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self,request):
        try:
            logger.info(f"POST data: {request.data}")

            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            parameter = request.data.get("Parameter")

            # Check if an entry already exists for the given facility and financial year
            if Air_Emissions_Other_Than_GHG_Emissions.objects.filter(Facility=Facility, Financial_Year=Financial_Year,Parameter=parameter).count() > 0:
                return Response({'error': 'Entry for this facility, parameter and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Air_Emissions_Other_Than_GHG_Emissions.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Air_Emissions_Other_Than_GHG_Emissions.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id


            Total_Air_Emission = request.data.get('Air_Emissions_Apr', 0) + request.data.get('Air_Emissions_May', 0)  + request.data.get('Air_Emissions_Jun', 0) + request.data.get('Air_Emissions_Jul', 0) + request.data.get('Air_Emissions_Aug', 0) + request.data.get('Air_Emissions_Sep', 0) + request.data.get('Air_Emissions_Oct', 0) + request.data.get('Air_Emissions_Nov', 0) + request.data.get('Air_Emissions_Dec', 0) + request.data.get('Air_Emissions_Jan', 0) + request.data.get('Air_Emissions_Feb', 0) + request.data.get('Air_Emissions_Mar', 0)
            request.data["Total_Air_Emission"] = round(Total_Air_Emission ,2)

            # Serialize the data
            serializer =  Air_Emissions_Other_Than_GHG_EmissionsSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Air_Emissions_Other_Than_GHG_Emissions"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data added successfully.'})
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def put(self, request, id):
        try:
            Total_Air_Emission = request.data.get('Air_Emissions_Apr', 0) + request.data.get('Air_Emissions_May', 0)  + request.data.get('Air_Emissions_Jun', 0) + request.data.get('Air_Emissions_Jul', 0) + request.data.get('Air_Emissions_Aug', 0) + request.data.get('Air_Emissions_Sep', 0) + request.data.get('Air_Emissions_Oct', 0) + request.data.get('Air_Emissions_Nov', 0) + request.data.get('Air_Emissions_Dec', 0) + request.data.get('Air_Emissions_Jan', 0) + request.data.get('Air_Emissions_Feb', 0) + request.data.get('Air_Emissions_Mar', 0)
            request.data["Total_Air_Emission"] = round(Total_Air_Emission ,2)

            logger.info(f"PUT data: {request.data}")
            Air_emissions = Air_Emissions_Other_Than_GHG_Emissions.objects.get(id=id)
            serializer = Air_Emissions_Other_Than_GHG_EmissionsSerializer(Air_emissions, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Air_Emissions_Other_Than_GHG_Emissions"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            Air_emissions = Air_Emissions_Other_Than_GHG_Emissions.objects.get(id=id)
            Air_emissions.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Air_Emissions_Other_Than_GHG_Emissions"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
                
############################################    Waste     ##########################################################

# Create your views here.
class Waste_AgencyTypeList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            agency_type_list = WATER_AGENCY_TYPE

            if not agency_type_list:
                return Response({'error': 'Agency Type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(agency_type_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Agency Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Waste_Assessment_By_External_Agency_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            assessments = Waste_Assessment_By_External_Agency.objects.all().order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(assessments, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = WasteAssessmentbyExternalAgencySerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            financial_year = request.data.get('Financial_Year')
            agency_type = request.data.get('Agency_Type')
            
            # Check if an entry for this financial year already exists
            if Waste_Assessment_By_External_Agency.objects.filter(Financial_Year=financial_year,Agency_Type=agency_type).count() > 0:
                return Response({'error': 'Entry for this Financial Year  and Agency_Type already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Waste_Assessment_By_External_Agency.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Waste_Assessment_By_External_Agency.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = WasteAssessmentbyExternalAgencySerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Assessment_By_External_Agency"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")
            assessment = Waste_Assessment_By_External_Agency.objects.get(id=id)
            serializer = WasteAssessmentbyExternalAgencySerializer(assessment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Assessment_By_External_Agency"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            assessment = Waste_Assessment_By_External_Agency.objects.get(id=id)
            assessment.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Assessment_By_External_Agency"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

















class GeneratedTypeList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            generated_type_list = WASTE_GENERATED_TYPE

            if not generated_type_list:
                return Response({'error': 'Generated Type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(generated_type_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Generated Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# class Water_Consumption_Filter_View(APIView):
#     permission_classes = [IsAuthenticated]
   
#     def get(self,request):
#         try:
#             user_role = request.user.role
#             # if user_role == "Plant Operations" or user_role == "ESG Lead":

#             facility = request.query_params.get('Facility')
#             production = Water_Consumption.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

#             page_size = request.query_params.get('page_size', 5)
#             paginator = Paginator(production, page_size)
#             page_number = request.query_params.get('page', 1)

#             try:
#                 paginated_queryset = paginator.page(page_number)
#             except EmptyPage:
#                 return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
#             except PageNotAnInteger:
#                 return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
#             serializer = WaterConsumptionSerializer(paginated_queryset, many=True)
#             response_data = {
#                 'data': serializer.data,
#                 'page': int(page_number),
#                 'total_pages': paginator.num_pages,
#                 'count': paginator.count,
#             }
#             return Response(response_data, status=status.HTTP_200_OK)
            
#             # else:
#             #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Waste_Generated_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            Facility = request.query_params.get('Facility')
            production = Waste_Generated.objects.filter(Facility=Facility).order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)
            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = WasteGeneratedSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Waste_Generated_View(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, id=None):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            if id:
                waste_generated = Waste_Generated.objects.filter(Facility__in=user_location)
                serializer = WasteGeneratedSerializer(waste_generated)
                return Response(serializer.data)
            else:
                facility = request.query_params.get('Facility', None)
                
                filter_kwargs = {}
                if facility:
                    filter_kwargs['Facility'] = facility
                    waste_generated = Waste_Generated.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')
                else:
                    waste_generated = Waste_Generated.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
                page_size = request.query_params.get('page_size', 65)
                paginator = Paginator(waste_generated, page_size)
                page_number = request.query_params.get('page', 1)

                try:
                    paginated_queryset = paginator.page(page_number)
                except EmptyPage:
                    return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
                except PageNotAnInteger:
                    return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = WasteGeneratedSerializer(paginated_queryset, many=True)
                response_data = {
                    'data': serializer.data,
                    'page': int(page_number),
                    'total_pages': paginator.num_pages,
                    'count': paginator.count,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self,request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            type = request.data.get("Type")
            # Check if an entry already exists for the given facility and financial year
            if Waste_Generated.objects.filter(Facility=Facility, Financial_Year=Financial_Year,Type=type):
                return Response({'error': 'Entry for this facility, type and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the count of existing objects
            if Waste_Generated.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Waste_Generated.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id
            
            Waste_Generated_Total = request.data.get('Waste_Generated_Apr', 0) + request.data.get('Waste_Generated_May', 0)  + request.data.get('Waste_Generated_Jun', 0) + request.data.get('Waste_Generated_Jul', 0) + request.data.get('Waste_Generated_Aug', 0) + request.data.get('Waste_Generated_Sep', 0) + request.data.get('Waste_Generated_Oct', 0) + request.data.get('Waste_Generated_Nov', 0) + request.data.get('Waste_Generated_Dec', 0) + request.data.get('Waste_Generated_Jan', 0) + request.data.get('Waste_Generated_Feb', 0) + request.data.get('Waste_Generated_Mar', 0)
            request.data["Waste_Generated_Total"] = round(Waste_Generated_Total ,2)

            # Serialize the data
            serializer =  WasteGeneratedSerializer(data=request.data)
            if serializer.is_valid():

                
                serializer.save()

                waste_intensity = calculate_waste_intensity()
                Waste_Intensity.objects.all().delete()
                for i in waste_intensity:
                    serializer6=WasteIntensitySerializer(data=i)
                    if serializer6.is_valid(): 
                        serializer6.save() 




                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Waste_Generated"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data added successfully.'})
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, id):
        try:
            Waste_Generated_Total = request.data.get('Waste_Generated_Apr', 0) + request.data.get('Waste_Generated_May', 0)  + request.data.get('Waste_Generated_Jun', 0) + request.data.get('Waste_Generated_Jul', 0) + request.data.get('Waste_Generated_Aug', 0) + request.data.get('Waste_Generated_Sep', 0) + request.data.get('Waste_Generated_Oct', 0) + request.data.get('Waste_Generated_Nov', 0) + request.data.get('Waste_Generated_Dec', 0) + request.data.get('Waste_Generated_Jan', 0) + request.data.get('Waste_Generated_Feb', 0) + request.data.get('Waste_Generated_Mar', 0)
            request.data["Waste_Generated_Total"] = round(Waste_Generated_Total,2)

            logger.info(f"PUT data: {request.data}")
            waste_generated = Waste_Generated.objects.get(id=id)
            serializer = WasteGeneratedSerializer(waste_generated, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()



                waste_intensity = calculate_waste_intensity()
                Waste_Intensity.objects.all().delete()
                for i in waste_intensity:
                    serializer6=WasteIntensitySerializer(data=i)
                    if serializer6.is_valid(): 
                        serializer6.save() 


                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Waste_Generated"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            waste_generated = Waste_Generated.objects.get(id=id)
            waste_generated.delete()



            waste_intensity = calculate_waste_intensity()
            Waste_Intensity.objects.all().delete()
            for i in waste_intensity:
                serializer6=WasteIntensitySerializer(data=i)
                if serializer6.is_valid(): 
                    serializer6.save() 

                    
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Waste_Generated"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Waste_Recovered_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            Facility = request.query_params.get('Facility')
            production = Waste_Recovered.objects.filter(Facility=Facility).order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)
            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = WasteRecoveredSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecoveredCategoryList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            category_list = WASTE_RECOVERED_CATEGORY

            if not category_list:
                return Response({'error': 'Category list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(category_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Category list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class Waste_Recovered_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id=None):
        try:
            user_role = request.user.role
            user_location = request.user.location
            #if user_role == "Plant Operations" or user_role == "ESG Lead":

            if id:
                waste_recovered = Waste_Recovered.objects.filter(Facility__in=user_location)
                serializer = WasteRecoveredSerializer(waste_recovered)
                return Response(serializer.data)
            else:
                facility = request.query_params.get('Facility', None)
                
                filter_kwargs = {}
                if facility:
                    filter_kwargs['Facility'] = facility
                    waste_recovered = Waste_Recovered.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')
                else:
                    waste_recovered = Waste_Recovered.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
                page_size = request.query_params.get('page_size', 5)
                paginator = Paginator(waste_recovered, page_size)
                page_number = request.query_params.get('page', 1)

                try:
                    paginated_queryset = paginator.page(page_number)
                except EmptyPage:
                    return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
                except PageNotAnInteger:
                    return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = WasteRecoveredSerializer(paginated_queryset, many=True)
                response_data = {
                    'data': serializer.data,
                    'page': int(page_number),
                    'total_pages': paginator.num_pages,
                    'count': paginator.count,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self,request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            catagory = request.data.get("Waste_Recovered_Category")

            # Check if an entry already exists for the given facility and financial year
            if Waste_Recovered.objects.filter(Facility=Facility, Financial_Year=Financial_Year,Waste_Recovered_Category=catagory).count() > 0:
                return Response({'error': 'Entry for this facility, category and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
            # Get the count of existing objects
            if Waste_Recovered.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Waste_Recovered.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id
            
            Waste_Recovered_Total = request.data.get('Waste_Recovered_Apr', 0) + request.data.get('Waste_Recovered_May', 0)  + request.data.get('Waste_Recovered_Jun', 0) + request.data.get('Waste_Recovered_Jul', 0) + request.data.get('Waste_Recovered_Aug', 0) + request.data.get('Waste_Recovered_Sep', 0) + request.data.get('Waste_Recovered_Oct', 0) + request.data.get('Waste_Recovered_Nov', 0) + request.data.get('Waste_Recovered_Dec', 0) + request.data.get('Waste_Recovered_Jan', 0) + request.data.get('Waste_Recovered_Feb', 0) + request.data.get('Waste_Recovered_Mar', 0)
            request.data["Waste_Recovered_Total"] = round(Waste_Recovered_Total,2)

            # Serialize the data
            serializer =  WasteRecoveredSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Waste_Recovered"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data added successfully.'})
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def put(self, request, id):
        try:
            Waste_Recovered_Total = request.data.get('Waste_Recovered_Apr', 0) + request.data.get('Waste_Recovered_May', 0)  + request.data.get('Waste_Recovered_Jun', 0) + request.data.get('Waste_Recovered_Jul', 0) + request.data.get('Waste_Recovered_Aug', 0) + request.data.get('Waste_Recovered_Sep', 0) + request.data.get('Waste_Recovered_Oct', 0) + request.data.get('Waste_Recovered_Nov', 0) + request.data.get('Waste_Recovered_Dec', 0) + request.data.get('Waste_Recovered_Jan', 0) + request.data.get('Waste_Recovered_Feb', 0) + request.data.get('Waste_Recovered_Mar', 0)
            request.data["Waste_Recovered_Total"] = round(Waste_Recovered_Total,2)

            logger.info(f"PUT data: {request.data}")
            waste_recovered = Waste_Recovered.objects.get(id=id)
            serializer = WasteRecoveredSerializer(waste_recovered, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Waste_Recovered"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            waste_recovered = Waste_Recovered.objects.get(id=id)
            waste_recovered.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Waste_Recovered"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






class DisposedCategoryList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            category_list = WASTE_DISPOSED_CATEGORY

            if not category_list:
                return Response({'error': 'Category list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(category_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Category list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Waste_Disposed_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            user_role = request.user.role
            #if user_role == "Plant Operations" or user_role == "ESG Lead":
            Facility = request.query_params.get('Facility')
            production = Waste_Disposed.objects.filter(Facility=Facility).order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)
            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = WasteDisposedSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Waste_Disposed_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id=None):
        try:
            user_role = request.user.role
            user_location = request.user.location
            #if user_role == "Plant Operations" or user_role == "ESG Lead":
            if id:
                waste_disposed = Waste_Disposed.objects.filter(Facility__in=user_location)
                serializer = WasteDisposedSerializer(waste_disposed)
                return Response(serializer.data)
            else:
                facility = request.query_params.get('Facility', None)
                

                filter_kwargs = {}
                if facility:
                    filter_kwargs['Facility'] = facility
                
                waste_disposed = Waste_Disposed.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
                page_size = request.query_params.get('page_size', 5)
                paginator = Paginator(waste_disposed, page_size)
                page_number = request.query_params.get('page', 1)

                try:
                    paginated_queryset = paginator.page(page_number)
                except EmptyPage:
                    return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
                except PageNotAnInteger:
                    return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = WasteDisposedSerializer(paginated_queryset, many=True)
                response_data = {
                    'data': serializer.data,
                    'page': int(page_number),
                    'total_pages': paginator.num_pages,
                    'count': paginator.count,
                }
                return Response(response_data, status=status.HTTP_200_OK)
                
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self,request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            Facility = request.data.get('Facility')
            Financial_Year = request.data.get('Financial_Year')
            Waste_Disposed_Category = request.data.get('Waste_Disposed_Category')

            # Check if an entry already exists for the given facility and financial year
            if Waste_Disposed.objects.filter(Facility=Facility, Financial_Year=Financial_Year,Waste_Disposed_Category=Waste_Disposed_Category).count() > 0:
                return Response({'error': 'Entry for this facility, Category and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
            # Get the count of existing objects
            if Waste_Disposed.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Waste_Disposed.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id
            
            Waste_Disposed_Total = request.data.get('Waste_Disposed_Apr', 0) + request.data.get('Waste_Disposed_May', 0)  + request.data.get('Waste_Disposed_Jun', 0) + request.data.get('Waste_Disposed_Jul', 0) + request.data.get('Waste_Disposed_Aug', 0) + request.data.get('Waste_Disposed_Sep', 0) + request.data.get('Waste_Disposed_Oct', 0) + request.data.get('Waste_Disposed_Nov', 0) + request.data.get('Waste_Disposed_Dec', 0) + request.data.get('Waste_Disposed_Jan', 0) + request.data.get('Waste_Disposed_Feb', 0) + request.data.get('Waste_Disposed_Mar', 0)
            request.data["Waste_Disposed_Total"] = round(Waste_Disposed_Total,2)

            # Serialize the data
            serializer =  WasteDisposedSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Waste_Disposed"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data added successfully.'})
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def put(self, request, id):
        try:
            Waste_Disposed_Total = request.data.get('Waste_Disposed_Apr', 0) + request.data.get('Waste_Disposed_May', 0)  + request.data.get('Waste_Disposed_Jun', 0) + request.data.get('Waste_Disposed_Jul', 0) + request.data.get('Waste_Disposed_Aug', 0) + request.data.get('Waste_Disposed_Sep', 0) + request.data.get('Waste_Disposed_Oct', 0) + request.data.get('Waste_Disposed_Nov', 0) + request.data.get('Waste_Disposed_Dec', 0) + request.data.get('Waste_Disposed_Jan', 0) + request.data.get('Waste_Disposed_Feb', 0) + request.data.get('Waste_Disposed_Mar', 0)
            request.data["Waste_Disposed_Total"] = round(Waste_Disposed_Total,2)

            logger.info(f"PUT data: {request.data}")
            waste_disposed = Waste_Disposed.objects.get(id=id)
            serializer = WasteDisposedSerializer(waste_disposed, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Waste_Disposed"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            waste_disposed = Waste_Disposed.objects.get(id=id)
            waste_disposed.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Waste_Disposed"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class Waste_Intensity_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location
            #if user_role == "Plant Operations" or user_role == "ESG Lead":

            waste_intensity = Waste_Intensity.objects.filter(Facility__in=user_location).order_by('-Financial_Year')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(waste_intensity, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = WasteIntensitySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            financial_year = request.data.get('Financial_Year')
            
            # Check if an entry for this financial year already exists
            if Waste_Intensity.objects.filter(Financial_Year=financial_year).count() > 0:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Waste_Intensity.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Waste_Intensity.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            Total_Waste_Intensity = request.data.get('Waste_Intensity_Apr', 0) + request.data.get('Waste_Intensity_May', 0)  + request.data.get('Waste_Intensity_Jun', 0) + request.data.get('Waste_Intensity_Jul', 0) + request.data.get('Waste_Intensity_Aug', 0) + request.data.get('Waste_Intensity_Sep', 0) + request.data.get('Waste_Intensity_Oct', 0) + request.data.get('Waste_Intensity_Nov', 0) + request.data.get('Waste_Intensity_Dec', 0) + request.data.get('Waste_Intensity_Jan', 0) + request.data.get('Waste_Intensity_Feb', 0) + request.data.get('Waste_Intensity_Mar', 0)
            request.data["Total_Waste_Intensity"] = round(Total_Waste_Intensity,2)



            # Serialize the data
            serializer = WasteIntensitySerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Waste_Intensity"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


    def put(self, request, id):
        try:
            Total_Waste_Intensity = request.data.get('Waste_Intensity_Apr', 0) + request.data.get('Waste_Intensity_May', 0)  + request.data.get('Waste_Intensity_Jun', 0) + request.data.get('Waste_Intensity_Jul', 0) + request.data.get('Waste_Intensity_Aug', 0) + request.data.get('Waste_Intensity_Sep', 0) + request.data.get('Waste_Intensity_Oct', 0) + request.data.get('Waste_Intensity_Nov', 0) + request.data.get('Waste_Intensity_Dec', 0) + request.data.get('Waste_Intensity_Jan', 0) + request.data.get('Waste_Intensity_Feb', 0) + request.data.get('Waste_Intensity_Mar', 0)
            request.data["Total_Waste_Intensity"] = round(Total_Waste_Intensity,2)


            logger.info(f"PUT data: {request.data}")
            waste_intensity = Waste_Intensity.objects.get(id=id)
            serializer = WasteIntensitySerializer(waste_intensity, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Waste_Intensity"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            waste_intensity = Waste_Intensity.objects.get(id=id)
            waste_intensity.delete()

            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Waste_Intensity"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()

            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error("Object not found")
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


############################################  Sustainability     #########################################################



class Percentage_Of_R_and_D_and_Capex_Investments_View(APIView):  
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            #if user_role == "Plant Operations" or user_role == "ESG Lead":

            investments = Percentage_Of_R_and_D_and_Capex_Investments.objects.all().order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(investments, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = PercentageOfRandDandCapexInvestmentsSerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            financial_year = request.data.get('Financial_Year')
            
            # Check if an entry for this financial year already exists
            if Percentage_Of_R_and_D_and_Capex_Investments.objects.filter(Financial_Year=financial_year).count() > 0:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Percentage_Of_R_and_D_and_Capex_Investments.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Percentage_Of_R_and_D_and_Capex_Investments.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = PercentageOfRandDandCapexInvestmentsSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Percentage_Of_R_and_D_and_Capex_Investments"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"APIException: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")
            investments = Percentage_Of_R_and_D_and_Capex_Investments.objects.get(id=id)
            serializer = PercentageOfRandDandCapexInvestmentsSerializer(investments, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Percentage_Of_R_and_D_and_Capex_Investments"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            investments = Percentage_Of_R_and_D_and_Capex_Investments.objects.get(id=id)
            investments.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Percentage_Of_R_and_D_and_Capex_Investments"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class Operations_In_Ecologically_Sensitive_Areas_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            user_location = request.user.location
            #if user_role == "Plant Operations" or user_role == "ESG Lead":

            facility_name = request.query_params.get('facility', None)
            
            if facility_name:
                operations = Operations_In_Ecologically_Sensitive_Areas.objects.filter(Facility__in=user_location).order_by('-id')
            else:
                operations = Operations_In_Ecologically_Sensitive_Areas.objects.filter(Facility__in=user_location).order_by('-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(operations, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = OperationsInEcologicallySensitiveAreasSerializer(paginated_queryset, many=True)
            response_data = serializer.data

            # Manually add the Operation field
            for item in response_data:
                try:
                    facility = Facilities.objects.filter(Name_of_Facility=item['Facility']).first()
                    if facility:
                        item['Operation'] = facility.Description_of_Operations
                except Facilities.DoesNotExist:
                    item['Operation'] = None

            final_response = {
                'data': response_data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }

            return Response(final_response, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            # import pdb;pdb.set_trace()
            logger.info(f"POST data: {request.data}")
            facility = request.data.get('Facility')
          
            is_exist = Operations_In_Ecologically_Sensitive_Areas.objects.filter(Facility=facility)

            if is_exist:
                return Response({'error': 'Entry for this facility  already exists'}, status=status.HTTP_400_BAD_REQUEST)

            facility_name = request.data.get('Facility')
            try:
                facility = Facilities.objects.get(Name_of_Facility=facility_name)
                if facility:
                    request.data['Operation'] = facility.Description_of_Operations
            except Facilities.DoesNotExist:
                request.data['Operation'] = None
            
            if Operations_In_Ecologically_Sensitive_Areas.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                max_id = Operations_In_Ecologically_Sensitive_Areas.objects.aggregate(Max('id'))['id__max'] or 0
                id = max_id + 1
            request.data['id'] = id
            
            serializer = OperationsInEcologicallySensitiveAreasSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Operations_In_Ecologically_Sensitive_Areas"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")
            operations = Operations_In_Ecologically_Sensitive_Areas.objects.get(id=id)
            serializer = OperationsInEcologicallySensitiveAreasSerializer(operations, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Operations_In_Ecologically_Sensitive_Areas"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            operations = Operations_In_Ecologically_Sensitive_Areas.objects.get(id=id)
            operations.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Operations_In_Ecologically_Sensitive_Areas"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Environmental_Impact_Assessments_Of_Projects_Undertaken_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            environmental = Environmental_Impact_Assessments_Of_Projects_Undertaken.objects.all().order_by('-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(environmental, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = EnvironmentalImpactAssessmentsOfProjectsUndertakenSerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")


            results = request.data.get('Results', '')
            if results:
                try:
                    custom_url_validator(results)
                except ValidationError as e:
                    logger.error(f"Invalid URL: {e}")
                    return Response({'error': 'Invalid URL'}, status=status.HTTP_400_BAD_REQUEST)


            # Get the count of existing objects
            if Environmental_Impact_Assessments_Of_Projects_Undertaken.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Environmental_Impact_Assessments_Of_Projects_Undertaken.objects.aggregate(Max('id'))['id__max'] + 1

            if Environmental_Impact_Assessments_Of_Projects_Undertaken.objects.filter(Name_of_project=request.data.get('Name_of_project'),Eia_notification_no=request.data.get('Eia_notification_no'),Project_details=request.data.get('Project_details')).count() > 0:
                return Response({'error': 'Entry for this Name of project, EIA notification no, Project details already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = EnvironmentalImpactAssessmentsOfProjectsUndertakenSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Environmental_Impact_Assessments_Of_Projects_Undertaken"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")


            results = request.data.get('Results', '')
            if results:
                try:
                    custom_url_validator(results)
                except ValidationError as e:
                    logger.error(f"Invalid URL: {e}")
                    return Response({'error': 'Invalid URL'}, status=status.HTTP_400_BAD_REQUEST)

            environmental = Environmental_Impact_Assessments_Of_Projects_Undertaken.objects.get(id=id)
            serializer = EnvironmentalImpactAssessmentsOfProjectsUndertakenSerializer(environmental, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Environmental_Impact_Assessments_Of_Projects_Undertaken"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            environmental = Environmental_Impact_Assessments_Of_Projects_Undertaken.objects.get(id=id)
            environmental.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Environmental_Impact_Assessments_Of_Projects_Undertaken"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class Non_Compliance_With_The_Applicable_Environmental_Law_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            environmental_law = Non_Compliance_With_The_Applicable_Environmental_Law.objects.all().order_by('-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(environmental_law, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = NonComplianceWithTheApplicableEnvironmentalLawSerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")

            
            # Get the count of existing objects
            if Non_Compliance_With_The_Applicable_Environmental_Law.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Non_Compliance_With_The_Applicable_Environmental_Law.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            if Non_Compliance_With_The_Applicable_Environmental_Law.objects.filter(The_law_regulations_guidlines_which_was_not_complied_with=request.data.get('The_law_regulations_guidlines_which_was_not_complied_with')).count() > 0:
                return Response({'error': 'Entry for this The law regulations guidlines which was not complied already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Serialize the data
            serializer = NonComplianceWithTheApplicableEnvironmentalLawSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Non_Compliance_With_The_Applicable_Environmental_Law"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")
            environmental_law = Non_Compliance_With_The_Applicable_Environmental_Law.objects.get(id=id)
            serializer = NonComplianceWithTheApplicableEnvironmentalLawSerializer(environmental_law, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Non_Compliance_With_The_Applicable_Environmental_Law"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            environmental_law = Non_Compliance_With_The_Applicable_Environmental_Law.objects.get(id=id)
            environmental_law.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Non_Compliance_With_The_Applicable_Environmental_Law"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Initiatives_Towards_Carbon_Zero_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            initiative = Initiatives_Towards_Carbon_Zero.objects.all().order_by('-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(initiative, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = InitiativesTowardsCarbonZeroSerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")
            initiative_undertaken = request.data.get('Initiative_undertaken')
            is_exist = Initiatives_Towards_Carbon_Zero.objects.filter(Initiative_undertaken=initiative_undertaken)

           
            if is_exist:
                return Response({'error': 'Entry for this Initiative undertaken already exists'}, status=status.HTTP_400_BAD_REQUEST)

            web_link = request.data.get('Web_link', '')
            if web_link:
                try:
                    custom_url_validator(web_link)
                except ValidationError as e:
                    logger.error(f"Invalid URL: {e}")
                    return Response({'error': 'Invalid URL'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Initiatives_Towards_Carbon_Zero.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Initiatives_Towards_Carbon_Zero.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = InitiativesTowardsCarbonZeroSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Initiatives_Towards_Carbon_Zero"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")


            web_link = request.data.get('Web_link', '')
            if web_link:
                try:
                    custom_url_validator(web_link)
                except ValidationError as e:
                    logger.error(f"Invalid URL: {e}")
                    return Response({'error': 'Invalid URL'}, status=status.HTTP_400_BAD_REQUEST)

            initiative = Initiatives_Towards_Carbon_Zero.objects.get(id=id)
            serializer = InitiativesTowardsCarbonZeroSerializer(initiative, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Initiatives_Towards_Carbon_Zero"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            initiave = Initiatives_Towards_Carbon_Zero.objects.get(id=id)
            initiave.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Initiatives_Towards_Carbon_Zero"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#######################################  GHG Emmission   #################################################

class Scope1_Emissions_by_Facilities_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            scope1 = Scope1_Emissions_by_Facilities.objects.filter(Facility__in=user_location).order_by('-Financial_Year')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(scope1, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Scope1EmissionsbyFacilitiesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Scope1_Emissions_by_Fuel_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            scope1 = Scope1_Emissions_by_Fuel.objects.order_by('-Financial_Year')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(scope1, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Scope1EmissionsbyFuelSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Scope1_Emissions_by_GHG_Type_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            scope11 = Scope1_Emissions_by_GHG_Type.objects.order_by('-Financial_Year')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(scope11, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Scope1EmissionsbyGHGTypeSerializer(paginated_queryset, many=True)

            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Scope1_Intensity_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            scope1 = Scope1_Intensity.objects.filter(Facility__in=user_location).order_by('-Financial_Year')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(scope1, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Scope1IntensitySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Scope2_Emissions_by_Facilities_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            scope2 = Scope2_Emissions_by_Facilities.objects.filter(Facility__in=user_location).order_by('-Financial_Year')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(scope2, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Scope2EmissionsbyFacilitiesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Scope2_Emissions_by_Fuel_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            scope2 = Scope2_Emissions_by_Fuel.objects.order_by('-Financial_Year')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(scope2, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Scope2EmissionsbyFuelSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Scope2_Emissions_by_GHG_Type_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":


            scope2 = Scope2_Emissions_by_GHG_Type.objects.order_by('-Financial_Year')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(scope2, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Scope2EmissionsbyGHGTypeSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Scope2_Intensity_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            scope2 = Scope2_Intensity.objects.filter(Facility__in=user_location).order_by('-Financial_Year')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(scope2, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Scope2IntensitySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Emission_Assessment_By_External_Agency_view(APIView):
    permission_classes = [IsAuthenticated]

    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            Assessment_emissions = Emission_Assessment_By_External_Agency.objects.order_by('-Financial_Year', '-id')
        
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(Assessment_emissions, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = EmissionAssessmentByExternalAgencySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            agency_type = request.data.get('Type')
            count = Emission_Assessment_By_External_Agency.objects.filter(Financial_Year=year,Type=agency_type).count()
            if count > 0:
                return Response({'error':'Entry for this Financial Year and agency type already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Emission_Assessment_By_External_Agency.objects.count() == 0:
                id = 1
            else:
                id = Emission_Assessment_By_External_Agency.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            
            serializer = EmissionAssessmentByExternalAgencySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    assessment_by_external_agency_instance = Emission_Assessment_By_External_Agency.objects.get(id=id)
                    serializer = EmissionAssessmentByExternalAgencySerializer(assessment_by_external_agency_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    assessment_by_external_agency = Emission_Assessment_By_External_Agency.objects.get(id=id)
                    assessment_by_external_agency.delete()
                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Emission_Assessment_By_External_Agency.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 



class Scope3_Emissions_by_Facilities_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            scope3 = Scope3_Emissions_by_Facilities.objects.filter(Facility__in=user_location).order_by('-Financial_Year')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(scope3, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Scope3EmissionsbyFacilitiesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Scope3_Emissions_by_Activity_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            scope3 = Scope3_Emissions_by_Activity.objects.order_by('-Financial_Year')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(scope3, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Scope3EmissionsbyActivitySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Scope3_Emissions_by_GHG_Type_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            scope2 = Scope3_Emissions_by_GHG_Type.objects.order_by('-Financial_Year')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(scope2, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Scope3EmissionsbyGHGTypeSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Scope3_Intensity_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role

            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            scope3 = Scope3_Intensity.objects.order_by('-Financial_Year')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(scope3, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Scope3IntensitySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# for trial 
class EmissionFactorsView(APIView):
    def post(self, request):
        try:
            if EmissionFactors.objects.count() == 0:
                id = 1
            else:
                id = EmissionFactors.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            serializer = EmissionFactorsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":

            emission_factors = EmissionFactors.objects.all()
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(emission_factors, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = EmissionFactorsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Plant Operations or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def put(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            emission_factor_instance = EmissionFactors.objects.filter(id=id).first()
            if not emission_factor_instance:
                return Response({'error': 'id not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Serialize and validate the incoming data
            serializer = EmissionFactorsSerializer(
                emission_factor_instance, data=request.data
            )
            if serializer.is_valid():
                serializer.save()
                return Response({'success': 'Data updated successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    emission_factor = EmissionFactors.objects.get(id=id)
                    emission_factor.delete()
                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except EmissionFactors.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 