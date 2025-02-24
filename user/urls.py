from django.urls import path
from . import views


urlpatterns = [
    path('user_signup/', views.UserSignup.as_view(), name='add_get_User_signup'),
    path('user_signup/<email>/', views.UserSignup.as_view(), name='update_delete_User_signup'),
    path('user_login/', views.UserLogin.as_view(), name='User_login'),
    path('user/<email>/status/', views.UserStatus_View.as_view(), name='User_status'),
    path('roles/', views.UserRolesList.as_view(), name='User_Role_List'),
    
    path('access_control/', views.Access_Control_View.as_view(), name='get_add_Plant_Operations_Access_Control'),
    path('access_control/<int:id>/', views.Access_Control_View.as_view(), name='put_delete_Plant_Operations_Access_Control'),
    path('access-control/',views.AccessControlByRoleView.as_view(), name='access-control-by-role'),


    path('send_reset_password_link/', views.SendPasswordResetLink.as_view(), name='send-reset-password-link'),
    path('reset_password/<str:uidb64>/<str:token>/', views.ResetPassword.as_view(), name='reset-password'),




    path('employee-access-control/', views.EmployeesAccessControlAPI.as_view(), name='employee_access_control_list'),
    path('employee-access-control/<int:id>/', views.EmployeesAccessControlAPI.as_view(), name='employee_access_control_detail'),
    path('employee-role/', views.EmployeeRole.as_view(), name='employee_role'),
    path('employee-code/', views.EmployeeCodes.as_view(), name='employee_code'),
    path('project-access/', views.ProjectAccess.as_view(), name='project_access'),

    






    # path('test/', views.GetUserDetails.as_view(), name='test'),
]