import os
import asyncio
import instaloader
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ▼▼▼ VARIÁVEIS DE AMBIENTE ▼▼▼
TOKEN = os.environ.get("TOKEN")           # Token do Bot Telegram
IG_USERNAME = os.environ.get("IG_USERNAME")  # Seu usuário do Instagram
COOKIE_FILE = os.environ.get("COOKIE_FILE")  # Arquivo de cookies exportado
PORT = int(os.environ.get("PORT", 8443))    # Porta do Render
# ▲▲▲ VARIÁVEIS DE AMBIENTE ▲▲▲

# Criar pasta de downloads temporários
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Inicializa Instaloader
L = instaloader.Instaloader(download_video_thumbnails=False,
                            save_metadata=False,
                            post_metadata_txt_pattern='')

# Carregar sessão de cookies
if COOKIE_FILE and os.path.exists(COOKIE_FILE):
    try:
        L.load_session_from_file(username=IG_USERNAME, filename=COOKIE_FILE)
    except Exception as e:
        print(f"Erro ao carregar sessão de cookies: {e}")

# Função para baixar mídias
def baixar_midias(insta_url: str):
    media_files = []
    try:
        shortcode = insta_url.rstrip('/').split("/")[-1]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        count = 0

        for idx, resource in enumerate(post.get_sidecar_nodes() if post.is_sidecar else [post]):
            if count >= 20:
                break

            ext = "mp4" if resource.is_video else "jpg"
            filename = f"{DOWNLOAD_DIR}/{shortcode}_{idx}.{ext}"
            L.download_pic(filename, resource.display_url, post.date)
            media_files.append(filename)
            count += 1

    except Exception as e:
        print(f"Erro no download: {e}")

    return media_files

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! 👋 Envie um link do Instagram que eu baixo até 20 mídias para você."
    )

# Quando usuário envia link
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    media_paths = []

    processing_msg = await update.message.reply_text("⏳ Processando seu link...")

    try:
        if "instagram.com/p/" in url:
            media_paths = await asyncio.to_thread(baixar_midias, url)

            if not media_paths:
                await processing_msg.edit_text(
                    "❌ Não foi possível baixar nenhuma mídia.\n"
                    "O post pode ser privado ou os cookies expiraram."
                )
                return

            media_group = []
            files_to_send = [open(path, "rb") for path in media_paths]

            for i, path in enumerate(media_paths):
                ext = path.lower()
                if ext.endswith(".mp4"):
                    media_group.append(InputMediaVideo(files_to_send[i]))
                else:
                    media_group.append(InputMediaPhoto(files_to_send[i]))

            # Envia mídias em grupos de até 10
            for i in range(0, len(media_group), 10):
                await update.message.reply_media_group(media_group[i:i+10])

            await processing_msg.delete()

        else:
            await processing_msg.edit_text("❌ Por favor, envie um link válido do Instagram.")

    except Exception as e:
        await processing_msg.edit_text(f"❌ Ocorreu um erro: {e}")

    finally:
        if 'files_to_send' in locals():
            for f in files_to_send:
                f.close()
        for path in media_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError as e:
                    print(f"Erro ao remover arquivo {path}: {e}")

# Rodar bot via Webhook
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    # URL pública fornecida pelo Render
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"
    print(f"Webhook URL: {webhook_url}")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url_path="",
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()
