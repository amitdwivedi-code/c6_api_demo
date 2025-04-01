from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import APIException

from .models import *
from .serializers import *
from django.db.models import Q

# Create your views here.
class ActivityLog_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            search_query = request.query_params.get('name', '').strip()
            if user_role == "ESG Lead":
                if search_query:
                    activity_log = Activity_Log.objects.filter(Q(Name__icontains=search_query)).order_by('-Last_Update')
                else:
                    activity_log = Activity_Log.objects.all().order_by('-Last_Update')
            else:
                user_name = request.user.firstname + " " + request.user.lastname
                if search_query:
                    activity_log = Activity_Log.objects.filter(Q(Name__icontains=search_query)).order_by('-Last_Update')
                else:
                    activity_log = Activity_Log.objects.filter(Name=user_name).order_by('-Last_Update')          

            # Apply search filter if `search_query` is provided


            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(activity_log, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ActivityLogSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class BrsLog_View(APIView):
    permission_classes = [IsAuthenticated]
 
    def get(self,request):
        try:
            user_role = request.user.role
            search_query = request.query_params.get('name', '').strip()
            # if user_role == "ESG Lead":
            brs_log = BRS_Report_Log.objects.all().order_by('-Last_Update')
            # else:
            #     user_name = request.user.firstname+" "+request.user.lastname
            #     brs_log = BRS_Report_Log.objects.filter(User_Name=user_name).order_by('-Last_Update')          

            # Apply search filter if `search_query` is provided
            if search_query:
                brs_log = brs_log.filter(Q(User_Name__icontains=search_query))

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(brs_log, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = BRS_Report_LogSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

