import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import instaloader

# Variáveis de ambiente
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")

# Inicializar Instaloader e login
L = instaloader.Instaloader()

try:
    L.load_session_from_file(IG_USERNAME)
except FileNotFoundError:
    L.login(IG_USERNAME, IG_PASSWORD)
    L.save_session_to_file()

# Função de comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot ativo! Instagram conectado ✅")

# Inicializar bot
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # Rodar webhook
    port = int(os.environ.get("PORT", 8443))
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
