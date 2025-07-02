import telebot
import os
import shutil

from secrets import GITHUB_USERNAME, GITHUB_TOKEN, RENDER_API_KEY

# Remplace par le token de ton bot manager ici
TOKEN_MANAGER = "7889057057:AAFUKX0_7m260ZzD7FlZzDHV4ZzAJN82NH8"

bot = telebot.TeleBot(TOKEN_MANAGER)

# Stockage temporaire de l'état de conversation par utilisateur
user_states = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "👋 Bienvenue dans le Bot Manager !\n"
                     "Utilise la commande /deploy pour créer un nouveau bot.")

@bot.message_handler(commands=['deploy'])
def deploy_start(message):
    chat_id = message.chat.id
    user_states[chat_id] = {'step': 'awaiting_bot_name'}
    bot.send_message(chat_id, "🚀 Envoie le nom du nouveau bot que tu veux créer :")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    if chat_id not in user_states:
        return

    state = user_states[chat_id]

    if state['step'] == 'awaiting_bot_name':
        bot_name = message.text.strip()
        user_states[chat_id]['bot_name'] = bot_name
        user_states[chat_id]['step'] = 'awaiting_bot_token'
        bot.send_message(chat_id,
                         f"Nom reçu : *{bot_name}*\n"
                         f"Maintenant, envoie le token BotFather du nouveau bot :",
                         parse_mode='Markdown')

    elif state['step'] == 'awaiting_bot_token':
        bot_token = message.text.strip()
        user_states[chat_id]['bot_token'] = bot_token
        bot.send_message(chat_id, "Reçu ! Je crée ton bot...")

        bot_name = user_states[chat_id]['bot_name']

        # Appel à la fonction de création du bot
        success = create_new_bot(bot_name, bot_token)

        if success:
            bot.send_message(chat_id,
                             f"✅ Le bot *{bot_name}* a été créé avec succès !",
                             parse_mode='Markdown')
        else:
            bot.send_message(chat_id,
                             "❌ Une erreur est survenue lors de la création du bot.")

        # Nettoyer l'état
        del user_states[chat_id]

def create_new_bot(bot_name, bot_token):
    try:
        # 1. Copier le dossier template_bot vers un nouveau dossier nommé bot_name
        src = "template_bot"
        dst = bot_name
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

        # 2. Remplacer {{TOKEN}} dans main.py du nouveau bot par le token réel
        main_py_path = os.path.join(dst, "main.py")
        with open(main_py_path, "r") as f:
            content = f.read()
        content = content.replace("{{TOKEN}}", bot_token)
        with open(main_py_path, "w") as f:
            f.write(content)

        # TODO: Ici on ajoutera plus tard la création GitHub + déploiement Render

        return True
    except Exception as e:
        print("Erreur lors de la création du bot :", e)
        return False

# Lancement du bot manager
print("✅ Bot manager lancé...")
bot.polling()
