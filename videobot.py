import os
import time
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters
)
import yt_dlp

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Send any YouTube, Insta, TikTok, or X video link and I’ll fetch it in best quality!")

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("⏳ Downloading video...")

    try:
        start_time = time.time()

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": "downloads/%(title).70s.%(ext)s",
            "noplaylist": True,
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True
        }

        os.makedirs("downloads", exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            raw_filename = ydl.prepare_filename(info)

        # Detect actual file extension
        filename = None
        possible_exts = ["mp4", "webm", "mkv", "mov", "avi"]
        base_name = raw_filename.rsplit(".", 1)[0]

        for ext in possible_exts:
            path = f"{base_name}.{ext}"
            if os.path.exists(path):
                filename = path
                break

        if not filename or not os.path.isfile(filename):
            await update.message.reply_text(
                "❌ Could not download video. It may be private, deleted, or unsupported."
            )
            return

        # Prepare caption
        title = info.get("title", "Video")
        duration = info.get("duration", 0)
        views = info.get("view_count", 0)

        caption = (
            f"✅ *{title}*\n"
            f"⏱️ Duration: {duration}s\n"
            f"👁️ Views: {views}"
        )

        with open(filename, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption=caption,
                parse_mode="Markdown"
            )

        os.remove(filename)

        # Time taken
        end_time = time.time()
        total_time = round(end_time - start_time, 2)
        print(f"✅ Delivered in {total_time}s")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
        print("❌ Error:", e)

# Bot setup
BOT_TOKEN = "7703533568:AAH-OUb3CR87QXIFt_htVK2sknhyJINH1Yk"
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 Bot is running...")
app.run_polling()