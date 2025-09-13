import os
import asyncio
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import instaloader

# ▼▼▼ Variáveis de ambiente ▼▼▼
TOKEN = os.getenv("TOKEN")
IG_USERNAME = os.getenv("IG_USERNAME")
COOKIE_FILE = os.getenv("COOKIE_FILE")
# ▲▲▲ Variáveis de ambiente ▲▲▲

# Pasta temporária para downloads
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Inicializa Instaloader
L = instaloader.Instaloader(dirname_pattern=DOWNLOAD_DIR, download_videos=True, save_metadata=False)
if COOKIE_FILE and os.path.exists(COOKIE_FILE):
    try:
        L.load_session_from_file(username=IG_USERNAME, filename=COOKIE_FILE)
    except Exception as e:
        print(f"⚠️ Erro ao carregar sessão de cookies: {e}")

# Função para baixar mídias de um post
def baixar_midias_instagram(url: str):
    from instaloader import Post
    arquivos = []
    try:
        shortcode = url.rstrip("/").split("/")[-1]
        post = Post.from_shortcode(L.context, shortcode)
        count = 0

        # Feed
        for i, item in enumerate(post.get_sidecar_nodes() if post.is_sidecar else [post]):
            if count >= 20:
                break
            filename = f"{DOWNLOAD_DIR}/{post.owner_username}_{count+1}.jpg"
            if item.is_video:
                filename = f"{DOWNLOAD_DIR}/{post.owner_username}_{count+1}.mp4"
                L.download_pic(filename, item.video_url, post.date_utc)
            else:
                L.download_pic(filename, item.url, post.date_utc)
            arquivos.append(filename)
            count += 1

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
        if "instagram.com" in url:
            media_paths = await asyncio.to_thread(baixar_midias_instagram, url)

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
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("🤖 Bot rodando...")
    # Rodando como webhook no Render:
    port = int(os.environ.get("PORT", "8443"))
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"
    )

if __name__ == "__main__":
    main()
