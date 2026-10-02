import os
import threading
import time
import requests
import telebot
from telebot.apihelper import ApiTelegramException
from flask import Flask

# ----------------- CONFIGURATION -----------------
BOT_TOKEN = "8814355727:AAG7c-0teGiljwKq-liqCws1AoGGzH1feZY"
GEMINI_API_KEY = "AQ.Ab8RN6Ii6xTKce13KWXTvvIGovgkbVixDckeT_rbY84mjtQt5w"
OWNER_USERNAME = "itz_rohit_rss"

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
chats_file = "chats.txt"

# ----------------- FLASK SERVER (RENDER HEALTH CHECK) -----------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Miss Doctor Bot is Running Live!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# ----------------- CHAT STORAGE -----------------
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
        
        if "error" in data:
            print("Gemini API Error Detail:", data["error"])
            return f"API Error: {data['error'].get('message', 'Key issue')}"

        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                return candidate["content"]["parts"][0]["text"]
                
        return "Uff, mood kharab kar diya mera... jao baad mein aana! 😤💔"
    except Exception as e:
        print("Gemini Exception:", e)
        return "Network ne dhokha de diya babu, ruko thoda! 🥺"

# ----------------- MESSAGE HANDLERS -----------------
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_all_messages(message):
    save_chat(message.chat.id)
    text = (message.text or "").strip()
    text_lower = text.lower()

    if f"@{OWNER_USERNAME}".lower() in text_lower:
        bot.reply_to(message, "Sir busy hain abhi!")
        return

    if text_lower in ["/owner", "owner kaun hai", "who is owner", "owner", "admin"]:
        bot.reply_to(message, f"Mere owner aur creator @{OWNER_USERNAME} hain! ❤️")
        return

    if text.startswith("/broadcast") or text.startswith("/Broadcast"):
        sender_username = (message.from_user.username or "").lower()
        if sender_username != OWNER_USERNAME.lower():
            bot.reply_to(message, f"❌ Ye command sirf mere owner @{OWNER_USERNAME} use kar sakte hain!")
            return

        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Message sath mein likhein:\n`/broadcast hello sabko`")
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
        try:
            bot.send_chat_action(message.chat.id, 'typing')
        except Exception:
            pass
        reply = ask_gemini(text)
        bot.reply_to(message, reply)

# ----------------- MAIN RUNNER -----------------
if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    
    try:
        bot.remove_webhook()
        print("Webhook cleared.")
    except Exception as e:
        print("Webhook note:", e)

    print("Miss Doctor Polling Engine starting...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
        except ApiTelegramException as e:
            if e.error_code == 409:
                time.sleep(5)
            else:
                time.sleep(3)
        except Exception as err:
            time.sleep(3)
        
