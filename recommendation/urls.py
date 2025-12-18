from django.urls import path
from . import views

urlpatterns = [
    path('recommendation/', views.RecommendationView.as_view(), name='recommendation'),
    path('recommendation/<int:id>/', views.RecommendationView.as_view(), name='recommendation'),
    path('sop-document-uplode/', views.SOPDocumentUploadView.as_view(), name='sop-document-uplode'), 
    path('sop-document-uplode/<str:id>/', views.SOPDocumentUploadView.as_view(), name='sop-document-delete'),   
]