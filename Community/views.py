from django.shortcuts import render
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
# from EmissionFactors.models import EmissionFactors
from rest_framework.permissions import IsAuthenticated 
from Activity_Log.models import Activity_Log
from Activity_Log.serializers import ActivityLogSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from .serializers import *
from .choices import *
from django.db.models import Max, Sum
from rest_framework.exceptions import APIException,ValidationError
from django.db import transaction
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
# Create your views here.

class StakeHolderGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            stake_holder_group_list = STAKE_HOLDER_GROUP
            stake_holder_group_list = sorted(stake_holder_group_list,key=str.casefold)

            if not stake_holder_group_list:
                return Response({'error': 'Stakeholder group list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(stake_holder_group_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Stakeholder group list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
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

















class List_Stakeholder_Groups_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
        # if user_role == "Company Secretary" or user_role == "ESG Lead":
            stakeholder_groups = List_Stakeholder_Groups.objects.order_by('-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(stakeholder_groups, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            # Prepare custom response
            response_data = []
            for group in paginated_queryset:
                data = {
                    "id":group.id,
                    "Stack_Holder_Group": group.Stack_Holder_Group,
                    "Vulnerable_And_Marginalized": group.Vulnerable_And_Marginalized,
                    "Channels_Of_Communication": group.Channels_Of_Communication.split(", ") if group.Channels_Of_Communication else [],
                    "Frequency_Of_Engagement": group.Frequency_Of_Engagement.split(", ") if group.Frequency_Of_Engagement else [],
                    "Purpose_And_Scope_Of_Engagement": group.Purpose_And_Scope_Of_Engagement,
                }
                response_data.append(data)

            # Return paginated response
            return Response({
                'data': response_data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }, status=status.HTTP_200_OK)
        # else:
        #     return Response({'error': 'This data can only be accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:

            stack_holder= request.data.get('Stack_Holder_Group')
            is_exist = List_Stakeholder_Groups.objects.filter(Stack_Holder_Group=stack_holder)

            if is_exist:
                return Response({'error': 'Entry for this stack holder group already exists'}, status=status.HTTP_400_BAD_REQUEST)

            
            # Convert Channels_Of_Communication and Frequency_Of_Engagement from list to string
            if isinstance(request.data.get("Channels_Of_Communication"), list):
                request.data["Channels_Of_Communication"] = ", ".join(request.data["Channels_Of_Communication"])

            if isinstance(request.data.get("Frequency_Of_Engagement"), list):
                request.data["Frequency_Of_Engagement"] = ", ".join(request.data["Frequency_Of_Engagement"])

            # Get the next ID, default to 1 if the table is empty or id__max is None
            max_id = List_Stakeholder_Groups.objects.aggregate(Max('id'))['id__max']
            id = 1 if max_id is None else max_id + 1

            request.data['id'] = id
            serializer = ListStakeholderGroupsSerializer(data=request.data)

            if serializer.is_valid():
                # Save the new entry
                serializer.save()

                # Log the activity
                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - List_Stakeholder_Groups"
                }
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                # Prepare the custom response
                response_data = {
                    "Stack_Holder_Group": serializer.data.get("Stack_Holder_Group"),
                    "Vulnerable_And_Marginalized": serializer.data.get("Vulnerable_And_Marginalized"),
                    "Channels_Of_Communication": serializer.data.get("Channels_Of_Communication", "").split(", "),
                    "Frequency_Of_Engagement": serializer.data.get("Frequency_Of_Engagement", "").split(", "),
                    "Purpose_And_Scope_Of_Engagement": serializer.data.get("Purpose_And_Scope_Of_Engagement")
                }

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    stakeholder_group = List_Stakeholder_Groups.objects.get(id=id)

                    # Handle conversion of lists to comma-separated strings
                    if isinstance(request.data.get('Channels_Of_Communication'), list):
                        request.data['Channels_Of_Communication'] = ', '.join(request.data['Channels_Of_Communication'])
                    
                    if isinstance(request.data.get('Frequency_Of_Engagement'), list):
                        request.data['Frequency_Of_Engagement'] = ', '.join(request.data['Frequency_Of_Engagement'])

                    serializer = ListStakeholderGroupsSerializer(stakeholder_group, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                            "Name": request.user.firstname + " " + request.user.lastname,
                            "Activity": "Edited information in table - List_Stakeholder_Groups"
                        }
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    stakeholder_group = List_Stakeholder_Groups.objects.get(id=id)
                    stakeholder_group.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - List_Stakeholder_Groups"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Number_Of_Affiliations_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
        # if user_role == "Company Secretary" or user_role == "ESG Lead":
            affiliations = Number_Of_Affiliations.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(affiliations, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = NumberOfAffiliationsSerializer(paginated_queryset, many=True)
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
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            financial_year = request.data.get('Financial_Year')
            
            if Number_Of_Affiliations.objects.filter(Financial_Year=financial_year).count() > 0:
                return Response({'error': 'Entry for this financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
         
            if Number_Of_Affiliations.objects.count() == 0:
                id = 1
            else:
                id = Number_Of_Affiliations.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            serializer = NumberOfAffiliationsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Number_Of_Affiliations"}
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
                    affiliation = Number_Of_Affiliations.objects.get(id=id)
                    serializer = NumberOfAffiliationsSerializer(affiliation, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Number_Of_Affiliations"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                            return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    affiliation = Number_Of_Affiliations.objects.get(id=id)
                    affiliation.delete()
                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Number_Of_Affiliations"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Top_10_Trade_And_Industry_Chambers_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
            try:
                user_role = request.user.role
                # if user_role == "Company Secretary" or user_role == "ESG Lead":

                chambers = Top_10_Trade_And_Industry_Chambers.objects.order_by('-id')
                page_size = request.query_params.get('page_size', 5)
                paginator = Paginator(chambers, page_size)
                page_number = request.query_params.get('page', 1)

                try:
                    paginated_queryset = paginator.page(page_number)
                except EmptyPage:
                    return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
                except PageNotAnInteger:
                    return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

                serializer = Top10TradeAndIndustryChambersSerializer(paginated_queryset, many=True)
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
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            Name_Of_The_Trade_And_Industry_Chambers = request.data.get('Name_Of_The_Trade_And_Industry_Chambers')
            is_exist = Top_10_Trade_And_Industry_Chambers.objects.filter(Name_Of_The_Trade_And_Industry_Chambers=Name_Of_The_Trade_And_Industry_Chambers)

           
            if is_exist:
                return Response({'error': 'Entry for this Name Of Trade And Industry Chambers already exists'}, status=status.HTTP_400_BAD_REQUEST)


            if Top_10_Trade_And_Industry_Chambers.objects.count() == 0:
                id = 1
            else:
                id = Top_10_Trade_And_Industry_Chambers.objects.aggregate(Max('id'))['id__max'] + 1
            request.data['id'] = id

            max_sr_no = Top_10_Trade_And_Industry_Chambers.objects.aggregate(Max('Sr_No'))['Sr_No__max'] or 0
            request.data['Sr_No'] = max_sr_no + 1

            serializer = Top10TradeAndIndustryChambersSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Top_10_Trade_And_Industry_Chambers"}
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
                    chamber = Top_10_Trade_And_Industry_Chambers.objects.get(id=id)
                    serializer = Top10TradeAndIndustryChambersSerializer(chamber, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Top_10_Trade_And_Industry_Chambers"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    chamber = Top_10_Trade_And_Industry_Chambers.objects.get(id=id)
                    chamber.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Top_10_Trade_And_Industry_Chambers"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Details_Anti_Competitive_Conduct_By_The_Entity_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            issues = Details_Of_Any_Issues_Related_To_Anti_Competitive_Conduct_By_The_Entity.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(issues, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = DetailsOfAnyIssuesRelatedToAntiCompetitiveConductByTheEntitySerializer(paginated_queryset, many=True)
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
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            if Details_Of_Any_Issues_Related_To_Anti_Competitive_Conduct_By_The_Entity.objects.count() == 0:
                id = 1
            else:
                id = Details_Of_Any_Issues_Related_To_Anti_Competitive_Conduct_By_The_Entity.objects.aggregate(Max('id'))['id__max'] + 1
            request.data['id'] = id
            
            Financial_Year = request.data.get('Financial_Year')

            # Check if an entry already exists for the given facility and financial year
            if Details_Of_Any_Issues_Related_To_Anti_Competitive_Conduct_By_The_Entity.objects.filter(Financial_Year=Financial_Year).count() > 0:
                return Response({'error': 'Entry for this financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = DetailsOfAnyIssuesRelatedToAntiCompetitiveConductByTheEntitySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Details_Of_Any_Issues_Related_To_Anti_Competitive_Conduct_By_The_Entity"}
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
                    issue = Details_Of_Any_Issues_Related_To_Anti_Competitive_Conduct_By_The_Entity.objects.get(id=id)
                    serializer = DetailsOfAnyIssuesRelatedToAntiCompetitiveConductByTheEntitySerializer(issue, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Details_Of_Any_Issues_Related_To_Anti_Competitive_Conduct_By_The_Entity"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    issue = Details_Of_Any_Issues_Related_To_Anti_Competitive_Conduct_By_The_Entity.objects.get(id=id)
                    issue.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Details_Of_Any_Issues_Related_To_Anti_Competitive_Conduct_By_The_Entity"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Details_Of_Public_Policy_Positions_Advocated_By_The_Entity_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            issues = Details_Of_Public_Policy_Positions_Advocated_By_The_Entity.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(issues, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = DetailsOfPublicPolicyPositionsAdvocatedByTheEntitySerializer(paginated_queryset, many=True)
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
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
            count = Details_Of_Public_Policy_Positions_Advocated_By_The_Entity.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error':'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Details_Of_Public_Policy_Positions_Advocated_By_The_Entity.objects.count() == 0:
                id = 1
            else:
                id = Details_Of_Public_Policy_Positions_Advocated_By_The_Entity.objects.aggregate(Max('id'))['id__max'] + 1
            request.data['id'] = id

            max_sr_no = Details_Of_Public_Policy_Positions_Advocated_By_The_Entity.objects.aggregate(Max('Sr_No'))['Sr_No__max'] or 0
            request.data['Sr_No'] = max_sr_no + 1

            serializer = DetailsOfPublicPolicyPositionsAdvocatedByTheEntitySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Details_Of_Public_Policy_Positions_Advocated_By_The_Entity"
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
            id = kwargs.get('id')
            if id is not None:
                try:
                    details = Details_Of_Public_Policy_Positions_Advocated_By_The_Entity.objects.get(id=id)
                    serializer = DetailsOfPublicPolicyPositionsAdvocatedByTheEntitySerializer(details, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                            "Name": request.user.firstname + " " + request.user.lastname,
                            "Activity": "Edited information in table - Details_Of_Public_Policy_Positions_Advocated_By_The_Entity"
                        }
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    details = Details_Of_Public_Policy_Positions_Advocated_By_The_Entity.objects.get(id=id)
                    details.delete()

                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Deleted information in table - Details_Of_Public_Policy_Positions_Advocated_By_The_Entity"
                    }
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Awareness_Programmes_For_Value_Chain_Partners_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            user_location = request.user.location
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            # programmes = Awareness_Programmes_For_Value_Chain_Partners.objects.filter(Facility__in=user_location).order_by('-id')
            programmes = Awareness_Programmes_For_Value_Chain_Partners.objects.all().order_by('-Financial_Year')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(programmes, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = AwarenessProgrammesForValueChainPartnersSerializer(paginated_queryset, many=True)
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
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            year = request.data.get('Financial_Year')
            # facility =  request.data.get('Facility')
            count = Awareness_Programmes_For_Value_Chain_Partners.objects.filter(Financial_Year=year).count()
            if count > 0:
                return Response({'error':'Entry for this Financial Year  already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Awareness_Programmes_For_Value_Chain_Partners.objects.count() == 0:
                id = 1
            else:
                id = Awareness_Programmes_For_Value_Chain_Partners.objects.aggregate(Max('id'))['id__max'] + 1
            request.data['id'] = id

            serializer = AwarenessProgrammesForValueChainPartnersSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Awareness_Programmes_For_Value_Chain_Partners"}
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
                    programme = Awareness_Programmes_For_Value_Chain_Partners.objects.get(id=id)
                    serializer = AwarenessProgrammesForValueChainPartnersSerializer(programme, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Awareness_Programmes_For_Value_Chain_Partners"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    programme = Awareness_Programmes_For_Value_Chain_Partners.objects.get(id=id)
                    programme.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Awareness_Programmes_For_Value_Chain_Partners"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Information_on_CSR_Projects_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            informations = Information_on_CSR_Projects.objects.order_by('-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(informations, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Information_on_CSR_ProjectsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            # State = request.data.get('State')
            # district = request.data.get('Aspirational_District')
            # is_exist = Information_on_CSR_Projects.objects.filter(State=State, Aspirational_District= district)

            # if is_exist:
            #     return Response({'error': 'Entry for this State  and Aspirational District already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Information_on_CSR_Projects.objects.count() == 0:
                id = 1
            else:
                id = Information_on_CSR_Projects.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            serializer = Information_on_CSR_ProjectsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Information_on_CSR_Projects"}
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
                    informations = Information_on_CSR_Projects.objects.get(id=id)
                    with transaction.atomic():
                        Information_on_CSR_Projects.objects.filter(id=id).delete()

                        request_data = request.data.copy()  
                        if "id" in request_data:
                            request_data.pop("id")

                        Information_on_CSR_Projects.objects.create(id=id, **request_data)
                   
                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Information_on_CSR_Projects"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()
                        return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                   
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    informations = Information_on_CSR_Projects.objects.get(id=id)
                    informations.delete()
                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Information_on_CSR_Projects"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Owned_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            owned_list = OWNED

            if not owned_list:
                return Response({'error': 'list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(owned_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Benefit_Shared_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            benefit_shared_list = BENEFIT_SHARED

            if not benefit_shared_list:
                return Response({'error': 'list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(benefit_shared_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Benefits_Derived_And_Shared_From_Intellectual_Property_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            benefit = Benefits_Derived_And_Shared_From_Intellectual_Property.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(benefit, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Benefits_Derived_And_Shared_From_Intellectual_PropertySerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            Financial_Year = request.data.get('Financial_Year')

            # Check if an entry already exists for the given facility and financial year
            if Benefits_Derived_And_Shared_From_Intellectual_Property.objects.filter(Financial_Year=Financial_Year).count() > 0:
                return Response({'error': 'Entry for this financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
           
            if Benefits_Derived_And_Shared_From_Intellectual_Property.objects.count() == 0:
                id = 1
            else:
                id = Benefits_Derived_And_Shared_From_Intellectual_Property.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            serializer = Benefits_Derived_And_Shared_From_Intellectual_PropertySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Benefits_Derived_And_Shared_From_Intellectual_Property"}
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
                    benefit = Benefits_Derived_And_Shared_From_Intellectual_Property.objects.get(id=id)
                    serializer = Benefits_Derived_And_Shared_From_Intellectual_PropertySerializer(benefit, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Benefits_Derived_And_Shared_From_Intellectual_Property"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    benefit = Benefits_Derived_And_Shared_From_Intellectual_Property.objects.get(id=id)
                    benefit.delete()
                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Deleted information in table - Benefits_Derived_And_Shared_From_Intellectual_Property"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Details_Of_Intellectual_Property_Related_Disputes_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            property = Details_Of_Intellectual_Property_Related_Disputes.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(property, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Details_Of_Intellectual_Property_Related_DisputesSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            Financial_Year = request.data.get('Financial_Year')

            # Check if an entry already exists for the given facility and financial year
            if Details_Of_Intellectual_Property_Related_Disputes.objects.filter(Financial_Year=Financial_Year).count() > 0:
                return Response({'error': 'Entry for this financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
           
            if Details_Of_Intellectual_Property_Related_Disputes.objects.count() == 0:
                id = 1
            else:
                id = Details_Of_Intellectual_Property_Related_Disputes.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            serializer = Details_Of_Intellectual_Property_Related_DisputesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Added information in table - Details_Of_Intellectual_Property_Related_Disputes"}
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
                    property = Details_Of_Intellectual_Property_Related_Disputes.objects.get(id=id)
                    serializer = Details_Of_Intellectual_Property_Related_DisputesSerializer(property, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Details_Of_Intellectual_Property_Related_Disputes"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    property = Details_Of_Intellectual_Property_Related_Disputes.objects.get(id=id)
                    property.delete()
                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Deleted information in table - Details_Of_Intellectual_Property_Related_Disputes"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Details_Of_Beneficiaries_Of_CSR_Projects_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            csr = Details_Of_Beneficiaries_Of_CSR_Projects.objects.order_by('-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(csr, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Details_Of_Beneficiaries_Of_CSR_ProjectsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            csr = request.data.get('CSR_Project')

            # Check if an entry already exists for the given facility and financial year
            if Details_Of_Beneficiaries_Of_CSR_Projects.objects.filter(CSR_Project=csr).count() > 0:
                return Response({'error': 'Entry for this CSR Project already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Details_Of_Beneficiaries_Of_CSR_Projects.objects.count() == 0:
                id = 1
            else:
                id = Details_Of_Beneficiaries_Of_CSR_Projects.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            serializer = Details_Of_Beneficiaries_Of_CSR_ProjectsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname,
                "Activity": "Added information in table - Details_Of_Beneficiaries_Of_CSR_Projects"}
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
                    csr = Details_Of_Beneficiaries_Of_CSR_Projects.objects.get(id=id)
                    serializer = Details_Of_Beneficiaries_Of_CSR_ProjectsSerializer(csr, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Details_Of_Beneficiaries_Of_CSR_Projects"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    csr = Details_Of_Beneficiaries_Of_CSR_Projects.objects.get(id=id)
                    csr.delete()

                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Deleted information in table - Details_Of_Beneficiaries_Of_CSR_Projects"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Turnover_Of_Products_As_A_Percentage_Of_Turnover_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            turnover = Turnover_Of_Products_As_A_Percentage_Of_Turnover.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(turnover, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer =Turnover_Of_Products_As_A_Percentage_Of_TurnoverSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            Financial_Year = request.data.get('Financial_Year')

            # Check if an entry already exists for the given facility and financial year
            if Turnover_Of_Products_As_A_Percentage_Of_Turnover.objects.filter(Financial_Year=Financial_Year).count() > 0:
                return Response({'error': 'Entry for this financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
           
            if Turnover_Of_Products_As_A_Percentage_Of_Turnover.objects.count() == 0:
                id = 1
            else:
                id = Turnover_Of_Products_As_A_Percentage_Of_Turnover.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            serializer = Turnover_Of_Products_As_A_Percentage_Of_TurnoverSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Added information in table - Turnover_Of_Products_As_A_Percentage_Of_Turnover"}
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Entry for this facility and financial year already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    turnover = Turnover_Of_Products_As_A_Percentage_Of_Turnover.objects.get(id=id)
                    serializer = Turnover_Of_Products_As_A_Percentage_Of_TurnoverSerializer(turnover, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Turnover_Of_Products_As_A_Percentage_Of_Turnover"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    turnover = Turnover_Of_Products_As_A_Percentage_Of_Turnover.objects.get(id=id)
                    turnover.delete()

                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Deleted information in table - Turnover_Of_Products_As_A_Percentage_Of_Turnover"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Type_Consumer_Complaints_List_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            type_list = TYPE_COMPLAINTS

            if not type_list:
                return Response({'error': 'list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(type_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Number_of_Consumer_Complaints_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            consumer = Number_of_Consumer_Complaints.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 15)
            paginator = Paginator(consumer, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Number_of_Consumer_ComplaintsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            Financial_Year = request.data.get('Financial_Year')

            Type = request.data.get('Type')
            data_exists = Number_of_Consumer_Complaints.objects.filter(
                Financial_Year=Financial_Year,
                Type=Type
            )
            if data_exists:
                return Response({'error': 'Entry for this Financial Year and Type already exist.'}, status=status.HTTP_400_BAD_REQUEST)
            

            if Number_of_Consumer_Complaints.objects.count() == 0:
                id = 1
            else:
                id = Number_of_Consumer_Complaints.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            serializer = Number_of_Consumer_ComplaintsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Added information in table - Number_of_Consumer_Complaints"}
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
                    Financial_Year = request.data.get('Financial_Year')
                    Type = request.data.get('Type')
                    data_exists = Number_of_Consumer_Complaints.objects.filter(
                        Financial_Year=Financial_Year,
                        Type=Type
                    ).exclude(id=id)
                    if data_exists:
                        return Response({'success': 'Financial Year and Type Group already exist.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    consumer = Number_of_Consumer_Complaints.objects.get(id=id)
                    serializer = Number_of_Consumer_ComplaintsSerializer(consumer, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Number_of_Consumer_Complaints"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    consumer = Number_of_Consumer_Complaints.objects.get(id=id)
                    consumer.delete()

                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Deleted information in table - Number_of_Consumer_Complaints"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Recall_List_View(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            recall_list = RECALL_TYPE

            if not recall_list:
                return Response({'error': 'list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(recall_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Details_Of_Instances_Of_Product_Recalls_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            recall = Details_Of_Instances_Of_Product_Recalls.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(recall, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Details_Of_Instances_Of_Product_RecallsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            Financial_Year = request.data.get('Financial_Year')
            Recall_Type = request.data.get('Recall_Type')
            

            # Check if an entry already exists for the given facility and financial year
            if Details_Of_Instances_Of_Product_Recalls.objects.filter(Financial_Year=Financial_Year,Recall_Type=Recall_Type):
                return Response({'error': 'Entry for this financial year and Recall type already exists'}, status=status.HTTP_400_BAD_REQUEST)  
            
            if Details_Of_Instances_Of_Product_Recalls.objects.count() == 0:
                id = 1
            else:
                id = Details_Of_Instances_Of_Product_Recalls.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id
            serializer = Details_Of_Instances_Of_Product_RecallsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Added information in table - Details_Of_Instances_Of_Product_Recalls"}
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
                    recall = Details_Of_Instances_Of_Product_Recalls.objects.get(id=id)
                    serializer = Details_Of_Instances_Of_Product_RecallsSerializer(recall, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Details_Of_Instances_Of_Product_Recalls"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    recall = Details_Of_Instances_Of_Product_Recalls.objects.get(id=id)
                    recall.delete()

                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Deleted information in table - Details_Of_Instances_Of_Product_Recalls"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Corporate_Social_Responsibility_Details_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            social = Corporate_Social_Responsibility_Details.objects.all().order_by('id')

            page_size = request.query_params.get('page_size', 15)
            paginator = Paginator(social, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
        
            serializer = Corporate_Social_Responsibility_DetailsSerializer(paginated_queryset, many=True)
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

    def post(self, request):
        try:
            if isinstance(request.data, list):
                response_data = []
                all_success = True
                delete_all_record = Corporate_Social_Responsibility_Details.objects.all()
                delete_all_record.delete()

                for entry in request.data:
                    heading = entry.get('Heading')
                    exists = Corporate_Social_Responsibility_Details.objects.filter(Heading=heading).first()
                    
                    if exists:
                        serializer = Corporate_Social_Responsibility_DetailsSerializer(exists, data=entry, partial=True)
                    else:
                        # Get the next available ID
                        if Corporate_Social_Responsibility_Details.objects.count() == 0:
                            id = 1
                        else:
                            id = Corporate_Social_Responsibility_Details.objects.aggregate(Max('id'))['id__max'] + 1
                        entry['id'] = id  # Change request.data to entry
                        serializer = Corporate_Social_Responsibility_DetailsSerializer(data=entry)

                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                            "Name": request.user.firstname + " " + request.user.lastname,
                            "Activity": "Added information in table - Corporate_Social_Responsibility_Details"}
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
                delete_all_record = Corporate_Social_Responsibility_Details.objects.all()
                delete_all_record.delete()
                heading = request.data.get('Heading')
                exists = Corporate_Social_Responsibility_Details.objects.filter(Heading=heading).first()
                
                if exists:
                    serializer =Corporate_Social_Responsibility_DetailsSerializer(exists, data=request.data, partial=True)
                else:
                    # Get the next available ID
                    if Corporate_Social_Responsibility_Details.objects.count() == 0:
                        id = 1
                    else:
                        id =Corporate_Social_Responsibility_Details.objects.aggregate(Max('id'))['id__max'] + 1
                    request.data['id'] = id
                    serializer = Corporate_Social_Responsibility_DetailsSerializer(data=request.data)

                if serializer.is_valid():
                    serializer.save()
                    activity_log = {
                            "Name": request.user.firstname + " " + request.user.lastname,
                            "Activity": "Added information in table - Corporate_Social_Responsibility_Details"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                    return Response({'entry': serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except TypeError as e:
            logger.error(f"TypeError: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Consumer_Details_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            consumer = Consumer_Details.objects.all().order_by('id')
            page_size = int(request.query_params.get('page_size', 15))
            paginator = Paginator(consumer, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Consumer_DetailsSerializer(paginated_queryset, many=True)
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
            logger.error(f"Exception in GET: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

   
   
    def post(self, request):
        try:
            if isinstance(request.data, list):
                # Validate all records first
                for entry in request.data:
                    is_verified = entry.get('Is_Verified')
                    description = entry.get('Description_consumer')

                    if is_verified == 'Yes' and (not description or description.strip() == ""):
                        raise ValidationError("Description is mandatory and cannot be empty or spaces when Is_Verified is 'Yes'.")

                # If all records are valid, process them
                response_data = []
                all_success = True

                for entry in request.data:
                    heading = entry.get('Heading')
                    exists = Consumer_Details.objects.filter(Heading=heading).first()

                    if exists:
                        serializer = Consumer_DetailsSerializer(exists, data=entry, partial=True)
                    else:
                        # Get the next available ID
                        if Consumer_Details.objects.count() == 0:
                            id = 1
                        else:
                            id = Consumer_Details.objects.aggregate(Max('id'))['id__max'] + 1
                        entry['id'] = id
                        serializer = Consumer_DetailsSerializer(data=entry)

                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                            "Name": request.user.firstname + " " + request.user.lastname,
                            "Activity": "Added information in table - Consumer_Details"
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
                exists = Consumer_Details.objects.filter(Heading=heading).first()

                if exists:
                    serializer = Consumer_DetailsSerializer(exists, data=request.data, partial=True)
                else:
                    # Get the next available ID
                    if Consumer_Details.objects.count() == 0:
                        id = 1
                    else:
                        id = Consumer_Details.objects.aggregate(Max('id'))['id__max'] + 1
                    request.data['id'] = id
                    serializer = Consumer_DetailsSerializer(data=request.data)

                if serializer.is_valid():
                    serializer.save()

                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Consumer_Details"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'entry': serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            # Return only the success as a string without any additional structure
            return Response({'error': str(e.detail)}, status=status.HTTP_400_BAD_REQUEST)

        except TypeError as e:
            logger.error(f"TypeError: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Stakeholders_DetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    
    def get(self, request):
        try:
            stakeholder = Stakeholders_Details.objects.all().order_by('-id')

            # Convert page_size to integer
            page_size = int(request.query_params.get('page_size', 15))
            paginator = Paginator(stakeholder, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Stakeholders_DetailsSerializer(paginated_queryset, many=True)
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
            logger.error(f"Exception in GET: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            if isinstance(request.data, list):
                response_data = []
                all_success = True

                for entry in request.data:
                    Model_Name_Stakeholder = entry.get('Model_Name_Stakeholder')  # Removed leading space
                    if not Model_Name_Stakeholder:
                        response_data.append({'errors': 'Model_Name_Stakeholder is required', 'entry': entry})
                        all_success = False
                        continue
                    
                    exists = Stakeholders_Details.objects.filter(Model_Name_Stakeholder=Model_Name_Stakeholder).first()

                    if exists:
                        serializer = Stakeholders_DetailsSerializer(exists, data=entry, partial=True)
                    else:
                        # Get the next available ID
                        id = Stakeholders_Details.objects.aggregate(Max('id'))['id__max'] + 1 if Stakeholders_Details.objects.count() > 0 else 1
                        entry['id'] = id
                        serializer = Stakeholders_DetailsSerializer(data=entry)

                    if serializer.is_valid():
                        serializer.save()

                        # Log the activity
                        activity_log = {
                            "Name": f"{request.user.firstname} {request.user.lastname}",
                            "Activity": "Added information in table - Stakeholders_Details"
                        }
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        response_data.append({'entry': serializer.data})
                    else:
                        response_data.append({'errors': serializer.errors, 'entry': entry})
                        all_success = False

                if all_success:
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
                    return Response(response_data, status=status.HTTP_207_MULTI_STATUS)

            else:
                Model_Name_Stakeholder = request.data.get('Model_Name_Stakeholder')  # Removed leading space
                if not Model_Name_Stakeholder:
                    return Response({'error': 'Model_Name_Stakeholder is required'}, status=status.HTTP_400_BAD_REQUEST)

                exists = Stakeholders_Details.objects.filter(Model_Name_Stakeholder=Model_Name_Stakeholder).first()

                if exists:
                    serializer = Stakeholders_DetailsSerializer(exists, data=request.data, partial=True)
                else:
                    # Get the next available ID
                    id = Stakeholders_Details.objects.aggregate(Max('id'))['id__max'] + 1 if Stakeholders_Details.objects.count() > 0 else 1
                    request.data['id'] = id
                    serializer = Stakeholders_DetailsSerializer(data=request.data)

                if serializer.is_valid():
                    serializer.save()

                    # Log the activity
                    activity_log = {
                        "Name": f"{request.user.firstname} {request.user.lastname}",
                        "Activity": "Edited information in table - Stakeholders_Details"
                    }
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'entry': serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    logger.warning(f"Validation errors: {serializer.errors}")
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Exception in POST: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Society_Details_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            society = Society_Details.objects.all().order_by('-id')

            page_size = request.query_params.get('page_size', 15)
            paginator = Paginator(society, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
        
            serializer = Society_DetailsSerializer(paginated_queryset, many=True)
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

    def post(self, request):
        try:
            if isinstance(request.data, list):
                response_data = []
                all_success = True

                for entry in request.data:
                    heading = entry.get('Heading')
                    exists = Society_Details.objects.filter(Heading=heading).first()
                    
                    if exists:
                        serializer = Society_DetailsSerializer(exists, data=entry, partial=True)
                    else:
                        # Get the next available ID
                        if Society_Details.objects.count() == 0:
                            id = 1
                        else:
                            id = Society_Details.objects.aggregate(Max('id'))['id__max'] + 1
                        entry['id'] = id  # Change request.data to entry
                        serializer = Society_DetailsSerializer(data=entry)

                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Added information in table - Society_Details"}
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
                exists = Society_Details.objects.filter(Heading=heading).first()
                
                if exists:
                    serializer = Society_DetailsSerializer(exists, data=request.data, partial=True)
                else:
                    # Get the next available ID
                    if Society_Details.objects.count() == 0:
                        id = 1
                    else:
                        id = Society_Details.objects.aggregate(Max('id'))['id__max'] + 1
                    request.data['id'] = id
                    serializer = Society_DetailsSerializer(data=request.data)

                if serializer.is_valid():
                    serializer.save()

                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Society_Details"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'entry': serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except TypeError as e:
            logger.error(f"TypeError: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Exception: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Awareness_Programmes_For_Value_Chain_Partners_Filter_View(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":
            facility = request.query_params.get('facility')

            chain_partner_data = Awareness_Programmes_For_Value_Chain_Partners.objects.filter(Facility=facility).order_by('-Financial_Year', '-id')

            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(chain_partner_data, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = AwarenessProgrammesForValueChainPartnersSerializer(paginated_queryset, many=True)
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


   
   

class Details_Of_Social_Impact_Assessments_View(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            assessments = Details_Of_Social_Impact_Assessments.objects.order_by('-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(assessments, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = DetailsOfSocialImpactAssessmentsSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            Name_And_Brief_Details_Of_Project = request.data.get('Name_And_Brief_Details_Of_Project')
            SIA_Notification_No = request.data.get('SIA_Notification_No')
            is_exist = Details_Of_Social_Impact_Assessments.objects.filter(Name_And_Brief_Details_Of_Project=Name_And_Brief_Details_Of_Project, SIA_Notification_No=SIA_Notification_No)

           
            if is_exist:
                return Response({'error': 'Entry for this project name, SIA No already exists'}, status=status.HTTP_400_BAD_REQUEST)



            if Details_Of_Social_Impact_Assessments.objects.count() == 0:
                id = 1
            else:
                id = Details_Of_Social_Impact_Assessments.objects.aggregate(Max('id'))['id__max'] + 1
            request.data['id'] = id

            serializer = DetailsOfSocialImpactAssessmentsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Details_Of_Social_Impact_Assessments"}
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
            id = kwargs.get('id') 
            print(request.data,"----------------------------")
            Name_And_Brief_Details_Of_Project = request.data.get('Name_And_Brief_Details_Of_Project')
            SIA_Notification_No = request.data.get('SIA_Notification_No')
            if Name_And_Brief_Details_Of_Project and SIA_Notification_No:
                is_exist = Details_Of_Social_Impact_Assessments.objects.filter(Name_And_Brief_Details_Of_Project=Name_And_Brief_Details_Of_Project, SIA_Notification_No=SIA_Notification_No).exclude(id=id)

                if is_exist:
                    return Response({'error': 'Entry for this project name, SIA No already exists'}, status=status.HTTP_400_BAD_REQUEST)

            obj = Details_Of_Social_Impact_Assessments.objects.get(id=id) 
            description_details = obj.Description_Details
            if description_details :
                Name_And_Brief_Details_Of_Project = request.data.get('Name_And_Brief_Details_Of_Project')
                SIA_Notification_No = request.data.get('SIA_Notification_No')
                is_exist = Details_Of_Social_Impact_Assessments.objects.filter(Name_And_Brief_Details_Of_Project=Name_And_Brief_Details_Of_Project, SIA_Notification_No=SIA_Notification_No).exclude(id=id)

            
                if is_exist:
                    return Response({'error': 'Entry for this project name, SIA No already exists'}, status=status.HTTP_400_BAD_REQUEST)


            if id is not None:
                try:
                    assessment = Details_Of_Social_Impact_Assessments.objects.get(id=id)
                    with transaction.atomic():
                        Details_Of_Social_Impact_Assessments.objects.filter(id=id).delete()

                        request_data = request.data.copy()  
                         # Convert date fields to "YYYY-MM-DD" before saving
                        if "Date_Of_Notification" in request_data:
                            try:
                                request_data["Date_Of_Notification"] = datetime.strptime(
                                    request_data["Date_Of_Notification"], "%d-%m-%Y"
                                ).strftime("%Y-%m-%d")
                            except ValueError:
                                return Response({'error': 'Invalid date format. Use DD-MM-YYYY'}, status=status.HTTP_400_BAD_REQUEST)
                            
                        if "id" in request_data:
                            request_data.pop("id")

                        Details_Of_Social_Impact_Assessments.objects.create(id=id, **request_data)

                    # Log the activity
                    activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Updated information in table  - Details_Of_Social_Impact_Assessments"
                    }
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)

                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    assessment = Details_Of_Social_Impact_Assessments.objects.get(id=id)
                    assessment.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Details_Of_Social_Impact_Assessments"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Ongoing_Rehabilitation_And_Resettlement_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            rehabilitations = Ongoing_Rehabilitation_And_Resettlement.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(rehabilitations, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = OngoingRehabilitationAndResettlementSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            if Ongoing_Rehabilitation_And_Resettlement.objects.count() == 0:
                id = 1
            else:
                id = Ongoing_Rehabilitation_And_Resettlement.objects.aggregate(Max('id'))['id__max'] + 1
            request.data['id'] = id
            
            # Financial_Year = request.data.get('Financial_Year')
            # District = request.data.get('District')
            # State = request.data.get('State')

            # # Check if an entry already exists for the given facility and financial year
            # if Ongoing_Rehabilitation_And_Resettlement.objects.filter(Financial_Year=Financial_Year, District=District, State=State).count() > 0:
            #     return Response({'error': 'Entry for this State, District and financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = OngoingRehabilitationAndResettlementSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Ongoing_Rehabilitation_And_Resettlement"}
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
                    rehabilitation = Ongoing_Rehabilitation_And_Resettlement.objects.get(id=id)
                    with transaction.atomic():
                        Ongoing_Rehabilitation_And_Resettlement.objects.filter(id=id).delete()

                        request_data = request.data.copy()  
                        if "id" in request_data:
                            request_data.pop("id")

                        Ongoing_Rehabilitation_And_Resettlement.objects.create(id=id, **request_data)

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Edited information in table - Ongoing_Rehabilitation_And_Resettlement"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                   
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    rehabilitation = Ongoing_Rehabilitation_And_Resettlement.objects.get(id=id)
                    rehabilitation.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Ongoing_Rehabilitation_And_Resettlement"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Percentage_Of_Input_Material_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            materials = Percentage_Of_Input_Material.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(materials, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = PercentageOfInputMaterialSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            financial_year=request.data.get('Financial_Year')
            
            if Percentage_Of_Input_Material.objects.filter(Financial_Year=financial_year).count() > 0:
                return Response({'error': 'Entry for this financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
           
            if Percentage_Of_Input_Material.objects.count() == 0:
                id = 1
            else:
                id = Percentage_Of_Input_Material.objects.aggregate(Max('id'))['id__max'] + 1
            request.data['id'] = id

            serializer = PercentageOfInputMaterialSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Percentage_Of_Input_Material"}
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
                    material = Percentage_Of_Input_Material.objects.get(id=id)
                    serializer = PercentageOfInputMaterialSerializer(material, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Percentage_Of_Input_Material"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    material = Percentage_Of_Input_Material.objects.get(id=id)
                    material.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Percentage_Of_Input_Material"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class Details_Of_Actions_Taken_To_Mitigate_View(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            actions = Details_Of_Actions_Taken_To_Mitigate.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(actions, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = DetailsOfActionsTakenToMitigateSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            Financial_Year = request.data.get('Financial_Year')

            # Check if an entry already exists for the given facility and financial year
            if Details_Of_Actions_Taken_To_Mitigate.objects.filter(Financial_Year=Financial_Year).count() > 0:
                return Response({'error': 'Entry for this financial year already exists'}, status=status.HTTP_400_BAD_REQUEST)
           
            if Details_Of_Actions_Taken_To_Mitigate.objects.count() == 0:
                id = 1
            else:
                id = Details_Of_Actions_Taken_To_Mitigate.objects.aggregate(Max('id'))['id__max'] + 1
            request.data['id'] = id

            serializer = DetailsOfActionsTakenToMitigateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - Details_Of_Actions_Taken_To_Mitigate"}
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
                    action = Details_Of_Actions_Taken_To_Mitigate.objects.get(id=id)
                    serializer = DetailsOfActionsTakenToMitigateSerializer(action, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname,
                        "Activity": "Edited information in table - Details_Of_Actions_Taken_To_Mitigate"}
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    action = Details_Of_Actions_Taken_To_Mitigate.objects.get(id=id)
                    action.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - Details_Of_Actions_Taken_To_Mitigate"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    






"""
API's for Transparency and Disclosure Compliances
"""

class TransparencyAndDisclosureCompliancesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":
            compliances = TransparencyAndDisclosureCompliancesModel.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(compliances, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            response_data = []
            for compliances_obj in paginated_queryset:
                data = {
                    "id":compliances_obj.id,
                    "Financial_Year": compliances_obj.Financial_Year,
                    "Stack_Holder_Group": compliances_obj.Stack_Holder_Group,
                    "Field_Complaint": compliances_obj.Field_Complaint,
                    "Pending_Complaint": compliances_obj.Pending_Complaint,
                    "Weblink": compliances_obj.Weblink,
                    "Remarks": compliances_obj.Remarks,
                    "grievance_redressal_mechanism_in_place" : compliances_obj.grievance_redressal_mechanism_in_place
                }
                response_data.append(data)

            return Response({
                'data': response_data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }, status=status.HTTP_200_OK)
            # else:
            #     return Response({'error': 'This data can only be accessed by Company Secretary or ESG Lead.'}, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            Financial_Year = request.data.get('Financial_Year')
            Stack_Holder_Group = request.data.get('Stack_Holder_Group')
            data_exists = TransparencyAndDisclosureCompliancesModel.objects.filter(
                Financial_Year=Financial_Year,
                Stack_Holder_Group=Stack_Holder_Group
            )
            if data_exists:
                return Response({'error': 'Financial Year and Stack Holder Group already exist.'}, status=status.HTTP_400_BAD_REQUEST)

            max_id = TransparencyAndDisclosureCompliancesModel.objects.aggregate(Max('id'))['id__max']
            id = 1 if max_id is None else max_id + 1

            request.data['id'] = id
            serializer = TransparencyAndDisclosureCompliancesSerializer(data=request.data)
        
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Added information in table - TransparencyAndDisclosureCompliancesModel"
                }
                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                if activity_log_serializer.is_valid():
                    activity_log_serializer.save()

                return Response({'success': 'Data added successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                request.data['id'] = id
                Financial_Year = request.data.get('Financial_Year')
                Stack_Holder_Group = request.data.get('Stack_Holder_Group')
                data_exists = TransparencyAndDisclosureCompliancesModel.objects.filter(
                    Financial_Year=Financial_Year,
                    Stack_Holder_Group=Stack_Holder_Group
                ).exclude(id=id)
                if data_exists:
                    return Response({'error': 'Financial Year and Stack Holder Group already exist.'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    compliances_obj = TransparencyAndDisclosureCompliancesModel.objects.get(id=id)

                    serializer = TransparencyAndDisclosureCompliancesSerializer(compliances_obj, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                            "Name": request.user.firstname + " " + request.user.lastname,
                            "Activity": "Edited information in table - TransparencyAndDisclosureCompliancesModel"
                        }
                        activity_log_serializer = ActivityLogSerializer(data=activity_log)
                        if activity_log_serializer.is_valid():
                            activity_log_serializer.save()

                        return Response({'success': 'Data updated successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')
            if id is not None:
                try:
                    compliances_obj = TransparencyAndDisclosureCompliancesModel.objects.get(id=id)
                    compliances_obj.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname,
                    "Activity": "Deleted information in table - TransparencyAndDisclosureCompliances"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



"""
API's for Number_Of_Instance_Of_Data_BreacheView
"""
class Number_Of_Instance_Of_Data_BreacheView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_role = request.user.role
            # if user_role == "Company Secretary" or user_role == "ESG Lead":

            payables_obj = Number_Of_Instance_Of_Data_Breache.objects.order_by('-Financial_Year', '-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(payables_obj, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = Number_Of_Instance_Of_Data_BreacheSerializer(paginated_queryset, many=True)
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
            data = Number_Of_Instance_Of_Data_Breache.objects.filter(Financial_Year=financial_year)
            if data:
                return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if Number_Of_Instance_Of_Data_Breache.objects.count() == 0:
                id = 1
            else:
                id = Number_Of_Instance_Of_Data_Breache.objects.aggregate(Max('id'))['id__max'] + 1
            
            request.data['id'] = id

            serializer = Number_Of_Instance_Of_Data_BreacheSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                activity_log = {
                "Name": request.user.firstname + " " + request.user.lastname, 
                "Activity": "Added information in table - Number_Of_Instance_Of_Data_Breache"}
                                
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
                data = Number_Of_Instance_Of_Data_Breache.objects.filter(Financial_Year=financial_year).exclude(id=id)
                if data:
                    return Response({'error': 'Entry for this Financial Year already exists'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    payables_obj = Number_Of_Instance_Of_Data_Breache.objects.get(id=id)
                    serializer = Number_Of_Instance_Of_Data_BreacheSerializer(payables_obj, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        activity_log = {
                        "Name": request.user.firstname + " " + request.user.lastname, 
                        "Activity": "Edited information in table - Number_Of_Instance_Of_Data_Breache"}
                                        
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
                    breach_obj = Number_Of_Instance_Of_Data_Breache.objects.get(id=id)
                    breach_obj.delete()

                    activity_log = {
                    "Name": request.user.firstname + " " + request.user.lastname, 
                    "Activity": "Deleted information in table - Number_Of_Instance_Of_Data_Breache"}
                                    
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()

                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except Number_Of_Instance_Of_Data_Breache.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
