from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.ActivityLog_View.as_view(), name='get_activity_log'),
    path('brs_report_log/', views.BrsLog_View.as_view(), name='get_brs_log'),

]