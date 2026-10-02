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
OWNER_USERNAME = "itz_rohit_rss"

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

DATA_FILE = "group_data.json"
FILTERS_FILE = "filters.json"
CHATS_FILE = "chats.txt"

# ----------------- FLASK DUMMY SERVER (FOR RENDER) -----------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Supreme Group Ranking & Management Bot is Active 24/7!"

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
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save error:", e)

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

# ----------------- DATA LISTS -----------------
SHAYARIS = [
    "Aapki aankhon mein ajeeb si kashish hai,\nLagta hai yeh dil aapka hi aashiq hai! ❤️✨",
    "Dhadkan ko bhi sambhal kar rakha karo,\nHar baar aashiqui se ilaaj nahi hota! 🙈🩺",
    "Mohabbat ka koi nasha hi alag hota hai,\nTum samne na ho toh dil bechain rehta hai! 🌹🥀",
    "Hazaaron mehfilen hain aur laakhon mele hain,\nPar jahan tum nahi wahan hum bilkul akele hain! 🥺❤️"
]

JOKES = [
    "Pappu: Yaar doctor ne mujhe aam khane se mana kiya hai.\nFriend: Kyu?\nPappu: Kyunki unka kehna hai ki main pehle se hi bohot mitha hoon! 😂🤣",
    "Teacher: Class me sabse shant kaun rehta hai?\nStudent: Sir, jiska phone silent mode par ho aur charging 100% ho! 😜😆",
    "Biwi: Suniye ji, aap mere liye taare tod kar la sakte hain?\nPati: Pehle tu bartan dho le, taare baad me todunga! 💀🤣"
]

MIRROR_EMOJIS = ["🔥", "❤️", "😈", "⚡", "✨", "👑", "👀", "😎", "💯", "🥀"]

# ----------------- AUTO RANKING SCHEDULER (HAR 2 GHANTE) -----------------
def auto_ranking_announcer():
    while True:
        time.sleep(7200)
        try:
            group_data = load_json(DATA_FILE)
            for chat_id, users in group_data.items():
                if not users:
                    continue

                sorted_users = sorted(users.items(), key=lambda item: item[1].get("count", 0), reverse=True)
                if not sorted_users or sorted_users[0][1].get("count", 0) == 0:
                    continue

                top_user_id, top_info = sorted_users[0]
                name = top_info.get("name", "Mortal")
                username = top_info.get("username", "")
                user_tag = f"@{username}" if username else f"[{name}](tg://user?id={top_user_id})"
                total_msgs = top_info.get("count", 0)

                congrats_message = (
                    "╭━━━━〔 👑 𝐓𝐎𝐏 𝐂𝐇𝐀𝐓𝐓𝐄𝐑 𝐀𝐋𝐄𝐑𝐓 👑 〕━━━━╮\n\n"
                    f"🎉 **C O N G R A T U L A T I O N S** 🎉\n\n"
                    f"👤 **Winner:** {user_tag}\n"
                    f"📛 **Name:** `{name}`\n"
                    f"📊 **Messages:** `{total_msgs}` Sent in last 2 Hours!\n\n"
                    "⚡ *Group ke Asli Hero aap hi ho! Aise hi mahol banaye rakho!* 🥂🔥\n\n"
                    "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
                )
                
                try:
                    bot.send_message(int(chat_id), congrats_message, parse_mode="Markdown")
                except Exception as send_err:
                    print("Auto congrats error:", send_err)

                for uid in users:
                    users[uid]["count"] = 0
                
            save_json(DATA_FILE, group_data)
        except Exception as e:
            print("Auto ranking runner error:", e)

