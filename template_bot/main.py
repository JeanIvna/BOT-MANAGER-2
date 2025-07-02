import telebot

bot = telebot.TeleBot("{{TOKEN}}")  # Ce token sera remplacé automatiquement par le bot manager

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Salut, je suis un bot déployé automatiquement !")

bot.polling()
