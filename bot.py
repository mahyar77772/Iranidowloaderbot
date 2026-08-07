import os
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = os.environ.get("TOKEN")

def start(update, context):
    update.message.reply_text("سلام! لینک مستقیم دانلود رو بفرست.")

def download_file(update, context):
    url = update.message.text
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            filename = url.split("/")[-1] or "downloaded_file"
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            update.message.reply_document(document=open(filename, 'rb'))
            os.remove(filename)
        else:
            update.message.reply_text("❌ لینک معتبر نیست.")
    except Exception as e:
        update.message.reply_text(f"❌ خطا: {str(e)}")

updater = Updater(token=TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_file))
print("ربات در حال اجراست...")
updater.start_polling()
updater.idle()
