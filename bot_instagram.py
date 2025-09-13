import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import instaloader

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Variáveis de ambiente
TOKEN = os.getenv("TOKEN")
IG_USERNAME = os.getenv("IG_USERNAME")
COOKIE_FILE = os.getenv("COOKIE_FILE")  # Ex: cookies_instagram.txt
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Ex: https://instagram-bot-3awu.onrender.com/instagram
PORT = int(os.getenv("PORT", 5000))

# Inicializar Instaloader
L = instaloader.Instaloader()

# Carregar sessão de cookies
try:
    L.load_session_from_file(username=IG_USERNAME, filename=COOKIE_FILE)
    logging.info("Sessão de cookies carregada com sucesso.")
except Exception as e:
    logging.warning(f"Erro ao carregar sessão de cookies: {e}")

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot do Instagram ativo! Use /download <URL do post> para baixar mídias."
    )

# Comando /download
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Envie o link do post após o comando.")
        return

    post_url = context.args[0]
    try:
        shortcode = post_url.rstrip("/").split("/")[-1]
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        urls = []

        # Caso seja carrossel (múltiplas mídias)
        if post.typename == "GraphSidecar":
            for idx, node in enumerate(post.get_sidecar_nodes(), start=1):
                if idx > 20:  # limitar a 20 mídias
                    break
                urls.append(node.display_url)
        else:  # foto ou vídeo único
            urls.append(post.url)

        # Enviar URLs para o Telegram
        for url in urls:
            await update.message.reply_text(url)

        if not urls:
            await update.message.reply_text("❌ Nenhuma mídia encontrada.")

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao baixar mídia: {e}")

# Main
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download", download))

    # Rodar via webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
