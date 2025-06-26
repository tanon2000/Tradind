from telegram_bot import TradingBot

if __name__ == '__main__':
    bot = TradingBot()
    bot.updater.start_polling()
    bot.updater.idle()
