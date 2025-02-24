from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import APIException
from django.db.models import Max, Sum
from Activity_Log.serializers import ActivityLogSerializer

from .models import RecommendationModel
from .serializers import RecommendationSerializer

"""
API's for all tables recommendation and comments
"""
class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]
    """
    In this API if call with correct params then get single object data or error
    in case we did not call with params then get all data in list format
    """
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Human Resource" or user_role == "ESG Lead":

            recommendation_params_recommendation_key = request.query_params.get('recommendation_key')
            recommendation_params_financial_year = request.query_params.get('financial_year')
            if recommendation_params_recommendation_key and recommendation_params_financial_year:
                recommendation_data = RecommendationModel.objects.filter(recommendation_key = recommendation_params_recommendation_key, financial_year = recommendation_params_financial_year).first()
                serializer = RecommendationSerializer(recommendation_data)
                # if recommendation_data:
                #     serializer = RecommendationSerializer(recommendation_data)
                # else:
                #     return Response({'error': 'Invalid Recommendation Key or Financial year, Pass the valid Recommendation Key and Financial year.'}, status=status.HTTP_400_BAD_REQUEST)
            elif recommendation_params_financial_year:
                recommendation_data = RecommendationModel.objects.filter(financial_year = recommendation_params_financial_year)
                serializer = RecommendationSerializer(recommendation_data, many=True)
                # if recommendation_data:
                #     serializer = RecommendationSerializer(recommendation_data, many=True)
                # else:
                #     return Response({'error': 'Invalid  Financial year, Pass the valid Financial year.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Pass valid paramater.'}, status=status.HTTP_400_BAD_REQUEST)
            
            response_data = {
                'data': serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
            # else:
            #     return Response({'error': 'This data can only accessed by Human Resources or ESG Head.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    """
    In this API post data with table name and value
    If data already exist then can update on basic of key
    """
    def post(self, request):
        try:
            if RecommendationModel.objects.count() == 0:
                id = 1
            else:
                id = RecommendationModel.objects.aggregate(Max('id'))['id__max'] + 1
            request.data['id'] = id
            recommendation_key = request.data.get('recommendation_key')
            financial_year = request.data.get('financial_year')

            existing_data = RecommendationModel.objects.filter(recommendation_key=recommendation_key, financial_year=financial_year).first()
            if existing_data:
                RecommendationModel.objects.filter(recommendation_key=recommendation_key).update(
                    recommendation_value=request.data.get('recommendation_value'),
                    financial_year=request.data.get('financial_year')
                )

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - RecommendationModel"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
            else:
                serializer = RecommendationSerializer(data=request.data)
                # import pdb; pdb.set_trace()

                if serializer.is_valid():
                    serializer.save()


                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Updated information in table - RecommendationModel"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data added successfully'}, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    """
    API for delete data on the base on ID not mendetory api but still create for if want to implement delete functionality
    """
    def delete(self, request, **kwargs):
        try:
            id= kwargs.get('id')
            if id is not None:
                try:
                    recommendation = RecommendationModel.objects.get(id=id)
                    recommendation.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - RecommendationModel"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except RecommendationModel.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
   
