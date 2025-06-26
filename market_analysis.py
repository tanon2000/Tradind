import numpy as np
import pandas as pd
from ta import add_all_ta_features
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from ta.volume import VolumeWeightedAveragePrice

class MarketAnalyzer:
    def __init__(self):
        pass
    
    def add_technical_indicators(self, df):
        """Ajoute des indicateurs techniques au DataFrame"""
        df = df.copy()
        
        # Conversion des types
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['open'] = df['open'].astype(float)
        df['volume'] = df['volume'].astype(float)
        
        # RSI
        rsi = RSIIndicator(close=df['close'], window=14)
        df['rsi'] = rsi.rsi()
        
        # Bollinger Bands
        bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_high'] = bb.bollinger_hband()
        df['bb_low'] = bb.bollinger_lband()
        
        # VWAP
        vwap = VolumeWeightedAveragePrice(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            volume=df['volume'],
            window=20
        )
        df['vwap'] = vwap.volume_weighted_average_price()
        
        return df
    
    def analyze_market_conditions(self, df):
        """Analyse les conditions du marché"""
        if len(df) < 20:  # Pas assez de données
            return None
        
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]
        
        # Sur-achat/sur-vente
        overbought = last_row['rsi'] > 70
        oversold = last_row['rsi'] < 30
        
        # Position par rapport aux Bollinger Bands
        above_bb_high = last_row['close'] > last_row['bb_high']
        below_bb_low = last_row['close'] < last_row['bb_low']
        
        # Tendance
        short_trend = 'up' if last_row['close'] > df['close'].iloc[-5] else 'down'
        medium_trend = 'up' if last_row['close'] > df['close'].iloc[-20] else 'down'
        
        return {
            'overbought': overbought,
            'oversold': oversold,
            'above_bb_high': above_bb_high,
            'below_bb_low': below_bb_low,
            'short_trend': short_trend,
            'medium_trend': medium_trend,
            'vwap_position': 'above' if last_row['close'] > last_row['vwap'] else 'below'
        }
