import math
import unittest

from app import app


class LinkBudgetTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.inputs = {
            'current_elevation': 90, 'satAltitude': 550, 'frequency': 12.5,
            'satPower': 20, 'g_t': 15, 'zenithLoss': 0.5, 'required_c_n0': 50,
        }

    def calculate(self, **changes):
        response = self.client.post('/calculate', json=self.inputs | changes)
        self.assertEqual(response.status_code, 200)
        return response.get_json()

    def test_zenith_range_equals_altitude(self):
        result = self.calculate()
        self.assertEqual(result['d_km'], 550.0)
        self.assertEqual(result['l_a'], 0.5)
        expected_loss = 20 * math.log10(550_000) + 20 * math.log10(12.5e9) - 147.55
        self.assertAlmostEqual(result['l_fs'], expected_loss, delta=0.051)
        self.assertAlmostEqual(result['c_n0'] - 50, result['margin'], delta=0.11)

    def test_double_frequency_costs_six_db(self):
        baseline = self.calculate()
        doubled = self.calculate(frequency=25)
        self.assertAlmostEqual(doubled['l_fs'] - baseline['l_fs'], 20 * math.log10(2), delta=0.11)
        self.assertAlmostEqual(baseline['margin'] - doubled['margin'], 20 * math.log10(2), delta=0.11)

    def test_gt_gain_translates_to_margin(self):
        baseline = self.calculate()
        improved = self.calculate(g_t=18)
        self.assertAlmostEqual(improved['margin'] - baseline['margin'], 3, delta=0.11)

    def test_lower_elevation_increases_losses(self):
        zenith = self.calculate()
        low = self.calculate(current_elevation=10)
        self.assertGreater(low['d_km'], zenith['d_km'])
        self.assertGreater(low['l_a'], zenith['l_a'])
        self.assertLess(low['margin'], zenith['margin'])

    def test_missing_field_returns_error(self):
        response = self.client.post('/calculate', json={'satAltitude': 550})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())

    def test_zero_frequency_returns_error(self):
        response = self.client.post('/calculate', json=self.inputs | {'frequency': 0})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())


if __name__ == '__main__':
    unittest.main()
