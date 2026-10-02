import os
import json
import random
import time
import requests
import telebot
from flask import Flask, request

# ----------------- CONFIGURATION -----------------
BOT_TOKEN = "8814355727:AAG7c-0teGiljwKq-liqCws1AoGGzH1feZY"
RENDER_URL = "https://telegram-dr-bot.onrender.com"  # Aapka Render domain

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

DATA_FILE = "group_data.json"
FILTERS_FILE = "filters.json"
CHATS_FILE = "chats.txt"

app = Flask(__name__)

# ----------------- HELPERS -----------------
def load_json(fp):
    if os.path.exists(fp):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_json(fp, d):
    try:
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

SHAYARIS = [
    "Aapki aankhon mein ajeeb si kashish hai,\nLagta hai yeh dil aapka hi aashiq hai! ❤️✨",
    "Dhadkan ko bhi sambhal kar rakha karo,\nHar baar aashiqui se ilaaj nahi hota! 🙈🩺",
    "Mohabbat ka koi nasha hi alag hota hai,\nTum samne na ho toh dil bechain rehta hai! 🌹🥀"
]

JOKES = [
    "Pappu: Yaar doctor ne mujhe aam khane se mana kiya hai.\nFriend: Kyu?\nPappu: Kyunki unka kehna hai ki main pehle se hi bohot mitha hoon! 😂🤣",
    "Teacher: Class me sabse shant kaun rehta hai?\nStudent: Sir, jiska phone silent mode par ho aur charging 100% ho! 😜😆"
]

MIRROR_EMOJIS = ["🔥", "❤️", "😈", "⚡", "✨", "👑", "👀", "😎", "💯", "🥀"]

