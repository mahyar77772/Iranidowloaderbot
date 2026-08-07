import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

TOKEN = os.environ.get("TOKEN")
CHANNEL = "@kanalasli2424"  # اسم کانال شما

async def is_member(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context):
    await update.message.reply_text(
        "🎯 به ربات دانلودر خوش آمدید!\n\n"
        "📌 لینک مستقیم دانلود رو بفرست تا برات دانلود کنم.\n"
        f"🔒 برای استفاده، ابتدا عضو کانال ما شوید:\n{CHANNEL}"
    )

async def download_file(update: Update, context):
    user_id = update.effective_user.id
    url = update.message.text

    if not await is_member(user_id, context):
        await update.message.reply_text(f"❌ ابتدا در کانال {CHANNEL} عضو شوید.")
        return

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
            await update.message.reply_text("❌ لینک معتبر نیست.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_file))
print("✅ ربات با موفقیت روشن شد و در حال اجراست...")
app.run_polling()
