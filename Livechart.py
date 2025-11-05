import pandas as pd
import pandas_ta as ta
import configparser
from datetime import datetime
import time
from delta_rest_client import DeltaRestClient

class LiveChart:
    def __init__(self, config_path='config.ini'):
        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

        # Initialize Delta client
        self.api_key = self.config['api']['key']
        self.api_secret = self.config['api']['secret']
        self.base_url = "https://api.india.delta.exchange"
        self.client = DeltaRestClient(
            api_key=self.api_key,
            api_secret=self.api_secret,
            base_url=self.base_url
        )

        # Chart settings
        self.symbol = self.config['trading']['symbol']
        self.timeframe = self.config['trading']['timeframe']
        self.candle_limit = self.config.getint('chart', 'candle_limit')
        self.update_interval = self.config.getint('chart', 'update_interval')

        # Indicator settings
        self.show_sma = self.config.getboolean('indicators', 'show_sma')
        self.show_supertrend = self.config.getboolean('indicators', 'show_supertrend')
        self.atr_period = self.config.getint('indicators', 'atr_period')
        self.atr_multiplier = self.config.getfloat('indicators', 'atr_multiplier')

        # Initialize empty DataFrame
        self.df = pd.DataFrame()

    def calculate_indicators(self, df):
        """Calculate technical indicators using pandas_ta"""
        if self.show_sma:
            df.ta.sma(length=20, append=True, col_names=('SMA20',))
            df.ta.sma(length=50, append=True, col_names=('SMA50',))

        if self.show_supertrend:
            st = df.ta.supertrend(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                length=self.atr_period,
                multiplier=self.atr_multiplier
            )
            df['Supertrend'] = st[f'SUPERT_{self.atr_period}_{self.atr_multiplier}']
            df['Supertrend_Direction'] = st[f'SUPERTd_{self.atr_period}_{self.atr_multiplier}']

        return df

    def fetch_candles(self):
        """Fetch latest candles from Delta Exchange using traded prices"""
        try:
            # Get current timestamp
            end_time = int(datetime.now().timestamp())
            start_time = end_time - (self.candle_limit * self.get_timeframe_seconds())

            # Prepare parameters for traded price history
            query_params = {
                'symbol': self.symbol,
                'resolution': self.timeframe,
                'start': start_time,
                'end': end_time
            }

            # Use the request method with the correct endpoint
            response = self.client.request(
                method='GET',
                path='/v2/history/candles',
                query=query_params
            )

            if not response.ok:
                print(f"API request failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None

            data = response.json()
            if not data or 'result' not in data:
                print("No data received from API")
                print(f"Response: {data}")
                return None

            candles = data['result']
            df = pd.DataFrame(candles)

            # Verify required columns exist
            required_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                print(f"Missing required columns. Available columns: {df.columns.tolist()}")
                return None

            # Convert timestamp and set index
            df['timestamp'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('timestamp', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume']]

            # Convert string values to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Sort index to ensure chronological order
            df.sort_index(inplace=True)

            return df

        except Exception as e:
            print(f"Error fetching candles: {str(e)}")
            print(f"Parameters: {query_params}")
            import traceback
            print(traceback.format_exc())
            return None

    def get_timeframe_seconds(self):
        """Convert timeframe to seconds"""
        unit = self.timeframe[-1]
        value = int(self.timeframe[:-1])

        if unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
        elif unit == 'd':
            return value * 86400
        return 60  # default to 1m

    def run(self):
        """Main loop for live chart updates"""
        print(f"Starting live data feed for {self.symbol} on {self.timeframe} timeframe")

        while True:
            try:
                new_data = self.fetch_candles()
                if new_data is not None:
                    self.df = new_data
                    self.df = self.calculate_indicators(self.df)
                    print(self.df)

                print(f"Data updated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(self.update_interval)
            except KeyboardInterrupt:
                print("\nStopping live data feed...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    print("This script fetches live cryptocurrency data and calculates technical indicators.")
    print("Due to limitations in the execution environment, the plotting functionality has been disabled.")
    print("You can run this script on your local machine to see the charts.")
    chart = LiveChart('config.ini')
    chart.run()
