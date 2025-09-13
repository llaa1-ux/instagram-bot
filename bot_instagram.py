# bot_instagram_render.py
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
TOKEN = os.getenv("TOKEN")  # Token do Bot
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Ex: https://instagram-bot-3awu.onrender.com/
PORT = int(os.getenv("PORT", 5000))  # Porta padrão Render

if not TOKEN or not WEBHOOK_URL:
    raise ValueError("As variáveis de ambiente TOKEN e WEBHOOK_URL devem estar definidas.")

# Função /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot ativo! 🚀 Tentando pegar posts do Instagram...")

    # Instaloader
    L = instaloader.Instaloader()
    
    test_profile = "instagram"  # perfil público para teste
    try:
        profile = instaloader.Profile.from_username(L.context, test_profile)
        post = next(profile.get_posts())  # pegar último post
        await update.message.reply_text(f"Último post de {test_profile}: {post.url}")
    except Exception as e:
        logging.warning(f"Erro ao buscar post: {e}")
        await update.message.reply_text("Não foi possível acessar o Instagram ou perfil privado.")

# Criar aplicação
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

# Rodar webhook
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=WEBHOOK_URL
)
