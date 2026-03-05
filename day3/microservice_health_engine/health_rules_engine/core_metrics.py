from decimal import Decimal, getcontext
from typing import Union

# Set precision for critical calculations
getcontext().prec = 10

def calculate_average_latency(latencies: list) -> Decimal:
    """Calculates average latency using Decimal for precision."""
    if not latencies:
        return Decimal('0.0')
    total_latency = sum(Decimal(str(l)) for l in latencies)
    average = total_latency / Decimal(str(len(latencies)))
    return average

def calculate_resource_utilization(used: int, total: int) -> float:
    """Calculates resource utilization as a percentage."""
    if total == 0:
        return 0.0
    return (used / total) * 100.0

def check_threshold(metric_value: Union[float, Decimal], threshold: Union[float, Decimal], operator: str) -> bool:
    """
    Checks if a metric value meets a given threshold condition.
    `operator` can be '>', '<', '>=', '<=', '==', '!='.
    """
    if operator == '>':
        return metric_value > threshold
    elif operator == '<':
        return metric_value < threshold
    elif operator == '>=':
        return metric_value >= threshold
    elif operator == '<=':
        return metric_value <= threshold
    elif operator == '==':
        return metric_value == threshold
    elif operator == '!=':
        return metric_value != threshold
    else:
        raise ValueError(f"Unsupported operator: {operator}")
