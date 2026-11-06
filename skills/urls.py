from django.urls import path
from skills import views

app_name = 'skills'

urlpatterns = [
    path('my-skills/', views.my_skills_view, name='my_skills'),
    path('add/', views.add_skill_view, name='add_skill'),
    path('delete/<int:pk>/', views.delete_skill_view, name='delete_skill'),
    path('resume-upload/', views.resume_upload_view, name='resume_upload'),
    path('gap-analysis/<int:posting_id>/', views.gap_analysis_view, name='gap_analysis'),
    path('explore/', views.explore_skills_view, name='explore'),
]
