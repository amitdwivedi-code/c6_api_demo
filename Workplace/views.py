from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max, Sum
from django.db.models import Max


from rest_framework import status
from rest_framework.permissions import IsAuthenticated 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from Activity_Log.models import Activity_Log
from Activity_Log.serializers import ActivityLogSerializer
from django.db import transaction

from .choices import *
from .models import *
from .serializers import *
from .utils import *


from decimal import Decimal, ROUND_HALF_UP


import logging
logger = logging.getLogger(__name__)


class GenderList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            gender_list = GENDER

            if not gender_list:
                return Response({'error': 'Gender list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(gender_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Gender list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TypeList_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            type_list = TYPE

            if not type_list:
                return Response({'error': 'Type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(type_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Employees_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            user_role = request.user.role
            location = request.user.location 

            # if user_role == "Human Resource" or user_role == "ESG Lead" :
            if id:
                employees = Employees.objects.filter(id=id, Facility__in=location)
                if not employees.count() > 0:
                    return Response({'error': 'No employee found with this ID in the user’s facilities.'}, status=status.HTTP_404_NOT_FOUND)

                serializer = EmployeesSerializer(employees, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            employees = Employees.objects.filter(Facility__in=location).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(employees, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            # Serialize paginated results
            serializer = EmployeesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

            # return Response({'error': 'This data can only be accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def post(self,request):
        try:
            logger.info(f"POST data: {request.data}")

            # Get the count of existing objects
            if Employees.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Employees.objects.aggregate(Max('id'))['id__max'] + 1
                
            financial_year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            type = request.data.get('Type')
            gender = request.data.get('Gender')
            if Employees.objects.filter(Financial_Year=financial_year,Facility=facility,Type=type,Gender=gender).count() > 0:
                return Response({'error': 'Entry for this Facility, Type, Gender and Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Assign the new ID to the request data
            request.data['id'] = id
            Total_Employees = request.data.get('Employees_Apr', 0) + request.data.get('Employees_May', 0)  + request.data.get('Employees_Jun', 0) + request.data.get('Employees_Jul', 0) + request.data.get('Employees_Aug', 0) + request.data.get('Employees_Sep', 0) + request.data.get('Employees_Oct', 0) + request.data.get('Employees_Nov', 0) + request.data.get('Employees_Dec', 0) + request.data.get('Employees_Jan', 0) + request.data.get('Employees_Feb', 0) + request.data.get('Employees_Mar', 0)
            request.data["Total_Employees"] = round(Total_Employees ,2)
          
            serializer =  EmployeesSerializer(data=request.data)
           
            if serializer.is_valid():
                serializer.save()
                
                total_employees = calculate_total_employees()
                EmployeeSummary.objects.all().delete()
                for i in total_employees:
                    serializer = EmployeeSummarySerializer(data=i)
                    if serializer.is_valid():
                        serializer.save()
            

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Employees"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                # financial_year = request.data.get('Financial_Year')
                # facility = request.data.get('Facility')
                # utils.save_employee_summary(financial_year, facility)
                return Response({'success': 'Data added successfully.'})

            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            Total_Employees = request.data.get('Employees_Apr', 0) + request.data.get('Employees_May', 0)  + request.data.get('Employees_Jun', 0) + request.data.get('Employees_Jul', 0) + request.data.get('Employees_Aug', 0) + request.data.get('Employees_Sep', 0) + request.data.get('Employees_Oct', 0) + request.data.get('Employees_Nov', 0) + request.data.get('Employees_Dec', 0) + request.data.get('Employees_Jan', 0) + request.data.get('Employees_Feb', 0) + request.data.get('Employees_Mar', 0)
            request.data["Total_Employees"] = round(Total_Employees ,2)

            logger.info(f"PUT data: {request.data}")
            employee = Employees.objects.get(id=id)
            serializer = EmployeesSerializer(employee, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                total_employees = calculate_total_employees()
                EmployeeSummary.objects.all().delete()
                for i in total_employees:
                    serializer = EmployeeSummarySerializer(data=i)
                    if serializer.is_valid():
                        serializer.save()
            
                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Edited information in table - Employees"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                # financial_year = request.data.get('Financial_Year', employee.Financial_Year)
                # facility = request.data.get('Facility', employee.Facility)
                # utils.save_employee_summary(financial_year, facility)
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            with transaction.atomic():  # Begin transaction
                employee = Employees.objects.get(id=id)

                # Delete related attachments
                attachments = Attachment.objects.filter(parent_type="Employees", parent_id=employee.id)
                for attachment in attachments:
                    if attachment.file:
                        attachment.file.delete(save=False)
                    attachment.delete()

                # Delete employee
                employee.delete()

            total_employees = calculate_total_employees()
            EmployeeSummary.objects.all().delete()
            for i in total_employees:
                serializer = EmployeeSummarySerializer(data=i)
                if serializer.is_valid():
                    serializer.save()

                activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Deleted information from table - Employees"}
                
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

            # utils.save_employee_summary(financial_year, facility)
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Differently_Abled_Employees_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            user_role = request.user.role
            location = request.user.location 
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            employees = Differently_Abled_Employees.objects.filter(Facility__in=location).order_by('-Financial_Year', '-id')
            serializer = Differently_Abled_EmployeesSerializer(employees)
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(employees, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = Differently_Abled_EmployeesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self,request):
        try:
            logger.info(f"POST data: {request.data}")

            # Get the count of existing objects
            if Differently_Abled_Employees.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Differently_Abled_Employees.objects.aggregate(Max('id'))['id__max'] + 1

            financial_year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            type = request.data.get('Type')
            gender = request.data.get('Gender')
            if Differently_Abled_Employees.objects.filter(Financial_Year=financial_year,Facility=facility,Type=type,Gender=gender).count() > 0:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Assign the new ID to the request data
            request.data['id'] = id

            Total_Differently_Abled_Employees = request.data.get('Differently_Abled_Employees_Apr', 0) + request.data.get('Differently_Abled_Employees_May', 0)  + request.data.get('Differently_Abled_Employees_Jun', 0) + request.data.get('Differently_Abled_Employees_Jul', 0) + request.data.get('Differently_Abled_Employees_Aug', 0) + request.data.get('Differently_Abled_Employees_Sep', 0) + request.data.get('Differently_Abled_Employees_Oct', 0) + request.data.get('Differently_Abled_Employees_Nov', 0) + request.data.get('Differently_Abled_Employees_Dec', 0) + request.data.get('Differently_Abled_Employees_Jan', 0) + request.data.get('Differently_Abled_Employees_Feb', 0) + request.data.get('Differently_Abled_Employees_Mar', 0)
            request.data["Total_Differently_Abled_Employees"] = round(Total_Differently_Abled_Employees ,2)

            serializer =  Differently_Abled_EmployeesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Differently_Abled_Employees"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'})
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            Total_Differently_Abled_Employees = request.data.get('Differently_Abled_Employees_Apr', 0) + request.data.get('Differently_Abled_Employees_May', 0)  + request.data.get('Differently_Abled_Employees_Jun', 0) + request.data.get('Differently_Abled_Employees_Jul', 0) + request.data.get('Differently_Abled_Employees_Aug', 0) + request.data.get('Differently_Abled_Employees_Sep', 0) + request.data.get('Differently_Abled_Employees_Oct', 0) + request.data.get('Differently_Abled_Employees_Nov', 0) + request.data.get('Differently_Abled_Employees_Dec', 0) + request.data.get('Differently_Abled_Employees_Jan', 0) + request.data.get('Differently_Abled_Employees_Feb', 0) + request.data.get('Differently_Abled_Employees_Mar', 0)
            request.data["Total_Differently_Abled_Employees"] = round(Total_Differently_Abled_Employees ,2)

            logger.info(f"PUT data: {request.data}")
            employee = Differently_Abled_Employees.objects.get(id=id)
            serializer = Differently_Abled_EmployeesSerializer(employee, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Edited information in table - Differently_Abled_Employees"}
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
            employee = Differently_Abled_Employees.objects.get(id=id)
            employee.delete()

            activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Differently_Abled_Employees"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()

            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Workers_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Human Resource" or user_role == "ESG Lead":

            electricity_consumption_mwh = Workers.objects.filter(Facility__in = user_location).order_by('-Financial_Year', '-id')
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(electricity_consumption_mwh, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = WorkersSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def post(self, request):
        try:
            financial_year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            type = request.data.get('Type')

            gender = request.data.get('Gender')
            is_exist = Workers.objects.filter(Financial_Year=financial_year, Facility=facility, Type=type, Gender=gender)

           
            if is_exist:
                return Response({'error': 'Entry for this Financial Year, Type and Facility already exists'}, status=status.HTTP_400_BAD_REQUEST)

            
            
            if Workers.objects.count() == 0:
                id = 1
            else:
                id = Workers.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            total_Differently_Abled_Workers = request.data.get('Differently_Abled_Workers_Apr', 0) + request.data.get('Differently_Abled_Workers_May', 0)  + request.data.get('Differently_Abled_Workers_Jun', 0) + request.data.get('Differently_Abled_Workers_Jul', 0) + request.data.get('Differently_Abled_Workers_Aug', 0) + request.data.get('Differently_Abled_Workers_Sep', 0) + request.data.get('Differently_Abled_Workers_Oct', 0) + request.data.get('Differently_Abled_Workers_Nov', 0) + request.data.get('Differently_Abled_Workers_Dec', 0) + request.data.get('Differently_Abled_Workers_Jan', 0) + request.data.get('Differently_Abled_Workers_Feb', 0) + request.data.get('Differently_Abled_Workers_Mar', 0)
            request.data["Total_Differently_Abled_Workers"] = round(total_Differently_Abled_Workers, 2)

            serializer =  WorkersSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                total_workers = calculate_total_workers()
                WorkerSummary.objects.all().delete()
                for i in total_workers:
                    serializer = WorkerSummarySerializer(data=i)
                    if serializer.is_valid():
                        serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Workers"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'})
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, id):
        try:
            Total_Differently_Abled_Workers = request.data.get('Differently_Abled_Workers_Apr', 0) + request.data.get('Differently_Abled_Workers_May', 0)  + request.data.get('Differently_Abled_Workers_Jun', 0) + request.data.get('Differently_Abled_Workers_Jul', 0) + request.data.get('Differently_Abled_Workers_Aug', 0) + request.data.get('Differently_Abled_Workers_Sep', 0) + request.data.get('Differently_Abled_Workers_Oct', 0) + request.data.get('Differently_Abled_Workers_Nov', 0) + request.data.get('Differently_Abled_Workers_Dec', 0) + request.data.get('Differently_Abled_Workers_Jan', 0) + request.data.get('Differently_Abled_Workers_Feb', 0) + request.data.get('Differently_Abled_Workers_Mar', 0)
            request.data["Total_Differently_Abled_Workers"] = round(Total_Differently_Abled_Workers ,2)

            logger.info(f"PUT data: {request.data}")
            employee = Workers.objects.get(id=id)
            serializer = WorkersSerializer(employee, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                total_workers = calculate_total_workers()
                WorkerSummary.objects.all().delete()
                for i in total_workers:
                    serializer = WorkerSummarySerializer(data=i)
                    if serializer.is_valid():
                        serializer.save()
                
                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Edited information in table - Workers"}
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
            # employee = Workers.objects.get(id=id)
            # employee.delete()

            with transaction.atomic():  # Begin transaction
                employee = Workers.objects.get(id=id)

                # Delete related attachments
                attachments = Attachment.objects.filter(parent_type="Workers", parent_id=employee.id)
                for attachment in attachments:
                    if attachment.file:
                        attachment.file.delete(save=False)
                    attachment.delete()

                # Delete employee
                employee.delete()

            total_workers = calculate_total_workers()
            WorkerSummary.objects.all().delete()
            for i in total_workers:
                serializer = WorkerSummarySerializer(data=i)
                if serializer.is_valid():
                    serializer.save()

            activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Workers"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()

            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class DifferentlyAbledWorkersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Human Resource" or user_role == "ESG Lead":

            differently_abled_workers = Differently_Abled_Workers.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(differently_abled_workers, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Differently_Abled_WorkersSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            financial_year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            type = request.data.get('Type')

            gender = request.data.get('Gender')
            is_exist = Differently_Abled_Workers.objects.filter(Financial_Year=financial_year, Facility=facility, Type=type, Gender=gender)

           
            if is_exist:
                return Response({'error': 'Entry for this Financial Year, Type and Facility already exists'}, status=status.HTTP_400_BAD_REQUEST)

            
            
            
            
            
            if Differently_Abled_Workers.objects.count() == 0:
                id = 1
            else:
                id = Differently_Abled_Workers.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            total_differently_abled_workers = sum([
                request.data.get(f'Differently_Abled_Workers_{month}', 0) for month in [
                    'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'
                ]
            ])
            request.data["Total_Differently_Abled_Workers"] = round(total_differently_abled_workers, 2)

            serializer = Differently_Abled_WorkersSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Differently_Abled_Workers"}
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
            total_differently_abled_workers = sum([
                request.data.get(f'Differently_Abled_Workers_{month}', 0) for month in [
                    'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'
                ]
            ])
            request.data["Total_Differently_Abled_Workers"] = round(total_differently_abled_workers, 2)

            logger.info(f"PUT data: {request.data}")
            employee = Differently_Abled_Workers.objects.get(id=id)
            serializer = Differently_Abled_WorkersSerializer(employee, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Edited information in table - Differently_Abled_Workers"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            employee = Differently_Abled_Workers.objects.get(id=id)
            employee.delete()
            activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Differently_Abled_Workers"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class BoardOfDirectorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":
            financial_year = request.query_params.get('financial_year', None)
            if financial_year:
                directors = Management_Board_of_Directors.objects.filter(Financial_Year=financial_year).order_by('-Financial_Year', '-id')
            else:
                directors = Management_Board_of_Directors.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(directors, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Management_Board_of_DirectorsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
            gender = request.data.get('Gender')
            count = Management_Board_of_Directors.objects.filter(Financial_Year=year,Gender=gender).count()
            if count > 0:
                return Response({'error':f'Entry for this Financial Year {year} and Gender {gender} already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            if Management_Board_of_Directors.objects.count() == 0:
                id = 1
            else:
                id = Management_Board_of_Directors.objects.aggregate(Max('id'))['id__max'] + 1
            request.data['id'] = id
            # Calculate the total number of board of directors
            total_board_of_directors = sum([
                request.data.get(f'Board_of_Directors_{month}', 0) for month in [
                    'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'
                ]
            ])
            request.data["Total_Board_of_Directors"] = round(total_board_of_directors, 2)
            serializer = Management_Board_of_DirectorsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Management_Board_of_Directors"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, id):
        try:
            total_board_of_directors = sum([
                request.data.get(f'Board_of_Directors_{month}', 0) for month in [
                    'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'
                ]
            ])
            request.data["Total_Board_of_Directors"] = round(total_board_of_directors, 2)

            logger.info(f"PUT data: {request.data}")
            director = Management_Board_of_Directors.objects.get(id=id)
            serializer = Management_Board_of_DirectorsSerializer(director, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Edited information in table - Management_Board_of_Directors"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            director = Management_Board_of_Directors.objects.get(id=id)
            director.delete()

            activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Management_Board_of_Directors"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()

            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class KeyManagementPersonnelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":
            financial_year = request.query_params.get('financial_year', None)
            if financial_year:
                personnel = Key_Management_Personnel.objects.filter(Financial_Year=financial_year).order_by('-Financial_Year', '-id')
            else:
                personnel = Key_Management_Personnel.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(personnel, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Key_Management_PersonnelSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
            gender = request.data.get("Gender")
            count = Key_Management_Personnel.objects.filter(Financial_Year=year,Gender=gender).count()
            if count > 0:
                return Response({'error':f'Entry for this Financial Year {year} and Gender {gender} already exists'}, status=status.HTTP_400_BAD_REQUEST)
            if Key_Management_Personnel.objects.count() == 0:
                id = 1
            else:
                id = Key_Management_Personnel.objects.aggregate(Max('id'))['id__max'] + 1
            request.data['id'] = id
            total_key_management_personnel = sum([
                request.data.get(f'Key_Management_Personnel_{month}', 0) for month in [
                    'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'
                ]
            ])
            request.data["Total_Key_Management_Personnel"] = round(total_key_management_personnel, 2)
            serializer = Key_Management_PersonnelSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Key_Management_Personnel"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            total_key_management_personnel = sum([
                request.data.get(f'Key_Management_Personnel_{month}', 0) for month in [
                    'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'
                ]
            ])
            request.data["Total_Key_Management_Personnel"] = round(total_key_management_personnel, 2)

            logger.info(f"PUT data: {request.data}")
            personnel = Key_Management_Personnel.objects.get(id=id)
            serializer = Key_Management_PersonnelSerializer(personnel, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Edited information in table - Key_Management_Personnel"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            personnel = Key_Management_Personnel.objects.get(id=id)
            personnel.delete()
            activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Key_Management_Personnel"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()

            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class TotalEmployees_View(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        print('request: ', request)
        try:
            user_role = request.user.role
            user_facility = request.user.location
            # if user_role == "Human Resource" or user_role == "ESG Lead":
            # Fetch all EmployeeSummary records, ordered by financial_year descending
            employees = EmployeeSummary.objects.filter(Facility__in = user_facility).order_by('-Financial_Year')

            # Pagination logic
            page_size = request.query_params.get('page_size', 5)
            page_number = request.query_params.get('page', 1)

            # Ensure page_size and page_number are integers
            try:
                page_size = int(page_size)
                page_number = int(page_number)
            except ValueError:
                return Response({'error': 'Invalid page size or page number'}, status=status.HTTP_400_BAD_REQUEST)

            paginator = Paginator(employees, page_size)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': 'Invalid page number'}, status=status.HTTP_400_BAD_REQUEST)

            # Serialize the paginated data
            serializer = EmployeeSummarySerializer(paginated_queryset, many=True)

            response_data = {
                'data': serializer.data,
                'page': page_number,
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
class TotalEmployees_Filter_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            production = EmployeeSummary.objects.filter(Facility=facility).order_by('-Financial_Year')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = EmployeeSummarySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Employees_Membership_In_Association_View(APIView):
    permission_classes = [IsAuthenticated]

    
    def get(self, request):
        try:
            user_role = request.user.role
            location =  request.user.location
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            personnel = Employees_Membership_In_Association_Or_Unions.objects.filter(Facility__in=location).order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(personnel, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Employees_Membership_In_AssociationSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            count = Employees_Membership_In_Association_Or_Unions.objects.filter(Financial_Year=year,Facility=facility).count()
            if count > 0:
                return Response({'error':'Entry for this Financial Year and Facility already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Employees_Membership_In_Association_Or_Unions.objects.count() == 0:
                id = 1
            else:
                id = Employees_Membership_In_Association_Or_Unions.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            # Extract data from request
            facility = request.data.get('Facility')
            financial_year = request.data.get('Financial_Year')
            permanent_males = request.data.get('Permanent_Males', 0)
            permanent_females = request.data.get('Permanent_Females', 0)

            percent_male_covered, percent_female_covered = calculate_employees_percent_covered(facility, financial_year, permanent_males, permanent_females)

            request.data["Male_Percentage_Covered"] = percent_male_covered
            request.data["Female_Percentage_Covered"] = percent_female_covered
 
            # Serialize and save the data
            serializer = Employees_Membership_In_AssociationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Employees_Membership_In_Association_Or_Unions"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)

            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:

                    # Extract data from request
                    facility = request.data.get('Facility')
                    financial_year = request.data.get('Financial_Year')
                    permanent_males = request.data.get('Permanent_Males', 0)
                    permanent_females = request.data.get('Permanent_Females', 0)

                    percent_male_covered, percent_female_covered = calculate_employees_percent_covered(facility, financial_year, permanent_males, permanent_females)
                    request.data["Male_Percentage_Covered"] = percent_male_covered
                    request.data["Female_Percentage_Covered"] = percent_female_covered

                    instance = Employees_Membership_In_Association_Or_Unions.objects.get(id=id)
                    serializer = Employees_Membership_In_AssociationSerializer(instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                            "Name": request.user.firstname + " " + request.user.lastname,
                            "Activity": "Edited information in table - Employees_Membership_In_Association_Or_Unions"}
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
        


    def delete(self, request, id):
        try:
            personnel = Employees_Membership_In_Association_Or_Unions.objects.get(id=id)
            personnel.delete()
            activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Employees_Membership_In_Association_Or_Unions"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Workers_Membership_In_Association_View(APIView):
    permission_classes = [IsAuthenticated]
     
    def get(self, request):
        try:
            
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Human Resource" or user_role == "ESG Lead":
            personnel = Workers_Membership_In_Association_Or_Unions.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(personnel, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Workers_Membership_In_Association_Or_UnionsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            count = Workers_Membership_In_Association_Or_Unions.objects.filter(Financial_Year=year,Facility=facility).count()
            if count > 0:
                return Response({'error':'Entry for this Financial Year and Facility already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Workers_Membership_In_Association_Or_Unions.objects.count() == 0:
                id = 1
            else:
                id = Workers_Membership_In_Association_Or_Unions.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            # Extract data from request
            facility = request.data.get('Facility')
            financial_year = request.data.get('Financial_Year')
            permanent_males = request.data.get('Permanent_Males', 0)
            permanent_females = request.data.get('Permanent_Females', 0)

            percent_male_covered, percent_female_covered = calculate_workers_percent_covered(facility, financial_year, permanent_males, permanent_females)

            request.data["Male_Percentage_Covered"] = percent_male_covered
            request.data["Female_Percentage_Covered"] = percent_female_covered

            serializer = Workers_Membership_In_Association_Or_UnionsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Workers_Membership_In_Association_Or_Unions"}
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

                    # Extract data from request
                    facility = request.data.get('Facility')
                    financial_year = request.data.get('Financial_Year')
                    permanent_males = request.data.get('Permanent_Males', 0)
                    permanent_females = request.data.get('Permanent_Females', 0)

                    percent_male_covered, percent_female_covered = calculate_workers_percent_covered(facility, financial_year, permanent_males, permanent_females)

                    request.data["Male_Percentage_Covered"] = percent_male_covered
                    request.data["Female_Percentage_Covered"] = percent_female_covered

                    reclaim_process_instance = Workers_Membership_In_Association_Or_Unions.objects.get(id=id)
                    serializer = Workers_Membership_In_Association_Or_UnionsSerializer(reclaim_process_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                            "Name": request.user.firstname + " " + request.user.lastname,
                            "Activity": "Edited information in table - Workers_Membership_In_Association_Or_Unions"}
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
    
    
    def delete(self, request, id):
        try:
            personnel = Workers_Membership_In_Association_Or_Unions.objects.get(id=id)
            personnel.delete()
            activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Workers_Membership_In_Association_Or_Unions"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class Wages_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:

            segment_list = SEGMENT

            if not segment_list:
                return Response({'error': 'Segment list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(segment_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Segment list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WagesPaidView(APIView):
    permission_classes = [IsAuthenticated]
     
    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":
            financial_year = request.query_params.get('financial_year', None)
            if financial_year:
                personnel = Wages_Paid.objects.filter(Financial_Year=financial_year).order_by('-Financial_Year', '-id')
            else:
                personnel = Wages_Paid.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(personnel, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Wages_PaidSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def post(self, request):
        try:
            # year = request.data.get('Financial_Year')
            # count = Wages_Paid.objects.filter(Financial_Year=year).count()
            # if count > 0:
            #     return Response({'message':'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)
            financial_year = request.data.get('Financial_Year')
            type = request.data.get('Type')
            segment = request.data.get('Segment')
            gender = request.data.get('Gender')
            # is_exist = Wages_Paid.objects.filter(Financial_Year=financial_year,  Type=type, Gender=gender,Segment=segment)
            is_exist = Wages_Paid.objects.filter(Financial_Year=financial_year,  Type=type,Segment=segment)

           
            if is_exist:
                return Response({'error': 'Entry for this Financial Year, Type and Segment already exists'}, status=status.HTTP_400_BAD_REQUEST)

                     
             
            if Wages_Paid.objects.count() == 0:
                id = 1
            else:
                id = Wages_Paid.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            financial_year = request.data.get('Financial_Year')
            segment = request.data.get('Segment')
            type = request.data.get('Type')
            Males_With_Equal_To_Minimum_Wages = request.data.get('Males_With_Equal_To_Minimum_Wages')
            Females_With_Equal_To_Minimum_Wages = request.data.get('Females_With_Equal_To_Minimum_Wages')
            Males_With_More_Than_Minimum_Wages = request.data.get('Males_With_More_Than_Minimum_Wages')
            Females_With_More_Than_Minimum_Wages = request.data.get('Females_With_More_Than_Minimum_Wages')

            Percent_Males_With_Equal_To_Minimum_Wages = calculate_percent_males(financial_year,segment,type,Males_With_Equal_To_Minimum_Wages)
            Percent_Females_With_Equal_To_Minimum_Wages = calculate_percent_females(financial_year,segment,type,Females_With_Equal_To_Minimum_Wages)
            Percent_Males_With_More_Than_Minimum_Wages = calculate_percent_males(financial_year,segment,type,Males_With_More_Than_Minimum_Wages)
            Percent_Females_With_More_Than_Minimum_Wages = calculate_percent_females(financial_year,segment,type,Females_With_More_Than_Minimum_Wages)

            request.data['Percent_Males_With_Equal_To_Minimum_Wages'] = Percent_Males_With_Equal_To_Minimum_Wages
            request.data['Percent_Females_With_Equal_To_Minimum_Wages'] = Percent_Females_With_Equal_To_Minimum_Wages
            request.data['Percent_Males_With_More_Than_Minimum_Wages'] = Percent_Males_With_More_Than_Minimum_Wages
            request.data['Percent_Females_With_More_Than_Minimum_Wages'] = Percent_Females_With_More_Than_Minimum_Wages

            serializer = Wages_PaidSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Wages_Paid"}
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

            financial_year = request.data.get('Financial_Year')
            segment = request.data.get('Segment')
            type = request.data.get('Type')
            Males_With_Equal_To_Minimum_Wages = request.data.get('Males_With_Equal_To_Minimum_Wages')
            Females_With_Equal_To_Minimum_Wages = request.data.get('Females_With_Equal_To_Minimum_Wages')
            Males_With_More_Than_Minimum_Wages = request.data.get('Males_With_More_Than_Minimum_Wages')
            Females_With_More_Than_Minimum_Wages = request.data.get('Females_With_More_Than_Minimum_Wages')

            Percent_Males_With_Equal_To_Minimum_Wages = calculate_percent_males(financial_year,segment,type,Males_With_Equal_To_Minimum_Wages)
            Percent_Females_With_Equal_To_Minimum_Wages = calculate_percent_females(financial_year,segment,type,Females_With_Equal_To_Minimum_Wages)
            Percent_Males_With_More_Than_Minimum_Wages = calculate_percent_males(financial_year,segment,type,Males_With_More_Than_Minimum_Wages)
            Percent_Females_With_More_Than_Minimum_Wages = calculate_percent_females(financial_year,segment,type,Females_With_More_Than_Minimum_Wages)

            request.data['Percent_Males_With_Equal_To_Minimum_Wages'] = Percent_Males_With_Equal_To_Minimum_Wages
            request.data['Percent_Females_With_Equal_To_Minimum_Wages'] = Percent_Females_With_Equal_To_Minimum_Wages
            request.data['Percent_Males_With_More_Than_Minimum_Wages'] = Percent_Males_With_More_Than_Minimum_Wages
            request.data['Percent_Females_With_More_Than_Minimum_Wages'] = Percent_Females_With_More_Than_Minimum_Wages


            wages = Wages_Paid.objects.get(id=id)
            serializer = Wages_PaidSerializer(wages, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Edited information in table - Wages_Paid"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request, id):
        try:
            personnel = Wages_Paid.objects.get(id=id)
            personnel.delete()

            activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Wages_Paid"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()

            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Median_Remuneration_Salary_WagesView(APIView):
    permission_classes = [IsAuthenticated]
     
    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":
            financial_year = request.query_params.get('financial_year', None)
            if financial_year:
                personnel = Median_Remuneration_Salary_Wages.objects.filter(Financial_Year=financial_year).order_by('-Financial_Year', '-id')
            else:
                personnel = Median_Remuneration_Salary_Wages.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(personnel, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Median_Remuneration_Salary_WagesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            personnel = Median_Remuneration_Salary_Wages.objects.get(id=id)
            personnel.delete()

            activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Median_Remuneration_Salary_Wages"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()

            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
    
    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
            count = Median_Remuneration_Salary_Wages.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error':'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Median_Remuneration_Salary_Wages.objects.count() == 0:
                id = 1
            else:
                id = Median_Remuneration_Salary_Wages.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            
            serializer = Median_Remuneration_Salary_WagesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Median_Remuneration_Salary_Wages"}
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
            director = Median_Remuneration_Salary_Wages.objects.get(id=id)
            serializer = Median_Remuneration_Salary_WagesSerializer(director, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Edited information in table - Median_Remuneration_Salary_Wages"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TotalWorkers_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            user_location = request.user.location
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            # Fetch all EmployeeSummary records, ordered by financial_year descending
            employees = WorkerSummary.objects.filter(Facility__in=user_location).order_by('-Financial_Year')

            # Pagination logic
            page_size = request.query_params.get('page_size', 5)
            page_number = request.query_params.get('page', 1)

            # Ensure page_size and page_number are integers
            try:
                page_size = int(page_size)
                page_number = int(page_number)
            except ValueError:
                return Response({'error': 'Invalid page size or page number'}, status=status.HTTP_400_BAD_REQUEST)

            paginator = Paginator(employees, page_size)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': 'Invalid page number'}, status=status.HTTP_400_BAD_REQUEST)

            # Serialize the paginated data
            serializer = WorkerSummarySerializer(paginated_queryset, many=True)

            response_data = {
                'data': serializer.data,
                'page': page_number,
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

class TotalWorkers_Filter_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            production = WorkerSummary.objects.filter(Facility=facility).order_by('-Financial_Year')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = WorkerSummarySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class Employees_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
   
    def get(self,request):
        try:
            
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            production = Employees.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = EmployeesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Differently_Abled_Employees_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
   
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            production = Differently_Abled_Employees.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Differently_Abled_EmployeesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Employees_Membership_In_Association_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
   
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('Facility')
            production = Employees_Membership_In_Association_Or_Unions.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Employees_Membership_In_AssociationSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Workers_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
   
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            production = Workers.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = WorkersSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Differently_Abled_Workers_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
   
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            production = Differently_Abled_Workers.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(production, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Differently_Abled_WorkersSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Workers_Membership_In_Association_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
   
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            workers = Workers_Membership_In_Association_Or_Unions.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(workers, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Workers_Membership_In_Association_Or_UnionsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
API's for Employee Turnover Rate
"""
# Function to convert Decimal128 to float
def convert_decimal128_to_float(value):
    if isinstance(value, Decimal128):
        return float(value.to_decimal())  
    elif isinstance(value, Decimal):
        return float(value)  
    return value  
class EmployeeTurnoverRateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            user_role = request.user.role
            location = request.user.location 
            facility = request.query_params.get('facility',None)
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            if facility:
                employees =  Employee_Turnover_Rate.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')
            else:
                employees =  Employee_Turnover_Rate.objects.filter(Facility__in=location).order_by('-Financial_Year', '-id')

            serializer = Employee_Turnover_RateSerializer(employees)
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(employees, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = Employee_Turnover_RateSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self,request):
        try:
            logger.info(f"POST data: {request.data}")

            financial_year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            type = request.data.get('Type')

            gender = request.data.get('Gender')
            is_exist = Employee_Turnover_Rate.objects.filter(Financial_Year=financial_year, Facility=facility, Type=type, Gender=gender)

           
            if is_exist:
                return Response({'error': 'Entry for this Financial Year, Type and Facility already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Employee_Turnover_Rate.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Employee_Turnover_Rate.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            Total_Employee_Turnover_Rate = request.data.get('Employee_Turnover_Rate_Apr', 0) + request.data.get('Employee_Turnover_Rate_May', 0)  + request.data.get('Employee_Turnover_Rate_Jun', 0) + request.data.get('Employee_Turnover_Rate_Jul', 0) + request.data.get('Employee_Turnover_Rate_Aug', 0) + request.data.get('Employee_Turnover_Rate_Sep', 0) + request.data.get('Employee_Turnover_Rate_Oct', 0) + request.data.get('Employee_Turnover_Rate_Nov', 0) + request.data.get('Employee_Turnover_Rate_Dec', 0) + request.data.get('Employee_Turnover_Rate_Jan', 0) + request.data.get('Employee_Turnover_Rate_Feb', 0) + request.data.get('Employee_Turnover_Rate_Mar', 0)
            request.data["Total_Employee_Turnover_Rate"] = round(Total_Employee_Turnover_Rate ,2)

            serializer =  Employee_Turnover_RateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Employee_Turnover_Rate"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'})
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            request.data["id"] = id
           
            Total_Employee_Turnover_Rate = request.data.get('Employee_Turnover_Rate_Apr', 0) + request.data.get('Employee_Turnover_Rate_May', 0)  + request.data.get('Employee_Turnover_Rate_Jun', 0) + request.data.get('Employee_Turnover_Rate_Jul', 0) + request.data.get('Employee_Turnover_Rate_Aug', 0) + request.data.get('Employee_Turnover_Rate_Sep', 0) + request.data.get('Employee_Turnover_Rate_Oct', 0) + request.data.get('Employee_Turnover_Rate_Nov', 0) + request.data.get('Employee_Turnover_Rate_Dec', 0) + request.data.get('Employee_Turnover_Rate_Jan', 0) + request.data.get('Employee_Turnover_Rate_Feb', 0) + request.data.get('Employee_Turnover_Rate_Mar', 0)
            request.data["Total_Employee_Turnover_Rate"] = round(Total_Employee_Turnover_Rate ,2)

            employee = Employee_Turnover_Rate.objects.get(id=id)
            serializer = Employee_Turnover_RateSerializer(employee, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Edited information in table - Employee_Turnover_Rate"}
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
            employee = Employee_Turnover_Rate.objects.get(id=id)
            employee.delete()

            activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Employee_Turnover_Rate"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()

            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




"""
API's for Workers Turnover Rate
"""
class WorkersTurnoverRateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            user_location = request.user.location
            facility =  request.query_params.get('facility',None)
            # if user_role == "Human Resource" or user_role == "ESG Lead":
            if facility:
                workers_turnover_rate = Workers_Turnover_Rate.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')
            else:
                workers_turnover_rate = Workers_Turnover_Rate.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(workers_turnover_rate, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Workers_Turnover_RateSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            financial_year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            type = request.data.get('Type')
            Gender = request.data.get('Gender')
            is_exist = Workers_Turnover_Rate.objects.filter(Financial_Year=financial_year, Facility=facility, Type=type, Gender=Gender)
            if is_exist:
                return Response({'error': 'Entry for this Financial Year, Type and Facility already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Workers_Turnover_Rate.objects.count() == 0:
                id = 1
            else:
                id = Workers_Turnover_Rate.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            total_Workers_Turnover_Rate = sum([
                request.data.get(f'Workers_Turnover_Rate_{month}', 0) for month in [
                    'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'
                ]
            ])
            request.data["Total_Workers_Turnover_Rate"] = round(total_Workers_Turnover_Rate, 2)

            serializer = Workers_Turnover_RateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Workers_Turnover_Rate"}
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
            request.data["id"] = id
            # financial_year = request.data.get('Financial_Year')
            # facility = request.data.get('Facility')
            # type = request.data.get('Type')
            # is_exist = Workers_Turnover_Rate.objects.filter(Financial_Year=financial_year, Facility=facility, Type=type).exclude(id=id)
            # if is_exist:
            #     return Response({'error': 'Entry for this Financial Year, Type and Facility already exists'}, status=status.HTTP_400_BAD_REQUEST)

            total_Workers_Turnover_Rate = sum([
                request.data.get(f'Workers_Turnover_Rate_{month}', 0) for month in [
                    'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'
                ]
            ])

            request.data["Total_Workers_Turnover_Rate"] = round(total_Workers_Turnover_Rate, 2)

            logger.info(f"PUT data: {request.data}")
            employee = Workers_Turnover_Rate.objects.get(id=id)
            serializer = Workers_Turnover_RateSerializer(employee, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Edited information in table - Workers_Turnover_Rate"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            employee = Workers_Turnover_Rate.objects.get(id=id)
            employee.delete()
            activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Workers_Turnover_Rate"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
API's for Gross Wages Paid
"""

class Gross_Wages_Paid_View(APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_classes = Gross_Wages_PaidSerializer

    def post(self, request):
        try:
            financial_year = request.data.get('Financial_Year')
            data = Gross_Wages_Paid.objects.filter(Financial_Year=financial_year)
            if data:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Gross_Wages_Paid.objects.count() == 0:
                id = 1
            else:
                id = Gross_Wages_Paid.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            serializer = self.serializer_classes(data=request.data)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Gross_Wages_Paid"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': f'Data added successfully.'}, status=201)
            else:
                for k in serializer.errors.keys():
                    if k in serializer.errors:
                        error_message = serializer.errors[k][0]
                    else:
                        error_message = 'Invalid data.'
                return Response({'error': error_message, 'is_success': 0}, status=400)
        except Exception as error:
            return Response({'error': str(error)}, status=500)
        

    def get(self, request, id=None):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":
            if id != None:
                data = Gross_Wages_Paid.objects.get(id = id)
                serializer = self.serializer_classes(data)
                response_data = {
                    'data': serializer.data,
                    'page': 1,
                    'total_pages': 1,
                    'count': 1,
                }

            else:
                data = Gross_Wages_Paid.objects.all().order_by('-Financial_Year', '-id')
                page_size = request.query_params.get('page_size', 5)
                paginator = Paginator(data, page_size)
                page_number = request.query_params.get('page', 1)

                try:
                    paginated_queryset = paginator.page(page_number)
                except EmptyPage:
                    return Response({'error': f'No data available on Page Number {page_number}'}, status=204)
                except PageNotAnInteger:
                    return Response({'error': f'Invalid Page Number {page_number}'}, status=400)
                
                serializer = self.serializer_classes(paginated_queryset, many=True)
                response_data = {
                    'data': serializer.data,
                    'page': int(page_number),
                    'total_pages': paginator.num_pages,
                    'count': paginator.count,
                }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e), 'is_success': 0}, status=400)
        
    def put(self, request, id=None):
        try:
            if id is not None:
                request.data['id'] = id
                try:
                    financial_year = request.data.get('Financial_Year')
                    data = Gross_Wages_Paid.objects.filter(Financial_Year=financial_year).exclude(id=id)
                    if data:
                        return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

                    data = Gross_Wages_Paid.objects.get(id=id)
                    serializer = self.serializer_classes(data, data=request.data)

                    if serializer.is_valid():
                        serializer.save()
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Gross_Wages_Paid"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()
                    
                        return Response({'success': 'Data updated successfully.'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Gross_Wages_Paid.DoesNotExist:

                    return Response({'error': 'ID not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def delete(self, request, id=None):
        try:
            if id is not None:
                try:
                    data = Gross_Wages_Paid.objects.get(id=id)
                    data.delete()
                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Gross_Wages_Paid"}

                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    
                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_200_OK)
                except Gross_Wages_Paid.DoesNotExist:
                    return Response({'message': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

"""
API's for Job creation in smaller town
"""

class Job_Creation_In_Smaller_Town_View(APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_classes = Job_Creation_In_Smaller_TownSerializer

    def post(self, request):
        try:
            financial_year = request.data.get('Financial_Year')
            data = Job_Creation_In_Smaller_Town.objects.filter(Financial_Year=financial_year)
            if data:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Job_Creation_In_Smaller_Town.objects.count() == 0:
                id = 1
            else:
                id = Job_Creation_In_Smaller_Town.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            serializer = self.serializer_classes(data=request.data)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Job_Creation_In_Smaller_Town"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': f'Data added successfully.'}, status=201)
            else:
                for k in serializer.errors.keys():
                    if k in serializer.errors:
                        error_message = serializer.errors[k][0]
                    else:
                        error_message = 'Invalid data.'
                return Response({'error': error_message, 'is_success': 0}, status=400)
        except Exception as error:
            return Response({'error': str(error)}, status=500)
        

    def get(self, request, id=None):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":
            if id != None:
                data = Job_Creation_In_Smaller_Town.objects.get(id = id)
                serializer = self.serializer_classes(data)
                response_data = {
                    'data': serializer.data,
                    'page': 1,
                    'total_pages': 1,
                    'count': 1,
                }

            else:
                data = Job_Creation_In_Smaller_Town.objects.all().order_by('-Financial_Year', '-id')
                page_size = request.query_params.get('page_size', 5)
                paginator = Paginator(data, page_size)
                page_number = request.query_params.get('page', 1)

                try:
                    paginated_queryset = paginator.page(page_number)
                except EmptyPage:
                    return Response({'error': f'No data available on Page Number {page_number}'}, status=204)
                except PageNotAnInteger:
                    return Response({'error': f'Invalid Page Number {page_number}'}, status=400)
                
                serializer = self.serializer_classes(paginated_queryset, many=True)
                response_data = {
                    'data': serializer.data,
                    'page': int(page_number),
                    'total_pages': paginator.num_pages,
                    'count': paginator.count,
                }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e), 'is_success': 0}, status=400)
        
    def put(self, request, id=None):
        try:
            if id is not None:
                request.data['id'] = id
                try:
                    financial_year = request.data.get('Financial_Year')
                    data = Job_Creation_In_Smaller_Town.objects.filter(Financial_Year=financial_year).exclude(id=id)
                    if data:
                        return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

                    data = Job_Creation_In_Smaller_Town.objects.get(id=id)
                    serializer = self.serializer_classes(data, data=request.data)

                    if serializer.is_valid():
                        serializer.save()
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Job_Creation_In_Smaller_Town"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()
                    
                        return Response({'success': 'Data updated successfully.'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Job_Creation_In_Smaller_Town.DoesNotExist:

                    return Response({'error': 'ID not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def delete(self, request, id=None):
        try:
            if id is not None:
                try:
                    data = Job_Creation_In_Smaller_Town.objects.get(id=id)
                    data.delete()
                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Job_Creation_In_Smaller_Town"}

                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    
                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_200_OK)
                except Job_Creation_In_Smaller_Town.DoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        









"""
views for traingin app
"""




class Ingeneral_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Human Resource" or user_role == "ESG Lead":

            ingeneral_data = Ingeneral.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(ingeneral_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = IngeneralSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            segment = request.data.get('Segment')

            count = Ingeneral.objects.filter(Financial_Year=year,Facility= facility,Segment=segment).count()
            if count > 0:
                return Response({'error':'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Ingeneral.objects.count() == 0:
                id = 1
            else:
                id = Ingeneral.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            Total_Ingeneral_Consumption = request.data.get('Ingeneral_Consumption_Apr', 0) + request.data.get('Ingeneral_Consumption_May', 0)  + request.data.get('Ingeneral_Consumption_Jun', 0) + request.data.get('Ingeneral_Consumption_Jul', 0) + request.data.get('Ingeneral_Consumption_Aug', 0) + request.data.get('Ingeneral_Consumption_Sep', 0) + request.data.get('Ingeneral_Consumption_Oct', 0) + request.data.get('Ingeneral_Consumption_Nov', 0) + request.data.get('Ingeneral_Consumption_Dec', 0) + request.data.get('Ingeneral_Consumption_Jan', 0) + request.data.get('Ingeneral_Consumption_Feb', 0) + request.data.get('Ingeneral_Consumption_Mar', 0)
            request.data["Total_Ingeneral_Consumption"] = round(Total_Ingeneral_Consumption ,2)
 
            serializer = IngeneralSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Ingeneral"}
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
                    Total_Ingeneral_Consumption = request.data.get('Ingeneral_Consumption_Apr', 0) + request.data.get('Ingeneral_Consumption_May', 0)  + request.data.get('Ingeneral_Consumption_Jun', 0) + request.data.get('Ingeneral_Consumption_Jul', 0) + request.data.get('Ingeneral_Consumption_Aug', 0) + request.data.get('Ingeneral_Consumption_Sep', 0) + request.data.get('Ingeneral_Consumption_Oct', 0) + request.data.get('Ingeneral_Consumption_Nov', 0) + request.data.get('Ingeneral_Consumption_Dec', 0) + request.data.get('Ingeneral_Consumption_Jan', 0) + request.data.get('Ingeneral_Consumption_Feb', 0) + request.data.get('Ingeneral_Consumption_Mar', 0)
                    request.data["Total_Ingeneral_Consumption"] = round(Total_Ingeneral_Consumption ,2)

            
                    assessment_by_external_agency_instance = Ingeneral.objects.get(id=id)
                    serializer = IngeneralSerializer(assessment_by_external_agency_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Ingeneral"}
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
                    assessment_by_external_agency = Ingeneral.objects.get(id=id)
                    assessment_by_external_agency.delete()

                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Deleted information in table - Ingeneral"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Ingeneral.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
   

class Segment_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            segment_list = SEGMENT

            if not segment_list:
                return Response({'error': 'Segment list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(segment_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Segment list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Ingeneral_Filter_View(APIView):
    permission_classes = [IsAuthenticated]

   
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            ingeneral_data = Ingeneral.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(ingeneral_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = IngeneralSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class On_Skill_Upgradation_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')

            ingeneral_data = On_Skill_Upgradation.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(ingeneral_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = OnSkillUpgradationSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class  On_Skill_Upgradation_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            On_Skill_Upgradation_data = On_Skill_Upgradation.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(On_Skill_Upgradation_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = OnSkillUpgradationSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            segment = request.data.get('Segment')

            count = On_Skill_Upgradation.objects.filter(Financial_Year=year,Facility= facility,Segment=segment).count()
            if count > 0:
                return Response({'error':'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if On_Skill_Upgradation.objects.count() == 0:
                id = 1
            else:
                id = On_Skill_Upgradation.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            no_of_male = request.data.get('No_Of_Male', 0)
            no_of_female = request.data.get('No_Of_Female', 0)
            total_male_and_female =  no_of_male + no_of_female
            if total_male_and_female > 0:
                percentage_of_male = round(((no_of_male / total_male_and_female) * 100),2) if total_male_and_female else 0
                percentage_of_female =round(((no_of_female / total_male_and_female) * 100),2) if total_male_and_female else 0
            else:
                percentage_of_male = 0
                percentage_of_female = 0

            request.data["Total_Male_And_Female"] = total_male_and_female 
            request.data["Percentage_Of_Male"] = percentage_of_male
            request.data["Percentage_Of_Female"] = percentage_of_female


            serializer = OnSkillUpgradationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Added information in table - On_Skill_Upgradation"}
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
                    no_of_male = request.data.get('No_Of_Male', 0)
                    no_of_female = request.data.get('No_Of_Female', 0)
                    total_male_and_female =  no_of_male + no_of_female
                    if total_male_and_female > 0:
                        percentage_of_male = round(((no_of_male / total_male_and_female) * 100),2) if total_male_and_female else 0
                        percentage_of_female = round(((no_of_female / total_male_and_female) * 100),2) if total_male_and_female else 0
                    else:
                        percentage_of_male = 0
                        percentage_of_female = 0

                    request.data["Total_Male_And_Female"] = total_male_and_female 
                    request.data["Percentage_Of_Male"] = percentage_of_male
                    request.data["Percentage_Of_Female"] = percentage_of_female

                    assessment_by_external_agency_instance = On_Skill_Upgradation.objects.get(id=id)
                    serializer = OnSkillUpgradationSerializer(assessment_by_external_agency_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        activity_log = {
                            "Name": request.user.firstname + " " + request.user.lastname,
                            "Activity": "Edited information in table - On_Skill_Upgradation"}
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
                    assessment_by_external_agency = On_Skill_Upgradation.objects.get(id=id)
                    assessment_by_external_agency.delete()

                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Deleted information in table - On_Skill_Upgradation"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Ingeneral.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


class Performance_And_Career_Reviews_View(APIView):
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            On_Skill_Upgradation_data = Performance_And_Career_Reviews.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(On_Skill_Upgradation_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = PerformanceAndCareerReviewsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            segment = request.data.get('Segment')
            count = Performance_And_Career_Reviews.objects.filter(Financial_Year=year,Facility= facility,Segment=segment).count()
            if count > 0:
                return Response({'error':'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Performance_And_Career_Reviews.objects.count() == 0:
                id = 1
            else:
                id = Performance_And_Career_Reviews.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            # import pdb;pdb.set_trace()
            no_of_male = request.data.get('No_Of_Male', 0)
            no_of_female = request.data.get('No_Of_Female', 0)
            total_male_and_female =  no_of_male + no_of_female
            if total_male_and_female > 0:
                percentage_of_male = round(((no_of_male / total_male_and_female) * 100),2) if total_male_and_female else 0
                percentage_of_female =round(((no_of_female / total_male_and_female) * 100),2) if total_male_and_female else 0
            else:
                percentage_of_male = 0
                percentage_of_female = 0

            request.data["Total_Male_And_Female"] = total_male_and_female 
            request.data["Percentage_Of_Male"] = percentage_of_male
            request.data["Percentage_Of_Female"] = percentage_of_female


            serializer = PerformanceAndCareerReviewsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Added information in table - Performance_And_Career_Reviews"}
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
                    no_of_male = request.data.get('No_Of_Male', 0)
                    no_of_female = request.data.get('No_Of_Female', 0)
                    total_male_and_female =  no_of_male + no_of_female
                    if total_male_and_female > 0:
                        percentage_of_male = round(((no_of_male / total_male_and_female) * 100),2) if total_male_and_female else 0
                        percentage_of_female =round(((no_of_female / total_male_and_female) * 100),2) if total_male_and_female else 0
                    else:
                        percentage_of_male = 0
                        percentage_of_female = 0

                    request.data["Total_Male_And_Female"] = total_male_and_female 
                    request.data["Percentage_Of_Male"] = percentage_of_male
                    request.data["Percentage_Of_Female"] = percentage_of_female

                    assessment_by_external_agency_instance = Performance_And_Career_Reviews.objects.get(id=id)
                    serializer = PerformanceAndCareerReviewsSerializer(assessment_by_external_agency_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Performance_And_Career_Reviews"}
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
                    assessment_by_external_agency = Performance_And_Career_Reviews.objects.get(id=id)
                    assessment_by_external_agency.delete()

                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                            "Activity": "Deleted information in table - Performance_And_Career_Reviews"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Ingeneral.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
   
class Performance_And_Career_Reviews_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            ingeneral_data = Performance_And_Career_Reviews.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(ingeneral_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = PerformanceAndCareerReviewsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Awareness_Programmes_On_ESG_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            awareness_programmes_on_esg_data = Awareness_Programmes_On_ESG.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(awareness_programmes_on_esg_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = AwarenessProgrammesOnESGSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Awareness_Programmes_On_ESG_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Human Resource" or user_role == "ESG Lead":
            awareness_programmes_on_esg_data = Awareness_Programmes_On_ESG.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(awareness_programmes_on_esg_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = AwarenessProgrammesOnESGSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            
            segment = request.data.get('Segment')

            count = Awareness_Programmes_On_ESG.objects.filter(Financial_Year=year,Segment = segment).count()
            if count > 0:
                return Response({'error':'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Awareness_Programmes_On_ESG.objects.count() == 0:
                id = 1
            else:
                id = Awareness_Programmes_On_ESG.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            Percentage_Of_Persons = float(request.data.get("Percentage_Of_Persons",0))
            request.data["Percentage_Of_Persons"] = round(Percentage_Of_Persons,2)

            serializer = AwarenessProgrammesOnESGSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Added information in table - Awareness_Programmes_On_ESG"}
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
                    Percentage_Of_Persons = float(request.data.get("Percentage_Of_Persons",0))
                    request.data["Percentage_Of_Persons"] = round(Percentage_Of_Persons,2)
            
                    awareness_programmes_on_esg_data = Awareness_Programmes_On_ESG.objects.get(id=id)
                    serializer = AwarenessProgrammesOnESGSerializer(awareness_programmes_on_esg_data, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Awareness_Programmes_On_ESG"}
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
                    awareness_programmes_on_esg_data = Awareness_Programmes_On_ESG.objects.get(id=id)
                    awareness_programmes_on_esg_data.delete()


                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Deleted information in table - Awareness_Programmes_On_ESG"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Ingeneral.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
   

class On_Health_And_Safety_Measures_View(APIView):
    permission_classes = [IsAuthenticated]
     
    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Human Resource" or user_role == "ESG Lead":

            on_health_and_safety_measures = On_Health_And_Safety_Measures.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(on_health_and_safety_measures, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = OnHealthAndSafetyMeasuresSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            segment = request.data.get('Segment')

            count = On_Health_And_Safety_Measures.objects.filter(Financial_Year=year,Facility= facility,Segment=segment).count()
            if count > 0:
                return Response({'error':'Entry for this Financial Year, Facility, Segment already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if On_Health_And_Safety_Measures.objects.count() == 0:
                id = 1
            else:
                id = On_Health_And_Safety_Measures.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            no_of_male = request.data.get('No_Of_Male', 0)
            no_of_female = request.data.get('No_Of_Female', 0)
            total_male_and_female =  no_of_male + no_of_female
            if total_male_and_female > 0:
                percentage_of_male = round(((no_of_male / total_male_and_female) * 100),2) if total_male_and_female else 0
                percentage_of_female =round(((no_of_female / total_male_and_female) * 100),2) if total_male_and_female else 0
            else:
                percentage_of_male = 0
                percentage_of_female = 0

            request.data["Total_Male_And_Female"] = total_male_and_female 
            request.data["Percentage_Of_Male"] = percentage_of_male
            request.data["Percentage_Of_Female"] = percentage_of_female


            serializer = OnHealthAndSafetyMeasuresSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Added information in table - On_Health_And_Safety_Measures"}
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
                    no_of_male = request.data.get('No_Of_Male', 0)
                    no_of_female = request.data.get('No_Of_Female', 0)
                    total_male_and_female =  no_of_male + no_of_female
                    if total_male_and_female > 0:
                        percentage_of_male = round(((no_of_male / total_male_and_female) * 100),2) if total_male_and_female else 0
                        percentage_of_female = round(((no_of_female / total_male_and_female) * 100),2) if total_male_and_female else 0
                    else:
                        percentage_of_male = 0
                        percentage_of_female = 0

                    request.data["Total_Male_And_Female"] = total_male_and_female 
                    request.data["Percentage_Of_Male"] = percentage_of_male
                    request.data["Percentage_Of_Female"] = percentage_of_female

                    assessment_by_external_agency_instance = On_Health_And_Safety_Measures.objects.get(id=id)
                    serializer = OnHealthAndSafetyMeasuresSerializer(assessment_by_external_agency_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - On_Health_And_Safety_Measures"}
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
                    on_health_and_safety_measures = On_Health_And_Safety_Measures.objects.get(id=id)
                    on_health_and_safety_measures.delete()

                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Deleted information in table - On_Health_And_Safety_Measures"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Ingeneral.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


class On_Health_And_Safety_Measures_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            on_health_and_safety_measures = On_Health_And_Safety_Measures.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(on_health_and_safety_measures, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = OnHealthAndSafetyMeasuresSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class On_Human_Rights_Issues_And_Policies_View(APIView):
    permission_classes = [IsAuthenticated]


    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Human Resource" or user_role == "ESG Lead":

            On_Human_Rights_Issues_And_Policies_data = On_Human_Rights_Issues_And_Policies.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(On_Human_Rights_Issues_And_Policies_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = OnHumanRightsIssuesAndPoliciesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def post(self, request):
        try:

            year = request.data.get('Financial_Year')
            facility = request.data.get("Facility")
            segment = request.data.get("Segment")
            
            count = On_Human_Rights_Issues_And_Policies.objects.filter(Financial_Year=year, Facility=facility , Segment = segment).count()
            if count > 0:
                return Response({'error':'Entry for this Financial Year, Facility, Segment already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if On_Human_Rights_Issues_And_Policies.objects.count() == 0:
                id = 1
            else:
                id = On_Human_Rights_Issues_And_Policies.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            employees_record = Employees.objects.filter(Financial_Year = year, Facility = facility)
            workers_record = Workers.objects.filter(Financial_Year = year, Facility = facility)

            total_employees = sum(float(record.Total_Employees.to_decimal()) for record in employees_record)
            total_workers = sum(float(record.Total_Differently_Abled_Workers.to_decimal()) for record in workers_record)

            Total_Employees_And_Workers = total_employees + total_workers
           
            Total_Permanent_Covered = request.data.get('Total_Permanent_Covered', 0)
            Total_Non_Permanent_Covered = request.data.get('Total_Non_Permanent_Covered', 0)

             
            if Total_Employees_And_Workers > 0:
                        Permanent_Covered_Percentage = round(((Total_Permanent_Covered / Total_Employees_And_Workers) * 100),2) if Total_Employees_And_Workers else 0
                        Non_Permanent_Covered_Percentage = round(((Total_Non_Permanent_Covered / Total_Employees_And_Workers) * 100),2) if Total_Employees_And_Workers else 0
            else:
                Permanent_Covered_Percentage = 0
                Non_Permanent_Covered_Percentage = 0

            request.data["Permanent_Covered_Percentage"] = Permanent_Covered_Percentage
            request.data["Non_Permanent_Covered_Percentage"] = Non_Permanent_Covered_Percentage

            
            serializer = OnHumanRightsIssuesAndPoliciesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Added information in table - On_Human_Rights_Issues_And_Policies"}
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
                    year = request.data.get('Financial_Year')
                    facility = request.data.get("Facility")
                    employees_record = Employees.objects.filter(Financial_Year = year, Facility = facility)
                    workers_record = Workers.objects.filter(Financial_Year = year, Facility = facility)

                    total_employees = sum(float(record.Total_Employees.to_decimal()) for record in employees_record)
                    total_workers = sum(float(record.Total_Differently_Abled_Workers.to_decimal()) for record in workers_record)

                    Total_Employees_And_Workers = total_employees + total_workers
                
                    Total_Permanent_Covered = request.data.get('Total_Permanent_Covered', 0)
                    Total_Non_Permanent_Covered = request.data.get('Total_Non_Permanent_Covered', 0)

                    
                    if Total_Employees_And_Workers > 0:
                                Permanent_Covered_Percentage = round(((Total_Permanent_Covered / Total_Employees_And_Workers) * 100),2) if Total_Employees_And_Workers else 0
                                Non_Permanent_Covered_Percentage = round(((Total_Non_Permanent_Covered / Total_Employees_And_Workers) * 100),2) if Total_Employees_And_Workers else 0
                    else:
                        Permanent_Covered_Percentage = 0
                        Non_Permanent_Covered_Percentage = 0

                    request.data["Permanent_Covered_Percentage"] = Permanent_Covered_Percentage
                    request.data["Non_Permanent_Covered_Percentage"] = Non_Permanent_Covered_Percentage


                    on_human_rights_issues_and_policies_data = On_Human_Rights_Issues_And_Policies.objects.get(id=id)
                    serializer = OnHumanRightsIssuesAndPoliciesSerializer(on_human_rights_issues_and_policies_data, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                                "Name": request.user.firstname + " " + request.user.lastname,
                                "Activity": "Edited information in table - On_Human_Rights_Issues_And_Policies"}
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
                    on_human_rights_issues_and_policies_data = On_Human_Rights_Issues_And_Policies.objects.get(id=id)
                    on_human_rights_issues_and_policies_data.delete()

                    activity_log = {
                            "Name": request.user.firstname + " " + request.user.lastname,
                            "Activity": "Deleted information in table - On_Human_Rights_Issues_And_Policies"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                        
                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Ingeneral.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


class On_Human_Rights_Issues_And_Policies_Filter(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')

            On_Human_Rights_Issues_And_Policies_data = On_Human_Rights_Issues_And_Policies .objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(On_Human_Rights_Issues_And_Policies_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = OnHumanRightsIssuesAndPoliciesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)










































class TypeList_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            type_list = TYPE

            if not type_list:
                return Response({'error': 'Type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(type_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class Segment_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            segment_list = SEGMENT

            if not segment_list:
                return Response({'error': 'Segment list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(segment_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Segment list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Percentage_Covered_In_Wellbeing_Measures_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            ingeneral_data = Percentage_Covered_In_Wellbeing_Measures.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(ingeneral_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = PercentageCoveredInWellbeingMeasuresSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            financial_year = request.data.get('Financial_Year')
            type = request.data.get('Type')
            segment = request.data.get('Segment')
            data = Percentage_Covered_In_Wellbeing_Measures.objects.filter(Financial_Year=financial_year, Type=type, Segment=segment)
            if data:
                return Response({'error': 'Entry for this Financial Year, Type, Segment already exists'}, status=status.HTTP_400_BAD_REQUEST)

            
            if Percentage_Covered_In_Wellbeing_Measures.objects.count() == 0:
                id = 1
            else:
                id = Percentage_Covered_In_Wellbeing_Measures.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            serializer = PercentageCoveredInWellbeingMeasuresSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Percentage_Covered_In_Wellbeing_Measures"}
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
                    financial_year = request.data.get('Financial_Year')
                    type = request.data.get('Type')
                    segment = request.data.get('Segment')
                    data = Percentage_Covered_In_Wellbeing_Measures.objects.filter(Financial_Year=financial_year, Type=type, Segment=segment).exclude(id=id)
                    if data:
                        return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

                    assessment_by_external_agency_instance = Percentage_Covered_In_Wellbeing_Measures.objects.get(id=id)
                    serializer = PercentageCoveredInWellbeingMeasuresSerializer(assessment_by_external_agency_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Percentage_Covered_In_Wellbeing_Measures"}
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
                    assessment_by_external_agency = Percentage_Covered_In_Wellbeing_Measures.objects.get(id=id)
                    assessment_by_external_agency.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Percentage_Covered_In_Wellbeing_Measures"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except PercentageCoveredInWellbeingMeasuresSerializer.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
   



class Percentage_Covered_In_Wellbeing_Measures_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
     
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            fy = request.query_params.get('financial_year')

            ingeneral_data = Percentage_Covered_In_Wellbeing_Measures.objects.filter(Financial_Year=fy).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(ingeneral_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = PercentageCoveredInWellbeingMeasuresSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Retirement_Benefits_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
     
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            fy = request.query_params.get('financial_year')
            retirement_benefits_data = Retirement_Benefits.objects.filter(Financial_Year=fy).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(retirement_benefits_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = RetirementBenefitsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Retirement_Benefits_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            retirement_benefits_data = Retirement_Benefits.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(retirement_benefits_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = RetirementBenefitsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            financial_year = request.data.get('Financial_Year')
            segment = request.data.get('Segment')
            data = Retirement_Benefits.objects.filter(Financial_Year=financial_year, Segment=segment)
            if data:
                return Response({'error': 'Entry for this Financial Year, Segment already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Retirement_Benefits.objects.count() == 0:
                id = 1
            else:
                id = Retirement_Benefits.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            serializer = RetirementBenefitsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Retirement_Benefits"}
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
                    financial_year = request.data.get('Financial_Year')
                    segment = request.data.get('Segment')
                    data = Retirement_Benefits.objects.filter(Financial_Year=financial_year, Segment=segment).exclude(id=id)
                    if data:
                        return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

                    retirement_benefits_data = Retirement_Benefits.objects.get(id=id)
                    serializer = RetirementBenefitsSerializer(retirement_benefits_data, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Retirement_Benefits"}
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
                    retirement_benefits_data = Retirement_Benefits.objects.get(id=id)
                    retirement_benefits_data.delete()
                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Retirement_Benefits"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except PercentageCoveredInWellbeingMeasuresSerializer.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
   
class Post_Paternal_Leave_For_Permanent_Employee_And_Worker_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
     
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            financial_year = request.query_params.get('financial_year')

            employee_and_workes_data = Post_Paternal_Leave_For_Permanent_Employee_And_Worker.objects.filter(Financial_Year=financial_year).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(employee_and_workes_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = PostPaternalLeaveForPermanentEmployeeAndWorkerSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Post_Paternal_Leave_For_Permanent_Employee_And_Worker_view(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            employee_and_worker_data = Post_Paternal_Leave_For_Permanent_Employee_And_Worker.objects.order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(employee_and_worker_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = PostPaternalLeaveForPermanentEmployeeAndWorkerSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:

            financial_year = request.data.get('Financial_Year')
            data = Post_Paternal_Leave_For_Permanent_Employee_And_Worker.objects.filter(Financial_Year=financial_year)
            if data:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Post_Paternal_Leave_For_Permanent_Employee_And_Worker.objects.count() == 0:
                id = 1
            else:
                id = Post_Paternal_Leave_For_Permanent_Employee_And_Worker.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            # Extract fields from request data
            male_return_to_work_employee = request.data.get('Return_To_Work_Rate_For_Male_Employee', 0) or 0
            female_return_to_work_employee = request.data.get('Return_To_Work_Rate_For_Female_Employee', 0) or 0
            male_retention_employee = request.data.get('Retention_Rate_For_Male_Employee', 0) or 0
            female_retention_employee = request.data.get('Retention_Rate_For_Female_Employee', 0) or 0

            male_return_to_work_workers = request.data.get('Return_To_Work_Rate_Male_Workers', 0) or 0
            female_return_to_work_workers = request.data.get('Return_To_Work_Rate_Female_Workers', 0) or 0
            male_retention_workers = request.data.get('Retention_Rate_For_Male_Workers', 0) or 0
            female_retention_workers = request.data.get('Retention_Rate_For_Female_Workers', 0) or 0

            # Perform calculations
            total_return_to_work_employee = (male_return_to_work_employee + female_return_to_work_employee) / 2 if (male_return_to_work_employee + female_return_to_work_employee) != 0 else 0
            total_retention_employee = (male_retention_employee + female_retention_employee) / 2 if (male_retention_employee + female_retention_employee) != 0 else 0
            total_return_to_work_workers = (male_return_to_work_workers + female_return_to_work_workers) / 2 if (male_return_to_work_workers + female_return_to_work_workers) != 0 else 0
            total_retention_workers = (male_retention_workers + female_retention_workers) / 2 if (male_retention_workers + female_retention_workers) != 0 else 0


            # Update request data with calculated fields
            request.data['Total_Return_To_Work_Rate_Employee'] = total_return_to_work_employee
            request.data['Total_Retention_Rate_Employee'] = total_retention_employee
            request.data['Total_Return_To_Work_Rate_Of_Workers'] = total_return_to_work_workers
            request.data['Total_Retention_Rate_Workers'] = total_retention_workers

            serializer = PostPaternalLeaveForPermanentEmployeeAndWorkerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Post_Paternal_Leave_For_Permanent_Employee_And_Worker"}
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

                    financial_year = request.data.get('Financial_Year')
                    data = Post_Paternal_Leave_For_Permanent_Employee_And_Worker.objects.filter(Financial_Year=financial_year).exclude(id=id)
                    if data:
                        return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

                    # Extract fields from request data
                    male_return_to_work_employee = request.data.get('Return_To_Work_Rate_For_Male_Employee', 0) or 0
                    female_return_to_work_employee = request.data.get('Return_To_Work_Rate_For_Female_Employee', 0) or 0
                    male_retention_employee = request.data.get('Retention_Rate_For_Male_Employee', 0) or 0
                    female_retention_employee = request.data.get('Retention_Rate_For_Female_Employee', 0) or 0

                    male_return_to_work_workers = request.data.get('Return_To_Work_Rate_Male_Workers', 0) or 0
                    female_return_to_work_workers = request.data.get('Return_To_Work_Rate_Female_Workers', 0) or 0
                    male_retention_workers = request.data.get('Retention_Rate_For_Male_Workers', 0) or 0
                    female_retention_workers = request.data.get('Retention_Rate_For_Female_Workers', 0) or 0

                    # Perform calculations
                    total_return_to_work_employee = male_return_to_work_employee + female_return_to_work_employee
                    total_retention_employee = male_retention_employee + female_retention_employee
                    total_return_to_work_workers = male_return_to_work_workers + female_return_to_work_workers
                    total_retention_workers = male_retention_workers + female_retention_workers

                    # Update request data with calculated fields
                    request.data['Total_Return_To_Work_Rate_Employee'] = total_return_to_work_employee
                    request.data['Total_Retention_Rate_Employee'] = total_retention_employee
                    request.data['Total_Return_To_Work_Rate_Of_Workers'] = total_return_to_work_workers
                    request.data['Total_Retention_Rate_Workers'] = total_retention_workers

                    retirement_benefits_data = Post_Paternal_Leave_For_Permanent_Employee_And_Worker.objects.get(id=id)
                    serializer = PostPaternalLeaveForPermanentEmployeeAndWorkerSerializer(retirement_benefits_data, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Post_Paternal_Leave_For_Permanent_Employee_And_Worker"}
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
                    employee_and_worker_data = Post_Paternal_Leave_For_Permanent_Employee_And_Worker.objects.get(id=id)
                    employee_and_worker_data.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Post_Paternal_Leave_For_Permanent_Employee_And_Worker"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except PostPaternalLeaveForPermanentEmployeeAndWorkerSerializer.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
   
class Lost_Time_Injury_Frequency_Rate_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Human Resource" or user_role == "ESG Lead":

            employee_and_worker_data = Lost_Time_Injury_Frequency_Rate.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(employee_and_worker_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = LostTimeInjuryFrequencyRateSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            segment = request.data.get('Segment')

            count = Lost_Time_Injury_Frequency_Rate.objects.filter(Financial_Year=year, Facility=facility,Segment=segment).count()
            if count > 0:
                return Response({'error':'Entry for this Financial Year, Facility, Segment already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Lost_Time_Injury_Frequency_Rate.objects.count() == 0:
                id = 1
            else:
                id = Lost_Time_Injury_Frequency_Rate.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            Total_Frequency_Rate = request.data.get('Frequency_Rate_Apr', 0) + request.data.get('Frequency_Rate_May', 0)  + request.data.get('Frequency_Rate_Jun', 0) + request.data.get('Frequency_Rate_Jul', 0) + request.data.get('Frequency_Rate_Aug', 0) + request.data.get('Frequency_Rate_Sep', 0) + request.data.get('Frequency_Rate_Oct', 0) + request.data.get('Frequency_Rate_Nov', 0) + request.data.get('Frequency_Rate_Dec', 0) + request.data.get('Frequency_Rate_Jan', 0) + request.data.get('Frequency_Rate_Feb', 0) + request.data.get('Frequency_Rate_Mar', 0)
            request.data["Total_Frequency_Rate"] = round(Total_Frequency_Rate ,2)
 
            serializer = LostTimeInjuryFrequencyRateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Lost_Time_Injury_Frequency_Rate"}
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
                   
                    Total_Frequency_Rate = request.data.get('Frequency_Rate_Apr', 0) + request.data.get('Frequency_Rate_May', 0)  + request.data.get('Frequency_Rate_Jun', 0) + request.data.get('Frequency_Rate_Jul', 0) + request.data.get('Frequency_Rate_Aug', 0) + request.data.get('Frequency_Rate_Sep', 0) + request.data.get('Frequency_Rate_Oct', 0) + request.data.get('Frequency_Rate_Nov', 0) + request.data.get('Frequency_Rate_Dec', 0) + request.data.get('Frequency_Rate_Jan', 0) + request.data.get('Frequency_Rate_Feb', 0) + request.data.get('Frequency_Rate_Mar', 0)
                    request.data["Total_Frequency_Rate"] = round(Total_Frequency_Rate ,2)
 
                    retirement_benefits_data = Lost_Time_Injury_Frequency_Rate.objects.get(id=id)
                    serializer = LostTimeInjuryFrequencyRateSerializer(retirement_benefits_data, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Lost_Time_Injury_Frequency_Rate"}
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
                    employee_and_worker_data = Lost_Time_Injury_Frequency_Rate.objects.get(id=id)
                    employee_and_worker_data.delete()
                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Lost_Time_Injury_Frequency_Rate"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except LostTimeInjuryFrequencyRateSerializer.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
   
class Lost_Time_Injury_Frequency_Rate_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
     
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')

            retirement_benefits_data = Lost_Time_Injury_Frequency_Rate.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(retirement_benefits_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = LostTimeInjuryFrequencyRateSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Total_Work_Related_Injuries_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Human Resource" or user_role == "ESG Lead":

            injuries_data = Total_Work_Related_Injuries.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(injuries_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = TotalWorkRelatedInjuriesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            segment = request.data.get('Segment')

            count = Total_Work_Related_Injuries.objects.filter(Financial_Year=year, Facility=facility,Segment=segment).count()
            if count > 0:
                return Response({'error':'Entry for this Financial Year, Facility, Segment Already Exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Total_Work_Related_Injuries.objects.count() == 0:
                id = 1
            else:
                id = Total_Work_Related_Injuries.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            Total_Injuries_Rate = (
                (request.data.get('Injuries_Rate_Apr') or 0) +
                (request.data.get('Injuries_Rate_May') or 0) +
                (request.data.get('Injuries_Rate_Jun') or 0) +
                (request.data.get('Injuries_Rate_Jul') or 0) +
                (request.data.get('Injuries_Rate_Aug') or 0) +
                (request.data.get('Injuries_Rate_Sep') or 0) +
                (request.data.get('Injuries_Rate_Oct') or 0) +
                (request.data.get('Injuries_Rate_Nov') or 0) +
                (request.data.get('Injuries_Rate_Dec') or 0) +
                (request.data.get('Injuries_Rate_Jan') or 0) +
                (request.data.get('Injuries_Rate_Feb') or 0) +
                (request.data.get('Injuries_Rate_Mar') or 0)
            )
            request.data["Total_Injuries_Rate"] = round(Total_Injuries_Rate, 2)

            serializer = TotalWorkRelatedInjuriesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Total_Work_Related_Injuries"}
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
            id = kwargs.get('id')
            if id is not None:
                try:
                    injuries_data = Total_Work_Related_Injuries.objects.get(id=id)

                    Total_Injuries_Rate = ((request.data.get('Injuries_Rate_Apr') or 0) +(request.data.get('Injuries_Rate_May') or 0) +(request.data.get('Injuries_Rate_Jun') or 0) +(request.data.get('Injuries_Rate_Jul') or 0) +(request.data.get('Injuries_Rate_Aug') or 0) + (request.data.get('Injuries_Rate_Sep') or 0) + (request.data.get('Injuries_Rate_Oct') or 0) + (request.data.get('Injuries_Rate_Nov') or 0) +(request.data.get('Injuries_Rate_Dec') or 0) +(request.data.get('Injuries_Rate_Jan') or 0) + (request.data.get('Injuries_Rate_Feb') or 0) + (request.data.get('Injuries_Rate_Mar') or 0)
                    )
                    request.data["Total_Injuries_Rate"] = round(Total_Injuries_Rate, 2)

                    serializer = TotalWorkRelatedInjuriesSerializer(injuries_data, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Total_Work_Related_Injuries"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()
                        return Response({'success': 'Data updated successfully.'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Total_Work_Related_Injuries.DoesNotExist:
                    return Response({'error': 'id not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    injuries_data = Total_Work_Related_Injuries.objects.get(id=id)
                    injuries_data.delete()
                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Total_Work_Related_Injuries"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Total_Work_Related_Injuries.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Total_Work_Related_Injuries_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')

            injuries_data = Total_Work_Related_Injuries.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(injuries_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = TotalWorkRelatedInjuriesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class No_Of_Fatalities_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Human Resource" or user_role == "ESG Lead":

            fatalities_data = No_Of_Fatalities.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(fatalities_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = NoOfFatalitiesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            segment = request.data.get('Segment')
            
            count = No_Of_Fatalities.objects.filter(Financial_Year=year, Facility=facility ,Segment = segment).count()
            if count > 0:
                return Response({'error': 'Entry for this Financial Year, Facility, Segment Already Exists'}, status=status.HTTP_400_BAD_REQUEST)

            if No_Of_Fatalities.objects.count() == 0:
                id = 1
            else:
                id = No_Of_Fatalities.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            Total_No_Of_Fatalities = (
                (request.data.get('No_Of_Fatalities_Apr') or 0) +
                (request.data.get('No_Of_Fatalities_May') or 0) +
                (request.data.get('No_Of_Fatalities_Jun') or 0) +
                (request.data.get('No_Of_Fatalities_Jul') or 0) +
                (request.data.get('No_Of_Fatalities_Aug') or 0) +
                (request.data.get('No_Of_Fatalities_Sep') or 0) +
                (request.data.get('No_Of_Fatalities_Oct') or 0) +
                (request.data.get('No_Of_Fatalities_Nov') or 0) +
                (request.data.get('No_Of_Fatalities_Dec') or 0) +
                (request.data.get('No_Of_Fatalities_Jan') or 0) +
                (request.data.get('No_Of_Fatalities_Feb') or 0) +
                (request.data.get('No_Of_Fatalities_Mar') or 0)
            )
            request.data["Total_No_Of_Fatalities"] = round(Total_No_Of_Fatalities, 2)

            serializer = NoOfFatalitiesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - No_Of_Fatalities"}
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
            id = kwargs.get('id')
            if id is not None:
                try:
                    fatalities_data = No_Of_Fatalities.objects.get(id=id)

                    Total_No_Of_Fatalities = (
                        (request.data.get('No_Of_Fatalities_Apr') or 0) +
                        (request.data.get('No_Of_Fatalities_May') or 0) +
                        (request.data.get('No_Of_Fatalities_Jun') or 0) +
                        (request.data.get('No_Of_Fatalities_Jul') or 0) +
                        (request.data.get('No_Of_Fatalities_Aug') or 0) +
                        (request.data.get('No_Of_Fatalities_Sep') or 0) +
                        (request.data.get('No_Of_Fatalities_Oct') or 0) +
                        (request.data.get('No_Of_Fatalities_Nov') or 0) +
                        (request.data.get('No_Of_Fatalities_Dec') or 0) +
                        (request.data.get('No_Of_Fatalities_Jan') or 0) +
                        (request.data.get('No_Of_Fatalities_Feb') or 0) +
                        (request.data.get('No_Of_Fatalities_Mar') or 0)
                    )
                    request.data["Total_No_Of_Fatalities"] = round(Total_No_Of_Fatalities, 2)

                    serializer = NoOfFatalitiesSerializer(fatalities_data, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - No_Of_Fatalities"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()
                        return Response({'success': 'Data updated successfully.'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except No_Of_Fatalities.DoesNotExist:
                    return Response({'error': 'id not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    fatalities_data = No_Of_Fatalities.objects.get(id=id)
                    fatalities_data.delete()
                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - No_Of_Fatalities"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    return Response({'success':'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except No_Of_Fatalities.DoesNotExist:
                    return Response({'error':'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class No_Of_Fatalities_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')

            fatalities_data = No_Of_Fatalities.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(fatalities_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = NoOfFatalitiesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Injury_Or_Ill_Health_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Human Resource" or user_role == "ESG Lead":

            injury_ill_health_data = Injury_Or_Ill_Health.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(injury_ill_health_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = InjuryOrIllHealthSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            segment = request.data.get('Segment')
            count = Injury_Or_Ill_Health.objects.filter(Financial_Year=year, Facility=facility , Segment = segment).count()
            if count > 0:
                return Response({'error': 'Entry for this Financial Year, Facility, Segment Already Exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Injury_Or_Ill_Health.objects.count() == 0:
                id = 1
            else:
                id = Injury_Or_Ill_Health.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            Total_Injury_Or_Ill_Health_Rate = (
                (request.data.get('Injury_Or_Ill_Health_Rate_Apr') or 0) +
                (request.data.get('Injury_Or_Ill_Health_Rate_May') or 0) +
                (request.data.get('Injury_Or_Ill_Health_Rate_Jun') or 0) +
                (request.data.get('Injury_Or_Ill_Health_Rate_Jul') or 0) +
                (request.data.get('Injury_Or_Ill_Health_Rate_Aug') or 0) +
                (request.data.get('Injury_Or_Ill_Health_Rate_Sep') or 0) +
                (request.data.get('Injury_Or_Ill_Health_Rate_Oct') or 0) +
                (request.data.get('Injury_Or_Ill_Health_Rate_Nov') or 0) +
                (request.data.get('Injury_Or_Ill_Health_Rate_Dec') or 0) +
                (request.data.get('Injury_Or_Ill_Health_Rate_Jan') or 0) +
                (request.data.get('Injury_Or_Ill_Health_Rate_Feb') or 0) +
                (request.data.get('Injury_Or_Ill_Health_Rate_Mar') or 0)
            )
            request.data["Total_Injury_Or_Ill_Health_Rate"] = round(Total_Injury_Or_Ill_Health_Rate, 2)

            serializer = InjuryOrIllHealthSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Injury_Or_Ill_Health"}
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
            id = kwargs.get('id')
            if id is not None:
                try:
                    injury_ill_health_data = Injury_Or_Ill_Health.objects.get(id=id)

                    Total_Injury_Or_Ill_Health_Rate = (
                        (request.data.get('Injury_Or_Ill_Health_Rate_Apr') or 0) +
                        (request.data.get('Injury_Or_Ill_Health_Rate_May') or 0) +
                        (request.data.get('Injury_Or_Ill_Health_Rate_Jun') or 0) +
                        (request.data.get('Injury_Or_Ill_Health_Rate_Jul') or 0) +
                        (request.data.get('Injury_Or_Ill_Health_Rate_Aug') or 0) +
                        (request.data.get('Injury_Or_Ill_Health_Rate_Sep') or 0) +
                        (request.data.get('Injury_Or_Ill_Health_Rate_Oct') or 0) +
                        (request.data.get('Injury_Or_Ill_Health_Rate_Nov') or 0) +
                        (request.data.get('Injury_Or_Ill_Health_Rate_Dec') or 0) +
                        (request.data.get('Injury_Or_Ill_Health_Rate_Jan') or 0) +
                        (request.data.get('Injury_Or_Ill_Health_Rate_Feb') or 0) +
                        (request.data.get('Injury_Or_Ill_Health_Rate_Mar') or 0)
                    )
                    request.data["Total_Injury_Or_Ill_Health_Rate"] = round(Total_Injury_Or_Ill_Health_Rate, 2)

                    serializer = InjuryOrIllHealthSerializer(injury_ill_health_data, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Injury_Or_Ill_Health"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()
                        return Response({'success': 'Data updated successfully.'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Injury_Or_Ill_Health.DoesNotExist:
                    return Response({'error': 'id not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    injury_ill_health_data = Injury_Or_Ill_Health.objects.get(id=id)
                    injury_ill_health_data.delete()
                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Injury_Or_Ill_Health"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except Injury_Or_Ill_Health.DoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Injury_Or_Ill_Health_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            injury_ill_health_data = Injury_Or_Ill_Health.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(injury_ill_health_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = InjuryOrIllHealthSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Suffered_High_Consequence_Work_Related_Injury_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            user_location = request.user.location

            # if user_role == "Human Resource" or user_role == "ESG Lead":
            data = Suffered_High_Consequence_Work_Related_Injury.objects.filter(Facility__in=user_location).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = SufferedHighConsequenceWorkRelatedInjurySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            count = Suffered_High_Consequence_Work_Related_Injury.objects.filter(Financial_Year=year, Facility=facility).count()
            if count > 0:
                return Response({'error': 'Entry for this Financial Year and Facility already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Suffered_High_Consequence_Work_Related_Injury.objects.count() == 0:
                id = 1
            else:
                id = Suffered_High_Consequence_Work_Related_Injury.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            serializer = SufferedHighConsequenceWorkRelatedInjurySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Suffered_High_Consequence_Work_Related_Injury"}
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
            id = kwargs.get('id')
            if id is not None:
                try:
                    data = Suffered_High_Consequence_Work_Related_Injury.objects.get(id=id)
                    serializer = SufferedHighConsequenceWorkRelatedInjurySerializer(data, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Suffered_High_Consequence_Work_Related_Injury"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully.'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Suffered_High_Consequence_Work_Related_Injury.DoesNotExist:
                    return Response({'error': 'id not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    data = Suffered_High_Consequence_Work_Related_Injury.objects.get(id=id)
                    data.delete()
                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Suffered_High_Consequence_Work_Related_Injury"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except Suffered_High_Consequence_Work_Related_Injury.DoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Suffered_High_Consequence_Work_Related_Injury_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            facility = request.query_params.get('facility')
            data = Suffered_High_Consequence_Work_Related_Injury.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = SufferedHighConsequenceWorkRelatedInjurySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Assessment_Of_Plants_And_Offices_Health_And_Safety_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            data = Assessment_Of_Plants_And_Offices_Health_And_Safety.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = AssessmentOfPlantsAndOfficesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
            count = Assessment_Of_Plants_And_Offices_Health_And_Safety.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Assessment_Of_Plants_And_Offices_Health_And_Safety.objects.count() == 0:
                id = 1
            else:
                id = Assessment_Of_Plants_And_Offices_Health_And_Safety.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            serializer = AssessmentOfPlantsAndOfficesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Assessment_Of_Plants_And_Offices"}
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
            id = kwargs.get('id')
            if id is not None:
                try:
                    data = Assessment_Of_Plants_And_Offices_Health_And_Safety.objects.get(id=id)
                    serializer = AssessmentOfPlantsAndOfficesSerializer(data, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Assessment_Of_Plants_And_Offices"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()
                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Assessment_Of_Plants_And_Offices_Health_And_Safety.DoesNotExist:
                    return Response({'error': 'ID not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    data = Assessment_Of_Plants_And_Offices_Health_And_Safety.objects.get(id=id)
                    data.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Assessment_Of_Plants_And_Offices"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except Assessment_Of_Plants_And_Offices_Health_And_Safety.DoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Assessment_Of_Value_Chain_Partners_Health_And_Safety_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            data = Assessment_Of_Value_Chain_Partners_Health_And_Safety.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = AssessmentOfValueChainPartnersSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
            count = Assessment_Of_Value_Chain_Partners_Health_And_Safety.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Assessment_Of_Value_Chain_Partners_Health_And_Safety.objects.count() == 0:
                id = 1
            else:
                id = Assessment_Of_Value_Chain_Partners_Health_And_Safety.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            serializer = AssessmentOfValueChainPartnersSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Assessment_Of_Value_Chain_Partners"}
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
            id = kwargs.get('id')
            if id is not None:
                try:
                    data = Assessment_Of_Value_Chain_Partners_Health_And_Safety.objects.get(id=id)
                    serializer = AssessmentOfValueChainPartnersSerializer(data, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Assessment_Of_Value_Chain_Partners"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()
                    
                        return Response({'success': 'Data updated successfully.'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Assessment_Of_Value_Chain_Partners_Health_And_Safety.DoesNotExist:
                    return Response({'error': 'ID not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    data = Assessment_Of_Value_Chain_Partners_Health_And_Safety.objects.get(id=id)
                    data.delete()
                    
                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Assessment_Of_Value_Chain_Partners"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    
                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except Assessment_Of_Value_Chain_Partners_Health_And_Safety.DoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Deposited_Deducted_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            list = DEDUCTED_AND_DEPOSITED
            if not list:
                return Response({'error': ' Deposited_Deducted list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)
            return Response(list, status=status.HTTP_200_OK)
        except NameError:
            return Response({'error': ' Deposited_Deducted list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





"""
API's for Receive and redress grievance mechanism
"""
class Receive_And_Redress_Grievance_Mechanism_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:

            data = Receive_And_Redress_Grievance_Mechanism.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Receive_And_Redress_Grievance_MechanismSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            financial_year = request.data.get('Financial_Year')
            facility = request.data.get('Facility')
            segment = request.data.get('Segment')
            data = Receive_And_Redress_Grievance_Mechanism.objects.filter(Financial_Year=financial_year, Facility=facility, Segment=segment)
            if data:
                return Response({'error': 'Entry for this Financial Year, Facility, Segment  already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Receive_And_Redress_Grievance_Mechanism.objects.count() == 0:
                id = 1
            else:
                id = Receive_And_Redress_Grievance_Mechanism.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            female = request.data.get('Female')
            male = request.data.get('Male')
            
            total = female / (male + female) * 100 if (male + female) else 0
            Percent_Of_Female_Employee_Divided_By_Worker = round(total, 2)

            request.data['Percent_Of_Female_Employee_Divided_By_Worker'] = Percent_Of_Female_Employee_Divided_By_Worker

            serializer = Receive_And_Redress_Grievance_MechanismSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Receive_And_Redress_Grievance_Mechanism"}
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
            id = kwargs.get('id')
            if id is not None:
                try:
                    financial_year = request.data.get('Financial_Year')
                    facility = request.data.get('Facility')
                    segment = request.data.get('Segment')
                    data = Receive_And_Redress_Grievance_Mechanism.objects.filter(Financial_Year=financial_year, Facility=facility, Segment=segment).exclude(id=id)
                    if data:
                        return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

                    request.data['id'] = id
                    data = Receive_And_Redress_Grievance_Mechanism.objects.get(id=id)

                    female = request.data.get('Female')
                    male = request.data.get('Male')
                    
                    total = female / (male + female) * 100 if (male + female) else 0
                    Percent_Of_Female_Employee_Divided_By_Worker = round(total, 2)

                    request.data['Percent_Of_Female_Employee_Divided_By_Worker'] = Percent_Of_Female_Employee_Divided_By_Worker

                    serializer = Receive_And_Redress_Grievance_MechanismSerializer(data, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Receive_And_Redress_Grievance_Mechanism"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()
                    
                        return Response({'success': 'Data updated successfully.'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Receive_And_Redress_Grievance_Mechanism.DoesNotExist:
                    return Response({'error': 'ID not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    data = Receive_And_Redress_Grievance_Mechanism.objects.get(id=id)
                    data.delete()
                    
                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Receive_And_Redress_Grievance_Mechanism"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    
                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except Receive_And_Redress_Grievance_Mechanism.DoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
        

class CostIncurredOnWellbeingMeasuresView(APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_classes = CostIncurredOnWellbeingMeasuresSerializer

    def post(self, request):
        try:
            financial_year = request.data.get('Financial_Year')
            data = CostIncurredOnWellbeingMeasures.objects.filter(Financial_Year=financial_year)
            if data:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if CostIncurredOnWellbeingMeasures.objects.count() == 0:
                id = 1
            else:
                id = CostIncurredOnWellbeingMeasures.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            serializer = self.serializer_classes(data=request.data)
            if serializer.is_valid():
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - CostIncurredOnWellbeingMeasures"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()
                return Response({'success': f'Data added successfully.', 'is_success': 1}, status=201)
            else:
                for k in serializer.errors.keys():
                    if k in serializer.errors:
                        error_message = serializer.errors[k][0]
                    else:
                        error_message = 'Invalid data.'
                return Response({'error': error_message, 'is_success': 0}, status=400)
        except Exception as error:
            return Response({'error': str(error)}, status=500)
        

    def get(self, request, id=None):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":
            if id != None:
                data = CostIncurredOnWellbeingMeasures.objects.get(id = id)
                serializer = self.serializer_classes(data)
                response_data = {
                    'data': serializer.data,
                    'page': 1,
                    'total_pages': 1,
                    'count': 1,
                }

            else:
                data = CostIncurredOnWellbeingMeasures.objects.all().order_by('-Financial_Year', '-id')
                page_size = request.query_params.get('page_size', 5)
                paginator = Paginator(data, page_size)
                page_number = request.query_params.get('page', 1)

                try:
                    paginated_queryset = paginator.page(page_number)
                except EmptyPage:
                    return Response({'error': f'No data available on Page Number {page_number}'}, status=204)
                except PageNotAnInteger:
                    return Response({'error': f'Invalid Page Number {page_number}'}, status=400)
                
                serializer = self.serializer_classes(paginated_queryset, many=True)
                response_data = {
                    'data': serializer.data,
                    'page': int(page_number),
                    'total_pages': paginator.num_pages,
                    'count': paginator.count,
                }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e), 'is_success': 0}, status=400)
        
    def put(self, request, id=None):
        try:
            if id is not None:
                try:
                    financial_year = request.data.get('Financial_Year')
                    data = CostIncurredOnWellbeingMeasures.objects.filter(Financial_Year=financial_year).exclude(id=id)
                    if data:
                        return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

                    data = CostIncurredOnWellbeingMeasures.objects.get(id=id)
                    serializer = self.serializer_classes(data, data=request.data)

                    if serializer.is_valid():
                        serializer.save()
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - CostIncurredOnWellbeingMeasures"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()
                    
                        return Response({'success': 'Data updated successfully.'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except CostIncurredOnWellbeingMeasures.DoesNotExist:

                    return Response({'error': 'ID not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def delete(self, request, id=None):
        try:
            if id is not None:
                try:
                    data = CostIncurredOnWellbeingMeasures.objects.get(id=id)
                    data.delete()
                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - CostIncurredOnWellbeingMeasures"}

                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    
                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except CostIncurredOnWellbeingMeasures.DoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




































"""
Graviences views
"""
class ComplaintHSTypeList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            complaint_HS = COMPLAINT_TYPE_OF_HEALTH_SAFETY

            if not complaint_HS :
                return Response({'error': 'Complaint Type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(complaint_HS, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Complaint Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class  Health_and_safety_related_complaints_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            Hscomplaint =  Health_and_safety_related_complaints.objects.all().order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(Hscomplaint, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = HealthandSafetyComplaintsSerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            financial_year = request.data.get('Financial_Year')
            complaint_type = request.data.get('Complaint_Type')
            
            # Check if an entry for this financial year already exists
            if Health_and_safety_related_complaints.objects.filter(Financial_Year=financial_year,Complaint_Type=complaint_type).count() > 0:
                return Response({'error': 'Entry for this Financial Year, Complaint Type  already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Health_and_safety_related_complaints.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Health_and_safety_related_complaints.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = HealthandSafetyComplaintsSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")
            Hscomplaint = Health_and_safety_related_complaints.objects.get(id=id)
            serializer = HealthandSafetyComplaintsSerializer(Hscomplaint, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            Hscomplaint = Health_and_safety_related_complaints.objects.get(id=id)
            Hscomplaint.delete()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


#################### Human_Rights_related_complaints
class ComplaintHRTypeList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            complaint_HR = COMPLAINT_TYPE_OF_HUMAN_RIGHTS

            if not complaint_HR :
                return Response({'error': 'Complaint Type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(complaint_HR, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Complaint Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Human_Rights_related_complaints_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            HRcomplaint = Human_Rights_related_complaints.objects.all().order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(HRcomplaint, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = HumanRightsComplaintsSerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            financial_year = request.data.get('Financial_Year')
            complaint_type = request.data.get('Complaint_Type')
            
            # Check if an entry for this financial year already exists
            if Human_Rights_related_complaints.objects.filter(Financial_Year=financial_year,Complaint_Type=complaint_type).count() > 0:
                return Response({'error': 'Entry for this Financial Year,  Complaint Type already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Human_Rights_related_complaints.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Human_Rights_related_complaints.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = HumanRightsComplaintsSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")
            HRcomplaint = Human_Rights_related_complaints.objects.get(id=id)
            serializer = HumanRightsComplaintsSerializer(HRcomplaint, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            HRcomplaint = Human_Rights_related_complaints.objects.get(id=id)
            HRcomplaint.delete()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   



###################Conflict_of_interest_complaints  


class SegmentConflictsList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            segment_conflicts = SEGMENT_OF_CONFLICTS

            if not segment_conflicts :
                return Response({'error': 'Segment list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(segment_conflicts, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Segment list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Conflict_of_interest_complaints_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            interest_complaint = Conflict_of_interest_complaints.objects.all().order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(interest_complaint, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ConflictsofInterestComplaintsSerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            financial_year = request.data.get('Financial_Year')
            segment = request.data.get('Segment')

            # Check if an entry for this financial year already exists
            if Conflict_of_interest_complaints.objects.filter(Financial_Year=financial_year,Segment=segment).count() > 0:
                return Response({'error': 'Entry for this Financial Year, Segment already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Conflict_of_interest_complaints.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Conflict_of_interest_complaints.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = ConflictsofInterestComplaintsSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")
            interest_complaint = Conflict_of_interest_complaints.objects.get(id=id)
            serializer = ConflictsofInterestComplaintsSerializer(interest_complaint, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            interest_complaint = Conflict_of_interest_complaints.objects.get(id=id)
            interest_complaint.delete()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
        


##################### Receive_and_redress_grievances_mechanism 
class TypeList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            type = TYPE

            if not type :
                return Response({'error': 'Type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(type, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SegmentReceiveRedressList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            segment_receive = SEGMENT_OF_RECEIVE_REDRESS

            if not segment_receive :
                return Response({'error': 'Segment list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(segment_receive, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Segment list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Receive_and_redress_grievances_mechanism_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            receive_redress = Receive_and_redress_grievances_mechanism.objects.all().order_by('-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(receive_redress, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ReceiveRedressGrievancesSerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            segment = request.data.get('Segment')
            
            type = request.data.get('Type')

            gender = request.data.get('Gender')
            is_exist = Receive_and_redress_grievances_mechanism.objects.filter(Segment=segment,Type=type)

           
            if is_exist:
                return Response({'error': 'Entry for this Segment and Type already exists'}, status=status.HTTP_400_BAD_REQUEST)

            
            
            
            logger.info(f"POST data: {request.data}")

            # Get the count of existing objects
            if Receive_and_redress_grievances_mechanism.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Receive_and_redress_grievances_mechanism.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Check if Yes_No field is "Yes"
            # if request.data.get('Yes_No') == "Yes":
            #     # Check if Description is present
            #     if 'Description' not in request.data or not request.data['Description']:
            #         logger.info('No need of Description')
            #         return Response({'error': 'Description is required when Yes_No is Yes'}, status=status.HTTP_400_BAD_REQUEST)  # Optionally, you can set Description to an empty string or handle it as you need.
            # else:
            #     # Remove Description if Yes_No is not "Yes"
            #     request.data.pop('Description', None)

            # Serialize the data
            serializer = ReceiveRedressGrievancesSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")
            receive_redress= Receive_and_redress_grievances_mechanism.objects.get(id=id)
            serializer = ReceiveRedressGrievancesSerializer(receive_redress, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': 'Data updated successfully'})
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            receive_redress = Receive_and_redress_grievances_mechanism.objects.get(id=id)
            receive_redress.delete()
            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   


"""
View for policy and penelty
"""

class Policy_Details_Health_Safety_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            descriptionshs = Policy_Details_Health_safety.objects.all().order_by('-id')

            page_size = request.query_params.get('page_size', 15)
            paginator = Paginator(descriptionshs, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
        
            serializer =Policy_Details_Health_safetySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def post(self, request):
        try:
            if isinstance(request.data, list):
                response_data = []
                all_success = True

                for entry in request.data:
                    
                    # Check the condition for Model_Name_Health_safety and Descriptions_Health_safety
                    if entry.get("Model_Name_Health_safety") in ["Event of death workers", "Event of Death employees"]:
                        if entry.get("Descriptions_Health_safety") is None:
                            entry["Descriptions_Health_safety"] = "Yes"


                    heading = entry.get('Heading')
                    exists = Policy_Details_Health_safety.objects.filter(Heading=heading).first()
                    
                    if exists:
                        serializer = Policy_Details_Health_safetySerializer(exists, data=entry, partial=True)
                    else:
                        # Get the next available ID
                        if Policy_Details_Health_safety.objects.count() == 0:
                            id = 1
                        else:
                            id = Policy_Details_Health_safety.objects.aggregate(Max('id'))['id__max'] + 1
                        entry['id'] = id  # Change request.data to entry
                        serializer = Policy_Details_Health_safetySerializer(data=entry)

                    if serializer.is_valid():
                        serializer.save()
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Added information in table - Policy_Details_Health_safetyfrom Activity_Log.serializers import ActivityLogSerializer"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()
                        response_data.append({'entry': serializer.data})
                    else:
                        response_data.append({'errors': serializer.errors, 'entry': entry})
                        all_success = False

                if all_success:
                    return Response(status=status.HTTP_201_CREATED)
                else:
                    return Response(response_data, status=status.HTTP_207_MULTI_STATUS)  # 207 for multi-status response

            else:
                
                for entry in request.data:
                    
                    # Check the condition for Model_Name_Health_safety and Descriptions_Health_safety
                    if entry.get("Model_Name_Health_safety") in ["Event of death workers", "Event of Death employees"]:
                        if entry.get("Descriptions_Health_safety") is None:
                            entry["Descriptions_Health_safety"] = "Yes"


                heading = request.data.get('Heading')
                exists =Policy_Details_Health_safety.objects.filter(Heading=heading).first()
                
                if exists:
                    serializer = Policy_Details_Health_safetySerializer(exists, data=request.data, partial=True)
                else:
                    # Get the next available ID
                    if Policy_Details_Health_safety.objects.count() == 0:
                        id = 1
                    else:
                        id = Policy_Details_Health_safety.objects.aggregate(Max('id'))['id__max'] + 1
                    request.data['id'] = id
                    serializer =Policy_Details_Health_safetySerializer(data=request.data)

                if serializer.is_valid():
                    serializer.save()
                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Edited information in table - Policy_Details_Health_safety"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    return Response({'entry': serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class Policy_Details_Human_Rights_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":
            descriptionshr = Policy_Details_Human_Rights.objects.all().order_by('-id')

            page_size = request.query_params.get('page_size', 15)
            paginator = Paginator(descriptionshr, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
        
            serializer = Policy_Details_Human_RightsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def post(self, request):
        try:
            if isinstance(request.data, list):
                response_data = []
                all_success = True

                for entry in request.data:
                    heading = entry.get('Heading')
                    exists = Policy_Details_Human_Rights.objects.filter(Heading=heading).first()
                    
                    if exists:
                        serializer = Policy_Details_Human_RightsSerializer(exists, data=entry, partial=True)
                    else:
                        # Get the next available ID
                        if Policy_Details_Human_Rights.objects.count() == 0:
                            id = 1
                        else:
                            id = Policy_Details_Human_Rights.objects.aggregate(Max('id'))['id__max'] + 1
                        entry['id'] = id
                        serializer = Policy_Details_Human_RightsSerializer(data=entry)

                    # Check Descriptions_Human_Rights for each entry
                    if entry.get("Descriptions_Human_Rights") == "No":
                        entry["Is_Verified"] = "No" # Set Is_Verified to "No"

                    if serializer.is_valid():
                        serializer.save()

                        # Log the activity
                        activity_log = {
                            "Name": request.user.firstname + " " + request.user.lastname,
                            "Activity": "Added information in table - Policy_Details_Human_Rights"
                        }
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        response_data.append({'entry': serializer.data})
                    else:
                        response_data.append({'errors': serializer.errors, 'entry': entry})
                        all_success = False

                if all_success:
                    return Response(status=status.HTTP_201_CREATED)
                else:
                    return Response(response_data, status=status.HTTP_207_MULTI_STATUS)

            else:
                heading = request.data.get('Heading')
                exists = Policy_Details_Human_Rights.objects.filter(Heading=heading).first()
                
                if exists:
                    serializer = Policy_Details_Human_RightsSerializer(exists, data=request.data, partial=True)
                else:
                    # Get the next available ID
                    if Policy_Details_Human_Rights.objects.count() == 0:
                        id = 1
                    else:
                        id = Policy_Details_Human_Rights.objects.aggregate(Max('id'))['id__max'] + 1
                    request.data['id'] = id
                    serializer = Policy_Details_Human_RightsSerializer(data=request.data)

                # Check Descriptions_Human_Rights for the single entry
                if request.data.get("Descriptions_Human_Rights") == "No":
                    request.data["Is_Verified"] = "No"  # Set Is_Verified to "No"

                if serializer.is_valid():
                    serializer.save()

                    # Log the activity
                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Policy_Details_Human_Rights"
                    }
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'entry': serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Policy_Details_Penalty_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            penalty = Policy_Details_Penalty.objects.all().order_by('id')
            page_size = request.query_params.get('page_size', 15)
            paginator = Paginator(penalty, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
        
            serializer = Policy_Details_PenaltySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def post(self, request):
        try:
            if isinstance(request.data, list):
                # Validate all records first
                for entry in request.data:
                    is_verified = entry.get('Is_Verified')
                    descriptions_penalty = entry.get('Descriptions_Penalty')

                    if is_verified == 'Yes' and (not descriptions_penalty or descriptions_penalty.strip() == ""):
                        raise ValidationError("Descriptions_Penalty is mandatory and cannot be empty or spaces when Is_Verified is 'Yes'.")

                # If all records are valid, process them
                response_data = []
                all_success = True

                for entry in request.data:
                    heading = entry.get('Heading')
                    exists = Policy_Details_Penalty.objects.filter(Heading=heading).first()

                    if exists:
                        serializer = Policy_Details_PenaltySerializer(exists, data=entry, partial=True)
                    else:
                        # Get the next available ID
                        if Policy_Details_Penalty.objects.count() == 0:
                            id = 1
                        else:
                            id = Policy_Details_Penalty.objects.aggregate(Max('id'))['id__max'] + 1
                        entry['id'] = id
                        serializer = Policy_Details_PenaltySerializer(data=entry)

                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                            "Name": request.user.firstname + " " + request.user.lastname,
                            "Activity": "Added information in table - Policy_Details_Penalty"
                        }
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        response_data.append({'entry': serializer.data})
                    else:
                        response_data.append({'errors': serializer.errors, 'entry': entry})
                        all_success = False

                if all_success:
                    return Response(status=status.HTTP_201_CREATED)
                else:
                    return Response(response_data, status=status.HTTP_207_MULTI_STATUS)

            else:
                # Single entry processing
                is_verified = request.data.get('Is_Verified')
                descriptions_penalty = request.data.get('Descriptions_Penalty')

                if is_verified == 'Yes' and (not descriptions_penalty or descriptions_penalty.strip() == ""):
                    raise ValidationError("Descriptions_Penalty is mandatory and cannot be empty or spaces when Is_Verified is 'Yes'.")

                
                heading = request.data.get('Heading')
                exists = Policy_Details_Penalty.objects.filter(Heading=heading).first()

                if exists:
                    serializer = Policy_Details_PenaltySerializer(exists, data=request.data, partial=True)
                else:
                    # Get the next available ID
                    if Policy_Details_Penalty.objects.count() == 0:
                        id = 1
                    else:
                        id = Policy_Details_Penalty.objects.aggregate(Max('id'))['id__max'] + 1
                    request.data['id'] = id
                    serializer = Policy_Details_PenaltySerializer(data=request.data)

                if serializer.is_valid():
                    serializer.save()

                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Policy_Details_Penalty"
                    }
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'entry': serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class  Assessment_of_plants_and_offices_Policies_and_Penalties_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":
            assessment_plants =  Assessment_of_plants_and_offices_Policies_and_Penalties.objects.all().order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(assessment_plants, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Assessment_of_plants_and_officesSerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            financial_year = request.data.get('Financial_Year')
            
            # Check if an entry for this financial year already exists
            if Assessment_of_plants_and_offices_Policies_and_Penalties.objects.filter(Financial_Year=financial_year).count() > 0:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Assessment_of_plants_and_offices_Policies_and_Penalties.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Assessment_of_plants_and_offices_Policies_and_Penalties.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = Assessment_of_plants_and_officesSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table -  Assessment_of_plants_and_offices"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")
            assessment_plants = Assessment_of_plants_and_offices_Policies_and_Penalties.objects.get(id=id)
            serializer = Assessment_of_plants_and_officesSerializer(assessment_plants, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()


                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table -  Assessment_of_plants_and_offices"}
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
            assessment_plants = Assessment_of_plants_and_offices_Policies_and_Penalties.objects.get(id=id)
            assessment_plants.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table -  Assessment_of_plants_and_offices"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()

            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class  Assessment_of_value_chain_partners_Policies_and_Penalties_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            assessment_value =  Assessment_of_value_chain_partners_Policies_and_Penalties.objects.all().order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(assessment_value, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Assessment_of_value_chain_partnersSerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            financial_year = request.data.get('Financial_Year')
            
            # Check if an entry for this financial year already exists
            if Assessment_of_value_chain_partners_Policies_and_Penalties.objects.filter(Financial_Year=financial_year).count() > 0:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Assessment_of_value_chain_partners_Policies_and_Penalties.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Assessment_of_value_chain_partners_Policies_and_Penalties.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = Assessment_of_value_chain_partnersSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()
                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Assessment_of_value_chain_partners"}
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
            assessment_value = Assessment_of_value_chain_partners_Policies_and_Penalties.objects.get(id=id)
            serializer = Assessment_of_value_chain_partnersSerializer(assessment_value, data=request.data, partial=True) 

            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Assessment_of_value_chain_partners"}
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
            assessment_value = Assessment_of_value_chain_partners_Policies_and_Penalties.objects.get(id=id)
            assessment_value.delete()

            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Assessment_of_value_chain_partners"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()

            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
##################################################################################################
class MonetaryTypeList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            monetary_list = MONETARY_TYPE

            if not monetary_list :
                return Response({'error': 'Monetary Type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(monetary_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Monetary Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OptionsList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            options_list = HAS_AN_APPEAL_BEEN_PREFFERED

            if not options_list : 
                return Response({'error': 'list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(options_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class  Penalty_Monetary_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            financial_year = request.query_params.get('financial_year', None)
            
            filters = {}
            if financial_year:
                filters['Financial_Year'] = financial_year
        
            monetary = Penalty_Monetary.objects.filter(**filters).order_by('-Financial_Year', '-id')
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(monetary, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Penalty_MonetarySerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            financial_year = request.data.get('Financial_Year')
            type = request.data.get("Monetary_Type")
            
            
            # Check if an entry for this financial year already exists
            if Penalty_Monetary.objects.filter(Financial_Year=financial_year,Monetary_Type=type).count() > 0:
                return Response({'error': 'Entry for this Financial Year, Monetary Type  already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Penalty_Monetary.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Penalty_Monetary.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = Penalty_MonetarySerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Penalty_Monetary"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")
            monetary = Penalty_Monetary.objects.get(id=id)
            serializer = Penalty_MonetarySerializer(monetary, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Penalty_Monetary"}
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
            monetary = Penalty_Monetary.objects.get(id=id)
            monetary.delete()
            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Penalty_Monetary"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()

            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)       
        

class Non_MonetaryTypeList_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            non_monetary_list = NON_MONETARY_TYPE

            if not non_monetary_list :
                return Response({'error': 'Non_Monetary Type list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(non_monetary_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Non_Monetary Type list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class  Penalty_Non_Monetary_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":
            financial_year = request.query_params.get('financial_year', None)
            
            filters = {}
            if financial_year:
                filters['Financial_Year'] = financial_year
            
            non_monetary = Penalty_Non_Monetary.objects.filter(**filters).order_by('-Financial_Year', '-id')
            
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(non_monetary, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Penalty_Non_MonetarySerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            financial_year = request.data.get('Financial_Year')
            non_monetary_type = request.data.get("Non_Monetary_Type")
            
            # Check if an entry for this financial year already exists
            if Penalty_Non_Monetary.objects.filter(Financial_Year=financial_year,Non_Monetary_Type=non_monetary_type).count() > 0:
                return Response({'error': 'Entry for this Financial Year, Type  already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Penalty_Non_Monetary.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Penalty_Non_Monetary.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = Penalty_Non_MonetarySerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Penalty_Non_Monetary"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")
            non_monetary = Penalty_Non_Monetary.objects.get(id=id)
            serializer = Penalty_Non_MonetarySerializer(non_monetary, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()


                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Penalty_Non_Monetary"}
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
            non_monetary = Penalty_Non_Monetary.objects.get(id=id)
            non_monetary.delete()

            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Penalty_Non_Monetary"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()

            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)               
        

######################################################################################
class Details_of_the_appeal_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            appeal =  Details_of_the_appeal.objects.all().order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(appeal, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Details_of_the_appealSerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            financial_year = request.data.get('Financial_Year')
            
            
            # Check if an entry for this financial year already exists

            if Details_of_the_appeal.objects.filter(Financial_Year=financial_year).count()> 0:

                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects
            if Details_of_the_appeal.objects.count() == 0:
                id = 1
            else:
                # Get the maximum current ID and increment it by 1
                id = Details_of_the_appeal.objects.aggregate(Max('id'))['id__max'] + 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = Details_of_the_appealSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Details_of_the_appeal"}
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
            appeal = Details_of_the_appeal.objects.get(id=id)
            serializer = Details_of_the_appealSerializer(appeal, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Details_of_the_appeal"}
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
            appeal = Details_of_the_appeal.objects.get(id=id)
            appeal.delete()

            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Details_of_the_appeal"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()
                

            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   

###################################################################################################


class Disciplinary_Action_Against_For_curruption_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            curruption =  Disciplinary_Action_Against_For_curruption.objects.all().order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(curruption, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Disciplinary_Action_Against_For_curruptionSerializer(paginated_queryset,many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"POST data: {request.data}")

            # Retrieve the financial year from the request data
            financial_year = request.data.get('Financial_Year')

            # Check if an entry for this financial year already exists
            if Disciplinary_Action_Against_For_curruption.objects.filter(Financial_Year=financial_year).count() > 0:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the count of existing objects and set a new ID
            max_id = Disciplinary_Action_Against_For_curruption.objects.aggregate(Max('id'))['id__max']
            id = max_id + 1 if max_id is not None else 1

            # Assign the new ID to the request data
            request.data['id'] = id

            # Serialize the data
            serializer = Disciplinary_Action_Against_For_curruptionSerializer(data=request.data)
            if serializer.is_valid():
                # Save the serialized data
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Disciplinary_Action_Against_For_curruption"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        try:
            logger.info(f"PUT data: {request.data}")
            curruption = Disciplinary_Action_Against_For_curruption.objects.get(id=id)
            serializer = Disciplinary_Action_Against_For_curruptionSerializer(curruption, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Edited information in table - Disciplinary_Action_Against_For_curruption"}
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
            curruption = Disciplinary_Action_Against_For_curruption.objects.get(id=id)
            curruption.delete()

            activity_log = {
            "Name": request.user.firstname + " " + request.user.lastname,
            "Activity": "Deleted information in table - Disciplinary_Action_Against_For_curruption"}
            activity_log_serializer = ActivityLogSerializer(data=activity_log)
            if activity_log_serializer.is_valid():
                activity_log_serializer.save()

            return Response({'success': 'Data deleted successfully.'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   





class AttachmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parent_type = request.query_params.get("parent_type")
        parent_id = request.query_params.get("parent_id")

        if not parent_type or not parent_id:
            return Response(
                {"error": "parent_type and parent_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        attachments = Attachment.objects.filter(
            parent_type=parent_type,
            parent_id=int(parent_id)
        )

        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        parent_type = request.data.get("parent_type")
        parent_id = request.data.get("parent_id")

        if not parent_type or not parent_id:
            return Response(
                {"error": "parent_type and parent_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        files = request.FILES.getlist("file")
        if not files:
            return Response(
                {"error": "No files provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        created = []

        for file in files:
            # Auto increment ID
            if Attachment.objects.count() == 0:
                attachment_id = 1
            else:
                attachment_id = (
                    Attachment.objects.aggregate(Max("id"))["id__max"] + 1
                )

            attachment = Attachment.objects.create(
                id=attachment_id,
                parent_type=parent_type,
                parent_id=int(parent_id),
                file=file
            )

            created.append(AttachmentSerializer(attachment).data)

        return Response(
            {
                "success": f"{len(created)} files uploaded",
                "attachments": created
            },
            status=status.HTTP_201_CREATED
        )


    def delete(self, request, id):
        try:
            attachment = Attachment.objects.get(id=id)
            attachment.file.delete(save=False)  # delete file from storage
            attachment.delete()
            return Response(
                {"success": "Attachment deleted"},
                status=status.HTTP_200_OK
            )
        except Attachment.DoesNotExist:
            return Response(
                {"error": "Attachment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

