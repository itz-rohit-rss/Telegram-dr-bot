import os
import json
import random
import threading
import time
import requests
import telebot
from telebot.apihelper import ApiTelegramException
from flask import Flask

# ----------------- CONFIGURATION -----------------
BOT_TOKEN = "8814355727:AAG7c-0teGiljwKq-liqCws1AoGGzH1feZY"
GROQ_API_KEY = "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"
OWNER_USERNAME = "itz_rohit_rss"

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# File names
CHATS_FILE = "chats.txt"
FILTERS_FILE = "filters.json"
USERS_FILE = "users_data.json"
RIDDLES_TRACK_FILE = "asked_riddles.json"

# ----------------- FLASK DUMMY SERVER (FOR RENDER) -----------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Miss Doctor Bot is Running Live 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# ----------------- DATABASE HELPERS -----------------
def load_json(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_chats():
    if os.path.exists(CHATS_FILE):
        with open(CHATS_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_chat(chat_id):
    active_chats = load_chats()
    if str(chat_id) not in active_chats:
        with open(CHATS_FILE, "a") as f:
            f.write(f"{chat_id}\n")

# ----------------- GROQ AI ENGINE -----------------
def ask_ai(user_prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_instruction = (
        "Tumhara naam 'Miss Doctor' hai. Tum ek charming, flirty, thodi nautanki, "
        "aur moody ladki ho jo Telegram par chat karti hai. "
        "Pyaar se baat karne par full flirt aur cute replies do. Badtameezi par nakhre aur cute anger dikhao. "
        "Har mood ke hisaab se emojis use karo (😘, 🙈, 🥺, 😡, 💔, 🩺, 💋). "
        "Desi Hinglish mein girlfriend/crush ban kar 1-3 short lines me natural baat karo. "
        "Kabhi robotic mat bano."
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 150
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        return "Haan bolo babu, sun rahi hoon! 😘"
    except Exception as e:
        print("AI network error:", e)
        return "Network ne dhokha de diya babu, ruko thoda! 🥺"

# ----------------- DATA LISTS -----------------
SHAYARIS = [
    "Aapki aankhon mein ajeeb si kashish hai,\nDoctor kehte hain yeh ishq ki bandish hai! 😘🩺",
    "Dhadkan ko bhi sambhal kar rakha karo,\nHar baar injection se ilaaj nahi hota! 💉🙈",
    "Dil ka operation toh kar diya humne,\nPar marz yeh nikla ki tum par hi fida ho gaye! ❤️💋",
    "Nazar mili toh bukhar chadha diya tumne,\nBolo ab dawa kya dega yeh haseen doctor? 🥺🩺",
    "Hum toh aate the tumhari nabz check karne,\nTumne toh seene ki dhadkan hi chura li! 🙈❤️️"
]

RANDOM_TAG_WORDS = [
    "Oye hero kahan ho? 🙈", "Doctor bula rahi hai chupchap aao! 🩺",
    "Online aao warna injection lagega! 💉", "Kisko dhoondh rahe ho, main yahan hoon! 😘",
    "Chai peene chalte hain jaldi aao! ☕", "Koi sunta hi nahi meri baat... 🥺"
]

RIDDLES_LIST = [
    "Woh kya hai jo saal mein 1 baar, mahine mein 2 baar, hafte mein 4 baar aur din mein 6 baar aata hai? 🤔💭",
    "Aisi kaun si cheez hai jise hum nigal jayein toh theek, par woh hume nigal jaye toh hum mar jayein? 🌊🤫",
    "Woh kya hai jo bina pairon ke chalti hai aur kabhi thakti nahi? ⏰👀",
    "Aisi kaun si cheez hai jo subah ko chaar taangon par, dopahar ko do taangon par aur shaam ko teen taangon par chalti hai? 🚶‍♂️👴",
    "Woh kaun si cheez hai jise jitna kheecho woh utni hi chhoti hoti jati hai? 🚬🔥",
    "Ek aisi cheez ka naam batao jise kaatne par log gaana gaate hain? 🎂🎉",
    "Woh kya hai jiske paas daant toh hain par woh kaat nahi sakta? 🪮💁‍♂️",
    "Aisi kaun si sabzi hai jisme taala aur chaabi dono aate hain? 🔐🥒",
    "Katora pe katora, beta baap se bhi gora! Batao kya? 🥥✨",
    "Lal ghoda ruka rahe, kala ghoda bhagta jaye! Batao kya? 🔥💨",
    "Woh kya hai jo aati hai toh aati hai, jaati hai toh jaati hai, par dikhai nahi deti? 🌬️💨",
    "Aisi kaun si cheez hai jo sukhi ho toh 2 kilo, geeli ho toh 1 kilo aur jal jaye toh 3 kilo ho jati hai? ⚗️🧪",
    "Do sundar ladke, dono ek rang ke, ek bichhad jaye toh doosra kaam na aaye! Batao kya? 👞👟",
    "Kaali hai par koyal nahi, lambi hai par saanp nahi, bal khati hai par rassi nahi! Batao kya? 💇‍♀️🖤",
    "Aisi kaun si jagah hai jahan 100 log jaate hain toh 101 log wapas aate hain? 👰🤵"
]

# ----------------- MESSAGE HANDLERS -----------------
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_all_messages(message):
    save_chat(message.chat.id)
    text = (message.text or "").strip()
    text_lower = text.lower()
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name

    # 1. Custom Filters
    filters_data = load_json(FILTERS_FILE)
    chat_filters = filters_data.get(chat_id, {})
    if text_lower in chat_filters:
        bot.reply_to(message, chat_filters[text_lower])
        return

    # 2. Owner Protection Mention
    if f"@{OWNER_USERNAME}".lower() in text_lower:
        bot.reply_to(message, "Sir busy hain abhi!")
        return

    # 3. /start Command
    if text.startswith("/start"):
        bot.reply_to(message, "Hii baby! Main Miss Doctor hoon 🩺. Aao baatein karein ya masti karein! 😘")
        return

    # 4. /owner Command
    if text_lower in ["/owner", "owner kaun hai", "who is owner", "owner", "admin"]:
        bot.reply_to(message, f"Mere owner aur creator @{OWNER_USERNAME} hain! ❤️")
        return

    # 5. /q Command (Unique Paheli / Riddle without repeat)
    if text.startswith("/q") or text.startswith("/Q"):
        asked_data = load_json(RIDDLES_TRACK_FILE)
        asked_indices = asked_data.get(chat_id, [])

        # Saare index jo abhi tak nahi puchhe gaye
        remaining_indices = [i for i in range(len(RIDDLES_LIST)) if i not in asked_indices]

        # Agar saari khatam ho chuki hon toh reset karo
        if not remaining_indices:
            asked_indices = []
            remaining_indices = list(range(len(RIDDLES_LIST)))

        selected_idx = random.choice(remaining_indices)
        asked_indices.append(selected_idx)

        asked_data[chat_id] = asked_indices
        save_json(RIDDLES_TRACK_FILE, asked_data)

        bot.reply_to(message, f"🧩 **Miss Doctor ki Paheli:**\n\n{RIDDLES_LIST[selected_idx]}\n\n_Dimag lagao aur sahi jawab do babu! Dekhein kisme kitna dimaag hai 🙈🩺_", parse_mode="Markdown")
        return

    # 6. /shayari Command
    if text.startswith("/shayari"):
        bot.reply_to(message, random.choice(SHAYARIS))
        return

    # 7. /vc Command
    if text.startswith("/vc"):
        vc_quotes = [
            "🔊 Aao sab Voice Chat par aa jao, main injection le kar baithi hoon! 💉",
            "🎙️ VC start ho chuki hai baby, aao thodi masti karein! 😘🎧",
            "📞 Sab log fatfat VC join karo, Doctor saab live checkup karenge! 🩺🙈"
        ]
        bot.reply_to(message, random.choice(vc_quotes))
        return

    # 8. /rob Command (Coins Game)
    if text.startswith("/rob"):
        users_data = load_json(USERS_FILE)
        if user_id not in users_data:
            users_data[user_id] = {"coins": 100, "last_rob": 0}

        current_time = time.time()
        if current_time - users_data[user_id].get("last_rob", 0) < 60:
            remaining = int(60 - (current_time - users_data[user_id].get("last_rob", 0)))
            bot.reply_to(message, f"⏳ Thoda ruk jao babu! Agli chori {remaining} second baad karna. 🙈")
            return

        users_data[user_id]["last_rob"] = current_time
        outcome = random.choice(["success", "caught", "lucky"])

        if outcome == "success":
            stolen = random.randint(30, 150)
            users_data[user_id]["coins"] += stolen
            bot.reply_to(message, f"💰 Are waah! Tumne chori karke **{stolen} coins** kama liye! Total: {users_data[user_id]['coins']} 🪙", parse_mode="Markdown")
        elif outcome == "lucky":
            jackpot = random.randint(200, 400)
            users_data[user_id]["coins"] += jackpot
            bot.reply_to(message, f"🎉 Jackpot! Doctor ki tijori se **{jackpot} coins** uda le gaye tum! Total: {users_data[user_id]['coins']} 🪙", parse_mode="Markdown")
        else:
            fine = random.randint(20, 60)
            users_data[user_id]["coins"] = max(0, users_data[user_id]["coins"] - fine)
            bot.reply_to(message, f"🚔 Pakde gaye badmash! Doctor ne **{fine} coins** ka fine laga diya! Bacha: {users_data[user_id]['coins']} 🪙", parse_mode="Markdown")

        save_json(USERS_FILE, users_data)
        return

    # 9. Fun Commands: /kiss and /slap
    if text.startswith("/kiss"):
        if message.reply_to_message:
            target_name = message.reply_to_message.from_user.first_name
            bot.reply_to(message, f"💋 {user_name} ne {target_name} ko ek geeli aur sweet pappi di! 🙈😘")
        else:
            bot.reply_to(message, f"💋 Miss Doctor ne {user_name} ke gaal par ek sweet kiss kar di! 😘")
        return

    if text.startswith("/slap"):
        if message.reply_to_message:
            target_name = message.reply_to_message.from_user.first_name
            bot.reply_to(message, f"👋 {user_name} ne {target_name} ko zor ka thappad mara! Chatak! 😡💥")
        else:
            bot.reply_to(message, "Kis badmash ko thappad marna hai? Message reply karke bolo! 😤")
        return

    # 10. /filter and /stopfilter
    if text.startswith("/filter"):
        parts = text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(message, "⚠️ Format:\n`/filter word reply_message`\nJaise: `/filter hi hello baby`", parse_mode="Markdown")
            return
        keyword = parts[1].lower()
        reply_content = parts[2]
        if chat_id not in filters_data:
            filters_data[chat_id] = {}
        filters_data[chat_id][keyword] = reply_content
        save_json(FILTERS_FILE, filters_data)
        bot.reply_to(message, f"✅ Filter set ho gaya: `{keyword}` -> `{reply_content}`", parse_mode="Markdown")
        return

    if text.startswith("/stopfilter"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Keyword likhein: `/stopfilter word`", parse_mode="Markdown")
            return
        keyword = parts[1].lower()
        if chat_id in filters_data and keyword in filters_data[chat_id]:
            del filters_data[chat_id][keyword]
            save_json(FILTERS_FILE, filters_data)
            bot.reply_to(message, f"🗑️ Filter `{keyword}` hata diya gaya!", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Ye filter exist nahi karta!")
        return

    # 11. /tagall Command
    if text.startswith("/tagall"):
        if message.chat.type in ["group", "supergroup"]:
            custom_msg = text.replace("/tagall", "").strip() or "Sabhi log online aao jaldi!"
            try:
                admins = bot.get_chat_administrators(message.chat.id)
                tag_list = []
                for admin in admins:
                    u = admin.user
                    tag_list.append(f"[{u.first_name}](tg://user?id={u.id})")
                tag_chunk = " ".join(tag_list)
                bot.send_message(message.chat.id, f"📢 {custom_msg}\n\n{tag_chunk}", parse_mode="Markdown")
            except Exception as e:
                bot.reply_to(message, f"Oye members nahi mil rahe: {e}")
        else:
            bot.reply_to(message, "Yeh command sirf group me kaam karega baby! 🩺")
        return

    # 12. /rtag Command
    if text.startswith("/rtag"):
        if message.chat.type in ["group", "supergroup"]:
            tag_quote = random.choice(RANDOM_TAG_WORDS)
            try:
                admins = bot.get_chat_administrators(message.chat.id)
                if admins:
                    random_user = random.choice(admins).user
                    mention = f"[{random_user.first_name}](tg://user?id={random_user.id})"
                    bot.send_message(message.chat.id, f"{mention} {tag_quote}", parse_mode="Markdown")
            except Exception:
                bot.reply_to(message, f"Oye babu {tag_quote}")
        else:
            bot.reply_to(message, "Yeh sirf group ke liye hai baby! 🙈")
        return

    # 13. /broadcast Command (Owner Only)
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

    # 14. AI Flirty Chatting
    is_private = message.chat.type == "private"
    is_reply_to_bot = bool(message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)
    bot_called = any(name in text_lower for name in ["doctor", "miss doctor", "bot", "babu", "baby"])

    if is_private or is_reply_to_bot or bot_called:
        try:
            bot.send_chat_action(message.chat.id, 'typing')
        except Exception:
            pass
        reply = ask_ai(text)
        bot.reply_to(message, reply)

# ----------------- MAIN RUNNER -----------------
if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()

    try:
        bot.remove_webhook()
        print("Webhook cleared.")
    except Exception:
        pass

    print("Miss Doctor Polling Engine starting...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
        except ApiTelegramException as e:
            if e.error_code == 409:
                time.sleep(5)
            else:
                time.sleep(3)
        except Exception:
            time.sleep(3)
                                 
