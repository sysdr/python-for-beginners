# main.py
from health_rules_engine.health_evaluator import HealthEvaluator

def run_health_check(cpu_usage, memory_usage, latencies, scenario_name):
    print(f"\n--- Scenario: {scenario_name} ---")
    evaluator = HealthEvaluator()

    # Assignment: Add your custom rules here, paying attention to operator precedence
    # Use parentheses for clarity, even if not strictly required by Python's precedence rules.
    evaluator.add_rule("high_cpu_or_memory", "(cpu_util > 70.0 or mem_util > 80.0)")
    # Explanation: Parentheses ensure 'or' condition is evaluated correctly for these two metrics.

    evaluator.add_rule("critical_latency_and_stress", "(avg_lat > 750.0 and is_system_stressed)")
    # Explanation: Parentheses group the two conditions for 'and' evaluation, making intent clear.

    evaluator.add_rule("extreme_resource_exhaustion", "(cpu_util > 95.0 and mem_util > 98.0 and avg_lat > 1000.0)")
    # Explanation: Parentheses ensure all three 'and' conditions are grouped for precise evaluation.

    evaluator.add_rule("degraded_but_not_critical", "is_performance_degraded and not is_system_stressed")
    # Explanation: Parentheses clarify the 'and not' logic for complex state interpretation.

    results = evaluator.evaluate_health(cpu_usage, memory_usage, latencies)

    # CLI Dashboard Output
    print("📊 Health Status Dashboard 📊")
    print("---------------------------------")
    print(f"CPU Utilization:   {results['cpu_utilization']:.2f}%")
    print(f"Memory Utilization: {results['memory_utilization']:.2f}%")
    print(f"Average Latency:   {results['average_latency']:.2f} ms")
    print("---------------------------------")
    print(f"Is CPU High (>80%):        {results['is_cpu_high']}")
    print(f"Is Memory High (>90%):     {results['is_memory_high']}")
    print(f"Is Latency Critical (>500ms): {results['is_latency_critical']}")
    print("---------------------------------")
    print(f"Is System Stressed:        {results['is_system_stressed']}")
    print(f"Is Performance Degraded:   {results['is_performance_degraded']}")
    print("---------------------------------")
    print(f"Overall Status:    {results['overall_status']}")
    print("---------------------------------")
    print(f"Custom Rule 'high_cpu_or_memory' met:        {results.get('rule_high_cpu_or_memory_met', 'N/A')}")
    print(f"Custom Rule 'critical_latency_and_stress' met: {results.get('rule_critical_latency_and_stress_met', 'N/A')}")
    print(f"Custom Rule 'extreme_resource_exhaustion' met: {results.get('rule_extreme_resource_exhaustion_met', 'N/A')}")
    print(f"Custom Rule 'degraded_but_not_critical' met:   {results.get('rule_degraded_but_not_critical_met', 'N/A')}")
    print("---------------------------------")


if __name__ == "__main__":
    print("--- Microservice Health Rule Engine Demo ---")

    # Test Case 1: Healthy System
    run_health_check(cpu_usage=0.4, memory_usage=0.5, latencies=[50, 60, 70], scenario_name="Healthy System (All OK)")

    # Test Case 2: High CPU, but not critical
    run_health_check(cpu_usage=0.75, memory_usage=0.4, latencies=[100, 120, 110], scenario_name="High CPU Only (Degraded by custom rule)")

    # Test Case 3: Degraded Performance (Memory High, Latency Critical)
    run_health_check(cpu_usage=0.6, memory_usage=0.92, latencies=[400, 550, 600], scenario_name="Degraded Performance (Memory High, Latency Critical)")

    # Test Case 4: Critical State (CPU, Memory, Latency all critical)
    run_health_check(cpu_usage=0.98, memory_usage=0.99, latencies=[800, 1200, 1500], scenario_name="Critical State (All Metrics High)")

    # Test Case 5: Degraded but not stressed (demonstrates 'and not' logic)
    run_health_check(cpu_usage=0.75, memory_usage=0.85, latencies=[400, 450, 510], scenario_name="Degraded But Not Stressed (Custom Rule Check)")
