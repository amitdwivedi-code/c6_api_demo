from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('brs_policy1/', views.Brs_Policy1_View.as_view(), name='add_get_brs_policy_1'),
    path('brs_policy1/<str:id>/', views.Brs_Policy1_View.as_view(), name='update_brs_policy_1'),
    
    path('brs_policy1a/', views.Brs_Policy1a_View.as_view(), name='add_get_brs_policy_1'),
    path('brs_policy1a/<int:id>/', views.Brs_Policy1a_View.as_view(), name='update_brs_policy_1'),
    
    
    path('brs_policy2/', views.Brs_Policy2_View.as_view(), name='add_get_brs_policy_1'),
    path('brs_policy2/<int:id>/', views.Brs_Policy2_View.as_view(), name='update_brs_policy_1'),
    
    path('frequency_of_engagement/',views.FrequencyOfEngagementView.as_view(), name='frequency-of-engagement'),
    
    
    
]