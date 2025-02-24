from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from datetime import datetime
import pytz

from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers import serialize
from .choices import *

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from .models import *
from .serializers import *
from Activity_Log.serializers import ActivityLogSerializer
import logging
logger = logging.getLogger(__name__)




class Brs_Policy1_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            brs = BRS_Policy_1.objects.all().order_by('-id')
            page_size = request.query_params.get('page_size', 15)
            paginator = Paginator(brs, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = BRSPolicy1Serializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ValidationError as e:
            logger.error(f"ValidationError: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError as e:
            logger.error(f"TypeError: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

    def post(self, request):
        try:
            if isinstance(request.data, list):
                all_success = True
                response_data = []
                delete_all_record = BRS_Policy_1.objects.all()
                delete_all_record.delete()
                for entry in request.data:
                    heading = entry.get('Heading')  # Get Heading from the entry
                    select_all = entry.get('Select_All')  # Get Select_All for processing

                    # Set P1 to P10 to 'Yes' if Select_All is 'Yes'
                    if select_all == 'Yes':
                        for i in range(1, 10):
                            entry[f'P{i}'] = 'Yes'

                                    # Handle the Description field if it's a list
                    if isinstance(entry.get('Description'), list):
                        unique_links = list(set(entry['Description']))  # Remove duplicates within the current entry

                        # Check for duplicate links in the database
                        existing_descriptions = BRS_Policy_1.objects.values_list('Description', flat=True)
                        existing_links = set()
                        for desc in existing_descriptions:
                            if desc:
                                existing_links.update(desc.split(', '))  # Collect existing links from all records

                        duplicates = [link for link in unique_links if link in existing_links]
                        if duplicates:
                            Response({'error': "link alreday exits"}, status=status.HTTP_400_BAD_REQUEST)

                            all_success = False
                            continue  # Skip to the next entry

                        entry['Description'] = ', '.join(unique_links)  # Join unique links for storage



                    # Check for an existing entry based on Heading
                    exists = BRS_Policy_1.objects.filter(Heading=heading).first()

                    if exists:
                        # Update existing entry
                        serializer = BRSPolicy1Serializer(exists, data=entry, partial=True)
                    else:
                        # Create new entry
                        #  id = User.objects.aggregate(Max('id'))['id__max'] + 1
                        max_id = BRS_Policy_1.objects.aggregate(Max('id'))['id__max'] 
                        entry['id'] = (max_id + 1) if max_id is not None else 1  # Set new ID for the entry
                        serializer = BRSPolicy1Serializer(data=entry)

                    if serializer.is_valid():
                        serializer.save()

                        # Log the activity
                        activity_log = {
                            "Name": f"{request.user.firstname} {request.user.lastname}",
                            "Activity": "Edited or added information in table - BRS_Policy_1"
                        }
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()
                    else:
                        all_success = False  # Set success to False if any serializer fails
                        response_data.append({'errors': serializer.errors})  # Capture errors

                # Return a single success message if all operations were successful
                if all_success:
                    return Response({'success': 'Data inserted and updated successfully'}, status=status.HTTP_201_CREATED)
                else:
                    return Response(response_data, status=status.HTTP_207_MULTI_STATUS)

            else:
                delete_all_record = BRS_Policy_1.objects.all()
                delete_all_record.delete()
                # Handle single request
                heading = request.data.get('Heading')  # Get Heading
                select_all = request.data.get('Select_All')  # Get Select_All

                # Set P1 to P10 to 'Yes' if Select_All is 'Yes'
                if select_all == 'Yes':
                    for i in range(1, 10):
                        request.data[f'P{i}'] = 'Yes'

                exists = BRS_Policy_1.objects.filter(Heading=heading).first()

                if exists:
                    serializer = BRSPolicy1Serializer(exists, data=request.data, partial=True)
                else:
                    # Create new entry
                    max_id = BRS_Policy_1.objects.aggregate(Max('id'))['id__max']
                    request.data['id'] = (max_id + 1) if max_id is not None else 1  # Set new ID for the entry
                    serializer = BRSPolicy1Serializer(data=request.data)

                if serializer.is_valid():
                    serializer.save()

                    # Log the activity
                    activity_log = {
                        "Name": f"{request.user.firstname} {request.user.lastname}",
                        "Activity": "Edited or added information in table - BRS_Policy_1"
                    }
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data inserted and updated successfully'}, status=status.HTTP_201_CREATED)  # Return only success message
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if serializer fails

        except TypeError as e:
            logger.error(f"TypeError: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    

class Brs_Policy1a_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            brs1 = BRS_Policy_1a.objects.all().order_by('-id')

            page_size = request.query_params.get('page_size', 15)
            paginator = Paginator(brs1, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
        
            serializer = BRSPolicy1aSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            logger.error(f"ValidationError: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError as e:
            logger.error(f"TypeError: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def post(self, request):
        try:
            if isinstance(request.data, list):
                all_success = True
                response_data = []
                delete_all_record = BRS_Policy_1a.objects.all()
                delete_all_record.delete()
                for entry in request.data:
                    heading = entry.get('Heading')  # Get Heading from the entry
                    select_all = entry.get('Select_All')  # Get Select_All for processing

                    # Set P1 to P10 to 'Yes' if Select_All is 'Yes'
                    if select_all == 'Yes':
                        for i in range(1, 10):
                            entry[f'P{i}'] = 'Yes'

                    # Handle the Description field if it's a list
                    if isinstance(entry.get('Description'), list):
                        entry['Description'] = ', '.join(entry['Description'])

                    # Check for an existing entry based on Heading
                    exists = BRS_Policy_1a.objects.filter(Heading=heading).first()

                    if exists:
                        # Update existing entry
                        serializer = BRSPolicy1aSerializer(exists, data=entry, partial=True)
                    else:
                        # Create new entry
                        max_id = BRS_Policy_1a.objects.aggregate(Max('id'))['id__max']
                        entry['id'] = (max_id + 1) if max_id is not None else 1  # Set new ID for the entry
                        serializer = BRSPolicy1aSerializer(data=entry)

                    if serializer.is_valid():
                        serializer.save()

                        # Log the activity
                        activity_log = {
                            "Name": f"{request.user.firstname} {request.user.lastname}",
                            "Activity": "Edited or added information in table - BRS_Policy_1"
                        }
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()
                    else:
                        all_success = False  # Set success to False if any serializer fails
                        response_data.append({'errors': serializer.errors})  # Capture errors

                # Return a single success message if all operations were successful
                if all_success:
                    return Response({'success': 'Data inserted and updated successfully'}, status=status.HTTP_201_CREATED)
                else:
                    return Response(response_data, status=status.HTTP_207_MULTI_STATUS)

            else:
                delete_all_record = BRS_Policy_1a.objects.all()
                delete_all_record.delete()
                # Handle single request
                heading = request.data.get('Heading')  # Get Heading
                select_all = request.data.get('Select_All')  # Get Select_All

                # Set P1 to P10 to 'Yes' if Select_All is 'Yes'
                if select_all == 'Yes':
                    for i in range(1, 10):
                        request.data[f'P{i}'] = 'Yes'

                exists = BRS_Policy_1a.objects.filter(Heading=heading).first()

                if exists:
                    serializer = BRSPolicy1aSerializer(exists, data=request.data, partial=True)
                else:
                    # Create new entry
                    max_id = BRS_Policy_1.objects.aggregate(Max('id'))['id__max']
                    request.data['id'] = (max_id + 1) if max_id is not None else 1  # Set new ID for the entry
                    serializer = BRSPolicy1aSerializer(data=request.data)

                if serializer.is_valid():
                    serializer.save()

                    # Log the activity
                    activity_log = {
                        "Name": f"{request.user.firstname} {request.user.lastname}",
                        "Activity": "Edited or added information in table - BRS_Policy_1"
                    }
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data inserted and updated successfully'}, status=status.HTTP_201_CREATED)  # Return only success message
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if serializer fails

        except TypeError as e:
            logger.error(f"TypeError: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        
        


class Brs_Policy2_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
       
        try:
            brs2 = BRS_Policy_2.objects.all().order_by('-id')
            

            page_size = request.query_params.get('page_size', 15)
            paginator = Paginator(brs2, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
        
            serializer = BRSPolicy2Serializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            logger.error(f"ValidationError: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError as e:
            logger.error(f"TypeError: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def post(self, request):
        try:
            # import pdb;pdb.set_trace()
            if isinstance(request.data, list):
                all_success = True
                response_data = []
                delete_all_record = BRS_Policy_2.objects.all()
                delete_all_record.delete()
                for entry in request.data:
                    heading = entry.get('Heading')  # Get Heading from the entry
                    select_all = entry.get('Select_All')  # Get Select_All for processing

                    # Set P1 to P10 to 'Yes' if Select_All is 'Yes'
                    if select_all == 'Yes':
                        for i in range(1, 10):
                            entry[f'P{i}'] = 'Yes'

                    # Handle the Description field if it's a list
                    if isinstance(entry.get('Description'), list):
                        entry['Description'] = ', '.join(entry['Description'])

                    # Check for an existing entry based on Heading
                    exists = BRS_Policy_2.objects.filter(Heading=heading).first()

                    if exists:
                        # Update existing entry
                        serializer = BRSPolicy2Serializer(exists, data=entry, partial=True)
                    else:
                        # Create new entry
                        max_id = BRS_Policy_2.objects.aggregate(Max('id'))['id__max']
                        entry['id'] = (max_id + 1) if max_id is not None else 1  # Set new ID for the entry
                        serializer = BRSPolicy2Serializer(data=entry)

                    if serializer.is_valid():
                        serializer.save()

                        # Log the activity
                        activity_log = {
                            "Name": f"{request.user.firstname} {request.user.lastname}",
                            "Activity": "Edited or added information in table - BRS_Policy_1"
                        }
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()
                    else:
                        all_success = False  # Set success to False if any serializer fails
                        response_data.append({'errors': serializer.errors})  # Capture errors

                # Return a single success message if all operations were successful
                if all_success:
                    return Response({'success': 'Data inserted and updated successfully'}, status=status.HTTP_201_CREATED)
                else:
                    return Response(response_data, status=status.HTTP_207_MULTI_STATUS)

            else:
                # delete_all_record = BRS_Policy_2.objects.all()
                # delete_all_record.delete()
                # Handle single request
                heading = request.data.get('Heading')  # Get Heading
                select_all = request.data.get('Select_All')  # Get Select_All

                # Set P1 to P10 to 'Yes' if Select_All is 'Yes'
                if select_all == 'Yes':
                    for i in range(1, 10):
                        request.data[f'P{i}'] = 'Yes'

                exists = BRS_Policy_2.objects.filter(Heading=heading).first()

                if exists:
                    serializer = BRSPolicy2Serializer(exists, data=request.data, partial=True)
                else:
                    # Create new entry
                    max_id = BRS_Policy_1.objects.aggregate(Max('id'))['id__max']
                    request.data['id'] = (max_id + 1) if max_id is not None else 1  # Set new ID for the entry
                    serializer = BRSPolicy2Serializer(data=request.data)

                if serializer.is_valid():
                    serializer.save()

                    # Log the activity
                    activity_log = {
                        "Name": f"{request.user.firstname} {request.user.lastname}",
                        "Activity": "Edited or added information in table - BRS_Policy_1"
                    }
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data inserted and updated successfully'}, status=status.HTTP_201_CREATED)  # Return only success message
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if serializer fails

        except TypeError as e:
            logger.error(f"TypeError: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class FrequencyOfEngagementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            frequency_of_engagement_list = FREQUENCY_OF_ENGAGEMENT

            if not frequency_of_engagement_list:
                return Response({'error': 'Frequency of engagement list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(frequency_of_engagement_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Frequency of engagement list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)