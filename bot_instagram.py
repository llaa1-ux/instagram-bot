import os
import asyncio
import instaloader
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# -----------------------
# Configurações
# -----------------------
IG_USERNAME = os.environ.get("IG_USERNAME")  # usuário Instagram
SESSION_FILE = f"session-{IG_USERNAME}"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # token Telegram
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # URL completa do webhook, ex: https://meuapp.onrender.com/webhook

# -----------------------
# Instaloader
# -----------------------
L = instaloader.Instaloader()
try:
    L.load_session_from_file(IG_USERNAME, filename=SESSION_FILE)
    print(f"Sessão do Instagram carregada: {SESSION_FILE}")
except Exception as e:
    print(f"Erro ao carregar sessão: {e}")
    exit(1)

# -----------------------
# Comando /start
# -----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot online! Testando acesso ao Instagram...")

    try:
        profile = instaloader.Profile.from_username(L.context, IG_USERNAME)
        await update.message.reply_text(
            f"Nome: {profile.full_name}\nSeguidores: {profile.followers}"
        )
    except Exception as e:
        await update.message.reply_text(f"Erro ao acessar perfil: {e}")

# -----------------------
# Aplicação Telegram
# -----------------------
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # Remove webhook antigo
    await app.bot.delete_webhook(drop_pending_updates=True)
    # Define webhook novo
    await app.bot.set_webhook(url=WEBHOOK_URL)

    # Cria servidor para receber updates
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8000)))
    print(f"Webhook definido: {WEBHOOK_URL}")
    await site.start()

    # Mantém o bot rodando
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
