import telebot

# Ton token BotFather ici
TOKEN_MANAGER = '7889057057:AAFUKX0_7m260ZzD7FlZzDHV4ZzAJN82NH8'

# Créer l'objet bot
bot = telebot.TeleBot(TOKEN_MANAGER)

# Commande /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Bienvenue dans le *Bot Manager*.\n\nUtilise /deploy pour créer un nouveau bot.", parse_mode='Markdown')

# Commande /deploy
@bot.message_handler(commands=['deploy'])
def deploy(message):
    bot.send_message(message.chat.id, "🛠️ La fonction de déploiement arrive bientôt.\nPrépare-toi à créer un nouveau bot automatiquement !")

# Lancer le bot
print("✅ Bot manager lancé...")
bot.polling()