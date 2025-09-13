import os
import re
import shutil
import asyncio
import instaloader
from pathlib import Path
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ---------- Config ----------
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
IG_USERNAME = os.environ.get("IG_USERNAME")  # usado apenas para carregar a sessão
WEBHOOK_URL = os.environ["WEBHOOK_URL"]     # ex: https://meuapp.onrender.com/webhook
PORT = int(os.environ.get("PORT", 8443))

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

SESSION_FILE = f"session-{IG_USERNAME}"

# ---------- Instaloader (carrega sessão obrigatória) ----------
L = instaloader.Instaloader(dirname_pattern=str(DOWNLOAD_DIR / "{profile}"))

try:
    # Tenta carregar sessão já salva
    L.load_session_from_file(IG_USERNAME, filename=SESSION_FILE)
    print(f"Loaded session from {SESSION_FILE}.")
except FileNotFoundError:
    print(f"Session file '{SESSION_FILE}' not found. Please generate it locally and upload it.")
    raise SystemExit(1)
except Exception as e:
    print("Erro ao carregar sessão:", e)
    raise SystemExit(1)


# ---------- Utils ----------
SHORTCODE_RE = re.compile(r"instagram\.com/(?:p|reel|tv)/([^/?#&]+)")

def extract_shortcode(url: str) -> str | None:
    m = SHORTCODE_RE.search(url)
    return m.group(1) if m else None

def download_post_by_shortcode(shortcode: str) -> list:
    """
    Faz o download do post (sidecar incluído) usando instaloader.
    Retorna lista de caminhos de arquivo baixados.
    """
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    target = DOWNLOAD_DIR / shortcode
    # Limpa pasta anterior se existir
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    # instaloader.download_post cria arquivos dentro de <target>/<shortcode> ou <profile>/<shortcode>
    # Para garantir que os arquivos acabem no target, usamos download_post com target=target
    L.download_post(post, target=str(target))

    # Coleta arquivos de mídia comuns
    media_files = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.mp4", "*.webm", "*.mov", "*.webp"):
        media_files.extend(sorted(target.rglob(ext)))
    # Retorna caminhos como strings
    return [str(p) for p in media_files]

# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Envie o link do post do Instagram (ou do Twitter/X). Eu baixo até 20 mídias por post.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("Envie um link válido do Instagram.")
        return

    if "instagram.com" not in text:
        await update.message.reply_text("Por favor, envie um link do Instagram.")
        return

    processing = await update.message.reply_text("⏳ Processando...")

    shortcode = extract_shortcode(text)
    if not shortcode:
        await processing.edit_text("Não consegui extrair o shortcode do link. Verifique o link.")
        return

    # Faz o download em thread para não bloquear o loop
    try:
        files = await asyncio.to_thread(download_post_by_shortcode, shortcode)
    except Exception as e:
        await processing.edit_text(f"❌ Erro no download: {e}")
        return

    if not files:
        await processing.edit_text("❌ Não foram encontrados arquivos para esse post (pode ser privado).")
        return

    # Telegram limita 10 itens por media_group; precisamos enviar em lotes
    media_items = []
    files_to_send = []
    try:
        for path in files[:20]:  # limita a 20 mídias conforme solicitado
            lower = path.lower()
            f = open(path, "rb")
            files_to_send.append(f)
            if lower.endswith((".mp4", ".mov", ".webm")):
                media_items.append(InputMediaVideo(f))
            else:
                media_items.append(InputMediaPhoto(f))

        # Envia em lotes de 10
        for i in range(0, len(media_items), 10):
            await update.message.reply_media_group(media_items[i:i+10])

        await processing.delete()
        await update.message.reply_text("✅ Download concluído e enviado (até 20 mídias).")

    except Exception as e:
        await processing.edit_text(f"Erro ao enviar mídias: {e}")

    finally:
        # fecha e remove os arquivos baixados
        for f in files_to_send:
            try:
                f.close()
            except:
                pass
        # limpar pasta do shortcode
        target_dir = DOWNLOAD_DIR / shortcode
        if target_dir.exists():
            try:
                shutil.rmtree(target_dir)
            except Exception as e:
                print("Erro ao remover pasta:", e)


# ---------- Bootstrap do bot com webhook ----------
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start webhook — certifique-se que WEBHOOK_URL termina com /webhook e url_path corresponde a isso
    print("Iniciando run_webhook() com webhook_url=", WEBHOOK_URL)
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="/webhook",      # o caminho que o servidor irá escutar
        webhook_url=WEBHOOK_URL,  # URL pública completa (deve terminar com /webhook)
    )

if __name__ == "__main__":
    main()
