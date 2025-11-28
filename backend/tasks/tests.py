from django.test import TestCase

# Create your tests here.
from .scoring import score_tasks
from datetime import date, timedelta

class ScoringTests(TestCase):

    def test_past_due_has_highest_urgency(self):
        today = date.today().isoformat()

        tasks = [
            {
                "id": "late",
                "title": "Past due task",
                "due_date": "2023-01-01",
                "estimated_hours": 3,
                "importance": 5,
                "dependencies": []
            },
            {
                "id": "normal",
                "title": "Normal task",
                "due_date": today,
                "estimated_hours": 3,
                "importance": 5,
                "dependencies": []
            }
        ]

        result = score_tasks(tasks)
        scored = result['tasks']

        self.assertGreater(scored[0]['score'], scored[1]['score'])
        self.assertTrue(scored[0]['past_due'])

    
    def test_fast_strategy_favors_low_effort(self):
        tasks = [
            {
                "id": "long",
                "title": "Long task",
                "due_date": "2030-01-01",
                "estimated_hours": 20,
                "importance": 9,
                "dependencies": []
            },
            {
                "id": "short",
                "title": "Short task",
                "due_date": "2030-01-01",
                "estimated_hours": 1,
                "importance": 4,
                "dependencies": []
            }
        ]

        result = score_tasks(tasks, strategy="fast")
        scored = result['tasks']

        self.assertEqual(scored[0]['id'], "short")

    
    def test_circular_dependency_detection(self):
        tasks = [
            {
                "id": "A",
                "title": "Task A",
                "due_date": "2025-12-01",
                "estimated_hours": 3,
                "importance": 7,
                "dependencies": ["B"]
            },
            {
                "id": "B",
                "title": "Task B",
                "due_date": "2025-12-03",
                "estimated_hours": 2,
                "importance": 6,
                "dependencies": ["A"]
            }
        ]

        result = score_tasks(tasks)
        scored = result['tasks']

        # both should be flagged
        flagged = [t for t in scored if t['dependency_issue']]
        self.assertEqual(len(flagged), 2)
        self.assertTrue(len(result['warnings']) > 0)


from rest_framework.test import APITestCase
from django.urls import reverse

class SuggestEndpointTests(APITestCase):

    def test_suggest_returns_top_three(self):
        url = "/api/tasks/suggest/"

        payload = {
            "strategy": "smart",
            "tasks": [
                {"id": "1", "title": "A", "due_date": "2025-11-27", "estimated_hours": 1, "importance": 9, "dependencies": []},
                {"id": "2", "title": "B", "due_date": "2025-12-01", "estimated_hours": 4, "importance": 8, "dependencies": []},
                {"id": "3", "title": "C", "due_date": "2025-12-05", "estimated_hours": 2, "importance": 6, "dependencies": []},
                {"id": "4", "title": "D", "due_date": "2025-12-10", "estimated_hours": 1, "importance": 4, "dependencies": []}
            ]
        }

        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['suggestions']), 3)



