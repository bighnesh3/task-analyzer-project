from django.shortcuts import render

# Create your views here.
# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AnalyzeRequestSerializer, TaskSerializer
from .scoring import score_tasks


class AnalyzeTasksAPIView(APIView):
    """
    POST /api/tasks/analyze/
    
    Accepts a list of tasks and returns them sorted by priority score.
    
    Request body:
    {
        "tasks": [
            {
                "id": "task_1",
                "title": "Fix login bug",
                "due_date": "2025-11-30",
                "estimated_hours": 3,
                "importance": 8,
                "dependencies": []
            },
            ...
        ],
        "strategy": "smart",  # optional: smart, fast, impact, deadline
        "weight_overrides": {}  # optional
    }
    
    Response:
    {
        "tasks": [
            {
                ...original task fields...,
                "score": 85.5,
                "priority": "High",
                "explanation": "Priority driven by: overdue, critical importance",
                "past_due": false,
                "dependency_issue": false
            },
            ...
        ],
        "warnings": []
    }
    """
    
    def post(self, request):
        serializer = AnalyzeRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid request data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = serializer.validated_data
        tasks = validated_data['tasks']
        strategy = validated_data.get('strategy', 'smart')
        weight_overrides = validated_data.get('weight_overrides', None)
        
        try:
            result = score_tasks(tasks, strategy, weight_overrides)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Error processing tasks", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SuggestTasksAPIView(APIView):
    """
    GET /api/tasks/suggest/
    POST /api/tasks/suggest/
    
    Returns the top 3 tasks the user should work on, with explanations.
    
    For GET: Accepts tasks as query parameter (JSON string) or empty
    For POST: Accepts tasks in request body
    
    Request body (POST):
    {
        "tasks": [...],
        "strategy": "smart"  # optional
    }
    
    Query params (GET):
    ?strategy=smart
    
    Response:
    {
        "suggestions": [
            {
                ...task with score, priority, explanation...
            },
            ...up to 3 tasks...
        ],
        "warnings": []
    }
    """
    
    def get(self, request):
        """Handle GET requests with tasks in query params or body."""
        strategy = request.query_params.get('strategy', 'smart')
        
        # Try to get tasks from query params (as JSON string)
        import json
        tasks_json = request.query_params.get('tasks', None)
        
        if tasks_json:
            try:
                tasks = json.loads(tasks_json)
            except json.JSONDecodeError:
                return Response(
                    {"error": "Invalid JSON in tasks parameter"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            tasks = []
        
        return self._process_suggestion(tasks, strategy)
    
    def post(self, request):
        """Handle POST requests with tasks in body."""
        tasks = request.data.get('tasks', [])
        strategy = request.data.get('strategy', 'smart')
        
        # Validate strategy
        if strategy not in ['smart', 'fast', 'impact', 'deadline']:
            return Response(
                {"error": f"Invalid strategy: {strategy}. Must be one of: smart, fast, impact, deadline"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return self._process_suggestion(tasks, strategy)
    
    def _process_suggestion(self, tasks, strategy):
        """Common logic to process and return suggestions."""
        if not tasks:
            return Response(
                {
                    "suggestions": [],
                    "warnings": ["No tasks provided for analysis."]
                },
                status=status.HTTP_200_OK
            )
        
        # Validate tasks with serializer
        task_serializer = TaskSerializer(data=tasks, many=True)
        if not task_serializer.is_valid():
            return Response(
                {"error": "Invalid task data", "details": task_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = score_tasks(task_serializer.validated_data, strategy)
            
            # Extract top 3 tasks
            top_3 = result['tasks'][:3]
            
            return Response(
                {
                    "suggestions": top_3,
                    "warnings": result['warnings']
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Error processing task suggestions", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )