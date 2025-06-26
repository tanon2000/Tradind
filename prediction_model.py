import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os
from config import MODEL_PATH

class PredictionModel:
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Charge le modèle entraîné ou en crée un nouveau"""
        if os.path.exists(MODEL_PATH):
            self.model = xgb.XGBClassifier()
            self.model.load_model(MODEL_PATH)
        else:
            self.train_initial_model()
    
    def train_initial_model(self):
        """Entraîne un modèle initial avec des données factices (à remplacer par vos données réelles)"""
        # Génération de données factices pour l'exemple
        np.random.seed(42)
        X = np.random.rand(1000, 10)  # 10 features
        y = np.random.randint(0, 2, 1000)  # Target binaire (0=DOWN, 1=UP)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        self.model = xgb.XGBClassifier(
            objective='binary:logistic',
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1
        )
        
        self.model.fit(X_train, y_train)
        
        # Évaluation
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Modèle initial entraîné avec une précision de {accuracy:.2f}")
        
        # Sauvegarde du modèle
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        self.model.save_model(MODEL_PATH)
    
    def prepare_features(self, data_collector):
        """Prépare les features pour la prédiction"""
        if not data_collector.klines or not data_collector.order_book:
            return None
        
        # Dernières klines
        last_kline = data_collector.klines[-1]
        prev_kline = data_collector.klines[-2] if len(data_collector.klines) > 1 else last_kline
        
        # Features de prix
        price_change = last_kline['close'] - prev_kline['close']
        price_change_pct = (price_change / prev_kline['close']) * 100
        
        # Features de volume
        volume_change = last_kline['volume'] - prev_kline['volume']
        volume_change_pct = (volume_change / prev_kline['volume']) * 100
        
        # Features du carnet d'ordres
        bids = data_collector.order_book['bids']
        asks = data_collector.order_book['asks']
        
        bid_volume = sum(float(bid[1]) for bid in bids[:5])
        ask_volume = sum(float(ask[1]) for ask in asks[:5])
        order_book_imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume + 1e-6)
        
        # Features de whale activity
        whale_activity = 1 if data_collector.detect_whale_activity() else 0
        
        # Features de spoofing
        spoofing = 1 if data_collector.detect_spoofing() else 0
        
        # Création du vecteur de features
        features = np.array([
            price_change,
            price_change_pct,
            volume_change,
            volume_change_pct,
            bid_volume,
            ask_volume,
            order_book_imbalance,
            whale_activity,
            spoofing,
            last_kline['close']
        ])
        
        return features.reshape(1, -1)
    
    def predict(self, features):
        """Fait une prédiction UP/DOWN"""
        if features is None or self.model is None:
            return None, 0.0
        
        proba = self.model.predict_proba(features)[0]
        prediction = np.argmax(proba)
        confidence = np.max(proba)
        
        return 'UP' if prediction == 1 else 'DOWN', confidence
    
    def update_model(self, new_data, new_labels):
        """Met à jour le modèle avec de nouvelles données"""
        # Préparation des données
        X = np.array(new_data)
        y = np.array(new_labels)
        
        # Entraînement supplémentaire
        self.model.fit(X, y, xgb_model=MODEL_PATH)
        
        # Sauvegarde du modèle mis à jour
        self.model.save_model(MODEL_PATH)
