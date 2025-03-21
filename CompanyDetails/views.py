from django.shortcuts import render
from .city_constant import Indian_States_Cities_Obj
# Create your views here.
from django.utils import timezone
from datetime import datetime
import pytz

from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers import serialize

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
# from EmissionFactors.models import EmissionFactors
from rest_framework.permissions import IsAuthenticated 
from Environment.utils import *
from Environment.models import *
from Environment.serializers import *
from user.models import User
from CompanyDetails import utils
from . import serializers
from .choices import *
import pycountry
import pymongo
from environs import Env
from .models import *
from .serializers import *
from .utils import *

from Activity_Log.models import Activity_Log
from Activity_Log.serializers import ActivityLogSerializer


env = Env()
env.read_env()  # read .env



from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import APIException


import os

class ReportingBoundaryListView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        try:
            Reporting_Boundary_list = REPORTING_BOUNDARY

            if not Reporting_Boundary_list:
                return Response({'error': 'Reporting Boundary list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(Reporting_Boundary_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Reporting Boundary list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
      
class TypeOfAssuranceListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            Type_Of_Assurance_list = TYPE_OF_ASSURANCE

            if not Type_Of_Assurance_list:
                return Response({'error': 'Type Of Assurance list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(Type_Of_Assurance_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Type Of Assurance list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)      







class CompanyProfile(APIView):
    path = os.getcwd()
    UPLOAD_FOLDER = os.path.join(path, 'sustainability_api', 'images')

    def get(self, request, Company_Name=None, format=None):
        if Company_Name:
            try:
                profile = Company_Profile.objects.get(Company_Name=Company_Name)
                serializer = CompanyLogoSerializer(profile)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Company_Profile.DoesNotExist:
                return Response({'error': f'Company with name {Company_Name} does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            profiles = Company_Profile.objects.all()
            serializer = CompanyProfileSerializer(profiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            company_name = request.data['Company_Name']
            CIN = request.data['CIN']
            Year_of_Incorporation = request.data['Year_of_Incorporation']
            Registered_Office_Address_Line1 = request.data['Registered_Office_Address_Line1']
            Registered_Office_Address_Line2 = request.data['Registered_Office_Address_Line2']
            Registered_Office_Country = request.data['Registered_Office_Country']
            Registered_Office_State = request.data['Registered_Office_State']
            Registered_Office_City = request.data['Registered_Office_City']
            Registered_Office_Pincode = request.data['Registered_Office_Pincode']
            Corporate_Office_Address_Line1 = request.data['Corporate_Office_Address_Line1']
            Corporate_Office_Address_Line2 = request.data['Corporate_Office_Address_Line2']
            Corporate_Office_Country = request.data['Corporate_Office_Country']
            Corporate_Office_State = request.data['Corporate_Office_State']
            Corporate_Office_City = request.data['Corporate_Office_City']
            Corporate_Office_Pincode = request.data['Corporate_Office_Pincode']
            Email = request.data['Email']
            Website = request.data['Website']
            Phone_Ext = request.data['Phone_Ext']
            Phone_Number = request.data['Phone_Number']
            Shares_Listed_On = request.data['Shares_Listed_On']
            CSR_Applicable = request.data['CSR_Applicable']
            Name_of_Assurance_Provider = request.data ['Name_of_Assurance_Provider']
            Reporting_Boundary = request.data ['Reporting_Boundary']
            Type_Of_Assurance = request.data ['Type_Of_Assurance']

            Company_logo = request.FILES.get('Company_logo')
            company_logo_path = None

            if Company_logo:
                # Ensure the directory exists
                if not os.path.exists(self.UPLOAD_FOLDER):
                    os.makedirs(self.UPLOAD_FOLDER)

                # Construct the file path with the original file name
                company_logo_path = os.path.join(self.UPLOAD_FOLDER, Company_logo.name)

                # Save the uploaded file
                with open(company_logo_path, 'wb+') as destination:
                    for chunk in Company_logo.chunks():
                        destination.write(chunk)

                # Read the file in binary mode
                with open(company_logo_path, 'rb') as f:
                    company_logo_binary = f.read()

            profile = Company_Profile(
                Company_Name=company_name, CIN=CIN, Year_of_Incorporation=Year_of_Incorporation,
                Registered_Office_Address_Line1=Registered_Office_Address_Line1,
                Registered_Office_Address_Line2=Registered_Office_Address_Line2,
                Registered_Office_Country=Registered_Office_Country, Registered_Office_State=Registered_Office_State,
                Registered_Office_City=Registered_Office_City, Registered_Office_Pincode=Registered_Office_Pincode,
                Corporate_Office_Address_Line1=Corporate_Office_Address_Line1,
                Corporate_Office_Address_Line2=Corporate_Office_Address_Line2,
                Corporate_Office_Country=Corporate_Office_Country, Corporate_Office_State=Corporate_Office_State,
                Corporate_Office_City=Corporate_Office_City, Corporate_Office_Pincode=Corporate_Office_Pincode,
                Email=Email, Website=Website, Phone_Ext=Phone_Ext, Phone_Number=Phone_Number,
                Shares_Listed_On=Shares_Listed_On, CSR_Applicable=CSR_Applicable,
                Name_of_Assurance_Provider=Name_of_Assurance_Provider,Reporting_Boundary=Reporting_Boundary,
                Type_Of_Assurance=Type_Of_Assurance,
                
            )
            
            if Company_logo:
                profile.Company_logo = Company_logo

            profile.save()

            activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added Company Details"
            }
                            
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()

            return Response({'success': 'data successfully added'}, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        
    def put(self, request, Company_Name=None, format=None):
        if Company_Name:
            try:
                profile = Company_Profile.objects.get(Company_Name=Company_Name)
            except Company_Profile.DoesNotExist:
                return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = CompanyLogoSerializer(profile, data=request.data)
            if serializer.is_valid():
                if 'Company_Logo' in request.data:
                    if profile.Company_logo:
                        profile.Company_logo.delete(save=False)
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Edited Company Details"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success' : 'data update successfully'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Company_Name is required."}, status=status.HTTP_400_BAD_REQUEST)


class FinancialYearList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            financial_years_list = utils.generate_financial_years(1992)
            return Response(financial_years_list, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Turn_over(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Finance" or user_role == "ESG Lead":

            turnover = Turnover.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(turnover, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = TurnoverSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Finance or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            count = Turnover.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error':'Entry for this Financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Turnover.objects.count() == 0:
                id = 1
            else:
                id = Turnover.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            total_turnover = request.data.get('Turnover_Apr', 0) + request.data.get('Turnover_May', 0) + request.data.get('Turnover_Jun', 0) + request.data.get('Turnover_Jul', 0) + request.data.get('Turnover_Aug', 0) + request.data.get('Turnover_Sep', 0) + request.data.get('Turnover_Oct', 0) + request.data.get('Turnover_Nov', 0) + request.data.get('Turnover_Dec', 0) + request.data.get('Turnover_Jan', 0) + request.data.get('Turnover_Feb', 0) + request.data.get('Turnover_Mar', 0)
            request.data["Total_Turnover"] = round(total_turnover, 2)

            serializer = TurnoverSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                energy_intensity = calculate_energy_intensity()
                Energy_Intensity.objects.all().delete()
                for i in energy_intensity:
                    serializer2 = EnergyIntensitySerializer(data=i)
                    if serializer2.is_valid():
                        serializer2.save()

                scope_1_intensity = calculate_scope_1_intensity()
                Scope1_Intensity.objects.all().delete()
                for i in scope_1_intensity:
                    serializer3 = Scope1IntensitySerializer(data=i)
                    if serializer3.is_valid():
                        serializer3.save()
                    else:
                        print("Error",i)


                scope2_intensity = calculate_scope_2_intensity()
                Scope2_Intensity.objects.all().delete()
                for i in scope2_intensity:
                    serializer4 = Scope2IntensitySerializer(data=i)
                    if serializer4.is_valid():
                        serializer4.save()


                water_intensity = calculate_water_intensity()
                Water_Intensity.objects.all().delete()
                for i in water_intensity:
                    serializer5 = WaterIntensitySerializer(data=i)
                    if serializer5.is_valid():
                        serializer5.save()


                waste_intensity = calculate_waste_intensity()
                Waste_Intensity.objects.all().delete()
                for i in waste_intensity:
                    serializer6=WasteIntensitySerializer(data=i)
                    if serializer6.is_valid(): 
                        serializer6.save()      

                activity_log = {
                       "Name": request.user.firstname + " " + request.user.lastname, 
                       "Activity": "Added information to table - Turnover"}
                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()


                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except TypeError as e:
            return Response({'error': 'Quantity should be integer'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    total_turnover = request.data.get('Turnover_Apr', 0) + request.data.get('Turnover_May', 0) + request.data.get('Turnover_Jun', 0) + request.data.get('Turnover_Jul', 0) + request.data.get('Turnover_Aug', 0) + request.data.get('Turnover_Sep', 0) + request.data.get('Turnover_Oct', 0) + request.data.get('Turnover_Nov', 0) + request.data.get('Turnover_Dec', 0) + request.data.get('Turnover_Jan', 0) + request.data.get('Turnover_Feb', 0) + request.data.get('Turnover_Mar', 0)
                    request.data["Total_Turnover"] = round(total_turnover, 2)

                    turnover_instance = Turnover.objects.get(id=id)
                    serializer = TurnoverSerializer(turnover_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        energy_intensity = calculate_energy_intensity()
                        Energy_Intensity.objects.all().delete()
                        for i in energy_intensity:
                            serializer2 = EnergyIntensitySerializer(data=i)
                            if serializer2.is_valid():
                                serializer2.save()


                        scope_1_intensity = calculate_scope_1_intensity()
                        Scope1_Intensity.objects.all().delete()
                        for i in scope_1_intensity:
                            serializer3 = Scope1IntensitySerializer(data=i)
                            if serializer3.is_valid():
                                serializer3.save()
                            else:
                                print("ERROR",i)


                        scope2_intensity = calculate_scope_2_intensity()
                        Scope2_Intensity.objects.all().delete()
                        for i in scope2_intensity:
                            serializer4 = Scope2IntensitySerializer(data=i)
                            if serializer4.is_valid():
                                serializer4.save()

                        water_intensity = calculate_water_intensity()
                        Water_Intensity.objects.all().delete()
                        for i in water_intensity:
                            serializer5 = WaterIntensitySerializer(data=i)
                            if serializer5.is_valid():
                                serializer5.save()


                        waste_intensity = calculate_waste_intensity()
                        Waste_Intensity.objects.all().delete()
                        for i in waste_intensity:
                            serializer6=WasteIntensitySerializer(data=i)
                            if serializer6.is_valid(): 
                                serializer6.save()         


                        activity_log = {
                       "Name": request.user.firstname + " " + request.user.lastname, 
                       "Activity": "Edited table - Turnover"}
                
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
                    turnover = Turnover.objects.get(id=id)
                    turnover.delete()

                    energy_intensity = calculate_energy_intensity()
                    Energy_Intensity.objects.all().delete()
                    for i in energy_intensity:
                        serializer2 = EnergyIntensitySerializer(data=i)
                        if serializer2.is_valid():
                            serializer2.save()

                    scope_1_intensity = calculate_scope_1_intensity()
                    Scope1_Intensity.objects.all().delete()
                    for i in scope_1_intensity:
                        serializer3 = Scope1IntensitySerializer(data=i)
                        if serializer3.is_valid():
                            serializer3.save()
                        else:
                            print("Error",i)

                    scope2_intensity = calculate_scope_2_intensity()
                    Scope2_Intensity.objects.all().delete()
                    for i in scope2_intensity:
                        serializer4 = Scope2IntensitySerializer(data=i)
                        if serializer4.is_valid():
                            serializer4.save()

                    
                    water_intensity = calculate_water_intensity()
                    Water_Intensity.objects.all().delete()
                    for i in water_intensity:
                        serializer5 = WaterIntensitySerializer(data=i)
                        if serializer5.is_valid():
                            serializer5.save()


                    waste_intensity = calculate_waste_intensity()
                    Waste_Intensity.objects.all().delete()
                    for i in waste_intensity:
                        serializer6=WasteIntensitySerializer(data=i)
                        if serializer6.is_valid(): 
                            serializer6.save()         

                    activity_log = {
                       "Name": request.user.firstname + " " + request.user.lastname, 
                       "Activity": "Deleted information from table - Turnover"}
                
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Turnover.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  



class Networth_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Finance" or user_role == "ESG Lead":
            networth = Networth.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(networth, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = NetworthSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Finance or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)
            # serializer = NetworthSerializer(networth, many=True)
            # return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            
            year = request.data.get('Financial_Year')
            count = Networth.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error':'Entry for this Financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Networth.objects.count() == 0:
                id = 1
            else:
                id = Networth.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            total_networth = request.data.get('Networth_Apr', 0) + request.data.get('Networth_May', 0) + request.data.get('Networth_Jun', 0) + request.data.get('Networth_Jul', 0) + request.data.get('Networth_Aug', 0) + request.data.get('Networth_Sep', 0) + request.data.get('Networth_Oct', 0) + request.data.get('Networth_Nov', 0) + request.data.get('Networth_Dec', 0) + request.data.get('Networth_Jan', 0) + request.data.get('Networth_Feb', 0) + request.data.get('Networth_Mar', 0)
            request.data["Total_Networth"] = round(total_networth, 2)

            serializer = NetworthSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information to table - Networth"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()


                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except TypeError as e:
            return Response({'error': 'Quantity should be integer'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    # year = request.data.get('Financial_Year')
                    # count = Networth.objects.filter(Financial_Year=year).count()
                    # if count > 0:
                    #     return Response({'message':'Entry for this Financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

                    total_networth = request.data.get('Networth_Apr', 0) + request.data.get('Networth_May', 0) + request.data.get('Networth_Jun', 0) + request.data.get('Networth_Jul', 0) + request.data.get('Networth_Aug', 0) + request.data.get('Networth_Sep', 0) + request.data.get('Networth_Oct', 0) + request.data.get('Networth_Nov', 0) + request.data.get('Networth_Dec', 0) + request.data.get('Networth_Jan', 0) + request.data.get('Networth_Feb', 0) + request.data.get('Networth_Mar', 0)
                    request.data["Total_Networth"] = round(total_networth, 2)

                    networth_instance = Networth.objects.get(id=id)
                    serializer = NetworthSerializer(networth_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Networth"}
                                        
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
                    networth = Networth.objects.get(id=id)
                    networth.delete()

                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Deleted information in table - Networth"}
                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Networth.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 



class BusinessActivityDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            business_activity_details = Business_Activity_Details.objects.all().order_by('-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(business_activity_details, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = BusinessActivityDetailsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)


            #serializer = BusinessActivityDetailsSerializer(business_activity_details, many=True)
            #return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            bussiness_activity = request.data.get('Name_of_Business_Activity')
            is_exist = Business_Activity_Details.objects.filter(Name_of_Business_Activity=bussiness_activity)

            if is_exist:
                return Response({'error': 'Entry for this Business Activity already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Business_Activity_Details.objects.count() == 0:
                id = 1
            else:
                id = Business_Activity_Details.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            serializer = BusinessActivityDetailsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Business Activity Details"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()


                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except TypeError as e:
            return Response({'error': 'Quantity should be integer'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    
                    business_activity_details_instance = Business_Activity_Details.objects.get(id=id)
                    serializer = BusinessActivityDetailsSerializer(business_activity_details_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Business Activity Details"}
                                        
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
                    business_activity_details = Business_Activity_Details.objects.get(id=id)
                    Name_of_Business_Activity = business_activity_details.Name_of_Business_Activity
                  
                    all_instance = Business_Activity.objects.all()
                    for instance in all_instance:
                        for busness_act in instance.Business_Activity_and_Turnover:
                            Business_Activity_and_Turnover_obj = dict(busness_act)
                            if Business_Activity_and_Turnover_obj.get('Business_Activity') == Name_of_Business_Activity:
                                return Response(
                                    {'error': f'Cannot delete Business activity "{Name_of_Business_Activity}" is being used in the Business Activity table.'},
                                    status=status.HTTP_400_BAD_REQUEST
                                )

                    business_activity_details.delete()

                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Deleted information in table - Business Activity Details"}
                                        
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Turnover.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        

class ProductsServicesDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            products_services_details = Products_Services_Details.objects.all().order_by('-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(products_services_details, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ProductsServicesDetailsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

            #serializer = ProductsServicesDetailsSerializer(products_services_details, many=True)
            #return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            product_service = request.data.get('Name_of_Product_Service')
            is_exist = Products_Services_Details.objects.filter(Name_of_Product_Service=product_service)

            if is_exist:
                return Response({'error': 'Entry for this Product Service already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Products_Services_Details.objects.count() == 0:
                id = 1
            else:
                id = Products_Services_Details.objects.aggregate(Max('id'))['id__max'] + 1
            
            request.data['id'] = id

            serializer = ProductsServicesDetailsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Products/Services Details"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except TypeError as e:
            return Response({'error': 'Quantity should be integer'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    products_services_details_instance = Products_Services_Details.objects.get(id=id)
                    serializer = ProductsServicesDetailsSerializer(products_services_details_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Products/Services Details"}
                                        
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
                    products_services_details = Products_Services_Details.objects.get(id=id)

                    Name_of_Product_Service = products_services_details.Name_of_Product_Service
                  
                    all_instance = Products_Services.objects.all()
                    for instance in all_instance:
                        for busness_act in instance.Products_Services_and_Turnover:
                            Business_Activity_and_Turnover_obj = dict(busness_act)
                            if Business_Activity_and_Turnover_obj.get('Product_Service') == Name_of_Product_Service:
                                return Response(
                                    {'error': f'Cannot delete Product_Service "{Name_of_Product_Service}" is being used in the Product_Service table.'},
                                    status=status.HTTP_400_BAD_REQUEST
                                )

                    products_services_details.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Products/Services Details"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Turnover.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 



class Exports_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            exports = Exports.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(exports, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ExportsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

            # serializer = ExportsSerializer(exports, many=True)
            # return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            count = Exports.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error':'Entry for this Financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            if Exports.objects.count() == 0:
                id = 1
            else:
                id = Exports.objects.aggregate(Max('id'))['id__max'] + 1
            
            request.data['id'] = id

            serializer = ExportsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Exports"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except TypeError as e:
            return Response({'error': 'Quantity should be integer'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    exports_instance = Exports.objects.get(id=id)
                    serializer = ExportsSerializer(exports_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Exports"}
                                        
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
                    exports = Exports.objects.get(id=id)
                    exports.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Exports"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Turnover.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 




class BusinessActivityList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:

            business_activities = Business_Activity_Details.objects.values_list('Name_of_Business_Activity', flat=True)
            business_activity_list = list(business_activities)

            if not business_activity_list:
                return Response({'error': 'List is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(business_activity_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'List is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class ProductsServicesList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            products_services = Products_Services_Details.objects.values_list('Name_of_Product_Service', flat=True)
            products_services_list = list(products_services)

            if not products_services_list:
                return Response({'error': 'List is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(products_services_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'List is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Business_Activity_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            business_activity = Business_Activity.objects.order_by('-Financial_Year', '-id')
        
            page_size = request.query_params.get('page_size', 15)
            paginator = Paginator(business_activity, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = BusinessActivitySerializer(paginated_queryset, many=True)
            data = serializer.data
            response_data = {
                'data': data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

            # serializer = BusinessActivitySerializer(business_activity, many=True)
            # return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            count = Business_Activity.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error':'Entry for this Financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Business_Activity.objects.count() == 0:
                id = 1
            else:
                id = Business_Activity.objects.aggregate(Max('id'))['id__max'] + 1
            
            request.data['id'] = id

            serializer = BusinessActivitySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Business Activity"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except TypeError as e:
            return Response({'error': 'Quantity should be integer'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    year = request.data.get('Financial_Year')
                    count = Business_Activity.objects.filter(Financial_Year=year).exclude(id=id).count()
                    if count > 0:
                        return Response({'message':'Entry for this Financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

                    business_activity_instance = Business_Activity.objects.get(id=id)
                    serializer = BusinessActivitySerializer(business_activity_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Business Activity"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'message': 'Data updated successfully.'}, status=200)
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
                    business_activity = Business_Activity.objects.get(id=id)
                    business_activity.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Business Activity"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Turnover.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 



class Products_Services_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            products_services = Products_Services.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(products_services, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ProductsServicesSerializer(paginated_queryset, many=True)

            data = serializer.data
            response_data = {
                'data': data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

            # serializer = ProductsServicesSerializer(products_services, many=True)
            # return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            count = Products_Services.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error':'Entry for this Financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Products_Services.objects.count() == 0:
                id = 1
            else:
                id = Products_Services.objects.aggregate(Max('id'))['id__max'] + 1
            
            request.data['id'] = id

            serializer = ProductsServicesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Products/Services"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except TypeError as e:
            return Response({'error': 'Quantity should be integer'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    year = request.data.get('Financial_Year')
                    count = Products_Services.objects.filter(Financial_Year=year).exclude(id=id).count()
                    if count > 0:
                        return Response({'error':'Entry for this Financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

                    products_services_instance = Products_Services.objects.get(id=id)
                    serializer = ProductsServicesSerializer(products_services_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Products/Services"}
                                        
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
                    products_services = Products_Services.objects.get(id=id)
                    products_services.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Products/Services"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Turnover.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class OfficesandPlants_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            offices_and_plants = Offices_and_Plants.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(offices_and_plants, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = OfficesandPlantsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

            # serializer = OfficesandPlantsSerializer(offices_and_plants, many=True)
            # return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            count = Offices_and_Plants.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error':'Entry for this Financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Offices_and_Plants.objects.count() == 0:
                id = 1
            else:
                id = Offices_and_Plants.objects.aggregate(Max('id'))['id__max'] + 1
            
            request.data['id'] = id

            total = request.data.get('No_of_National_Offices', 0) + request.data.get('No_of_National_Plants', 0)  + request.data.get('No_of_International_Offices', 0) + request.data.get('No_of_International_Plants', 0)
            request.data["Total"] = total

            serializer = OfficesandPlantsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Offices and Plants"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except TypeError as e:
            return Response({'error': 'Quantity should be integer'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    total = request.data.get('No_of_National_Offices', 0) + request.data.get('No_of_National_Plants', 0)  + request.data.get('No_of_International_Offices', 0) + request.data.get('No_of_International_Plants', 0)
                    request.data["Total"] = total

                    offices_and_plants_instance = Offices_and_Plants.objects.get(id=id)
                    serializer = OfficesandPlantsSerializer(offices_and_plants_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Offices and Plants"}
                                        
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
                    offices_and_plants = Offices_and_Plants.objects.get(id=id)
                    offices_and_plants.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Offices and Plants"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Turnover.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        


class MarketsServed_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            markets_served = Markets_Served.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(markets_served, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = MarketsServedSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

            # serializer = MarketsServedSerializer(markets_served, many=True)
            # return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            
            year = request.data.get('Financial_Year')
            count = Markets_Served.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error':'Entry for this Financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            if Markets_Served.objects.count() == 0:
                id = 1
            else:
                id = Markets_Served.objects.aggregate(Max('id'))['id__max'] + 1
            
            request.data['id'] = id

            serializer = MarketsServedSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Markets Served"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except TypeError as e:
            return Response({'error': 'Quantity should be integer'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    markets_served_instance = Markets_Served.objects.get(id=id)
                    serializer = MarketsServedSerializer(markets_served_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Markets Served"}
                                        
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
                    markets_served = Markets_Served.objects.get(id=id)
                    markets_served.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Markets Served"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Turnover.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        


class PaidupCapital_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            paid_up_capital = Paid_up_Capital.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(paid_up_capital, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = PaidupCapitalSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

            # serializer = PaidupCapitalSerializer(paid_up_capital, many=True)
            # return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
           
            count = Paid_up_Capital.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error':'Entry for this Financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Paid_up_Capital.objects.count() == 0:
                id = 1
            else:
                id = Paid_up_Capital.objects.aggregate(Max('id'))['id__max'] + 1
            
            request.data['id'] = id

            serializer = PaidupCapitalSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Paid-up Capital"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except TypeError as e:
            return Response({'error': 'Quantity should be integer'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    paid_up_capital_instance = Paid_up_Capital.objects.get(id=id)
                    serializer = PaidupCapitalSerializer(paid_up_capital_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Paid-up Capital"}
                                        
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
                    paid_up_capital = Paid_up_Capital.objects.get(id=id)
                    paid_up_capital.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Paid-up Capital"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Turnover.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 



class PaidupCapital_Unit_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        
        try:
            paid_up_capital_unit = UNIT

            if not paid_up_capital_unit:
                return Response({'error': 'Reporting Boundary list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(paid_up_capital_unit, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Reporting Boundary list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      


class TypeofHoldingList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            type_of_holding_list = TYPE_OF_HOLDING

            if not type_of_holding_list:
                return Response({'error': 'Holding type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(type_of_holding_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Holding type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class Holdings_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":
            holdings = Holdings.objects.all().order_by('-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(holdings, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = HoldingsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

            # serializer = HoldingsSerializer(holdings, many=True)
            # return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            print("Incoming data:", request.data)
            holding = request.data.get('Type_of_Holding',[])
            if isinstance(holding, list) and holding:
                holding = holding[0]  

            # Check if an entry already exists for the given facility and financial year
            if Holdings.objects.filter(Type_of_Holding=holding).count() > 0:
                return Response({'error': 'Entry for this Holding Type already exists'}, status=status.HTTP_400_BAD_REQUEST)
           

            # Get the next ID for the Holdings model
            id = 1 if Holdings.objects.count() == 0 else Holdings.objects.aggregate(Max('id'))['id__max'] + 1
            request.data['id'] = id
            # next_id = Holdings.objects.aggregate(Max('id'))['id__max'] + 1 if Holdings.objects.count() > 0 else 1
            # request.data['id'] = next_id
            
            # Convert Type_of_Holding from list to string if it's a list
            if isinstance(request.data.get("Type_of_Holding"), list):
                request.data["Type_of_Holding"] = ", ".join(request.data["Type_of_Holding"])

            # Create the serializer with the processed data
            serializer = HoldingsSerializer(data=request.data)

            if serializer.is_valid():
                # Save the new Holdings instance
                serializer.save()

                # Log the activity
                activity_log = {
                    "Name": f"{request.user.firstname} {request.user.lastname}",
                    "Activity": "Added information in table - Holdings"
                }
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                else:
                    print("Activity log serializer errors:", activity_log_serializer.errors)
                    return Response(activity_log_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                print("Holdings serializer errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except TypeError as e:
            print(f"Type error: {str(e)}")
            return Response({'error': 'Quantity should be an integer'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Log the exception with more context to identify the issue
            print("Unhandled exception:", str(e))
            return Response({'error': str(e) or "An unknown error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    holdings_instance = Holdings.objects.get(id=id)

                    # Convert Type_of_Holding from list to string if it's provided as a list
                    if isinstance(request.data.get("Type_of_Holding"), list):
                        request.data["Type_of_Holding"] = ", ".join(request.data["Type_of_Holding"])

                    serializer = HoldingsSerializer(holdings_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        # Log the activity
                        activity_log = {
                            "Name": f"{request.user.firstname} {request.user.lastname}",
                            "Activity": "Edited information in table - Holdings"
                        }
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        # Return only the success message
                        return Response({'success': 'Data updated successfully.'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Holdings.DoesNotExist:
                    return Response({'error': 'ID not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    holdings = Holdings.objects.get(id=id)
                    holdings.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Holdings"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Turnover.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        


class TypeofFacilityList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            type_of_facility_list = TYPE_OF_FACILITY

            if not type_of_facility_list:
                return Response({'error': 'Facility type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(type_of_facility_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Facility type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class IndianStatesList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            states_list = list(Indian_States_Cities_Obj.keys())
            return Response(sorted(states_list), status=status.HTTP_200_OK)
            
        except NameError:
            return Response({'error': 'Indian states list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Facilities_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            facilities = Facilities.objects.all().order_by('-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(facilities, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = FacilitiesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

            # serializer = FacilitiesSerializer(facilities, many=True)
            # return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            facility  = request.data.get('Name_of_Facility')
            plant = request.data.get('Type_of_Facility')

            # Check if an entry already exists for the given facility and financial year
            if Facilities.objects.filter(Name_of_Facility=facility, Type_of_Facility = plant).count() > 0:
                return Response({'error': 'Entry for this facility and type already exists'}, status=status.HTTP_400_BAD_REQUEST)
           

            if Facilities.objects.count() == 0:
                id = 1
            else:
                id = Facilities.objects.aggregate(Max('id'))['id__max'] + 1
            
            request.data['id'] = id

            serializer = FacilitiesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Facilities"}
                                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                #  # Get the new facility name from the request data
                # new_facility_name = request.data['Name_of_Facility']
                # esg_lead_users = User.objects.filter(role='ESG Lead')

                # for user in esg_lead_users:
                #     if new_facility_name not in user.location:
                #         user.location.append(new_facility_name)
                #         user.save(update_fields=['location'])

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
                    facilities_instance = Facilities.objects.get(id=id)
                    old_facility_name = facilities_instance.Name_of_Facility 
                    print("old_facility_name:",old_facility_name,"----------------------")
                    
                    serializer = FacilitiesSerializer(facilities_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Facilities"}
                                        
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        new_facility_name = request.data['Name_of_Facility'] 
                        esg_lead_users = User.objects.filter(role='ESG Lead')

                        for user in esg_lead_users:
                            if old_facility_name in user.location:
                                user.location.remove(old_facility_name)  # Remove old facility name
                                if new_facility_name not in user.location:
                                    user.location.append(new_facility_name)  # Add new facility name
                                user.save()

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
                    facilities = Facilities.objects.get(id=id)
                    facility_name = facilities.Name_of_Facility 
                    facilities.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Facilities"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    
                    esg_lead_users = User.objects.filter(role='ESG Lead')

                    for user in esg_lead_users:
                        if facility_name in user.location:
                            user.location.remove(facility_name)
                            user.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Facilities.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Countries_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            
            # Get all countries
            countries = list(pycountry.countries)

            # Sort countries with India on top
            countries_sorted = sorted(countries, key=lambda x: (x.name != 'India', x.name))            

            # Extract country names from countries object
            country_names = [country.name for country in countries_sorted]

            return Response(country_names, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# client = pymongo.MongoClient(env.str('MONGO_DATABASE_URL', default='mongodb://localhost:27017/carbon_calculator'))
# db = client['carbon_calculator']

# states_and_cities_collection = db['Indian_States_Cities']

class States_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:

            if request.query_params.get('country') == "India":
                states_list = list(Indian_States_Cities_Obj.keys())
                # document = Indian_States_Cities.objects.all()
                # if document:
                #     # Get the list of state names (keys of the document)
                #    states_list = list(document.values_list('state_name', flat=True))
                # else:
                #     print("No document found")

            else:
                states_list = ["Other"]
            return Response(states_list, status=status.HTTP_200_OK)

            # country = request.query_params.get('country', None)

            # if country == "India":

            #     india = pycountry.countries.get(name='India')

            #     # Get subdivisions (states) for India
            #     subdivisions = pycountry.subdivisions.get(country_code=india.alpha_2)

            #     # Extract state names from subdivisions
            #     state_names = [subdivision.name for subdivision in subdivisions]

            #     # Sort state names alphabetically
            #     state_names_sorted = sorted(state_names)
            # if states_list:
            #     return Response(states_list, status=status.HTTP_200_OK)
            # else:
            #     return Response({"error":"data not found"}, status=status.HTTP_404_NOT_FOUND)

        # except ObjectDoesNotExist:
        #     return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        # except APIException as e:
        #     return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self,request):
        try:
            data = request.data
            if Indian_States_Cities.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                max_id = Indian_States_Cities.objects.aggregate(Max('id'))['id__max'] or 0
                id = max_id + 1
            request.data['id'] = id

            # Check if state already exists
            state_name = data.get("state_name")
            existing_state = Indian_States_Cities.objects.filter(state_name=state_name).first()
            if existing_state:
                return Response(
                    {"error": "State already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Deserialize and validate data
            serializer = Indian_States_CitiesSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class Cities_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            
            state = request.query_params.get('state', None)

            if state == "Other":
                cities = ["Other"]
            elif Indian_States_Cities_Obj.get(state):
                cities = Indian_States_Cities_Obj.get(state)
            else:
                cities = []
                # Query MongoDB
                # result = Indian_States_Cities.objects.get(state_name=state)
                # if result:
                #     # cities = result.cities
                # else:
                #     cities = []  # Handle case where state_name doesn't exist       

            return Response(sorted(cities), status=status.HTTP_200_OK)
        # except ObjectDoesNotExist:
        #     return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        # except APIException as e:
        #     return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class SharesListedOn_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            shares_listed_on_list = SHARES_LISTED_ON

            if not shares_listed_on_list:
                return Response({'error': 'Shares listed on list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(shares_listed_on_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Shares listed on list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       

class FacilityList_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "ESG Lead":
            #     name_of_facility = Facilities.objects.values_list('Name_of_Facility', flat=True).distinct()
            #     name_of_facility = list(name_of_facility)  # Convert to list for serialization
            # else:
            user_locations = request.user.location
            name_of_facility = Facilities.objects.filter(Name_of_Facility__in=user_locations).values_list('Name_of_Facility', flat=True).distinct()
            name_of_facility = sorted(set(name_of_facility), key=str.casefold)


            return Response(name_of_facility, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




"""
API's for Number of days of accounts payables (Accounts payable *365)
"""
class NumberOfDaysOfAccountsPayablesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            payables_obj = NumberOfDaysOfAccountsPayablesModel.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(payables_obj, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = NumberOfDaysOfAccountsPayablesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            financial_year = request.data.get('Financial_Year')
            data = NumberOfDaysOfAccountsPayablesModel.objects.filter(Financial_Year=financial_year)
            if data:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if NumberOfDaysOfAccountsPayablesModel.objects.count() == 0:
                id = 1
            else:
                id = NumberOfDaysOfAccountsPayablesModel.objects.aggregate(Max('id'))['id__max'] + 1
            
            request.data['id'] = id

            serializer = NumberOfDaysOfAccountsPayablesSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - NumberOfDaysOfAccountsPayablesModel"}
                                
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
                request.data['id'] = id
                financial_year = request.data.get('Financial_Year')
                data = NumberOfDaysOfAccountsPayablesModel.objects.filter(Financial_Year=financial_year).exclude(id=id)
                if data:
                    return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    payables_obj = NumberOfDaysOfAccountsPayablesModel.objects.get(id=id)
                    serializer = NumberOfDaysOfAccountsPayablesSerializer(payables_obj, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - NumberOfDaysOfAccountsPayablesModel"}
                                        
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
                    paid_up_capital = NumberOfDaysOfAccountsPayablesModel.objects.get(id=id)
                    paid_up_capital.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - NumberOfDaysOfAccountsPayablesModel"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Turnover.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 



"""
API's for Concentration Of Sales
"""
class ConcentrationOfSalesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            payables_obj = Concentration_Of_Sales.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(payables_obj, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Concentration_Of_SalesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            financial_year = request.data.get('Financial_Year')
            data = Concentration_Of_Sales.objects.filter(Financial_Year=financial_year)
            if data:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Concentration_Of_Sales.objects.count() == 0:
                id = 1
            else:
                id = Concentration_Of_Sales.objects.aggregate(Max('id'))['id__max'] + 1
            
            request.data['id'] = id

            serializer = Concentration_Of_SalesSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Concentration_Of_Sales"}
                                
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
                request.data['id'] = id
                financial_year = request.data.get('Financial_Year')
                data = Concentration_Of_Sales.objects.filter(Financial_Year=financial_year).exclude(id=id)
                if data:
                    return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    payables_obj = Concentration_Of_Sales.objects.get(id=id)
                    serializer = Concentration_Of_SalesSerializer(payables_obj, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Concentration_Of_Sales"}
                                        
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
                    paid_up_capital = Concentration_Of_Sales.objects.get(id=id)
                    paid_up_capital.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Concentration_Of_Sales"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Turnover.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 





"""
API's for Concentration of Purchases
"""
class ConcentrationOfPurchasesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            payables_obj = Concentration_Of_Purchases.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(payables_obj, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Concentration_Of_PurchasesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            financial_year = request.data.get('Financial_Year')
            data = Concentration_Of_Purchases.objects.filter(Financial_Year=financial_year)
            if data:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Concentration_Of_Purchases.objects.count() == 0:
                id = 1
            else:
                id = Concentration_Of_Purchases.objects.aggregate(Max('id'))['id__max'] + 1
            
            request.data['id'] = id

            serializer = Concentration_Of_PurchasesSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Concentration_Of_Purchases"}
                                
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
                request.data['id'] = id
                financial_year = request.data.get('Financial_Year')
                data = Concentration_Of_Purchases.objects.filter(Financial_Year=financial_year).exclude(id=id)
                if data:
                    return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    payables_obj = Concentration_Of_Purchases.objects.get(id=id)
                    serializer = Concentration_Of_PurchasesSerializer(payables_obj, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Concentration_Of_Purchases"}
                                        
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
                    paid_up_capital = Concentration_Of_Purchases.objects.get(id=id)
                    paid_up_capital.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Concentration_Of_Purchases"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Turnover.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


"""
API's for Share of RPTs in
"""
class ShareOfRPTsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            payables_obj = ShareOfRPTs.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(payables_obj, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ShareOfRPTsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            financial_year = request.data.get('Financial_Year')
            data = ShareOfRPTs.objects.filter(Financial_Year=financial_year)
            if data:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if ShareOfRPTs.objects.count() == 0:
                id = 1
            else:
                id = ShareOfRPTs.objects.aggregate(Max('id'))['id__max'] + 1
            
            request.data['id'] = id

            serializer = ShareOfRPTsSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - ShareOfRPTs"}
                                
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
                request.data['id'] = id
                financial_year = request.data.get('Financial_Year')
                data = ShareOfRPTs.objects.filter(Financial_Year=financial_year).exclude(id=id)
                if data:
                    return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    payables_obj = ShareOfRPTs.objects.get(id=id)
                    serializer = ShareOfRPTsSerializer(payables_obj, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - ShareOfRPTs"}
                                        
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
                    paid_up_capital = ShareOfRPTs.objects.get(id=id)
                    paid_up_capital.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - ShareOfRPTs"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Turnover.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 




class FacilityListAdmin_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "ESG Lead" or user_role == "Company Secretary":
            name_of_facility = Facilities.objects.values_list('Name_of_Facility', flat=True).distinct()
            name_of_facility = sorted(name_of_facility, key=str.casefold)  # Convert to list for serialization
        
            return Response(name_of_facility, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only be accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)


        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