# ----------------- COMMANDS -----------------
@bot.message_handler(commands=['start', 'help'])
def start_cmd(message):
    txt = (
        "╭━━━━〔 ⚡ 𝐒𝐔𝐏𝐑𝐄𝐌𝐄 𝐁𝐎𝐓 ⚡ 〕━━━━╮\n\n"
        "👑 **RANKING SYSTEM:**\n"
        "├ `/ranking` - Live Group Top Chatters\n"
        "├ Auto: Har 2 ghante me Top Chatter Winner Alert!\n\n"
        "📢 **COMMANDS:**\n"
        "├ `/tagall [msg]` - Sabhi members ko tag karein\n"
        "├ `/filter [word] [reply]` - Auto trigger set\n"
        "├ `/stopfilter [word]` - Trigger delete\n"
        "├ `/shayari` - Romantic Shayari\n"
        "├ `/joke` - Mazedaar Chutkule\n\n"
        "✨ **SMART FEATURES:**\n"
        "├ Shayari par 'Wah Wah' -> Special reply ❤️\n"
        "├ Joke par Laughing Emoji -> Thank you 😊\n"
        "├ Sticker aur Emoji response\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    bot.reply_to(message, txt, parse_mode="Markdown")

@bot.message_handler(commands=['ranking'])
def ranking_cmd(message):
    cid = str(message.chat.id)
    gdata = load_json(DATA_FILE)
    users = gdata.get(cid, {})
    if not users:
        bot.reply_to(message, "📊 Abhi tak kisi ne koi message nahi bheja! Chat shuru karo! 💬")
        return
    
    sorted_u = sorted(users.items(), key=lambda x: x[1].get("count", 0), reverse=True)[:10]
    out = "🏆 **LIVE GROUP LEADERBOARD** 🏆\n\n"
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i, (uid, inf) in enumerate(sorted_u):
        m = medals[i] if i < len(medals) else "🔹"
        out += f"{m} `{inf.get('name', 'User')}` ➔ **{inf.get('count', 0)} msgs**\n"
    bot.reply_to(message, out, parse_mode="Markdown")

@bot.message_handler(commands=['shayari'])
def shayari_cmd(message):
    bot.reply_to(message, f"🌹 **Shayari:**\n\n{random.choice(SHAYARIS)}")

@bot.message_handler(commands=['joke'])
def joke_cmd(message):
    bot.reply_to(message, f"🎭 **Joke:**\n\n{random.choice(JOKES)}")

@bot.message_handler(commands=['tagall'])
def tagall_cmd(message):
    if message.chat.type not in ["group", "supergroup"]:
        bot.reply_to(message, "⚠️ Ye command sirf group me kaam karegi!")
        return
    custom_text = message.text.replace("/tagall", "").strip() or "Hajiri lagao sab log!"
    try:
        admins = bot.get_chat_administrators(message.chat.id)
        mentions = [f"[{a.user.first_name}](tg://user?id={a.user.id})" for a in admins]
        bot.send_message(message.chat.id, f"📢 **ATTENTION EVERYONE** 📢\n\n💬 `{custom_text}`\n\n{' '.join(mentions)}", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['filter'])
def filter_cmd(message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "⚠️ Usage: `/filter [keyword] [reply]`", parse_mode="Markdown")
        return
    cid = str(message.chat.id)
    flt = load_json(FILTERS_FILE)
    if cid not in flt:
        flt[cid] = {}
    flt[cid][parts[1].lower()] = parts[2]
    save_json(FILTERS_FILE, flt)
    bot.reply_to(message, f"✅ Trigger set: `{parts[1]}`")

@bot.message_handler(commands=['stopfilter'])
def stopfilter_cmd(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Usage: `/stopfilter [keyword]`", parse_mode="Markdown")
        return
    cid = str(message.chat.id)
    flt = load_json(FILTERS_FILE)
    if cid in flt and parts[1].lower() in flt[cid]:
        del flt[cid][parts[1].lower()]
        save_json(FILTERS_FILE, flt)
        bot.reply_to(message, f"🗑️ Trigger deleted: `{parts[1]}`")
    else:
        bot.reply_to(message, "❌ Aisa koi trigger nahi mila.")

# ----------------- STICKER & TEXT HANDLER -----------------
@bot.message_handler(content_types=['sticker'])
def sticker_h(message):
    try:
        bot.send_sticker(message.chat.id, message.sticker.file_id)
    except Exception:
        pass

@bot.message_handler(content_types=['new_chat_members'])
def welcome_h(message):
    for u in message.new_chat_members:
        if not u.is_bot:
            name = u.first_name
            uname = f"@{u.username}" if u.username else "No Username"
            card = (
                "╭━━━━〔 ✨ 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 ✨ 〕━━━━╮\n\n"
                f"👋 **Hey:** [{name}](tg://user?id={u.id})\n"
                f"👤 **Username:** `{uname}`\n\n"
                "🌟 *Swagat hai aapka group me! Masti se chat karo!* 👑\n\n"
                "╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
            bot.reply_to(message, card, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True, content_types=['text'])
def text_analyser(message):
    t = (message.text or "").strip()
    tl = t.lower()
    cid = str(message.chat.id)
    uid = str(message.from_user.id)
    uname = message.from_user.first_name

    if t.startswith("/"):
        return

    # 1. Ranking counter update
    gd = load_json(DATA_FILE)
    if cid not in gd:
        gd[cid] = {}
    if uid not in gd[cid]:
        gd[cid][uid] = {"name": uname, "username": message.from_user.username or "", "count": 0}
    gd[cid][uid]["count"] += 1
    save_json(DATA_FILE, gd)

    # 2. Filters
    flt = load_json(FILTERS_FILE)
    if cid in flt and tl in flt[cid]:
        bot.reply_to(message, flt[cid][tl])
        return

    # 3. Wah Wah
    if any(k in tl for k in ["wah", "waah", "wah wah", "kya baat hai", "bohot khoob"]):
        bot.reply_to(message, "Thank you baby tum hi to samjhte ho mujhe 🙈❤️")
        return

    # 4. Laugh
    if any(e in tl for e in ["😂", "🤣", "😆", "haha", "hahaha"]):
        bot.reply_to(message, "Thank you 😊")
        return

    # 5. Emoji mirror
    if len(t) <= 2 and any(char in t for char in MIRROR_EMOJIS + ["😀", "😍", "😎", "🥺"]):
        bot.reply_to(message, random.choice(MIRROR_EMOJIS))
        return

# ----------------- FLASK WEBHOOK ROUTE (INSTANT TELEGRAM CONNECT) -----------------
@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def index():
    return "Bot Server is Running Live 24/7!"

def set_telegram_webhook():
    time.sleep(3)
    webhook_url = f"{RENDER_URL}/{BOT_TOKEN}"
    try:
        bot.remove_webhook()
        time.sleep(1)
        res = bot.set_webhook(url=webhook_url)
        print("Webhook Status:", res, "-> URL:", webhook_url)
    except Exception as e:
        print("Webhook Setup Error:", e)

if __name__ == "__main__":
    import threading
    threading.Thread(target=set_telegram_webhook, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
        
