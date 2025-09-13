import os
from instaloader import Instaloader, Profile
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Variáveis de ambiente
TOKEN = os.getenv("TOKEN")
PORT = int(os.getenv("PORT", 5000))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Ex: https://instagram-bot-3awu.onrender.com/

# Inicializando Instaloader
L = Instaloader()
SESSION_FILE = "session_instagram"  # nome do arquivo de sessão que você adicionou
USERNAME_INSTAGRAM = os.getenv("IG_USERNAME")

try:
    L.load_session_from_file(USERNAME_INSTAGRAM, SESSION_FILE)
    print("Sessão do Instagram carregada ✅")
except Exception as e:
    print(f"Erro ao carregar sessão de cookies: {e}")

# Função /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot ativo! ✅")

# Função /perfil para buscar info de perfil
async def perfil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: /perfil <username>")
        return
    username = context.args[0]
    try:
        profile = Profile.from_username(L.context, username)
        msg = (
            f"Perfil: {profile.username}\n"
            f"Nome: {profile.full_name}\n"
            f"Seguidores: {profile.followers}\n"
            f"Seguindo: {profile.followees}\n"
            f"Posts: {profile.mediacount}"
        )
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")

# Inicializando bot
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("perfil", perfil))

# Rodando webhook
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=WEBHOOK_URL
)
