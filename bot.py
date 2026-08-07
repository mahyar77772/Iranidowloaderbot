import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import requests

TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context):
    await update.message.reply_text("سلام! لینک مستقیم دانلود رو برام بفرست تا فایل رو برات دانلود کنم.")

async def download_file(update: Update, context):
    url = update.message.text
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            filename = url.split("/")[-1] or "downloaded_file"
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            await update.message.reply_document(document=open(filename, 'rb'))
            os.remove(filename)
        else:
            await update.message.reply_text("لینک معتبر نیست یا فایل پیدا نشد.")
    except Exception as e:
        await update.message.reply_text(f"خطا: {str(e)}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_file))
print("ربات در حال اجراست...")
app.run_polling()
