import os
import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- Configs (coloque via env vars no Render) ---
IG_USERNAME = os.environ.get("IG_USERNAME")
SESSION_FILE = f"session-{IG_USERNAME}"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]  # ex: https://seuapp.onrender.com/webhook
PORT = int(os.environ.get("PORT", "8443"))

# --- Instaloader: carrega sessão (deve existir) ---
L = instaloader.Instaloader()
try:
    L.load_session_from_file(IG_USERNAME, filename=SESSION_FILE)
    print(f"Sessão do Instagram carregada: {SESSION_FILE}")
except FileNotFoundError:
    print(f"Arquivo de sessão '{SESSION_FILE}' não encontrado. Gere o session file localmente e envie ao servidor.")
    raise SystemExit(1)
except Exception as e:
    print(f"Erro ao carregar sessão: {e}")
    raise SystemExit(1)

# --- Handler /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot online! Testando acesso ao Instagram...")
    try:
        profile = instaloader.Profile.from_username(L.context, IG_USERNAME)
        await update.message.reply_text(
            f"Nome: {profile.full_name}\nSeguidores: {profile.followers}"
        )
    except Exception as e:
        await update.message.reply_text(f"Erro ao acessar perfil: {e}")

# --- Cria app e roda webhook ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # NÃO chame app.bot.delete_webhook() / app.bot.set_webhook() sem await aqui.
    # Em vez disso, passe webhook_url para run_webhook — com [webhooks] instalado isso funciona.
    print("Iniciando run_webhook() com webhook_url...")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        # url_path vazio porque usamos WEBHOOK_URL completo no Render
        url_path="",
        webhook_url=WEBHOOK_URL,
    )
