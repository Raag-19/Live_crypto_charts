import unittest
import pandas as pd
import sqlite3
import os
import database as db

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db_file = 'test_charts.db'
        db.init_db(self.db_file)

    def tearDown(self):
        os.remove(self.db_file)

    def test_replace_and_get_candles(self):
        data = {
            'timestamp': [1672531200, 1672531260],
            'open': [100, 101],
            'high': [102, 103],
            'low': [99, 100],
            'close': [101, 102],
            'volume': [1000, 1100]
        }
        df = pd.DataFrame(data)
        db.replace_candles(df, self.db_file)

        retrieved_df = db.get_candles(self.db_file)
        self.assertEqual(len(retrieved_df), 2)
        self.assertEqual(retrieved_df.iloc[0]['open'], 100)

if __name__ == '__main__':
    unittest.main()
