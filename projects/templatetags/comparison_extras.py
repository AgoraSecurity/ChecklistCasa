from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    if dictionary and key:
        return dictionary.get(key, {})
    return {}

@register.filter
def get_assessment_value(assessments, criterion_id):
    """Get assessment value for a specific criterion."""
    if assessments and criterion_id:
        assessment_data = assessments.get(criterion_id, {})
        return assessment_data.get('value')
    return None

@register.filter
def get_display_value(assessments, criterion_id):
    """Get display value for a specific criterion."""
    if assessments and criterion_id:
        assessment_data = assessments.get(criterion_id, {})
        return assessment_data.get('display_value', '-')
    return '-'

@register.filter
def get_criterion_stats(stats, criterion_id):
    """Get statistics for a specific criterion."""
    if stats and criterion_id:
        return stats.get(criterion_id, {})
    return {}

@register.filter
def is_best_value(value, stats):
    """Check if value is the best (maximum) for this criterion."""
    if value is not None and stats:
        max_val = stats.get('max_val')
        return max_val is not None and float(value) == float(max_val)
    return False

@register.filter
def is_worst_value(value, stats):
    """Check if value is the worst (minimum) for this criterion."""
    if value is not None and stats:
        min_val = stats.get('min_val')
        max_val = stats.get('max_val')
        return (min_val is not None and max_val is not None and 
                min_val != max_val and float(value) == float(min_val))
    return False

@register.filter
def mul(value, arg):
    """Multiply two values."""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0