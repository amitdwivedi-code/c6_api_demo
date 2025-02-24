from django.urls import path
from . import views


urlpatterns = [ 
        
        path('principle_6_report2/', views.Principle_6_Report_View.as_view(), name='get_Principle_6_Report2'),
        path('brs_report/', views.BRS_Report_View.as_view(), name='get_brs_report'),
        path('brs_report1/', views.BRS_Report1_View.as_view(), name='get_brs_report'),



        path('section-a/', views.SectionAView.as_view(), name='section-a'),
        path('section-b/', views.SectionBView.as_view(), name='section-b'),
        path('section-c-p1/', views.SectionCPrinciple1View.as_view(), name='section-c-p1'),
        path('section-c-p2/', views.SectionCPrinciple2View.as_view(), name='section-c-p2'),
        path('section-c-p3/', views.SectionCPrinciple3View.as_view(), name='section-c-p3'),
        path('p4/', views.Principle4View.as_view(), name='p4'),
        path('p5/', views.Principle5View.as_view(), name='p5'),
        path('principle_6_report/', views.Principle_6_Report_View.as_view(), name='get_Principle_6_Report'),
        path('p7/', views.Principle7View.as_view(),name='p7'),
        path('p8/', views.Principle8View.as_view(), name='p8'),
        path('p9/', views.Principle9View.as_view(), name='p9')
        

]