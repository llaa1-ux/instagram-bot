# bot_render.py
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Variáveis de ambiente
TOKEN = os.getenv("TOKEN")  # Token do Bot
PORT = int(os.getenv("PORT", 5000))  # Porta do Render
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Ex: "https://instagram-bot-3awu.onrender.com/"

if not TOKEN or not WEBHOOK_URL:
    raise ValueError("As variáveis de ambiente TOKEN e WEBHOOK_URL devem estar definidas.")

# Função /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot ativo! 🚀")

# Criar aplicação
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

# Rodar webhook
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=WEBHOOK_URL
)
