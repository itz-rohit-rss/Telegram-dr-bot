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
BOT_TOKEN = "8814355727:AAHzf3UQXS1R-Fs_FwDeRujvB-iAAyHv7sU"
OWNER_USERNAME = "itz_rohit_rss"

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

DATA_FILE = "group_data.json"
FILTERS_FILE = "filters.json"
CHATS_FILE = "chats.txt"

# ----------------- FLASK SERVER (RENDER KEEP-ALIVE) -----------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Supreme Group Ranking & Management Bot is Live 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

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

def save_chat(chat_id):
    active_chats = set()
    if os.path.exists(CHATS_FILE):
        try:
            with open(CHATS_FILE, "r") as f:
                active_chats = set(line.strip() for line in f if line.strip())
        except Exception:
            pass
    if str(chat_id) not in active_chats:
        try:
            with open(CHATS_FILE, "a") as f:
                f.write(f"{chat_id}\n")
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

# ----------------- AUTO RANKING (HAR 2 GHANTE) -----------------
def auto_ranking_announcer():
    while True:
        time.sleep(7200)
        try:
            gdata = load_json(DATA_FILE)
            for cid, users in gdata.items():
                if not users:
                    continue
                sorted_u = sorted(users.items(), key=lambda x: x[1].get("count", 0), reverse=True)
                if not sorted_u or sorted_u[0][1].get("count", 0) == 0:
                    continue
                top_uid, top_info = sorted_u[0]
                name = top_info.get("name", "User")
                uname = top_info.get("username", "")
                tag = f"@{uname}" if uname else f"[{name}](tg://user?id={top_uid})"
                msgs = top_info.get("count", 0)

                congrats = (
                    "╭━━━━〔 👑 𝐓𝐎𝐏 𝐂𝐇𝐀𝐓𝐓𝐄𝐑 👑 〕━━━━╮\n\n"
                    f"🎉 **C O N G R A T U L A T I O N S** 🎉\n\n"
                    f"👤 **Winner:** {tag}\n"
                    f"📛 **Name:** `{name}`\n"
                    f"📊 **Messages:** `{msgs}` Sent in last 2 Hours!\n\n"
                    "⚡ *Group ke Asli Sultan aap hi ho!* 🥂🔥\n\n"
                    "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
                )
                try:
                    bot.send_message(int(cid), congrats, parse_mode="Markdown")
                except Exception:
                    pass

                for u in users:
                    users[u]["count"] = 0
            save_json(DATA_FILE, gdata)
        except Exception:
            pass

# ----------------- COMMANDS -----------------
@bot.message_handler(commands=['start', 'help'])
def start_cmd(message):
    save_chat(message.chat.id)
    txt = (
        "╭━━━━〔 ⚡ 𝐒𝐔𝐏𝐑𝐄𝐌𝐄 𝐁𝐎𝐓 ⚡ 〕━━━━╮\n\n"
        "👑 **RANKING SYSTEM:**\n"
        "├ `/ranking` - Leaderboard dekhein\n"
        "├ Har 2 ghante par Winner Announcement\n\n"
        "📢 **COMMANDS:**\n"
        "├ `/tagall [msg]` - Group tag all\n"
        "├ `/filter [word] [reply]` - Auto trigger set\n"
        "├ `/stopfilter [word]` - Trigger delete\n"
        "├ `/shayari` - Romantic Shayari\n"
        "├ `/joke` - Funny Joke\n\n"
        "✨ **SMART REACTIONS:**\n"
        "├ Shayari par 'Wah Wah' -> Special reply ❤️\n"
        "├ Joke par Laugh Emoji -> Thank you 😊\n"
        "├ Sticker aur Emoji auto-mirror\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    bot.reply_to(message, txt, parse_mode="Markdown")

@bot.message_handler(commands=['ranking'])
def ranking_cmd(message):
    save_chat(message.chat.id)
    cid = str(message.chat.id)
    gdata = load_json(DATA_FILE)
    users = gdata.get(cid, {})
    if not users:
        bot.reply_to(message, "📊 Abhi tak kisi ne koi message nahi bheja! Chat shuru karo pehle! 💬")
        return

    sorted_u = sorted(users.items(), key=lambda x: x[1].get("count", 0), reverse=True)[:10]
    out = "🏆 **LIVE GROUP LEADERBOARD** 🏆\n\n"
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i, (uid, inf) in enumerate(sorted_u):
        m = medals[i] if i < len(medals) else "🔹"
        out += f"{m} `{inf.get('name', 'User')}` ➔ **{inf.get('count', 0)} msgs**\n"
    out += "\n⏳ *Next Winner Announcement 2 Ghante me!*"
    bot.reply_to(message, out, parse_mode="Markdown")

@bot.message_handler(commands=['tagall'])
def tagall_cmd(message):
    save_chat(message.chat.id)
    if message.chat.type not in ["group", "supergroup"]:
        bot.reply_to(message, "⚠️ Ye command sirf group me kaam karegi!")
        return

    custom_text = message.text.replace("/tagall", "").strip() or "Hajiri lagao sabhi!"
    try:
        admins = bot.get_chat_administrators(message.chat.id)
        mentions = [f"[{a.user.first_name}](tg://user?id={a.user.id})" for a in admins]
        bot.send_message(message.chat.id, f"📢 **ATTENTION** 📢\n\n💬 `{custom_text}`\n\n{' '.join(mentions)}", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"Issue: {e}")

@bot.message_handler(commands=['shayari'])
def shayari_cmd(message):
    bot.reply_to(message, f"🌹 **Shayari:**\n\n{random.choice(SHAYARIS)}")

@bot.message_handler(commands=['joke'])
def joke_cmd(message):
    bot.reply_to(message, f"🎭 **Joke:**\n\n{random.choice(JOKES)}")

@bot.message_handler(commands=['filter'])
def filter_cmd(message):
    cid = str(message.chat.id)
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "⚠️ Format: `/filter [keyword] [reply]`", parse_mode="Markdown")
        return
    flt = load_json(FILTERS_FILE)
    if cid not in flt:
        flt[cid] = {}
    flt[cid][parts[1].lower()] = parts[2]
    save_json(FILTERS_FILE, flt)
    bot.reply_to(message, f"✅ Trigger set: `{parts[1]}`")

