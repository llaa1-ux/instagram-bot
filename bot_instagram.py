import os
import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

IG_USERNAME = os.environ["IG_USERNAME"]
SESSION_FILE = f"session-{IG_USERNAME}"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

# Instaloader
L = instaloader.Instaloader()
try:
    L.load_session_from_file(IG_USERNAME, filename=SESSION_FILE)
    print(f"Sessão do Instagram carregada: {SESSION_FILE}")
except Exception as e:
    print(f"Erro ao carregar sessão: {e}")
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
        await update.message.reply_text(f"Erro ao acessar perfil: {e}")

# Inicializa o bot com webhook
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # Remove webhook antigo e seta novo
    import asyncio
    asyncio.run(app.bot.delete_webhook(drop_pending_updates=True))
    asyncio.run(app.bot.set_webhook(url=WEBHOOK_URL))

    # Roda o webhook diretamente (porta padrão 8443 ou PORT do Render)
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        url_path="",  # não precisa de "/webhook" se a URL completa já tem
        webhook_url=WEBHOOK_URL
    )
