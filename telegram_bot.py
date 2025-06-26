import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import time
import threading
from config import TELEGRAM_BOT_TOKEN, ADMIN_CHAT_ID, SYMBOL, TIME_INTERVAL, PREDICTION_CONFIDENCE
from data_collector import DataCollector
from prediction_model import PredictionModel
from market_analysis import MarketAnalyzer

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        self.data_collector = DataCollector()
        self.prediction_model = PredictionModel()
        self.market_analyzer = MarketAnalyzer()
        self.is_running = False
        self.prediction_thread = None
        
        # Démarrer la collecte de données
        self.data_collector.start_collecting()
        
    def start(self, update: Update, context: CallbackContext):
        """Gère la commande /start"""
        user = update.effective_user
        if str(user.id) != ADMIN_CHAT_ID:
            update.message.reply_text("Désolé, vous n'êtes pas autorisé à utiliser ce bot.")
            return
        
        if self.is_running:
            update.message.reply_text("Le bot est déjà en cours d'exécution.")
            return
        
        self.is_running = True
        update.message.reply_text("🚀 Bot de trading ETH/USDT démarré!")
        
        # Démarrer le thread de prédiction
        self.prediction_thread = threading.Thread(target=self.run_prediction_loop, daemon=True)
        self.prediction_thread.start()
    
    def stop(self, update: Update, context: CallbackContext):
        """Gère la commande /stop"""
        user = update.effective_user
        if str(user.id) != ADMIN_CHAT_ID:
            update.message.reply_text("Désolé, vous n'êtes pas autorisé à utiliser ce bot.")
            return
        
        if not self.is_running:
            update.message.reply_text("Le bot n'est pas en cours d'exécution.")
            return
        
        self.is_running = False
        if self.prediction_thread:
            self.prediction_thread.join()
        update.message.reply_text("🛑 Bot de trading arrêté.")
    
    def status(self, update: Update, context: CallbackContext):
        """Gère la commande /status"""
        user = update.effective_user
        if str(user.id) != ADMIN_CHAT_ID:
            update.message.reply_text("Désolé, vous n'êtes pas autorisé à utiliser ce bot.")
            return
        
        status_msg = "🟢 En cours d'exécution" if self.is_running else "🔴 Arrêté"
        update.message.reply_text(f"Statut du bot: {status_msg}")
    
    def run_prediction_loop(self):
        """Boucle principale de prédiction"""
        while self.is_running:
            try:
                # Préparer les features
                features = self.prediction_model.prepare_features(self.data_collector)
                
                if features is not None:
                    # Faire la prédiction
                    prediction, confidence = self.prediction_model.predict(features)
                    
                    # Vérifier la confiance
                    if confidence >= PREDICTION_CONFIDENCE:
                        # Analyser les conditions du marché
                        df = pd.DataFrame(self.data_collector.klines)
                        if not df.empty:
                            df = self.market_analyzer.add_technical_indicators(df)
                            market_conditions = self.market_analyzer.analyze_market_conditions(df)
                            
                            # Préparer le message
                            message = (
                                f"📊 Prédiction ETH/USDT ({TIME_INTERVAL})\n"
                                f"🔮 Direction: {prediction}\n"
                                f"🔼 Confiance: {confidence:.2%}\n\n"
                                f"📈 Conditions du marché:\n"
                                f"- RSI: {'Sur-achat' if market_conditions['overbought'] else 'Sur-vente' if market_conditions['oversold'] else 'Neutre'}\n"
                                f"- Tendance court terme: {market_conditions['short_trend']}\n"
                                f"- Tendance moyen terme: {market_conditions['medium_trend']}\n"
                                f"- Position VWAP: {market_conditions['vwap_position']}\n\n"
                                f"⚠️ Activité des baleines: {'Oui' if self.data_collector.detect_whale_activity() else 'Non'}\n"
                                f"🔄 Spoofing détecté: {'Oui' if self.data_collector.detect_spoofing() else 'Non'}"
                            )
                            
                            # Envoyer la prédiction
                            self.updater.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)
                
                # Attendre l'intervalle suivant
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle de prédiction: {e}")
                time.sleep(10)
    
    def error_handler(self, update: Update, context: CallbackContext):
        """Gère les erreurs"""
        logger.error(f"Erreur: {context.error}")
        if update.effective_message:
            update.effective_message.reply_text("Une erreur s'est produite. Veuillez réessayer.")

def main():
    # Créer le bot de trading
    trading_bot = TradingBot()
    
    # Créer l'updater Telegram
    updater = Updater(TELEGRAM_BOT_TOKEN)
    trading_bot.updater = updater
    
    # Gestionnaires de commandes
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", trading_bot.start))
    dp.add_handler(CommandHandler("stop", trading_bot.stop))
    dp.add_handler(CommandHandler("status", trading_bot.status))
    
    # Gestionnaire d'erreurs
    dp.add_error_handler(trading_bot.error_handler)
    
    # Démarrer le bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
