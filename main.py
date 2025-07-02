import telebot
import os
import shutil
import requests
import subprocess

from secrets import GITHUB_USERNAME, GITHUB_TOKEN, RENDER_API_KEY

# Ton token de bot manager ici
TOKEN_MANAGER = "7889057057:AAFUKX0_7m260ZzD7FlZzDHV4ZzAJN82NH8"

bot = telebot.TeleBot(TOKEN_MANAGER)

# État temporaire
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

        success = create_new_bot(bot_name, bot_token)

        if success:
            bot.send_message(chat_id,
                             f"✅ Le bot *{bot_name}* a été créé et poussé sur GitHub !",
                             parse_mode='Markdown')
        else:
            bot.send_message(chat_id,
                             "❌ Une erreur est survenue lors de la création.")

        del user_states[chat_id]

# ------------------- Nouvelle fonction ici ----------------------

def push_to_github(repo_name, local_path):
    try:
        url = "https://api.github.com/user/repos"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "name": repo_name,
            "private": False  # True = privé, False = public
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print(f"✅ Repo GitHub '{repo_name}' créé avec succès.")
        elif response.status_code == 422:
            print(f"⚠️ Repo '{repo_name}' existe déjà, on continue.")
        else:
            print("❌ Erreur création GitHub :", response.text)
            return False

        subprocess.run(["git", "init"], cwd=local_path)
        subprocess.run(["git", "config", "user.name", GITHUB_USERNAME], cwd=local_path)
        subprocess.run(["git", "config", "user.email", f"{GITHUB_USERNAME}@users.noreply.github.com"], cwd=local_path)

        subprocess.run(["git", "add", "."], cwd=local_path)
        subprocess.run(["git", "commit", "-m", "🚀 Déploiement automatique du bot"], cwd=local_path)

        remote_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{repo_name}.git"
        subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=local_path)
        subprocess.run(["git", "push", "-u", "origin", "master"], cwd=local_path)

        print("✅ Code poussé sur GitHub.")
        return True
    except Exception as e:
        print("❌ Erreur lors du push GitHub :", e)
        return False

# ------------------- Mise à jour de create_new_bot ----------------------

def create_new_bot(bot_name, bot_token):
    try:
        src = "template_bot"
        dst = bot_name
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

        # Remplacer le token
        main_py_path = os.path.join(dst, "main.py")
        with open(main_py_path, "r") as f:
            content = f.read()
        content = content.replace("{{TOKEN}}", bot_token)
        with open(main_py_path, "w") as f:
            f.write(content)

        # Pousser sur GitHub
        pushed = push_to_github(bot_name, dst)
        if not pushed:
            return False

        return True
    except Exception as e:
        print("❌ Erreur dans create_new_bot :", e)
        return False

# ------------------- Lancement ----------------------

print("✅ Bot manager lancé...")
bot.polling()
