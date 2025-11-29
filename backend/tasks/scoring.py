"""
scoring.py - Task Priority Scoring Algorithm

This module implements an intelligent task scoring system that evaluates tasks
based on urgency, importance, effort, and dependency impact.
"""

from datetime import datetime, date
from typing import List, Dict, Any, Set, Tuple
import math


def score_tasks(
    tasks: List[Dict[str, Any]], 
    strategy: str = "smart", 
    weight_overrides: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Score and sort tasks based on multiple factors.
    
    Args:
        tasks: List of task dictionaries with fields:
            - id: unique identifier
            - title: task name
            - due_date: ISO date string (YYYY-MM-DD)
            - estimated_hours: numeric effort estimate
            - importance: 1-10 scale
            - dependencies: list of task IDs this task depends on
        strategy: scoring strategy ("smart", "fast", "impact", "deadline")
        weight_overrides: optional dict to override default weights
    
    Returns:
        Dictionary containing:
            - tasks: scored and sorted task list
            - warnings: list of validation issues
    """
    warnings = []
    today = date.today()
    
    # Validate and normalize tasks
    validated_tasks = []
    task_id_map = {}
    
    for idx, task in enumerate(tasks):
        validated_task, task_warnings = _validate_task(task, idx, today)
        warnings.extend(task_warnings)
        if validated_task:
            validated_tasks.append(validated_task)
            task_id_map[validated_task['id']] = validated_task
    
    if not validated_tasks:
        return {"tasks": [], "warnings": warnings}
    
    # Detect circular dependencies
    circular_deps = _detect_circular_dependencies(validated_tasks)
    if circular_deps:
        warnings.append(f"Circular dependencies detected involving tasks: {circular_deps}")
        for task in validated_tasks:
            if task['id'] in circular_deps:
                task['dependency_issue'] = True
    
    # Calculate dependency impact (how many tasks depend on each task)
    dependency_impact = _calculate_dependency_impact(validated_tasks)
    
    # Get weights for selected strategy
    weights = _get_strategy_weights(strategy, weight_overrides)
    
    # Score each task
    for task in validated_tasks:
        score, explanation = _calculate_task_score(
            task, today, dependency_impact, weights, task_id_map
        )
        task['score'] = score
        task['explanation'] = explanation
        task['priority'] = _get_priority_label(score)
    
    # Sort by score (highest first)
    validated_tasks.sort(key=lambda t: t['score'], reverse=True)
    
    return {
        "tasks": validated_tasks,
        "warnings": warnings
    }


def _validate_task(task, idx, today):
    warnings = []
    validated = {
        'id': task.get('id', f'task_{idx}'),
        'title': task.get('title', f'Untitled Task {idx}'),
        'past_due': False,
        'dependency_issue': False,
        'validation_warnings': [],
        'incomplete': False
    }

    # --- due_date (frontend guarantees valid) ---
    due_date_str = task.get('due_date')
    try:
        validated['due_date'] = datetime.fromisoformat(
            due_date_str.replace("Z", "+00:00")
        ).date()
        validated['past_due'] = validated['due_date'] < today
    except Exception:
        # Should not happen. Frontend validates, but be safe.
        msg = f"Task '{validated['title']}': Invalid or missing due date."
        warnings.append(msg)
        validated['validation_warnings'].append(msg)
        validated['due_date'] = today
        validated['incomplete'] = True

    # --- estimated_hours (soft field) ---
    if task.get('estimated_hours') is None:
        validated['estimated_hours'] = 1
        msg = f"Task '{validated['title']}': Missing estimated_hours. Using default 1."
        warnings.append(msg)
        validated['validation_warnings'].append(msg)
        validated['incomplete'] = True
    else:
        validated['estimated_hours'] = float(task.get('estimated_hours'))

    # --- importance (soft field) ---
    if task.get('importance') is None:
        validated['importance'] = 5
        msg = f"Task '{validated['title']}': Missing importance. Using default 5."
        warnings.append(msg)
        validated['validation_warnings'].append(msg)
        validated['incomplete'] = True
    else:
        validated['importance'] = float(task.get('importance'))

    # --- dependencies ---
    deps = task.get('dependencies', [])
    if isinstance(deps, list):
        validated['dependencies'] = [str(d) for d in deps]
    else:
        validated['dependencies'] = []
        msg = f"Task '{validated['title']}': Invalid dependencies format. Using empty list."
        warnings.append(msg)
        validated['validation_warnings'].append(msg)
        validated['incomplete'] = True

    # CONFIDENCE = 1.0 - missing_count * 0.25
    missing_count = 0
    if task.get('estimated_hours') is None:
        missing_count += 1
    if task.get('importance') is None:
        missing_count += 1

    validated['confidence'] = round(max(0.0, 1.0 - 0.25 * missing_count), 2)

    validated["validation_warnings"] = warnings.copy()
    return validated, warnings



def _detect_circular_dependencies(tasks: List[Dict[str, Any]]) -> Set[str]:
    """Detect circular dependencies using DFS."""
    task_id_map = {task['id']: task for task in tasks}
    visited = set()
    rec_stack = set()
    circular_tasks = set()
    
    def dfs(task_id: str, path: Set[str]) -> bool:
        """DFS helper to detect cycles."""
        if task_id in rec_stack:
            # Cycle detected - add all tasks in current path
            circular_tasks.update(path)
            return True
        
        if task_id in visited:
            return False
        
        visited.add(task_id)
        rec_stack.add(task_id)
        path.add(task_id)
        
        task = task_id_map.get(task_id)
        if task:
            for dep_id in task.get('dependencies', []):
                if dep_id in task_id_map:
                    if dfs(dep_id, path.copy()):
                        circular_tasks.add(task_id)
        
        rec_stack.remove(task_id)
        return False
    
    for task in tasks:
        if task['id'] not in visited:
            dfs(task['id'], set())
    
    return circular_tasks


def _calculate_dependency_impact(tasks: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate how many tasks depend on each task (blocking impact)."""
    impact = {task['id']: 0 for task in tasks}
    
    for task in tasks:
        for dep_id in task.get('dependencies', []):
            if dep_id in impact:
                impact[dep_id] += 1
    
    return impact


def _get_strategy_weights(
    strategy: str, 
    weight_overrides: Dict[str, float] = None
) -> Dict[str, float]:
    """Get weights based on strategy."""
    strategies = {
        "smart": {
            "urgency": 0.35,
            "importance": 0.35,
            "effort": 0.15,
            "dependency": 0.15
        },
        "fast": {
            "urgency": 0.20,
            "importance": 0.20,
            "effort": 0.50,
            "dependency": 0.10
        },
        "impact": {
            "urgency": 0.15,
            "importance": 0.60,
            "effort": 0.10,
            "dependency": 0.15
        },
        "deadline": {
            "urgency": 0.60,
            "importance": 0.20,
            "effort": 0.05,
            "dependency": 0.15
        }
    }
    
    weights = strategies.get(strategy, strategies["smart"])
    
    # Apply overrides if provided
    if weight_overrides:
        for key in ["urgency", "importance", "effort", "dependency"]:
            if key in weight_overrides:
                weights[key] = weight_overrides[key]
        
        # Normalize weights to sum to 1.0
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
    
    return weights


def _calculate_task_score(
    task: Dict[str, Any],
    today: date,
    dependency_impact: Dict[str, int],
    weights: Dict[str, float],
    task_id_map: Dict[str, Any]
) -> Tuple[float, str]:
    """Caluclate score and explanation for a single task."""
    
    # 1. Urgency Score (0-1)
    days_until_due = (task['due_date'] - today).days
    
    if task['past_due']:
        # recently overdue gets high urgency, old overdue decays
        days_overdue = (today - task['due_date']).days
        max_floor = 0.20
        decay_days = 14.0
        urgency_score = max_floor + (1.0 - max_floor) * math.exp(-days_overdue / decay_days)
        urgency_score = round(min(1.0, max(0.0, urgency_score)), 4)
        urgency_desc = f"overdue by {days_overdue}d"

    elif days_until_due <= 0:
        urgency_score = 0.98
        urgency_desc = "due today"
    elif days_until_due <= 1:
        urgency_score = 0.95
        urgency_desc = "due tomorrow"
    elif days_until_due <= 3:
        urgency_score = 0.85
        urgency_desc = "due very soon"
    elif days_until_due <= 7:
        urgency_score = 0.70
        urgency_desc = "due this week"
    elif days_until_due <= 14:
        urgency_score = 0.50
        urgency_desc = "due in 2 weeks"
    elif days_until_due <= 30:
        urgency_score = 0.30
        urgency_desc = "due this month"
    else:
        # Exponential decay for far-future tasks
        urgency_score = max(0.05, 1.0 / (1 + math.log(days_until_due / 7)))
        urgency_desc = "due later"
    
    # 2. Importance Score (0-1)
    importance_score = task['importance'] / 10.0
    if task['importance'] >= 9:
        importance_desc = "critical importance"
    elif task['importance'] >= 7:
        importance_desc = "high importance"
    elif task['importance'] >= 5:
        importance_desc = "moderate importance"
    else:
        importance_desc = "lower importance"
    
    # 3. Effort Score (0-1, inverse - lower effort = higher score)
    # Normalize effort with diminishing returns for very long tasks
    max_effort_hours = 40  # Consider 40+ hours as maximum complexity
    effort_normalized = min(task['estimated_hours'] / max_effort_hours, 1.0)
    effort_score = 1.0 - effort_normalized
    
    if task['estimated_hours'] <= 1:
        effort_desc = "quick win (≤1h)"
    elif task['estimated_hours'] <= 3:
        effort_desc = "short task"
    elif task['estimated_hours'] <= 8:
        effort_desc = "moderate effort"
    elif task['estimated_hours'] <= 16:
        effort_desc = "substantial effort"
    else:
        effort_desc = "large project"
    
    # 4. Dependency Score (0-1)
    blocking_count = dependency_impact.get(task['id'], 0)
    # Normalize: 0 tasks blocked = 0, 5+ tasks blocked = 1.0
    dependency_score = min(blocking_count / 5.0, 1.0)
    
    if blocking_count == 0:
        dependency_desc = None
    elif blocking_count == 1:
        dependency_desc = "blocks 1 task"
    else:
        dependency_desc = f"blocks {blocking_count} tasks"
    
    # Calculate weighted total score
    total_score = (
        weights['urgency'] * urgency_score +
        weights['importance'] * importance_score +
        weights['effort'] * effort_score +
        weights['dependency'] * dependency_score
    )
    
    # Scale to 0-100 for readability
    total_score = round(total_score * 100, 2)
    
    # Build explanation
    explanation_parts = []
    
    # Add top 2-3 contributing factors
    factors = [
        (weights['urgency'] * urgency_score, urgency_desc),
        (weights['importance'] * importance_score, importance_desc),
        (weights['effort'] * effort_score, effort_desc),
        (weights['dependency'] * dependency_score, dependency_desc)
    ]
    
    # Sort by contribution
    factors.sort(reverse=True, key=lambda x: x[0])
    
    for contribution, desc in factors[:3]:
        if desc and contribution > 0.05:  # Only mention meaningful factors
            explanation_parts.append(desc)
    
    if task['past_due']:
        explanation = f"OVERDUE task: {', '.join(explanation_parts)}"
    else:
        explanation = f"Priority driven by: {', '.join(explanation_parts)}" if explanation_parts else "Standard priority task"
    
    if task.get('incomplete'):
        explanation += " (NOTE: used default values where fields were missing)"

    return total_score, explanation


def _get_priority_label(score: float) -> str:
    """Convert numeric score to priority label."""
    if score >= 75:
        return "High"
    elif score >= 50:
        return "Medium"
    else:
        return "Low"