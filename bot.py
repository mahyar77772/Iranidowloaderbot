import os
import requests
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

TOKEN = os.environ.get("TOKEN")
CHANNELS = ["@your_channel1", "@your_channel2"]  # ← کانال‌های خودت رو اینجا بذار
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 مگابایت

async def is_member_all_channels(user_id, context):
    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False, channel
        except:
            return False, channel
    return True, None

async def start(update: Update, context):
    await update.message.reply_text(
        "🎯 به ربات دانلودر خوش آمدید!\n\n"
        "📌 لینک خود را ارسال کنید.\n"
        "✅ پشتیبانی از یوتیوب، اینستاگرام و لینک‌های مستقیم\n"
        f"🔒 برای دانلود، عضو همه کانال‌ها شوید:\n{', '.join(CHANNELS)}"
    )

async def download_file(update: Update, context):
    user_id = update.effective_user.id
    url = update.message.text

    check, channel = await is_member_all_channels(user_id, context)
    if not check:
        await update.message.reply_text(f"❌ لطفاً ابتدا در کانال {channel} عضو شوید.")
        return

    if "youtube.com" in url or "youtu.be" in url or "instagram.com" in url:
        try:
            await update.message.reply_text("⏳ در حال دانلود از شبکه اجتماعی...")
            ydl_opts = {
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'format': 'best',
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                await update.message.reply_document(document=open(filename, 'rb'))
                os.remove(filename)
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در دانلود: {str(e)}")
        return

    try:
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            await update.message.reply_text("❌ لینک معتبر نیست.")
            return

        content_length = int(response.headers.get('content-length', 0))
        if content_length > MAX_FILE_SIZE:
            await update.message.reply_text("❌ حجم فایل بیش از ۱۰۰ مگابایت است.")
            return

        filename = url.split("/")[-1] or "downloaded_file"
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        await update.message.reply_document(document=open(filename, 'rb'))
        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")

if __name__ == "__main__":
    while True:
        try:
            app = ApplicationBuilder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_file))
            print("✅ ربات با موفقیت روشن شد و در حال اجراست...")
            app.run_polling()
        except Exception as e:
            print(f"❌ خطا: {e}")
            print("🔄 ریاستارت خودکار در ۵ ثانیه...")
            import time
            time.sleep(5)