# ----------------- NEW MEMBER WELCOME -----------------
@bot.message_handler(content_types=['new_chat_members'])
def welcome_member(message):
    save_chat(message.chat.id)
    chat_title = message.chat.title or "Our Super Group"
    for new_user in message.new_chat_members:
        if new_user.is_bot:
            continue
        first_name = new_user.first_name
        uname = f"@{new_user.username}" if new_user.username else "No Username"
        user_link = f"[{first_name}](tg://user?id={new_user.id})"

        welcome_text = (
            "╭━━━━〔 ✨ 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 ✨ 〕━━━━╮\n\n"
            f"👋 **Hey:** {user_link}\n"
            f"👤 **Username:** `{uname}`\n"
            f"🏠 **Group:** `{chat_title}`\n\n"
            "🌟 *Swagat hai aapka humari mehfil me!*\n"
            "Masti se chat karo aur ranking jeeto! 🥂👑\n\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        bot.reply_to(message, welcome_text, parse_mode="Markdown")

# ----------------- COMMANDS -----------------
@bot.message_handler(commands=['start', 'help'])
def help_command(message):
    save_chat(message.chat.id)
    help_text = (
        "╭━━━━〔 ⚡ 𝐒𝐔𝐏𝐑𝐄𝐌𝐄 𝐁𝐎𝐓 ⚡ 〕━━━━╮\n\n"
        "👑 **RANKING SYSTEM:**\n"
        "├ `/ranking` - Live Group Top Chatters\n"
        "├ Auto: Har 2 ghante me Winner Alert!\n\n"
        "📢 **COMMANDS:**\n"
        "├ `/tagall [msg]` - Tag all admins/members\n"
        "├ `/filter [word] [reply]` - Auto trigger set\n"
        "├ `/stopfilter [word]` - Trigger remove\n"
        "├ `/shayari` - Romantic Shayari\n"
        "├ `/joke` - Mazedaar Chutkule\n\n"
        "✨ **SMART AUTO-REPLY:**\n"
        "├ Shayari par 'Wah Wah' bolne par cute reply ❤️\n"
        "├ Joke par hasne par Thank you 😊\n"
        "├ Sticker bhejo -> Sticker aayega\n"
        "├ Emoji bhejo -> Emoji aayega\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['ranking'])
def ranking_command(message):
    save_chat(message.chat.id)
    chat_id = str(message.chat.id)
    group_data = load_json(DATA_FILE)
    users = group_data.get(chat_id, {})

    if not users:
        bot.reply_to(message, "📊 Abhi tak kisi ne koi message nahi bheja! Chat shuru karo pehle! 💬")
        return

    sorted_users = sorted(users.items(), key=lambda item: item[1].get("count", 0), reverse=True)[:10]

    leaderboard = "🏆 **LIVE GROUP LEADERBOARD** 🏆\n\n"
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    for idx, (uid, info) in enumerate(sorted_users):
        name = info.get("name", "User")
        count = info.get("count", 0)
        medal = medals[idx] if idx < len(medals) else "🔹"
        leaderboard += f"{medal} `{name}` ➔ **{count} msgs**\n"

    leaderboard += "\n⏳ *Next Winner Announcement har 2 ghante me!* 🔥"
    bot.reply_to(message, leaderboard, parse_mode="Markdown")

@bot.message_handler(commands=['tagall'])
def tagall_command(message):
    save_chat(message.chat.id)
    if message.chat.type not in ["group", "supergroup"]:
        bot.reply_to(message, "⚠️ Ye command sirf group me kaam karti hai!")
        return

    custom_text = message.text.replace("/tagall", "").strip() or "Hajiri lagao sab log!"
    try:
        admins = bot.get_chat_administrators(message.chat.id)
        mentions = [f"[{admin.user.first_name}](tg://user?id={admin.user.id})" for admin in admins]
        tag_chunk = " ".join(mentions)
        bot.send_message(message.chat.id, f"📢 **ATTENTION EVERYONE** 📢\n\n💬 `{custom_text}`\n\n{tag_chunk}", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['shayari'])
def shayari_command(message):
    bot.reply_to(message, f"🌹 **Shayari:**\n\n{random.choice(SHAYARIS)}")

@bot.message_handler(commands=['joke'])
def joke_command(message):
    bot.reply_to(message, f"🎭 **Joke:**\n\n{random.choice(JOKES)}")

@bot.message_handler(commands=['filter'])
def add_filter(message):
    chat_id = str(message.chat.id)
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "⚠️ Format: `/filter [keyword] [reply]`", parse_mode="Markdown")
        return
    keyword = parts[1].lower()
    reply_msg = parts[2]

    filters = load_json(FILTERS_FILE)
    if chat_id not in filters:
        filters[chat_id] = {}
    filters[chat_id][keyword] = reply_msg
    save_json(FILTERS_FILE, filters)
    bot.reply_to(message, f"✅ Trigger set: `{keyword}` par auto-reply activate ho gaya!", parse_mode="Markdown")

@bot.message_handler(commands=['stopfilter'])
def remove_filter(message):
    chat_id = str(message.chat.id)
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Format: `/stopfilter [keyword]`", parse_mode="Markdown")
        return
    keyword = parts[1].lower()

    filters = load_json(FILTERS_FILE)
    if chat_id in filters and keyword in filters[chat_id]:
        del filters[chat_id][keyword]
        save_json(FILTERS_FILE, filters)
        bot.reply_to(message, f"🗑️ Trigger `{keyword}` delete ho gaya!", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Aisa koi trigger exist nahi karta.")

# ----------------- STICKER HANDLER -----------------
@bot.message_handler(content_types=['sticker'])
def sticker_mirror(message):
    save_chat(message.chat.id)
    try:
        bot.send_sticker(message.chat.id, message.sticker.file_id)
    except Exception:
        pass

# ----------------- GENERAL MESSAGE / REACTION TRACKER -----------------
@bot.message_handler(func=lambda m: True, content_types=['text'])
def tracker_and_react(message):
    save_chat(message.chat.id)
    text = (message.text or "").strip()
    text_lower = text.lower()
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    username = message.from_user.username or ""

    if text.startswith("/"):
        return

    # 1. COUNTER UPDATE
    group_data = load_json(DATA_FILE)
    if chat_id not in group_data:
        group_data[chat_id] = {}
    if user_id not in group_data[chat_id]:
        group_data[chat_id][user_id] = {"name": user_name, "username": username, "count": 0}

    group_data[chat_id][user_id]["count"] += 1
    group_data[chat_id][user_id]["name"] = user_name
    group_data[chat_id][user_id]["username"] = username
    save_json(DATA_FILE, group_data)

    # 2. AUTO FILTERS
    filters = load_json(FILTERS_FILE)
    chat_filters = filters.get(chat_id, {})
    if text_lower in chat_filters:
        bot.reply_to(message, chat_filters[text_lower])
        return

    # 3. WAH WAH REACTION
    wah_keywords = ["wah", "waah", "wah wah", "waah waah", "kya baat hai", "subhanallah", "gazab", "bohot khoob"]
    if any(k in text_lower for k in wah_keywords):
        bot.reply_to(message, "Thank you baby tum hi to samjhte ho mujhe 🙈❤️")
        return

    # 4. JOKE LAUGH REACTION
    laugh_emojis = ["😂", "🤣", "😆", "😹", "xd", "haha", "hahaha"]
    if any(e in text_lower for e in laugh_emojis):
        bot.reply_to(message, "Thank you 😊")
        return

    # 5. EMOJI MIRROR
    if len(text) <= 2 and any(char in text for char in MIRROR_EMOJIS + ["😀", "😍", "😎", "🥺", "😡", "🤔"]):
        bot.reply_to(message, random.choice(MIRROR_EMOJIS))
        return

# ----------------- MAIN RUNNER -----------------
if __name__ == "__main__":
    # Web server run karein alag thread me
    t_web = threading.Thread(target=run_web)
    t_web.daemon = True
    t_web.start()

    # Auto ranker run karein alag thread me
    t_rank = threading.Thread(target=auto_ranking_announcer)
    t_rank.daemon = True
    t_rank.start()

    # Webhook hard delete taaki polling freeze na ho
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=True", timeout=10)
        print("Webhook cleared.")
    except Exception as e:
        print("Webhook delete issue:", e)

    print("Telegram Polling Engine starting now...")
    
    # Polling loop directly on main thread
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=15)
        except ApiTelegramException as e:
            print("Telegram API Error:", e)
            time.sleep(3)
        except Exception as ex:
            print("Crash prevented, restarting in 2s:", ex)
            time.sleep(2)
    
