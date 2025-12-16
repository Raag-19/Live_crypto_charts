import unittest
import pandas as pd
from indicator_calculator import IncrementalSupertrend

class TestIncrementalSupertrend(unittest.TestCase):
    def setUp(self):
        data = {
            'timestamp': pd.to_datetime(['2023-01-01 00:00:00', '2023-01-01 00:01:00', '2023-01-01 00:02:00']),
            'open': [100, 101, 102],
            'high': [103, 104, 105],
            'low': [99, 100, 101],
            'close': [101, 102, 103],
            'volume': [1000, 1100, 1200]
        }
        self.df = pd.DataFrame(data).set_index('timestamp')
        self.calculator = IncrementalSupertrend(self.df, length=2, multiplier=3.0)

    def test_update(self):
        new_candle = {'high': 106, 'low': 102, 'close': 104}
        incremental_supertrend, incremental_direction = self.calculator.update(new_candle)

        # Perform a full recalculation for comparison
        new_data = {
            'timestamp': [pd.to_datetime('2023-01-01 00:03:00')],
            'open': [103],
            'high': [106],
            'low': [102],
            'close': [104],
            'volume': [1300]
        }
        new_df = pd.DataFrame(new_data).set_index('timestamp')
        combined_df = pd.concat([self.df, new_df])
        combined_df.ta.supertrend(length=2, multiplier=3.0, append=True)

        expected_supertrend = combined_df.iloc[-1]['SUPERT_2_3.0']
        expected_direction = combined_df.iloc[-1]['SUPERTd_2_3.0']

        self.assertAlmostEqual(incremental_supertrend, expected_supertrend, places=2)
        self.assertEqual(incremental_direction, expected_direction)

if __name__ == '__main__':
    unittest.main()
