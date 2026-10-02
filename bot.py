import os
import threading
import time
import requests
import telebot
from flask import Flask

# ----------------- CONFIGURATION -----------------
BOT_TOKEN = "8814355727:AAG7c-0teGiljwKq-liqCws1AoGGzH1feZY"
GEMINI_API_KEY = "AQ.Ab8RN6Ii6xTKce13KWXTvvIGovgkbVixDckeT_rbY84mjtQt5w"
OWNER_USERNAME = "itz_rohit_rss"

bot = telebot.TeleBot(BOT_TOKEN)
chats_file = "chats.txt"

# ----------------- DUMMY FLASK WEB SERVER (PORT BIND FIX) -----------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Miss Doctor Bot is Running Live!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ----------------- CHAT PERSISTENCE -----------------
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

# ----------------- GEMINI AI CALL -----------------
def ask_gemini(user_prompt):
    if not GEMINI_API_KEY:
        return "Doctor saab clinic par hain, pehle API key lagao! 🩺"
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    
    system_instruction = (
        "Tumhara naam 'Miss Doctor' hai. Tum ek charming, flirty, thodi nautanki, "
        "aur moody ladki ho jo Telegram par chat karti hai. "
        "Pyaar se baat karne par full flirt aur cute replies do. Badtameezi par nakhre aur cute anger dikhao. "
        "Har mood ke hisaab se emojis use karo (😘, 🙈, 🥺, 😡, 💔, 🩺, 💋). "
        "Desi Hinglish mein girlfriend/crush ban kar 1-3 lines me baat karo."
    )
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_instruction}\n\nUser: {user_prompt}"}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                return candidate["content"]["parts"][0]["text"]
        return "Uff, mood kharab kar diya mera... jao baad mein aana! 😤💔"
    except Exception:
        return "Network ne dhokha de diya babu, ruko thoda! 🥺"

# ----------------- TELEGRAM HANDLERS -----------------
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'sticker', 'new_chat_members'])
def handle_all_messages(message):
    save_chat(message.chat.id)

    if not message.text:
        return

    text = message.text.strip()
    text_lower = text.lower()

    if f"@{OWNER_USERNAME}".lower() in text_lower:
        bot.reply_to(message, "Sir busy hain abhi!")
        return

    if text_lower in ["/owner", "owner kaun hai", "who is owner", "owner", "admin"]:
        bot.reply_to(message, f"Mere owner aur creator @{OWNER_USERNAME} hain! ❤️️")
        return

    if text.startswith("/broadcast") or text.startswith("/Broadcast"):
        sender_username = (message.from_user.username or "").lower()
        if sender_username != OWNER_USERNAME.lower():
            bot.reply_to(message, f"❌ Ye command sirf mere owner @{OWNER_USERNAME} use kar sakte hain!")
            return

        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Message sath mein likhein:\n`/broadcast hello`", parse_mode="Markdown")
            return

        broadcast_msg = parts[1]
        all_chats = load_chats()
        success_count = 0
        status_msg = bot.reply_to(message, f"📢 Broadcast shuru: {len(all_chats)} chats...")

        for cid in all_chats:
            try:
                bot.send_message(cid, broadcast_msg)
                success_count += 1
            except Exception:
                pass

        bot.edit_message_text(
            f"✅ Broadcast complete! Sent to {success_count} chats.",
            chat_id=message.chat.id,
            message_id=status_msg.message_id
        )
        return

    if text.startswith("/start"):
        bot.reply_to(message, "Hii baby! Main Miss Doctor hoon 🩺. Aao baatein karein, kya chal raha hai? 😘")
        return

    is_private = message.chat.type == "private"
    is_reply_to_bot = bool(message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)
    bot_called = any(name in text_lower for name in ["doctor", "miss doctor", "bot", "babu", "baby"])

    if is_private or is_reply_to_bot or bot_called:
        bot.send_chat_action(message.chat.id, 'typing')
        reply = ask_gemini(text)
        bot.reply_to(message, reply)

def start_polling():
    time.sleep(2)
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print("Polling restart:", e)
            time.sleep(3)

# ----------------- MAIN RUNNER -----------------
if __name__ == "__main__":
    # Telegram bot background thread me chalega
    threading.Thread(target=start_polling, daemon=True).start()
    # Flask port bind karega Render deployment ke liye
    run_web()
    
