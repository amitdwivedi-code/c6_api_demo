from django.urls import path
from . import views

urlpatterns = [
    path('', views.Descriptions_View.as_view(), name='add_get_Descriptions'),
    path('<int:id>/', views.Descriptions_View.as_view(), name='update_descriptions'),
    path('descriptions_project_policies/', views.DescriptionsAnotherAPIView.as_view(),name = 'list'),
    path('descriptions_project_policies/<str:ids>/', views.DescriptionsAnotherAPIView.as_view(),name='get,edit'),
]