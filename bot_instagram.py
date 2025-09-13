import os
import instaloader
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Variáveis de ambiente
TOKEN = os.environ.get("TOKEN")
IG_USERNAME = os.environ.get("IG_USERNAME")
COOKIE_FILE = os.environ.get("COOKIE_FILE")
PORT = int(os.environ.get("PORT", 8443))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# Inicializa Instaloader
L = instaloader.Instaloader()
try:
    L.load_session_from_file(username=IG_USERNAME, filename=COOKIE_FILE)
except Exception as e:
    print("Erro ao carregar sessão de cookies:", e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Instagram ativo! Use /download <URL do post>.")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Envie o link do post do Instagram. Ex: /download https://www.instagram.com/p/xxxx")
        return

    post_url = context.args[0]
    shortcode = post_url.rstrip("/").split("/")[-1]
    
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        media_count = 0
        media_files = []

        for idx, resource in enumerate(post.get_sidecar_nodes(), start=1):
            if idx > 20:
                break
            filename = f"{shortcode}_{idx}.jpg"
            L.download_pic(filename, resource.display_url, post.date_utc)
            media_files.append(filename)
            media_count += 1

        if media_count == 0:
            # Se não for sidecar, tenta apenas a mídia principal
            filename = f"{shortcode}.jpg"
            L.download_pic(filename, post.url, post.date_utc)
            media_files.append(filename)
            media_count = 1

        await update.message.reply_text(f"✅ Baixadas {media_count} mídias do post {shortcode}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao baixar: {e}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download", download))

    # Webhook
    print("Webhook URL:", WEBHOOK_URL)
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
