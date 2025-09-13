import os
import instaloader
from aiohttp import web
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, TelegramObject

# Configurações
IG_USERNAME = os.environ.get("IG_USERNAME")
IG_PASSWORD = os.environ.get("IG_PASSWORD")
SESSION_FILE = f"session-{IG_USERNAME}"

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # ex: https://seu_app.onrender.com/webhook
PORT = int(os.environ.get("PORT", 8443))

# Instaloader
L = instaloader.Instaloader()

def carregar_sessao():
    try:
        L.load_session_from_file(IG_USERNAME, filename=SESSION_FILE)
        print("Sessão carregada!")
    except FileNotFoundError:
        print("Sessão não encontrada. Logando...")
        L.login(IG_USERNAME, IG_PASSWORD)
        L.save_session_to_file(filename=SESSION_FILE)
        print("Sessão salva!")

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot online! Testando acesso ao Instagram...")
    carregar_sessao()
    try:
        profile = instaloader.Profile.from_username(L.context, IG_USERNAME)
        await update.message.reply_text(
            f"Nome: {profile.full_name}\nSeguidores: {profile.followers}"
        )
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")

async def handle(request):
    """Recebe updates via webhook do Telegram"""
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.update_queue.put(update)
    return web.Response(text="OK")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))

async def main():
    # Remove webhook antigo e define o novo
    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.bot.set_webhook(url=WEBHOOK_URL)
    print(f"Webhook definido: {WEBHOOK_URL}")

    # Inicializa servidor aiohttp
    runner = web.AppRunner(web.Application())
    runner.app.router.add_post("/webhook", handle)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Servidor webhook rodando na porta {PORT}")

    # Mantém o bot rodando
    await app.initialize()
    await app.start()
    await app.updater.start_polling()  # polling vazio apenas para processar a queue
    while True:
        await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    carregar_sessao()
    asyncio.run(main())

