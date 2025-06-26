import os

# Configuration Telegram
TELEGRAM_BOT_TOKEN = 'votre_token_bot_telegram'
ADMIN_CHAT_ID = 'votre_chat_id'  # Obtenez-le avec @userinfobot sur Telegram

# Configuration Binance
BINANCE_API_KEY = 'votre_api_key_binance'
BINANCE_SECRET_KEY = 'votre_secret_key_binance'

# Paramètres du trading
SYMBOL = 'ETHUSDT'
TIME_INTERVAL = '30s'
PREDICTION_CONFIDENCE = 0.9  # 90% de confiance minimum

# Paramètres du modèle
MODEL_PATH = 'trained_model/xgboost_model.json'
