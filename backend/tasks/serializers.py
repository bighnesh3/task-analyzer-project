# serializers.py

from rest_framework import serializers


class TaskSerializer(serializers.Serializer):
    """Serializer for individual task objects."""
    
    id = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(required=False, allow_blank=True)
    due_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    estimated_hours = serializers.FloatField(required=False, allow_null=True)
    importance = serializers.FloatField(required=False, allow_null=True)
    dependencies = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )


class AnalyzeRequestSerializer(serializers.Serializer):
    """Serializer for the analyze tasks request."""
    
    tasks = TaskSerializer(many=True, required=True)
    strategy = serializers.ChoiceField(
        choices=['smart', 'fast', 'impact', 'deadline'],
        required=False,
        default='smart'
    )
    weight_overrides = serializers.DictField(
        child=serializers.FloatField(),
        required=False,
        allow_null=True
    )
    
    def validate_tasks(self, value):
        """Ensure tasks list is not empty."""
        if not value:
            raise serializers.ValidationError("Tasks list cannot be empty.")
        return value
    
    def validate_weight_overrides(self, value):
        """Validate weight override keys if provided."""
        if value is not None:
            valid_keys = {'urgency', 'importance', 'effort', 'dependency'}
            invalid_keys = set(value.keys()) - valid_keys
            if invalid_keys:
                raise serializers.ValidationError(
                    f"Invalid weight keys: {invalid_keys}. Valid keys are: {valid_keys}"
                )
        return value