import pandas as pd
import pandas_ta as ta

class IncrementalSupertrend:
    def __init__(self, initial_df, length=7, multiplier=3.0):
        self.length = length
        self.multiplier = multiplier
        self.prev_close = None
        self.prev_atr = None
        self.prev_supertrend = None
        self.prev_direction = None
        self._initialize(initial_df)

    def _initialize(self, df):
        # Calculate ATR and Supertrend using pandas_ta
        df.ta.atr(length=self.length, append=True)
        df.ta.supertrend(length=self.length, multiplier=self.multiplier, append=True)

        # Store the last known values
        last_row = df.iloc[-1]
        self.prev_close = last_row['close']
        self.prev_atr = last_row[f'ATRr_{self.length}']
        self.prev_supertrend = last_row[f'SUPERT_{self.length}_{self.multiplier}']
        self.prev_direction = last_row[f'SUPERTd_{self.length}_{self.multiplier}']

    def update(self, new_candle):
        high = new_candle['high']
        low = new_candle['low']
        close = new_candle['close']

        # Calculate True Range (TR)
        tr = max(high - low, abs(high - self.prev_close), abs(low - self.prev_close))

        # Calculate ATR
        atr = ((self.prev_atr * (self.length - 1)) + tr) / self.length

        # Calculate Supertrend bands
        basic_upper_band = (high + low) / 2 + self.multiplier * atr
        basic_lower_band = (high + low) / 2 - self.multiplier * atr

        # Update bands based on previous Supertrend
        upper_band = min(basic_upper_band, self.prev_supertrend if self.prev_direction == 1 else float('inf'))
        lower_band = max(basic_lower_band, self.prev_supertrend if self.prev_direction == -1 else float('-inf'))

        # Determine direction and Supertrend
        direction = self.prev_direction
        if close > self.prev_supertrend:
            direction = 1
            supertrend = lower_band
        else:
            direction = -1
            supertrend = upper_band

        # Update state for next iteration
        self.prev_close = close
        self.prev_atr = atr
        self.prev_supertrend = supertrend
        self.prev_direction = direction

        return supertrend, direction
