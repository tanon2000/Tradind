import pandas as pd
from binance.client import Client
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor
import json
import time
from config import BINANCE_API_KEY, BINANCE_SECRET_KEY, SYMBOL

class DataCollector:
    def __init__(self):
        self.client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
        self.bm = BinanceSocketManager(self.client)
        self.trades = []
        self.order_book = None
        self.klines = []
        
    def start_collecting(self):
        # Démarrer la collecte des trades
        trade_conn_key = self.bm.start_trade_socket(SYMBOL, self.process_trade_message)
        
        # Démarrer la collecte du carnet d'ordres
        depth_conn_key = self.bm.start_depth_socket(SYMBOL, self.process_depth_message)
        
        # Démarrer la collecte des klines
        kline_conn_key = self.bm.start_kline_socket(SYMBOL, Client.KLINE_INTERVAL_1MINUTE, self.process_kline_message)
        
        self.bm.start()
        
    def process_trade_message(self, msg):
        """Traite les messages de trade en temps réel"""
        self.trades.append(msg)
        if len(self.trades) > 1000:  # Garder seulement les 1000 derniers trades
            self.trades = self.trades[-1000:]
    
    def process_depth_message(self, msg):
        """Traite les messages du carnet d'ordres"""
        self.order_book = msg
    
    def process_kline_message(self, msg):
        """Traite les messages de kline"""
        kline = msg['k']
        self.klines.append({
            'timestamp': kline['t'],
            'open': float(kline['o']),
            'high': float(kline['h']),
            'low': float(kline['l']),
            'close': float(kline['c']),
            'volume': float(kline['v'])
        })
        if len(self.klines) > 500:  # Garder seulement les 500 dernières klines
            self.klines = self.klines[-500:]
    
    def get_historical_data(self, days=30):
        """Récupère les données historiques"""
        klines = self.client.get_historical_klines(
            SYMBOL,
            Client.KLINE_INTERVAL_1HOUR,
            f"{days} day ago UTC"
        )
        return pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
    
    def detect_whale_activity(self):
        """Détecte l'activité des baleines"""
        if not self.trades or not self.order_book:
            return False
        
        # Analyse des gros ordres
        large_trades = [t for t in self.trades if float(t['qty']) > 100]  # Plus de 100 ETH
        
        # Analyse des murs d'ordres
        bids = self.order_book['bids']
        asks = self.order_book['asks']
        large_bid_walls = any(float(bid[1]) > 500 for bid in bids[:5])  # Mur d'achat > 500 ETH
        large_ask_walls = any(float(ask[1]) > 500 for ask in asks[:5])  # Mur de vente > 500 ETH
        
        return len(large_trades) > 5 or large_bid_walls or large_ask_walls
    
    def detect_spoofing(self):
        """Détecte les tentatives de spoofing"""
        if not self.order_book:
            return False
        
        bids = self.order_book['bids']
        asks = self.order_book['asks']
        
        # Vérifie les annulations rapides d'ordres
        # (implémentation simplifiée - une vraie implémentation nécessiterait un suivi temporel)
        return False
