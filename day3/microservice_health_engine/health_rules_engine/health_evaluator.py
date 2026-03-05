from health_rules_engine.core_metrics import calculate_resource_utilization, check_threshold, calculate_average_latency
from decimal import Decimal

class HealthEvaluator:
    def __init__(self):
        self.rules = {}

    def add_rule(self, rule_name: str, condition: str):
        """Adds a health rule defined by a string condition."""
        self.rules[rule_name] = condition

    def evaluate_health(self, cpu_usage: float, memory_usage: float, latencies: list[float]) -> dict:
        """Evaluates overall system health based on defined rules."""
        results = {}

        current_cpu_util = calculate_resource_utilization(int(cpu_usage * 100), 100)
        current_memory_util = calculate_resource_utilization(int(memory_usage * 100), 100)
        avg_latency_decimal = calculate_average_latency(latencies)
        avg_latency = float(avg_latency_decimal)

        is_cpu_high = check_threshold(current_cpu_util, 80.0, '>')
        is_memory_high = check_threshold(current_memory_util, 90.0, '>')
        is_latency_critical = check_threshold(avg_latency, 500.0, '>')

        is_system_stressed = is_cpu_high and is_memory_high
        is_performance_degraded = is_latency_critical or is_system_stressed

        results["cpu_utilization"] = current_cpu_util
        results["memory_utilization"] = current_memory_util
        results["average_latency"] = avg_latency
        results["is_cpu_high"] = is_cpu_high
        results["is_memory_high"] = is_memory_high
        results["is_latency_critical"] = is_latency_critical
        results["is_system_stressed"] = is_system_stressed
        results["is_performance_degraded"] = is_performance_degraded

        overall_status = "HEALTHY"
        if is_performance_degraded:
            overall_status = "DEGRADED"
        if is_cpu_high and is_memory_high and is_latency_critical:
            overall_status = "CRITICAL"

        results["overall_status"] = overall_status

        for rule_name, condition_str in self.rules.items():
            try:
                safe_context = {
                    "cpu_util": current_cpu_util,
                    "mem_util": current_memory_util,
                    "avg_lat": avg_latency,
                    "is_cpu_high": is_cpu_high,
                    "is_memory_high": is_memory_high,
                    "is_latency_critical": is_latency_critical,
                    "is_system_stressed": is_system_stressed,
                    "is_performance_degraded": is_performance_degraded,
                }
                results[f"rule_{rule_name}_met"] = eval(condition_str, {"__builtins__": {}}, safe_context)
            except Exception as e:
                results[f"rule_{rule_name}_error"] = str(e)

        return results
