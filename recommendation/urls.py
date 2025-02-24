from django.urls import path
from . import views

urlpatterns = [
    path('recommendation/', views.RecommendationView.as_view(), name='recommendation'),
    path('recommendation/<int:id>/', views.RecommendationView.as_view(), name='recommendation'),
]