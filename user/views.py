from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers import serialize
from django.contrib.auth import authenticate, login
from Activity_Log.serializers import ActivityLogSerializer
from rest_framework_simplejwt.tokens import AccessToken

from . import models
from . import serializers
from django.shortcuts import render
from .models import User
from django.db.models import Max
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import APIException

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404

from .serializers import *
from .choices import *
from django.db.models import Q
from .permissions_constant import esg_lead_permissions, role_wise_permissions, user_permissions
# Create your views here.
class UserSignup(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            role = request.query_params.get('role', None)
            full_name = request.query_params.get('query_parameters', None)
            
            filters = Q()
            
            if role:
                filters &= Q(role__icontains=role)
                
            if full_name:
                # Normalize and split the search term
                name_parts = full_name.strip().split()
                if len(name_parts) == 1:
                    filters &= (
                        Q(firstname__icontains=name_parts[0]) |
                        Q(lastname__icontains=name_parts[0]) |
                        Q(employee_code__icontains=name_parts[0])
                    )
                else:
                    for name_part in name_parts:
                        filters &= (
                            Q(firstname__icontains=name_part) |
                            Q(employee_code__icontains=name_part) |
                            Q(lastname__icontains=name_part)
                        )
            
            # Fetch filtered users
            users = User.objects.filter(filters).order_by('-id')

            # Pagination
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(users, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = UserSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def post(self, request):
    #     if User.objects.count() == 0:
    #         id = 1
    #     else:
    #         id = User.objects.aggregate(Max('id'))['id__max'] + 1
        
        
    #     request.data['id'] = id

    #     if User.objects.filter(email=request.data.get("email")).count() > 0:

    #         return Response({'error':'User already exists'}, status=status.HTTP_400_BAD_REQUEST)

    #     if request.data.get("password") != request.data.get("confirm_password"):
    #         return Response({'error': 'Confirm password should be same as password'}, status=status.HTTP_400_BAD_REQUEST)

    #     # employee_code = self.generate_employee_code()
    #     # request.data['employee_code'] = employee_code

    #     # sub_business_unit_list = request.data.get('sub_business_unit')

    #     # sub_business_unit_dict = {str(index): value for index, value in enumerate(sub_business_unit_list)}

    #     # request.data['sub_business_unit'] = sub_business_unit_dict
          
    #     serializer = UserSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({'success': 'Member successfully signed up'}, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    
   
    
    
    
    def post(self, request):
        # Generate a unique ID for the user
        user_count = User.objects.count()
        user_id = 1 if user_count == 0 else User.objects.aggregate(Max('id'))['id__max'] + 1
        request.data['id'] = user_id

        # Check if the email already exists
        count=User.objects.filter(email=request.data.get("email")).count()
        if count >0 :
            return Response({'error': 'User is already exist with this Email.' }, status=status.HTTP_400_BAD_REQUEST)

        count_2=User.objects.filter(employee_code=request.data.get("employee_code")).count()
        if count_2 >0 :
            return Response({'error': 'User is already exist with this employee code.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if password and confirm password match
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")
        if password != confirm_password:
            return Response({'error': 'Confirm password should be the same as password'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            for section, page_obj in esg_lead_permissions.items() if user.role == 'ESG Lead' else user_permissions.items():
                for page, sub_page_obj in page_obj.items():
                    for sub_page, sub_page_permissions in sub_page_obj.items():
                        access_count = EmployeesAccessControl.objects.count()
                        access_id = 1 if access_count == 0 else EmployeesAccessControl.objects.aggregate(Max('id'))['id__max'] + 1
                        access_control_data = {'id': access_id, 'employee_name': user.firstname + ' ' + user.lastname, 'employee_code': user.employee_code, 'role': [user.role], 'section': section, 'page': page, 'sub_page': sub_page, 'permissions': sub_page_permissions}
                        employees_access_control_serializer = EmployeesAccessControlSerializer(data=access_control_data)
                        if employees_access_control_serializer.is_valid():
                            employees_access_control_serializer.save()

            user_role_permissions = role_wise_permissions.get(user.role, None)
            if user_role_permissions:
                for section, page_obj in user_role_permissions.items():
                    for page, sub_page_obj in page_obj.items():
                        for sub_page, sub_page_permissions in sub_page_obj.items():
                            access_count = EmployeesAccessControl.objects.filter(employee_code=user.employee_code, section=section, page=page,sub_page=sub_page).last()
                            access_count.permissions = sub_page_permissions
                            access_count.save()
            # Determine the password reset link based on the environment
            # password_reset_link = settings.PASSWORD_RESET_LINK
            
            
            host = request.get_host().split(":")[0]
            if host == "localhost" or host == "127.0.0.1":
                password_reset_link = "http://localhost:3000/forgot-password"
            else:
                password_reset_link = "http://kpcl-c6.indi4.io/forgot-password"
                
                
            # Prepare email content
            email_subject = "Welcome to C6"
            # email_body = f"""
            # Dear {user.firstname},

            # Welcome to C6! We are delighted to have you join our team.
            # As part of your onboarding process, we have created an account for you.

            # Your account credentials:
            # - Email: {user.email}
            # - Password: {password}

            # Steps:
            # 1. Sign in using the provided credentials.
            # 2. Follow <a href="{password_reset_link}">{password_reset_link}</a> to update your password.
            # 3. Start accessing your account.

            # Best regards,<br>
            # C6 Team
            # """
            
            email_body = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <style>
                                    body {{
                                        font-family: Arial, sans-serif;
                                        background-color: #f4f4f4;
                                        margin: 0;
                                        padding: 0;
                                    }}
                                    .email-container {{
                                        max-width: 600px;
                                        margin: 20px auto;
                                        background: #ffffff;
                                        border: 1px solid #dddddd;
                                        border-radius: 8px;
                                        padding: 20px;
                                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                                    }}
                                    .email-header {{
                                        text-align: center;
                                        padding: 10px 0;
                                        background-color: #008000;
                                        color: white;
                                        border-radius: 8px 8px 0 0;
                                    }}
                                    .email-header h1 {{
                                        margin: 0;
                                        font-size: 24px;
                                    }}
                                    .email-content {{
                                        padding: 20px;
                                        color: #333333;
                                        line-height: 1.6;
                                    }}
                                    .email-footer {{
                                        margin-top: 20px;
                                        font-size: 12px;
                                        text-align: center;
                                        color: #777777;
                                    }}
                                    .button {{
                                        display: inline-block;
                                        padding: 10px 20px;
                                        font-size: 16px;
                                        margin: 20px 0;
                                        text-align: center;
                                        color:white !important;
                                        background-color:#008000;
                                        border: none;
                                        border-radius: 4px;
                                        text-decoration: none;
                                    }}
                                    .button:hover {{
                                        background-color:#006400;
                                        color:black !important
                                    }}
                                    
                                </style>
                            </head>
                            <body>
                                <div class="email-container">
                                    <div class="email-header">
                                        <h1>Welcome to C6</h1>
                                    </div>
                                    <div class="email-content">
                                        <p>Dear <strong>{user.firstname}</strong>,</p>
                                       
                                        <p>Your account credentials:</p>
                                        <ul>
                                            <li><strong>Email:</strong> {user.email}</li>
                                            <li><strong>Password:</strong> {password}</li>
                                        </ul>
                                        <p>Steps to access your account:</p>
                                        <ol>
                                            <li>Sign in using the provided credentials.</li>
                                            <li>
                                                Follow this link to update your password: 
                                                <a href="{password_reset_link}" class="button">Reset Password</a>
                                            </li>
                                            <li>Start accessing your account.</li>
                                        </ol>
                                        <p>Best regards,<br><strong>C6 Team</strong></p>
                                    </div>
                                    <div class="email-footer">
                                        <p>This email was sent from the C6 system. If you have any questions, please contact us at test.dev@indi4.io.</p>
                                    </div>
                                </div>
                            </body>
                            </html>
                            """


            # Send the email
            send_mail(
                subject=email_subject,
                message="",  # Leave plain text empty since we're using HTML
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=email_body,  # Use HTML content
                fail_silently=False,
            )
            token = request.headers.get('Authorization', None)
            if token:
                try:
                    token = token.split(' ')[1] if token.startswith('Bearer') else token
                    access_token = AccessToken(token)
                    user_id = access_token['user_id']
                    data = User.objects.filter(email = user_id).first()

                    activity_log = {
                                "Name": data.firstname + " " + data.lastname,
                                "Activity": "Added information in table - User"}
                    activity_log_serializer = ActivityLogSerializer(data=activity_log)
                    if activity_log_serializer.is_valid():
                        activity_log_serializer.save()
                except Exception as e:
                    pass
            return Response({'success': 'Member successfully signed up, and email sent'}, status=status.HTTP_201_CREATED)
        else:
            # Handle validation errors
            first_field, first_error = next(iter(serializer.errors.items()))
            error_message = f"{first_field}: {first_error[0]}" if isinstance(first_error, list) else f"{first_field}: {first_error}"
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)


    def generate_employee_code(self):
        document_count = User.objects.count()
        if document_count == 0:
            employee_code = "EC100"
        else:
            max_employee_code = User.objects.aggregate(max_employee_code=Max('employee_code'))['max_employee_code']
            employee_code = "EC" + str(int(max_employee_code[2:]) + 1)
        return employee_code
    

    def put(self, request, **kwargs):
        try:
            
            mail= request.query_params.get('email')
           
            if mail is not None:
                try:
                    user_instance = User.objects.get(email=mail)
                    request.data['id'] = user_instance.id
                    # confirm_password
                    if request.data['password'] != request.data['confirm_password']:
                        return Response({'error': 'Password and Confirm password should be same.'}, status=400)
                    serializer = UserSerializer(user_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()

                        old_access = EmployeesAccessControl.objects.filter(employee_code=serializer.data.get('employee_code'))
                        old_access.delete()

                        for section, page_obj in esg_lead_permissions.items() if serializer.data.get('role') == 'ESG Lead' else user_permissions.items():
                            for page, sub_page_obj in page_obj.items():
                                for sub_page, sub_page_permissions in sub_page_obj.items():
                                    access_count = EmployeesAccessControl.objects.count()
                                    access_id = 1 if access_count == 0 else EmployeesAccessControl.objects.aggregate(Max('id'))['id__max'] + 1
                                    access_control_data = {'id': access_id,'employee_name': serializer.data.get('firstname')  + ' ' + serializer.data.get('lastname'),  'employee_code': serializer.data.get('employee_code'), 'role': [serializer.data.get('role')], 'section': section, 'page': page, 'sub_page': sub_page, 'permissions': sub_page_permissions}
                                    employees_access_control_serializer = EmployeesAccessControlSerializer(data=access_control_data)
                                    if employees_access_control_serializer.is_valid():
                                        employees_access_control_serializer.save()

                        user_role_permissions = role_wise_permissions.get(serializer.data.get('role'), None)
                        if user_role_permissions:
                            for section, page_obj in user_role_permissions.items():
                                for page, sub_page_obj in page_obj.items():
                                    for sub_page, sub_page_permissions in sub_page_obj.items():
                                        access_count = EmployeesAccessControl.objects.filter(employee_code=serializer.data.get('employee_code'), section=section, page=page,sub_page=sub_page).last()
                                        access_count.permissions = sub_page_permissions
                                        access_count.save()

                        token = request.headers.get('Authorization', None)
                        if token:
                            try:
                                token = token.split(' ')[1] if token.startswith('Bearer') else token
                                access_token = AccessToken(token)
                                user_id = access_token['user_id']
                                data = User.objects.filter(email = user_id).first()

                                activity_log = {
                                            "Name": data.firstname + " " + data.lastname,
                                            "Activity": "Updated information in table - User"}
                                activity_log_serializer = ActivityLogSerializer(data=activity_log)
                                if activity_log_serializer.is_valid():
                                    activity_log_serializer.save()
                            except Exception as e:
                                pass
                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response(e)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
    def delete(self, request, **kwargs):
        try:
            token = request.headers.get('Authorization', None)

            if token is None:
                return Response({"error": "Authorization credential or Token required."}, status=status.HTTP_400_BAD_REQUEST)
            token = token.split(' ')[1] if token.startswith('Bearer') else token
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            
            email = request.query_params.get('email')
            
            if user_id == email:
                return Response({"error": "You cannot delete your own account."}, status=status.HTTP_400_BAD_REQUEST)
            
            if email is not None:
                try:
                    user = User.objects.get(email=email)
                    employee_code = user.employee_code
                    user.delete()
                    try:
                        user_access = EmployeesAccessControl.objects.filter(employee_code=employee_code)
                        user_access.delete()
                    except ObjectDoesNotExist:
                        pass

                    token = request.headers.get('Authorization', None)
                    if token:
                        try:
                            token = token.split(' ')[1] if token.startswith('Bearer') else token
                            access_token = AccessToken(token)
                            user_id = access_token['user_id']
                            data = User.objects.filter(email = user_id).first()

                            activity_log = {
                                        "Name": data.firstname + " " + data.lastname,
                                        "Activity": "Deleted information in table - User"}
                            activity_log_serializer = ActivityLogSerializer(data=activity_log)
                            if activity_log_serializer.is_valid():
                                activity_log_serializer.save()
                        except Exception as e:
                            pass
                    return Response({'success':'Data deleted successfully'},status=status.HTTP_204_NO_CONTENT)
                except User.DoesNotExist:
                    return Response({'error':'Record not found'},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)     



class UserLogin(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            # import pdb;pdb.set_trace()
            if request.method == 'POST':
                email = request.data.get('email')
                password = request.data.get('password')
            
                user = User.objects.filter(email=email).first()
                
                if user and  user.status == "INACTIVE":
                    return Response({'error': 'Your account is inactive. Please contact admin.'}, status=status.HTTP_403_FORBIDDEN)
                
                if user is None:
                    return Response({"error": "The logged-in user does not exist or has been deleted"}, status=status.HTTP_404_NOT_FOUND)
                
                role = user.role

                employees_code = user.employee_code
                location = user.location

                full_name = f"{user.firstname} {user.lastname}"


                if user:
                    if user.password == password:  
                        permissions = EmployeesAccessControl.objects.filter(id=user.id).first()
                        permissions = permissions.permissions if permissions else None
                            
                        refresh = RefreshToken.for_user(user)
                        return Response({
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                            'role':role,
                            'permissions' : permissions,
                            'employee_code' :employees_code,
                            'location':location,


                            'name':full_name,
                            'message':'User Logged in Successfully'

                        }, status=status.HTTP_200_OK)
                    else:
                        # Password is incorrect
                        return Response({"error": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # User with given email doesn't exist
                    return Response({"error":"User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

class TokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is missing'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            return Response({'access': access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
        

class UserStatus_View(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, **kwargs):
        try:
            email= kwargs.get('email')
            if email is not None:
                try:
                    user_instance = User.objects.get(email=email)

                    if user_instance.status == "Active":
                        request.data["status"] = "Inactive"
                    else:
                        request.data["status"] = "Active"

                    serializer = UserSerializer(user_instance, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({'success': 'Data updated successfully.'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error':'id not found'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        


class UserRolesList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            roles_list = ROLES

            if not roles_list:
                return Response({'error': 'Roles list is empty or not defined'}, status=status.HTTP_404_NOT_FOUND)

            return Response(roles_list, status=status.HTTP_200_OK)

        except NameError:
            return Response({'error': 'Roles list is not defined'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Access_Control_View(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Set the new ID
            if Access_Control.objects.count() == 0:
                id = 1
            else:
                id = Access_Control.objects.aggregate(Max('id'))['id__max'] + 1

            request.data['id'] = id

            # Handle incoming request data
            role = request.data.get('Role')
            if role:
                # Creating the structured role representation
                role_data = {
                    "Role": role,
                    "Details": {
                        "Section": request.data.get('Section'),
                        "Page_Name": request.data.get('Page_Name'),
                        "Sub_Page_Name": request.data.get('Sub_Page_Name'),
                        "Menu_Access": request.data.get('Menu_Access'),
                        "View": request.data.get('View', True),  # Default to True
                        "Add": request.data.get('Add', False),
                        "Edit": request.data.get('Edit', False),
                        "Delete": request.data.get('Delete', False)
                    }
                }
                
                # Flattening role_data for saving in the database
                request.data.update(role_data["Details"])
                # The Role field in request.data will already contain the correct value

            # Serialize and save data
            serializer = Access_ControlSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': 'Access added successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            # Fetch all records from the model
            access_controls = Access_Control.objects.all().order_by('-id')
            
            # Set default page size, can be customized via query param
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(access_controls, page_size)
            
            # Get the requested page number, default is 1
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            # Serialize the paginated data
            serializer = Access_ControlSerializer(paginated_queryset, many=True)
            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request, **kwargs):
        try:
            id = kwargs.get('id')  # Get the ID from the URL
            if id is not None:
                try:
                    # Find the instance by ID
                    plant_operations_instance = Access_Control.objects.get(id=id)
                    
                    # Pass the instance and updated data to the serializer
                    serializer = Access_ControlSerializer(plant_operations_instance, data=request.data)
                    
                    if serializer.is_valid():
                        serializer.save()  # Save the updated data
                        return Response({'success': 'Access updated successfully.'}, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                except Access_Control.DoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, **kwargs):
        try:
            id = kwargs.get('id')  
            if id is not None:
                try:
                    # Find the instance by ID
                    plant_operations_instance = Access_Control.objects.get(id=id)
                    
                    # Delete the instance
                    plant_operations_instance.delete()
                    
                    return Response({'success': 'Access deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                
                except Access_Control.DoesNotExist:
                    return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccessControlByRoleView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
    
        try:
            role = request.query_params.get('role')
            access_controls = Access_Control.objects.filter(Role=role).order_by('-id')
            page_size = request.query_params.get('page_size', 5)
            paginator = Paginator(access_controls, page_size)
            page_number = request.query_params.get('page', 1)

            try:
                paginated_queryset = paginator.page(page_number)
            except EmptyPage:
                return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
            except PageNotAnInteger:
                return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = Access_ControlSerializer(paginated_queryset, many=True)

            response_data = {
                'data': serializer.data,
                'page': int(page_number),
                'total_pages': paginator.num_pages,
                'count': paginator.count,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# class Human_Resoursce_Access_Control_View(APIView):
#     permission_classes = [IsAuthenticated]

#     # POST method for creating new records
#     def post(self, request):
#         try:
#             # Assign new id
#             if Human_Resoursce_Access_Control.objects.count() == 0:
#                 id = 1
#             else:
#                 id = Human_Resoursce_Access_Control.objects.aggregate(Max('id'))['id__max'] + 1

#             request.data['id'] = id

#             # Serialize and validate the incoming data
#             serializer = Human_Resoursce_Access_ControlSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({'message': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

   
#     def get(self, request):
#         try:
#             # Fetch all records from the model
#             access_controls = Human_Resoursce_Access_Control.objects.all().order_by('id')

#             # Set default page size, customizable via query param
#             page_size = request.query_params.get('page_size', 5)
#             paginator = Paginator(access_controls, page_size)

#             # Get the requested page number, default is 1
#             page_number = request.query_params.get('page', 1)

#             try:
#                 paginated_queryset = paginator.page(page_number)
#             except EmptyPage:
#                 return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
#             except PageNotAnInteger:
#                 return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

#             # Serialize the paginated data
#             serializer = Human_Resoursce_Access_ControlSerializer(paginated_queryset, many=True)
#             response_data = {
#                 'data': serializer.data,
#                 'page': int(page_number),
#                 'total_pages': paginator.num_pages,
#                 'count': paginator.count,
#             }
#             return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

   
#     def put(self, request, **kwargs):
#         try:
#             id = kwargs.get('id') 
#             if id is not None:
#                 try:
#                     # Find the instance by ID
#                     hr_access_instance = Human_Resoursce_Access_Control.objects.get(id=id)

#                     # Serialize and validate the incoming data
#                     serializer = Human_Resoursce_Access_ControlSerializer(hr_access_instance, data=request.data)
#                     if serializer.is_valid():
#                         serializer.save()  # Save the updated data
#                         return Response({'message': 'Data updated successfully.'}, status=status.HTTP_200_OK)
#                     else:
#                         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#                 except Human_Resoursce_Access_Control.DoesNotExist:
#                     return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
#     def delete(self, request, **kwargs):
#         try:
#             id = kwargs.get('id')  # Get the ID from the URL
#             if id is not None:
#                 try:
#                     # Find the instance by ID
#                     hr_access_instance = Human_Resoursce_Access_Control.objects.get(id=id)

#                     # Delete the instance
#                     hr_access_instance.delete()

#                     return Response({'message': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

#                 except Human_Resoursce_Access_Control.DoesNotExist:
#                     return Response({'message': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class Finance_Access_Control_View(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         try:
#             # Assign new id
#             if Finance_Access_Control.objects.count() == 0:
#                 id = 1
#             else:
#                 id = Finance_Access_Control.objects.aggregate(Max('id'))['id__max'] + 1

#             request.data['id'] = id

#             # Serialize and validate the incoming data
#             serializer = Finance_Access_ControlSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({'message': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
#     def get(self, request):
#         try:
#             # Fetch all records from the model
#             access_controls = Finance_Access_Control.objects.all().order_by('id')

#             # Set default page size, customizable via query param
#             page_size = request.query_params.get('page_size', 5)
#             paginator = Paginator(access_controls, page_size)

#             # Get the requested page number, default is 1
#             page_number = request.query_params.get('page', 1)

#             try:
#                 paginated_queryset = paginator.page(page_number)
#             except EmptyPage:
#                 return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
#             except PageNotAnInteger:
#                 return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

#             # Serialize the paginated data
#             serializer = Finance_Access_ControlSerializer(paginated_queryset, many=True)
#             response_data = {
#                 'data': serializer.data,
#                 'page': int(page_number),
#                 'total_pages': paginator.num_pages,
#                 'count': paginator.count,
#             }
#             return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

   
#     def put(self, request, **kwargs):
#         try:
#             id = kwargs.get('id')  # Get the ID from the URL
#             if id is not None:
#                 try:
#                     # Find the instance by ID
#                     finance_access_instance = Finance_Access_Control.objects.get(id=id)

#                     # Serialize and validate the incoming data
#                     serializer = Finance_Access_ControlSerializer(finance_access_instance, data=request.data)
#                     if serializer.is_valid():
#                         serializer.save()  # Save the updated data
#                         return Response({'message': 'Data updated successfully.'}, status=status.HTTP_200_OK)
#                     else:
#                         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#                 except Finance_Access_Control.DoesNotExist:
#                     return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  
#     def delete(self, request, **kwargs):
#         try:
#             id = kwargs.get('id')  # Get the ID from the URL
#             if id is not None:
#                 try:
#                     # Find the instance by ID
#                     finance_access_instance = Finance_Access_Control.objects.get(id=id)

#                     # Delete the instance
#                     finance_access_instance.delete()

#                     return Response({'message': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

#                 except Finance_Access_Control.DoesNotExist:
#                     return Response({'message': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class Company_Secretary_Access_Control_View(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         try:
#             if Company_Secretary_Access_Control.objects.count() == 0:
#                 id = 1
#             else:
#                 id = Company_Secretary_Access_Control.objects.aggregate(Max('id'))['id__max'] + 1

#             request.data['id'] = id
#             serializer = Company_Secretary_Access_ControlSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({'message': 'Data added successfully.'}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

   
#     def get(self, request):
#         try:
#             access_controls = Company_Secretary_Access_Control.objects.all().order_by('id')

#             page_size = request.query_params.get('page_size', 5)
#             paginator = Paginator(access_controls, page_size)

#             page_number = request.query_params.get('page', 1)

#             try:
#                 paginated_queryset = paginator.page(page_number)
#             except EmptyPage:
#                 return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
#             except PageNotAnInteger:
#                 return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)

#             # Serialize the paginated data
#             serializer = Company_Secretary_Access_ControlSerializer(paginated_queryset, many=True)
#             response_data = {
#                 'data': serializer.data,
#                 'page': int(page_number),
#                 'total_pages': paginator.num_pages,
#                 'count': paginator.count,
#             }
#             return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

   
#     def put(self, request, **kwargs):
#         try:
#             id = kwargs.get('id')  
#             if id is not None:
#                 try:
                  
#                     company_secretary_instance = Company_Secretary_Access_Control.objects.get(id=id)

#                     serializer = Company_Secretary_Access_ControlSerializer(company_secretary_instance, data=request.data)
#                     if serializer.is_valid():
#                         serializer.save()  # Save the updated data
#                         return Response({'message': 'Data updated successfully.'}, status=status.HTTP_200_OK)
#                     else:
#                         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#                 except Company_Secretary_Access_Control.DoesNotExist:
#                     return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
#     def delete(self, request, **kwargs):
#         try:
#             id = kwargs.get('id')
#             if id is not None:
#                 try:
#                     company_secretary_instance = Company_Secretary_Access_Control.objects.get(id=id)

#                     company_secretary_instance.delete()

#                     return Response({'message': 'Data deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

#                 except Company_Secretary_Access_Control.DoesNotExist:
#                     return Response({'message': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SendPasswordResetLink(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        email = request.data.get('email')
        try:
            user = get_object_or_404(User, email=email)
            # Generate a unique token
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            # print("token:",token,"----------------------------")
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # print("uid:",uid,"----------------------------")
            host = request.get_host().split(":")[0]
        
            if host == "localhost" or host == "127.0.0.1":
                frontend_url = "localhost:3000"
                reset_link = f"{request.scheme}://{frontend_url}/reset-password/{uid}/{token}/"
            else:
                frontend_url = "kpcl-c6.indi4.io"
                reset_link = f"{request.scheme}://{frontend_url}/reset-password/{uid}/{token}/"

            # Send email with plain text
            subject = "Password Reset Request"
            message = (
                f"Hello {user.firstname},\n\n"  
                f"You requested to reset your password. Use the link below to reset it:\n\n"
                f"{reset_link}\n\n"
                f"If you didn’t request this, please ignore this email.\n\n"
                f"Thank you."
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            return Response({"success": "Password reset link sent to your email.",
                             "token":token,"uid":uid}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ResetPassword(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            # Validate token
            token_generator = PasswordResetTokenGenerator()
            if token_generator.check_token(user, token):
                new_password = request.data.get("new_password")
                confirm_password = request.data.get("confirm_password")

                if new_password != confirm_password:
                    return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

                user.password = new_password 
                user.save()

                return Response({"success": "Password reset successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def error_formatter(errors):
    errors = errors
    # formatted_errors = []
    for field, messages in errors.items():
        for message in messages:
            # formatted_errors.append(f"'{field}': {message}")
            return f"'{field}': {message}"

class EmployeesAccessControlAPI(APIView):
    def get(self, request, id=None):
        # import pdb; pdb.set_trace()
        employee_code = request.query_params.get('employee_code', None)
        if employee_code:
            try:
                employee_access = EmployeesAccessControl.objects.filter(employee_code=employee_code).order_by('-id')
                serializer = EmployeesAccessControlSerializer(employee_access, many=True)
                return Response({'data': serializer.data}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            try:
                employee_accesses = EmployeesAccessControl.objects.all().order_by('-id')

                # page_size = request.query_params.get('page_size', 5)
                # paginator = Paginator(employee_accesses, page_size)
                # page_number = request.query_params.get('page', 1)

                # try:
                #     paginated_queryset = paginator.page(page_number)
                # except EmptyPage:
                #     return Response({'error': f'No data available on Page Number {page_number}'}, status=status.HTTP_204_NO_CONTENT)
                # except PageNotAnInteger:
                #     return Response({'error': f'Invalid Page Number {page_number}'}, status=status.HTTP_400_BAD_REQUEST)
                serializer = EmployeesAccessControlSerializer(employee_accesses, many=True)
                response_data = {
                    'data': serializer.data,
                    # 'page': int(page_number),
                    # 'total_pages': paginator.num_pages,
                    # 'count': paginator.count,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def post(self, request):
        try:
            if EmployeesAccessControl.objects.count() == 0:
                id = 1
            else:
                id = EmployeesAccessControl.objects.aggregate(Max('id'))['id__max'] + 1
            
            request.data['id'] = id
        
            request_data = request.data
            employee_code = request_data.get("employee_code")
            section = request_data.get("section")
            page = request_data.get("page")
            sub_page = request_data.get("sub_page")

            if not employee_code:
                return Response({"error" : "Employee code required."}, status=status.HTTP_400_BAD_REQUEST)
            
            query_obj = User.objects.get(employee_code=employee_code)
            if query_obj:
                if query_obj.role == 'ESG Lead':
                    return Response({"error" : "Can't grant access to ESG Lead."}, status=status.HTTP_400_BAD_REQUEST)
            
            if EmployeesAccessControl.objects.filter(employee_code=employee_code,section=section,page=page,sub_page=sub_page).count() > 0:
                return Response({"error": f"Employees Access Control already exist for employee {employee_code} with {section}, {page} and {sub_page}"}, status=status.HTTP_400_BAD_REQUEST)
            serializer = EmployeesAccessControlSerializer(data=request_data)
            if serializer.is_valid():
                serializer.save()
                return Response({"success" : "Access added successfully."}, status=status.HTTP_201_CREATED)
            return Response({"error": error_formatter(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def put(self, request, id=None):
        try:
            # import pdb; pdb.set_trace()
            payload = request.data.get('data')
            # print('payload: ', payload)
            for obj in payload:
                # print('obj: ', obj)
                id = obj.get('id')
                # request.data['id'] = id
                employee_access = EmployeesAccessControl.objects.get(id=id)
                serializer = EmployeesAccessControlSerializer(employee_access, data=obj, partial=True)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response({"error": error_formatter(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
            # request.data['id'] = id
            # employee_access = EmployeesAccessControl.objects.get(id=id)
            # serializer = EmployeesAccessControlSerializer(employee_access, data=request.data, partial=True)
            # if serializer.is_valid():
            #     serializer.save()
            return Response({"success" : "Access updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, id=None):
        try:
            try:
                employee_access = EmployeesAccessControl.objects.get(id=id)
            except EmployeesAccessControl.DoesNotExist:
                return Response({"error": "Invalid id passed."}, status=status.HTTP_400_BAD_REQUEST)
            employee_access.delete()
            return Response({"success": "Access deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmployeeRole(APIView):
    def get(self, request):
        try:
            employee_code = request.query_params.get('employee_code', None)
            if not employee_code:
                return Response({"error" : "Employee code required."}, status=status.HTTP_400_BAD_REQUEST)
            
            response_data = []
            query_obj = User.objects.get(employee_code=employee_code)
            if query_obj:
                response_data.append(query_obj.role)
            else:
                return Response({"error" : "User not exist with this employee code"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"roles" : response_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmployeeCodes(APIView):
    def get(self, request):
        try:
            employee_code = request.query_params.get('employee_code', None)
            filters = Q()
            
            if employee_code:
                name_parts = employee_code.strip().split()
                if len(name_parts) == 1:
                    filters &= (
                        Q(firstname__icontains=name_parts[0]) |
                        Q(lastname__icontains=name_parts[0]) |
                        Q(employee_code__icontains=name_parts[0])
                    )
                else:
                    for name_part in name_parts:
                        filters &= (
                            Q(firstname__icontains=name_part) |
                            Q(employee_code__icontains=name_part) |
                            Q(lastname__icontains=name_part)
                        )
            
                users = User.objects.filter(filters)
            else:
                users = User.objects.all()
            serializer = EmployeeCodeNameSerializer(users, many=True)

            return Response({"data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

class ProjectAccess(APIView):
    # def get(self, request):
    #     try:
    #         employee_code = request.query_params.get('employee_code', None)
    #         if employee_code:
    #             access_obj = EmployeesAccessControl.objects.filter(employee_code=employee_code)
    #         else:
    #             return Response({"error": "Invalid id passed."}, status=status.HTTP_400_BAD_REQUEST)

    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get(self, request):
        try:

            employee_code = request.query_params.get('employee_code', None)
            # user_queryset = User.objects.filter(Q(employee_code=employee_code)).first()
            # if user_queryset:
            #     if user_queryset.role == 'ESG Lead':
            #         return Response(esg_lead_permissions, status=status.HTTP_200_OK)
            if not employee_code:
                return Response({"error": "employee_code parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

            queryset = EmployeesAccessControl.objects.filter(employee_code=employee_code).order_by('-id')

            grouped_data = {}
            # for obj in queryset:
            #     section = obj.section
            #     page = obj.page
            #     sub_page = obj.sub_page
            #     permissions = obj.permissions

            #     if section not in grouped_data:
            #         grouped_data[section] = {}

            #     if page not in grouped_data[section]:
            #         grouped_data[section][page] = {}

            #     grouped_data[section][page][sub_page] = permissions
            for obj in queryset:
                section, page, sub_page, permissions = obj.section, obj.page, obj.sub_page, obj.permissions
                grouped_data.setdefault(section, {}).setdefault(page, {})[sub_page] = permissions
            for section, pages in grouped_data.items():
                for page, sub_pages in pages.items():
                    grouped_data[section][page]["is_show"] = any(bool(permissions) for sub_page, permissions in sub_pages.items())

            return Response(grouped_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)