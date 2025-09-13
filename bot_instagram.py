import os
import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Configurações
IG_USERNAME = os.environ.get("IG_USERNAME", "seu_usuario")  # usuário definido na env
SESSION_FILE = f"session-{IG_USERNAME}"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]  # precisa estar definido no Render

# Instaloader
L = instaloader.Instaloader()
try:
    L.load_session_from_file(IG_USERNAME, filename=SESSION_FILE)
    print("Sessão carregada com sucesso!")
except Exception as e:
    print(f"Erro ao carregar sessão: {e}")
    exit(1)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot online! Testando acesso ao Instagram...")

    try:
        profile = instaloader.Profile.from_username(L.context, IG_USERNAME)
        await update.message.reply_text(
            f"Nome: {profile.full_name}\n"
            f"Usuário: @{profile.username}\n"
            f"Seguidores: {profile.followers}\n"
            f"Seguindo: {profile.followees}"
        )
    except Exception as e:
        await update.message.reply_text(f"Erro ao acessar Instagram: {e}")

# Inicializa bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot iniciado no Telegram 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
