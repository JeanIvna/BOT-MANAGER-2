import telebot

bot = telebot.TeleBot("{{TOKEN}}")  # Le token sera remplacé automatiquement

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Salut, je suis un bot déployé automatiquement !")

bot.polling()
