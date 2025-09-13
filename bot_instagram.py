import os
import asyncio
import instaloader
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ▼▼▼ TOKEN DO BOT ▼▼▼
TOKEN = os.getenv("TOKEN")
# ▲▲▲ TOKEN DO BOT ▲▲▲

# Usuário do Instagram (para carregar sessão)
IG_USERNAME = os.getenv("IG_USERNAME")
SESSION_FILE = f"{IG_USERNAME}.session"

# Pasta para downloads temporários
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Inicializa Instaloader
L = instaloader.Instaloader(dirname_pattern=DOWNLOAD_DIR, save_metadata=False, download_comments=False, post_metadata_txt_pattern="")

if os.path.exists(SESSION_FILE):
    L.load_session_from_file(username=IG_USERNAME, filename=SESSION_FILE)
else:
    print("⚠️ Sessão não encontrada. Crie o arquivo .session usando instaloader --login SEU_USUARIO.")

# Função para baixar mídias do Instagram
def baixar_midias_instagram(url: str):
    arquivos = []
    try:
        post = instaloader.Post.from_shortcode(L.context, url.strip("/").split("/")[-1])
        count = 0
        for idx, media in enumerate(post.get_sidecar_nodes() if post.is_sidecar else [post]):
            if count >= 20:
                break
            filename = os.path.join(DOWNLOAD_DIR, f"{post.shortcode}_{idx}")
            if media.is_video:
                L.download_pic(filename + ".mp4", media.video_url, post.date_utc)
                arquivos.append(filename + ".mp4")
            else:
                L.download_pic(filename + ".jpg", media.url, post.date_utc)
                arquivos.append(filename + ".jpg")
            count += 1
    except Exception as e:
        print(f"Erro ao baixar Instagram: {e}")
        return []

    return arquivos

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! 👋 Envie um link do Instagram e eu baixarei até 20 fotos ou vídeos desse post."
    )

# Quando usuário envia link
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    media_paths = []

    processing_msg = await update.message.reply_text("⏳ Processando seu link...")

    try:
        if "instagram.com/p/" in url:
            media_paths = await asyncio.to_thread(baixar_midias_instagram, url)

            if not media_paths:
                await processing_msg.edit_text(
                    "❌ Não foi possível baixar nenhuma mídia.\n"
                    "O post pode ser privado ou a sessão expirou."
                )
                return

            media_group = []
            files_to_send = [open(path, "rb") for path in media_paths]

            for i, path in enumerate(media_paths):
                ext = path.lower()
                if ext.endswith((".mp4", ".mov", ".webm")):
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

# Rodar bot
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("🤖 Bot Instagram rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()
