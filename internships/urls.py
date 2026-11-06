from django.urls import path
from internships import views

app_name = 'internships'

urlpatterns = [
    path('', views.internship_list_view, name='list'),
    path('<int:pk>/', views.internship_detail_view, name='detail'),
    path('<int:pk>/apply/', views.apply_view, name='apply'),
    path('post/', views.create_posting_view, name='create_posting'),
    path('my-postings/', views.company_postings_view, name='company_postings'),
    path('postings/<int:pk>/applicants/', views.manage_applicants_view, name='manage_applicants'),
    path('applications/<int:pk>/update-status/', views.update_application_status_view, name='update_status'),
    path('my-applications/', views.my_applications_view, name='my_applications'),
]
