import os
import asyncio
import instaloader
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ▼▼▼ TOKEN DO BOT ▼▼▼
TOKEN = os.getenv("TOKEN")
APP_URL = os.getenv("APP_URL")  # URL pública do Render
# ▲▲▲ TOKEN DO BOT ▲▲▲

# Pasta para downloads temporários
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Função para baixar mídias do Instagram
def baixar_midias(url: str):
    L = instaloader.Instaloader(
        download_videos=True,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        dirname_pattern=DOWNLOAD_DIR,
        filename_pattern="{shortcode}_{count}"
    )

    # Carrega cookies se existir
    if os.path.exists("cookies_instagram.txt"):
        L.load_session_from_file("your_username", filename="cookies_instagram.txt")

    arquivos = []

    try:
        shortcode = url.rstrip("/").split("/")[-1]
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        count = 1
        for idx, node in enumerate(post.get_sidecar_nodes() if post.typename == "GraphSidecar" else [post]):
            if hasattr(node, "is_video") and node.is_video:
                filename = os.path.join(DOWNLOAD_DIR, f"{shortcode}_{count}.mp4")
                L.download_pic(filename, node.video_url, post.date_utc)
            else:
                filename = os.path.join(DOWNLOAD_DIR, f"{shortcode}_{count}.jpg")
                L.download_pic(filename, node.url, post.date_utc)
            arquivos.append(filename)
            count += 1
            if count > 20:  # Limite de 20 mídias
                break

    except Exception as e:
        print(f"Erro no download: {e}")
        return []

    return arquivos

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! 👋 Envie um link do Instagram que eu baixo até 20 mídias para você.\n"
        "Posts com várias mídias também serão baixados."
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
                if ext.endswith((".mp4", ".mov", ".webm")):
                    media_group.append(InputMediaVideo(files_to_send[i]))
                elif ext.endswith((".jpg", ".jpeg", ".png", ".webp")):
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

# Rodar bot
def main():
    PORT = int(os.getenv("PORT", 10000))

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    # Rodar webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{APP_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
