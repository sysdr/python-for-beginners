import unittest
import sys
sys.path.insert(0, '.')
from health_rules_engine.health_evaluator import HealthEvaluator

class TestHealthEvaluator(unittest.TestCase):
    def test_healthy_system(self):
        e = HealthEvaluator()
        r = e.evaluate_health(0.4, 0.5, [50.0, 60.0, 70.0])
        self.assertEqual(r["overall_status"], "HEALTHY")
        self.assertAlmostEqual(r["cpu_utilization"], 40.0)
        self.assertAlmostEqual(r["memory_utilization"], 50.0)
        self.assertAlmostEqual(r["average_latency"], 60.0)

    def test_critical_system(self):
        e = HealthEvaluator()
        r = e.evaluate_health(0.98, 0.99, [800.0, 1200.0, 1500.0])
        self.assertEqual(r["overall_status"], "CRITICAL")
        self.assertTrue(r["is_cpu_high"])
        self.assertTrue(r["is_memory_high"])
        self.assertTrue(r["is_latency_critical"])
