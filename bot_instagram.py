import os
import instaloader
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Configurações
IG_USERNAME = os.environ["IG_USERNAME"]
IG_PASSWORD = os.environ["IG_PASSWORD"]
SESSION_FILE = f"session-{IG_USERNAME}"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
PORT = int(os.environ.get("PORT", 8443))

# Instaloader
L = instaloader.Instaloader()
try:
    L.load_session_from_file(IG_USERNAME, filename=SESSION_FILE)
    print("Sessão carregada!")
except Exception as e:
    print(f"Sessão não encontrada. Fazendo login... ({e})")
    try:
        L.login(IG_USERNAME, IG_PASSWORD)
        L.save_session_to_file(SESSION_FILE)
        print("Login realizado e sessão salva!")
    except Exception as e:
        print(f"Erro no login: {e}")
        exit(1)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot online! Testando acesso ao Instagram...")
    try:
        profile = instaloader.Profile.from_username(L.context, IG_USERNAME)
        await update.message.reply_text(
            f"Nome: {profile.full_name}\nSeguidores: {profile.followers}"
        )
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")

# Inicializa bot com webhook
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))

bot: Bot = app.bot
bot.delete_webhook(drop_pending_updates=True)
bot.set_webhook(url=WEBHOOK_URL)

app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url_path="/"
)
