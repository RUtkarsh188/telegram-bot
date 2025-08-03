from pyrogram import Client, filters
from textblob import TextBlob
from datetime import datetime
import pytz
import os

API_ID = 24715332
API_HASH = "2c0911650669882845606cb363dd8834"
BOT_TOKEN = "8389194407:AAFCC0zREfjSEmXRVA7422ej2lF64hVa4f4"
ADMIN_ID = 7818325536

app = Client("flirt_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# Load keywords from file
def load_keywords(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]


# Suspicious message detection
def is_suspicious(text):
    flirt_words = load_keywords("flirty_words.txt")
    abuse_words = load_keywords("abuse_words.txt")
    text_lower = text.lower()
    for word in flirt_words + abuse_words:
        if word in text_lower:
            return f"❗️ Suspicious keyword: {word}"
    blob = TextBlob(text)
    if blob.sentiment.polarity < -0.5:
        return "⚠️ Strong negative sentiment"
    return None


# Command to start bot
@app.on_message(filters.private & filters.command("start"))
def start_handler(client, message):
    message.reply_text("👋 Hello! Bot is now active.")
    print(f"Started by: {message.from_user.id}")


# Group message handler
@app.on_message(filters.group & filters.text)
def monitor_message(client, message):
    reason = is_suspicious(message.text)
    if reason:
        ist = pytz.timezone("Asia/Kolkata")
        timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
        alert = (
            f"🚨 *Suspicious Message Alert!*\n"
            f"🕒 *Time:* {timestamp}\n"
            f"👤 *User:* [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n"
            f"🗨 *Message:* {message.text}\n"
            f"📌 *Reason:* {reason}\n"
            f"📍 *Group:* {message.chat.title}"
        )

        # Try to send to ADMIN, if it fails, reply in group
        try:
            client.send_message(ADMIN_ID, alert)
        except Exception as e:
            message.reply_text("⚠️ Couldn't send alert to admin. Here's the message:\n\n" + alert)
            print("Error sending to admin:", e)

        with open("flagged_messages.log", "a", encoding="utf-8") as log:
            log.write(f"{timestamp} - {message.text} - {reason}\n")


print("✅ Bot is running... (Press Ctrl+C to stop)")
app.run()