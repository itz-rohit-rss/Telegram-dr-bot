import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
import requests

# ----------------- CONFIGURATION -----------------
BOT_TOKEN = "8814355727:AAH2tcXn3kUYbHhWs1PvVEGGDXbW7UgEPjg"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # Agar Gemini key hai toh yahan rakhein

OWNER_USERNAME = "itz_rohit_rss"

bot = telebot.TeleBot(BOT_TOKEN)

# Chats aur Users track karne ke liye set
chats_file = "chats.txt"

def load_chats():
    if os.path.exists(chats_file):
        with open(chats_file, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_chat(chat_id):
    active_chats = load_chats()
    if str(chat_id) not in active_chats:
        with open(chats_file, "a") as f:
            f.write(f"{chat_id}\n")

# ----------------- DUMMY SERVER FOR RENDER -----------------
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Miss Doctor Bot is Running!")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# ----------------- CHAT TRACKER MIDDLEWARE -----------------
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'sticker', 'new_chat_members'])
def handle_all_messages(message):
    save_chat(message.chat.id)

    # 1. Agar koi @itz_rohit_rss mention kare
    if message.text and f"@{OWNER_USERNAME}".lower() in message.text.lower():
        bot.reply_to(message, "Sir busy hain abhi!")
        return

    # 2. Owner ke baare mein poochna (/owner ya text query)
    if message.text:
        text_lower = message.text.lower()
        if text_lower in ["/owner", "owner kaun hai", "who is owner", "owner", "admin"]:
            bot.reply_to(message, f"Mere owner aur creator @{OWNER_USERNAME} hain! ❤️")
            return

    # 3. Broadcast Command (Sirf Owner ke liye)
    if message.text and (message.text.startswith("/broadcast") or message.text.startswith("/Broadcast")):
        # Check karein agar sender owner hai
        sender_username = (message.from_user.username or "").lower()
        if sender_username != OWNER_USERNAME.lower():
            bot.reply_to(message, "❌ Ye command sirf mere owner @itz_rohit_rss use kar sakte hain!")
            return

        # Broadcast text nikalna
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Message likhein, jaise:\n`/broadcast join please`", parse_mode="Markdown")
            return

        broadcast_msg = parts[1]
        all_chats = load_chats()
        success_count = 0

        status_msg = bot.reply_to(message, f"📢 Broadcast start ho raha hai {len(all_chats)} chats mein...")

        for cid in all_chats:
            try:
                bot.send_message(cid, broadcast_msg)
                success_count += 1
            except Exception:
                pass  # Blocked / Kicked chats ignore ho jayenge

        bot.edit_message_text(f"✅ Broadcast complete!\n{success_count} chats/groups tak message pahunch gaya.", 
                              chat_id=message.chat.id, message_id=status_msg.message_id)
        return

    # 4. Normal Start / Help
    if message.text.startswith("/start"):
        bot.reply_to(message, "Hello! Main Miss Doctor hoon. Main groups manage kar sakti hoon aur fun baatein bhi! 🩺✨")

# ----------------- START POLLING -----------------
print("Miss Doctor LIVE on Render Free Tier...")
bot.infinity_polling(skip_pending=True)

