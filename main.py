import time
import logging
import requests
import os
from threading import Thread
from flask import Flask
import tempfile
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ParseMode
from moviepy import VideoFileClip
from app import app
from utils import LOGGER
from config import COMMAND_PREFIX

# Setup minimal Flask server to prevent Heroku R10 error
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "Smart Tool Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# Start Flask in background
Thread(target=run_flask).start()


# Cache settings
media_cache = {}
CACHE_EXPIRY = 600  # 10 minutes

# Start message and buttons
START_PHOTO_URL = "https://t.me/botszonechat/5365"
START_MESSAGE = (
    "🌟 **Welcome to the Reddit Downloader Bot! 💥**\n\n"
    "✨ Download high-quality media from **Reddit** effortlessly.\n\n"
    "1️⃣ Use commands: `/red`, `.red`, `!red`, or `,red`\n"
    "2️⃣ Provide a Reddit URL. Example: `/red https://reddit.com/...`\n"
    "3️⃣ Select quality.\n"
    "4️⃣ Relax while I handle it!\n\n"
    "**❌ Issues? Contact the developer or check the updates channel.**\n"
    "**Happy downloading! 💫**"
)
START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Updates Channel", url="t.me/TheSmartDev"),
            InlineKeyboardButton("Developer", user_id=7303810912),
        ]
    ]
)

# Function to clean up expired cache entries
def cleanup_cache():
    current_time = time.time()
    for key in list(media_cache.keys()):
        if current_time - media_cache[key]["timestamp"] > CACHE_EXPIRY:
            media_cache.pop(key, None)

# Start command handler
@app.on_message(filters.command("start", prefixes=COMMAND_PREFIX) & filters.private)
def start_command(client, message: Message):
    LOGGER.info(f"User {message.from_user.id} started the bot.")
    client.send_photo(
        chat_id=message.chat.id,
        photo=START_PHOTO_URL,
        caption=START_MESSAGE,
        reply_markup=START_BUTTONS,
        parse_mode=ParseMode.MARKDOWN,
    )

