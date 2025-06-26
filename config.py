import os

# Configuration de l'API Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'VOTRE_TOKEN_BOT')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', 'VOTRE_CHAT_ID')

# Configuration Binance
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

# Paramètres du trading
SYMBOL = 'ETHUSDT'
TIME_INTERVAL = '30s'  # Intervalle de prédiction
PREDICTION_CONFIDENCE = 0.9  # 90% de confiance minimum

# Paramètres du modèle
MODEL_PATH = 'trained_model/xgboost_model.json'
