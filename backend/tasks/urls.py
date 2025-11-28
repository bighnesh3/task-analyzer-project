# urls.py

from django.urls import path
from .views import AnalyzeTasksAPIView, SuggestTasksAPIView

urlpatterns = [
    path('analyze/', AnalyzeTasksAPIView.as_view(), name='analyze_tasks'),
    path('suggest/', SuggestTasksAPIView.as_view(), name='suggest_tasks'),
]