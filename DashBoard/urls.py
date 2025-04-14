from django.urls import path
from . import views


urlpatterns = [
    path('companydetails_dashboard/', views.Companydetails_Dashboard.as_view(), name='get_turnover_networth_data'),
    






]