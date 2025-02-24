from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated 
from user.models import User
from CompanyDetails import utils
from . import serializers

from Descriptions.models import Descriptions,DescriptionsProjectandPolicies

from .serializers import DescriptionsSerializer,DescriptionsAnotherSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import APIException
import logging

from Activity_Log.models import Activity_Log
from Activity_Log.serializers import ActivityLogSerializer

logger = logging.getLogger(__name__)

class Descriptions_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            descriptions = Descriptions.objects.all().order_by('-id')
            serializer = DescriptionsSerializer(descriptions, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            
            heading = request.data.get('Heading')
            exists = Descriptions.objects.filter(Heading=heading).count()
            if exists > 0:
                return Response({'error':'This entry already exists.'},status=status.HTTP_400_BAD_REQUEST)

            if Descriptions.objects.count() == 0:
                id = 1
            else:
                id = Descriptions.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            serializer = serializers.DescriptionsSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Types of Customers"}
                                
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
                    description_instance = Descriptions.objects.get(id=id)
                    serializer = DescriptionsSerializer(description_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Types of Customers"}
                                        
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


class DescriptionsAnotherAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Plant Operations" or user_role == "ESG Lead":
            descriptions = DescriptionsProjectandPolicies.objects.all().order_by('id')

            page_size = request.query_params.get('page_size', 15)
            paginator = Paginator(descriptions, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
        
            serializer = DescriptionsAnotherSerializer(paginated_queryset, many=True)
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
            if isinstance(request.data, list):
                response_data = []
                all_success = True

                for entry in request.data:
                    heading = entry.get('Heading')
                    exists = DescriptionsProjectandPolicies.objects.filter(Heading=heading).first()
                    
                    if exists:
                        serializer = DescriptionsAnotherSerializer(exists, data=entry, partial=True)
                    else:
                        # Get the next available ID
                        if DescriptionsProjectandPolicies.objects.count() == 0:
                            id = 1
                        else:
                            id = DescriptionsProjectandPolicies.objects.aggregate(Max('id'))['id__max'] + 1
                        entry['id'] = id  # Change request.data to entry
                        serializer = DescriptionsAnotherSerializer(data=entry)

                    if serializer.is_valid():
                        serializer.save()
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Added information in table - DescriptionsProjectandPolicies"}
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
                heading = request.data.get('Heading')
                exists = DescriptionsProjectandPolicies.objects.filter(Heading=heading).first()
                
                if exists:
                    serializer = DescriptionsAnotherSerializer(exists, data=request.data, partial=True)
                else:
                    # Get the next available ID
                    if DescriptionsProjectandPolicies.objects.count() == 0:
                        id = 1
                    else:
                        id = DescriptionsProjectandPolicies.objects.aggregate(Max('id'))['id__max'] + 1
                    request.data['id'] = id
                    serializer = DescriptionsAnotherSerializer(data=request.data)

                if serializer.is_valid():
                    serializer.save()
                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Edited information in table - DescriptionsProjectandPolicies"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    return Response({'entry': serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

