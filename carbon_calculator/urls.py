from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


# Swagger

from rest_framework import permissions 
from drf_yasg.views import get_schema_view 
from drf_yasg import openapi 

  
schema_view = get_schema_view( 
   openapi.Info( 
      title="C6_API", 
      default_version='v1', 
      description="API Documenation", 
      terms_of_service="https://www.google.com/policies/terms/", 
      contact=openapi.Contact(email="contact@dummy.local"), 
      license=openapi.License(name="BSD License"), 
   ), 
   public=True, 
   permission_classes=(permissions.AllowAny,)
) 



from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('user/', include('user.urls')),
    path('brs_policy/', include('BRS.urls')),
    path('company_details/', include('CompanyDetails.urls')),
    path('workplace/',include('Workplace.urls')),
    path('environment/', include('Environment.urls')),
    path('descriptions/', include('Descriptions.urls')),
    path('community/', include('Community.urls')),
    path('activity_log/', include('Activity_Log.urls')),
    path('brs_policy/', include('BRS.urls')),
    path('reports/', include('Reports.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'), 
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
   
   
    
    # path('fuel/', include('Fuel.urls')),
    # path('environment/principle_6_report/', include('Principle_6_Report.urls')),
    # path('environment/emissions/', include('Emissions.urls')),
    # path('transport/', include('Transport.urls')),
    
    
    # path('environment/life_cycle/', include('Life_Cycle.urls')),
    # path('environment/water/',include('Water.urls')),
    # path('environment/waste/',include('Waste.urls')),
    # path('environment/energy/',include('Energy.urls')),
    # path('workplace/workforce/',include('WorkForce.urls')),
    # path('workplace/training/',include('Training.urls')),
    # path('workplace/grievances/',include('Grievances.urls')),
    # path('workplace/health_and_safety/',include('Health_And_Safety.urls')),
    # path('workplace/grievances/',include('Grievances.urls')),
    # path('workplace/policies_and_penalties/',include('Policies_and_Penalties.urls')),
    # path('environment/sustainability/',include('Sustainability.urls')),
    # path('admin/', admin.site.urls),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     
    path('api/', include('recommendation.urls')),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)