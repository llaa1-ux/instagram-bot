import os
import asyncio
import instaloader
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ▼▼▼ VARIÁVEIS DE AMBIENTE ▼▼▼
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
# ▲▲▲ VARIÁVEIS DE AMBIENTE ▲▲▲

# Configurar Instaloader
L = instaloader.Instaloader(download_videos=True, download_video_thumbnails=False,
                            download_geotags=False, download_comments=False,
                            post_metadata_txt_pattern="", max_connection_attempts=3)

if os.path.exists("cookies_instagram.txt"):
    L.load_session_from_file(username=None, filename="cookies_instagram.txt")

# Função para baixar mídias de um post do Instagram
def baixar_instagram(url: str):
    arquivos = []

    try:
        shortcode = url.rstrip("/").split("/")[-1]
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        count = 0
        for i, item in enumerate(post.get_sidecar_nodes() if post.typename == "GraphSidecar" else [post]):
            if count >= 20:  # limita a 20 mídias
                break

            filename = os.path.join(DOWNLOAD_DIR, f"{shortcode}_{i}")
            if hasattr(item, 'is_video') and item.is_video:
                arquivo = filename + ".mp4"
                L.download_pic(arquivo, item.video_url, post.date)
            else:
                arquivo = filename + ".jpg"
                L.download_pic(arquivo, item.url, post.date)

            arquivos.append(arquivo)
            count += 1

    except Exception as e:
        print(f"Erro no download do Instagram: {e}")
        return []

    return arquivos

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! 👋 Envie o link de um post do Instagram que eu baixo até 20 mídias para você."
    )

# Handler de links
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    media_paths = []

    processing_msg = await update.message.reply_text("⏳ Processando seu link...")

    try:
        if "instagram.com" in url:
            media_paths = await asyncio.to_thread(baixar_instagram, url)

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
                elif ext.endswith((".jpg", ".jpeg", ".png")):
                    media_group.append(InputMediaPhoto(files_to_send[i]))

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

# Rodar bot com webhook
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("🤖 Bot do Instagram rodando...")

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 443)),  # Render usa porta HTTPS
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
