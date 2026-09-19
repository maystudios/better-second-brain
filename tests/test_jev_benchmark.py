"""Accounting regressions: never turn cache/reasoning subsets into new tokens."""
import unittest
from benchmark.jev_compare_report import usage_totals, arm_summary


class BenchmarkAccountingTests(unittest.TestCase):
    def test_cache_and_reasoning_are_subsets(self):
        result = usage_totals([{'input_tokens': 100, 'cached_input_tokens': 30,
                               'cache_write_input_tokens': 10, 'output_tokens': 20,
                               'reasoning_output_tokens': 15}], [])
        self.assertEqual(result['main_tokens'], 120)
        self.assertAlmostEqual(result['usd_uncached'], 44 / 1_000_000)
        self.assertAlmostEqual(result['usd_cache_aware'], 39.1 / 1_000_000)

    def test_jev_overhead_is_included(self):
        result = usage_totals([{'input_tokens': 100, 'output_tokens': 20}],
                              [{'input_tokens': 1000, 'cached_input_tokens': 200,
                                'output_tokens': 80}])
        self.assertEqual(result['all_model_tokens'], 1400)
        self.assertAlmostEqual(result['usd_uncached'], 94.4 / 1_000_000)

    def test_missing_usage_is_not_zero_cost(self):
        with self.assertRaises(ValueError):
            usage_totals([], [None])

    def test_failed_quality_is_in_cost_per_solved_denominator(self):
        rows = [{'valid': True, 'usage': [{'input_tokens': 1000, 'output_tokens': 0}],
                 'jev_usage': [], 'jev_calls': 0, 'page_tokens': 100,
                 'seconds': 1, 'retrieval_seconds': 0, 'question_id': n,
                 'grade': {'correctness': 2, 'citation': 2, 'faithfulness': f}}
                for n,f in [(1,2),(2,1)]]
        summary = arm_summary(rows)
        self.assertEqual(summary['solved'], 1)
        self.assertAlmostEqual(summary['usd_per_solved'], .0004)
        self.assertEqual(summary['quality_mean'], 5.5)


if __name__ == '__main__':
    unittest.main()
