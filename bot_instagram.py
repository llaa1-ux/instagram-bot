import os
import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# ---------------- Configurações ----------------
IG_USERNAME = "seu_usuario"
IG_PASSWORD = "sua_senha"  # Necessário para criar a sessão
SESSION_FILE = f"session-{IG_USERNAME}"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # Ex: https://seu-app.onrender.com/{TELEGRAM_TOKEN}

# ---------------- Instaloader ----------------
L = instaloader.Instaloader()

# Tenta carregar a sessão
try:
    L.load_session_from_file(IG_USERNAME, filename=SESSION_FILE)
    print("Sessão carregada!")
except FileNotFoundError:
    # Se não existir, loga e salva a sessão
    try:
        L.login(IG_USERNAME, IG_PASSWORD)
        L.save_session_to_file(filename=SESSION_FILE)
        print("Sessão criada e salva!")
    except Exception as e:
        print(f"Erro ao logar no Instagram: {e}")
        exit(1)

# ---------------- Comando /start ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot online! Testando acesso ao Instagram...")
    try:
        profile = instaloader.Profile.from_username(L.context, IG_USERNAME)
        await update.message.reply_text(
            f"Nome: {profile.full_name}\nSeguidores: {profile.followers}"
        )
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")

# ---------------- Inicializa bot ----------------
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))

# Se você quiser responder mensagens genéricas
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Você disse: {update.message.text}")

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# ---------------- Webhook ----------------
if WEBHOOK_URL:
    # Render usa HTTPS, então webhook é obrigatório
    print(f"Usando webhook: {WEBHOOK_URL}")
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=WEBHOOK_URL
    )
else:
    # Fallback para polling (não recomendado em produção Render)
    print("WEBHOOK_URL não definido, usando polling (somente teste local).")
    app.run_polling()
