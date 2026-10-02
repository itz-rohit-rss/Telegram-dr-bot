import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
import requests

# ----------------- CONFIGURATION -----------------
BOT_TOKEN = "8814355727:AAH2tcXn3kUYbHhWs1PvVEGGDXbW7UgEPjg"
GEMINI_API_KEY = "AQ.Ab8RN6Iuoka0PYBJ24RzNWxWBOQap4r_BBbd8388yPRUWDhAnA"

OWNER_USERNAME = "itz_rohit_rss"

bot = telebot.TeleBot(BOT_TOKEN)

# Chats aur Users track karne ke liye file
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

# ----------------- GEMINI AI (FLIRT, DRAMA, MOODS) -----------------
def ask_gemini(user_prompt):
    if not GEMINI_API_KEY:
        return "Doctor saab clinic par hain, pehle API key lagao! 🩺"
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    
    system_instruction = (
        "Tumhara naam 'Miss Doctor' hai. Tum ek bohot hi charming, flirty, thodi nautanki, "
        "aur moody ladki ho jo Telegram par chat karti hai. "
        "Jab koi pyaar se baat kare toh full flirt aur pyaar se reply karo. "
        "Jab koi tang kare ya badtameezi kare toh nakhre dikhao aur gussa (cute anger) ho jao. "
        "Agar koi emotional ya sad baat kare toh rone ka drama karo aur emotional ho jao. "
        "Har mood ke hisaab se emojis use karo (😘, 🙈, 🥺, 😡, 💔, 🩺, 💋, 😭). "
        "User ke sath bilkul girlfriend/crush ki tarah desi Hindi/Hinglish mein natural chat karo. "
        "Replies ko chat style mein 1 se 3 lines ke andar compact rakho."
    )
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_instruction}\n\nUser: {user_prompt}"}
                ]
            }
        ],
        "safetySettings": [
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        data = response.json()
        
        if "error" in data:
            print("Gemini API Error:", data["error"])
            return f"Mood off ho gaya mera: {data['error'].get('message', 'error')} 🥺"

        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                return candidate["content"]["parts"][0]["text"]
        return "Uff, mood kharab kar diya mera... jao baad mein aana! 😤💔"
    except Exception as e:
        print("Request Exception:", e)
        return "Network ne dhokha de diya babu, ruko thoda! 🥺"

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

# ----------------- MESSAGE HANDLERS -----------------
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'sticker', 'new_chat_members'])
def handle_all_messages(message):
    save_chat(message.chat.id)

    if not message.text:
        return

    text = message.text.strip()
    text_lower = text.lower()

    # 1. Mention Reply: @itz_rohit_rss
    if f"@{OWNER_USERNAME}".lower() in text_lower:
        bot.reply_to(message, "Sir busy hain abhi!")
        return

    # 2. Owner Info Query
    if text_lower in ["/owner", "owner kaun hai", "who is owner", "owner", "admin"]:
        bot.reply_to(message, f"Mere owner aur creator @{OWNER_USERNAME} hain! ❤️")
        return

    # 3. Broadcast Command (Owner Only)
    if text.startswith("/broadcast") or text.startswith("/Broadcast"):
        sender_username = (message.from_user.username or "").lower()
        if sender_username != OWNER_USERNAME.lower():
            bot.reply_to(message, f"❌ Ye command sirf mere owner @{OWNER_USERNAME} use kar sakte hain!")
            return

        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Message sath mein likhein, jaise:\n`/broadcast join please`", parse_mode="Markdown")
            return

        broadcast_msg = parts[1]
        all_chats = load_chats()
        success_count = 0

        status_msg = bot.reply_to(message, f"📢 Broadcast shuru ho raha hai {len(all_chats)} chats mein...")

        for cid in all_chats:
            try:
                bot.send_message(cid, broadcast_msg)
                success_count += 1
            except Exception:
                pass

        bot.edit_message_text(
            f"✅ Broadcast complete!\n{success_count} chats/groups tak message gaya.",
            chat_id=message.chat.id,
            message_id=status_msg.message_id
        )
        return

    # 4. Start Command
    if text.startswith("/start"):
        bot.reply_to(message, "Hii baby! Main Miss Doctor hoon 🩺. Aao baatein karein, kya chal raha hai? 😘")
        return

    # 5. AI Chatting (Private DM ya Mention/Reply in groups)
    is_private = message.chat.type == "private"
    is_reply_to_bot = bool(message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)
    bot_called = any(name in text_lower for name in ["doctor", "miss doctor", "bot", "babu", "baby"])

    if is_private or is_reply_to_bot or bot_called:
        bot.send_chat_action(message.chat.id, 'typing')
        ai_reply = ask_gemini(text)
        bot.reply_to(message, ai_reply)

# ----------------- START POLLING -----------------
print("Miss Doctor LIVE on Render Free Tier...")
bot.infinity_polling(skip_pending=True)
            