# Reddit download command handler
@app.on_message(filters.command("red", prefixes=COMMAND_PREFIX) & (filters.private | filters.group))
def reddit_download(client, message: Message):
    LOGGER.info(f"Command from user {message.from_user.id}: {message.text}")
    if len(message.command) == 1:
        client.send_message(chat_id=message.chat.id, text="❄️ **Please provide a Reddit URL**", parse_mode=ParseMode.MARKDOWN)
        return

    reddit_url = message.text.split(maxsplit=1)[1]
    if not reddit_url.startswith("http"):
        client.send_message(chat_id=message.chat.id, text="❌ **Invalid URL provided**", parse_mode=ParseMode.MARKDOWN)
        return

    loading_message = client.send_message(chat_id=message.chat.id, text="💫 **Searching for media...**", parse_mode=ParseMode.MARKDOWN)
    api_url = f"https://reddit.bdbots.xyz/dl?url={reddit_url}"

    try:
        response = requests.get(api_url)
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code}")
        data = response.json()

        qualities = data.get("sd_links", [])
        if hd_link := data.get("hd_link"):
            qualities.insert(0, {"quality": "1080p", "url": hd_link})

        if not qualities:
            loading_message.edit("❌ **No media found for this URL**", parse_mode=ParseMode.MARKDOWN)
            return

        title = data.get("title", "Unknown Title")
        views = data.get("views", "Unknown")
        cache_key = f"{message.from_user.id}_{loading_message.id}"
        media_cache[cache_key] = {
            "qualities": qualities,
            "title": title,
            "views": views,
            "reddit_url": reddit_url,
            "original_message": message,
            "timestamp": time.time()
        }

        quality_buttons = [
            [InlineKeyboardButton(q["quality"], callback_data=f"download_{q['quality']}_{cache_key}")]
            for q in qualities
        ]
        loading_message.edit(
            "⭐️ **Media Successfully found! Select quality...**",
            reply_markup=InlineKeyboardMarkup(quality_buttons),
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        LOGGER.error(f"Error fetching media: {e}")
        loading_message.edit("❌ **Sorry Bro API Dead.**", parse_mode=ParseMode.MARKDOWN)

# Callback query handler for quality selection
@app.on_callback_query()
def callback_query_handler(client, callback_query):
    data = callback_query.data
    if not data.startswith("download_"):
        callback_query.answer("Invalid selection!", show_alert=True)
        return

    quality, cache_key = data.split("_", 2)[1], "_".join(data.split("_")[2:])
    LOGGER.info(f"User {callback_query.from_user.id} selected {quality} for {cache_key}")

    cache_data = media_cache.get(cache_key)
    if not cache_data or time.time() - cache_data["timestamp"] > CACHE_EXPIRY:
        callback_query.answer("Session expired!", show_alert=True)
        media_cache.pop(cache_key, None)
        return

    selected_quality = next((q for q in cache_data["qualities"] if q["quality"] == quality), None)
    if not selected_quality:
        callback_query.answer("Invalid quality!", show_alert=True)
        return

    url = selected_quality["url"]
    status_message = callback_query.message
    status_message.edit(f"**Downloading {quality} quality...**", parse_mode=ParseMode.MARKDOWN)

    temp_file_path = None
    try:
        # Download the media synchronously
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise Exception(f"Download failed: HTTP {response.status_code}")
        temp_file_path = os.path.join(tempfile.gettempdir(), f"reddit_{cache_key}_{quality}.mp4")
        with open(temp_file_path, "wb") as temp_file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                temp_file.write(chunk)

        # Get video duration
        try:
            clip = VideoFileClip(temp_file_path)
            duration = clip.duration
            clip.close()
        except Exception as e:
            LOGGER.error(f"Failed to get duration: {e}")
            duration = "Unknown"

        file_size = os.path.getsize(temp_file_path) / (1024 * 1024)  # Convert to MB
        message = cache_data["original_message"]
        user_info = (
            f"[{message.from_user.first_name} {message.from_user.last_name or ''}](tg://user?id={message.from_user.id})"
            if message.from_user else f"[{message.chat.title or 'this group'}](https://t.me/{message.chat.username or ''})"
        )

        video_caption = (
            f"🎵 **Title:** **{cache_data['title']}**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👁️‍🗨️ **Size:** **{file_size:.2f} MB**\n"
            f"🔗 [Watch On Reddit]({cache_data['reddit_url']})\n"
            f"⏱️ **Duration:** **{duration}**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡️ **Downloaded By** {user_info}"
        )

        # Upload with throttled progress updates
        status_message.edit(f"✨ **Uploading {quality} quality...**", parse_mode=ParseMode.MARKDOWN)

        start_time = time.time()
        last_update_time = [start_time]
        last_percentage = [0]

        def progress_callback(current, total):
            now = time.time()
            percentage = (current / total) * 100
            # Update only every 5 seconds or 5% change to avoid flooding
            if now - last_update_time[0] >= 5 or abs(percentage - last_percentage[0]) >= 5:
                last_update_time[0] = now
                last_percentage[0] = percentage
                elapsed_time = max(now - start_time, 1)
                progress_bar = "▓" * int(percentage // 5) + "░" * (20 - int(percentage // 5))
                speed = current / elapsed_time / 1024 / 1024  # MB/s
                uploaded = current / 1024 / 1024  # MB
                total_size = total / 1024 / 1024  # MB
                if speed > 1000:  # Prevent unrealistic speed values
                    speed = 0
                text = (
                    f"📥 **Smart Reddit DL Upload Progress**\n\n"
                    f"{progress_bar}\n\n"
                    f"🚧 PC: {percentage:.2f}%\n"
                    f"⚡️ Speed: {speed:.2f} MB/s\n"
                    f"📶 Uploaded: {uploaded:.2f} MB / {total_size:.2f} MB"
                )
                try:
                    status_message.edit(text)
                except Exception as e:
                    LOGGER.warning(f"Edit failed: {e}")

        client.send_video(
            chat_id=callback_query.message.chat.id,
            video=temp_file_path,
            caption=video_caption,
            parse_mode=ParseMode.MARKDOWN,
            height=720,
            width=1280,
            duration=int(duration) if duration != "Unknown" else 0,
            progress=progress_callback
        )

        # Cleanup after upload
        status_message.delete()
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        media_cache.pop(cache_key, None)
        cleanup_cache()  # Clean expired cache entries

    except Exception as e:
        LOGGER.error(f"Error in download/upload: {e}")
        status_message.edit("❌ **Sorry Bro Server Dead**", parse_mode=ParseMode.MARKDOWN)
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# Run the bot synchronously
if __name__ == "__main__":
    LOGGER.info("Reddit Downloader Bot is starting...")
    print("Reddit Downloader Successfully Started!")
    app.run()
