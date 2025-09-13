import os
import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Configurações do Instagram
IG_USERNAME = os.environ.get("IG_USERNAME")
IG_PASSWORD = os.environ.get("IG_PASSWORD")
SESSION_FILE = f"session-{IG_USERNAME}"

# Configurações do Telegram
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # Ex: https://seu_app.onrender.com/webhook
PORT = int(os.environ.get("PORT", 8443))

# Inicializa Instaloader
L = instaloader.Instaloader()

def carregar_sessao():
    """Tenta carregar a sessão existente; se falhar, faz login e salva."""
    try:
        L.load_session_from_file(IG_USERNAME, filename=SESSION_FILE)
        print("Sessão do Instagram carregada!")
    except FileNotFoundError:
        print("Arquivo de sessão não encontrado. Fazendo login manual...")
        try:
            L.login(IG_USERNAME, IG_PASSWORD)
            L.save_session_to_file(filename=SESSION_FILE)
            print("Login realizado e sessão salva!")
        except Exception as e:
            print(f"Erro ao fazer login: {e}")
            exit(1)
    except instaloader.exceptions.ConnectionException:
        # Sessão inválida ou expirada
        print("Sessão expirada ou inválida. Fazendo login novamente...")
        try:
            L.login(IG_USERNAME, IG_PASSWORD)
            L.save_session_to_file(filename=SESSION_FILE)
            print("Sessão renovada!")
        except Exception as e:
            print(f"Erro ao renovar sessão: {e}")
            exit(1)

# Comando /start do Telegram
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

# Inicializa bot com webhook
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # Remove webhook antigo e define o novo
    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.bot.set_webhook(url=WEBHOOK_URL)

    print(f"Webhook definido: {WEBHOOK_URL}")
    # Inicia o bot
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_path="/webhook",
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