@bot.message_handler(commands=['stopfilter'])
def stopfilter_cmd(message):
    cid = str(message.chat.id)
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Format: `/stopfilter [keyword]`", parse_mode="Markdown")
        return
    flt = load_json(FILTERS_FILE)
    if cid in flt and parts[1].lower() in flt[cid]:
        del flt[cid][parts[1].lower()]
        save_json(FILTERS_FILE, flt)
        bot.reply_to(message, f"🗑️ Trigger deleted: `{parts[1]}`")
    else:
        bot.reply_to(message, "❌ Trigger nahi mila.")

# ----------------- STICKER & WELCOME -----------------
@bot.message_handler(content_types=['sticker'])
def sticker_h(message):
    save_chat(message.chat.id)
    try:
        bot.send_sticker(message.chat.id, message.sticker.file_id)
    except Exception:
        pass

@bot.message_handler(content_types=['new_chat_members'])
def welcome_h(message):
    save_chat(message.chat.id)
    for u in message.new_chat_members:
        if not u.is_bot:
            name = u.first_name
            uname = f"@{u.username}" if u.username else "No Username"
            card = (
                "╭━━━━〔 ✨ 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 ✨ 〕━━━━╮\n\n"
                f"👋 **Hey:** [{name}](tg://user?id={u.id})\n"
                f"👤 **Username:** `{uname}`\n\n"
                "🌟 *Swagat hai aapka humari mehfil me! Masti karo aur ranking jeeto!* 🥂👑\n\n"
                "╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
            bot.reply_to(message, card, parse_mode="Markdown")

# ----------------- TEXT & REACTIONS -----------------
@bot.message_handler(func=lambda m: True, content_types=['text'])
def text_h(message):
    save_chat(message.chat.id)
    t = (message.text or "").strip()
    tl = t.lower()
    cid = str(message.chat.id)
    uid = str(message.from_user.id)
    name = message.from_user.first_name

    if t.startswith("/"):
        return

    # Counter
    gd = load_json(DATA_FILE)
    if cid not in gd:
        gd[cid] = {}
    if uid not in gd[cid]:
        gd[cid][uid] = {"name": name, "username": message.from_user.username or "", "count": 0}
    gd[cid][uid]["count"] += 1
    gd[cid][uid]["name"] = name
    gd[cid][uid]["username"] = message.from_user.username or ""
    save_json(DATA_FILE, gd)

    # Filter trigger
    flt = load_json(FILTERS_FILE)
    if cid in flt and tl in flt[cid]:
        bot.reply_to(message, flt[cid][tl])
        return

    # Wah Wah
    if any(k in tl for k in ["wah", "waah", "wah wah", "kya baat hai"]):
        bot.reply_to(message, "Thank you baby tum hi to samjhte ho mujhe 🙈❤️")
        return

    # Laugh
    if any(e in tl for e in ["😂", "🤣", "😆", "haha"]):
        bot.reply_to(message, "Thank you 😊")
        return

    # Mirror single emoji
    if len(t) <= 2 and any(char in t for char in MIRROR_EMOJIS + ["😀", "😍", "😎"]):
        bot.reply_to(message, random.choice(MIRROR_EMOJIS))
        return

# ----------------- MAIN RUNNER -----------------
def start_bot_polling():
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=True", timeout=5)
    except Exception:
        pass
    print(">>> TELEGRAM POLLING STARTED SUCCESSFULLY <<<")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

if __name__ == "__main__":
    threading.Thread(target=auto_ranking_announcer, daemon=True).start()
    threading.Thread(target=start_bot_polling, daemon=True).start()
    run_web()
    
