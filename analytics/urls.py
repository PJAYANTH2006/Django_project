from django.urls import path
from analytics import views

app_name = 'analytics'

urlpatterns = [
    path('faculty-overview/', views.faculty_overview_view, name='faculty_overview'),
    path('student-readiness/', views.student_readiness_view, name='student_readiness'),
    path('api/skill-stats/', views.api_skill_stats_view, name='api_skill_stats'),
    path('api/placement-stats/', views.api_placement_stats_view, name='api_placement_stats'),
]
