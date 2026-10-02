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
BOT_TOKEN = "8814355727:AAHZYDdWxsfZbKG78V8Mq-ZJlx4_FEYioxk"
GROQ_API_KEY = "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"
OWNER_USERNAME = "itz_rohit_rss"

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

CHATS_FILE = "chats.txt"
FILTERS_FILE = "filters.json"
USERS_FILE = "users_data.json"
RIDDLES_TRACK_FILE = "asked_riddles.json"

# ----------------- FLASK SERVER -----------------
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

# ----------------- AI ENGINE (GROQ + HIGH-SPEED BACKUP) -----------------
def ask_ai(user_prompt):
    system_instruction = (
        "Tumhara naam 'Miss Doctor' hai. Tum ek bold, dangerous devil doctor, flirty aur moody ladki ho. "
        "Tumhare creator @itz_rohit_rss hain. "
        "User ke har message ka bilkul naya, flirty, funny, thoda nakhrewala reply Hinglish mein do. "
        "Emojis zaroor use karo (😈, 🖤, 🩺, 💋, ⚡, 💉). "
        "Short 1-2 lines mein jawab do aur kabhi same reply repeat mat karo."
    )

    # 1. Try Groq API
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.85,
        "max_tokens": 150
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=8)
        if res.status_code == 200:
            data = res.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
        else:
            print("Groq Error Status:", res.status_code, res.text)
    except Exception as e:
        print("Groq Exception:", e)

    # 2. Unlimited 100% Free AI Engine Backup (Kabhi fail nahi hota)
    try:
        backup_url = f"https://text.pollinations.ai/{requests.utils.quote(user_prompt)}?system={requests.utils.quote(system_instruction)}&model=openai"
        b_res = requests.get(backup_url, timeout=10)
        if b_res.status_code == 200 and b_res.text.strip():
            return b_res.text.strip()
    except Exception as e:
        print("Backup Engine Error:", e)

    return "Dil ki dhadkan tez ho rahi hai ya mujhse darr lag raha hai? 😈💉"

# ----------------- DATA LISTS -----------------
SHAYARIS = [
    "Aapki aankhon mein ajeeb si kashish hai,\nDoctor kehte hain yeh ishq ki bandish hai! 😘🩺",
    "Dhadkan ko bhi sambhal kar rakha karo,\nHar baar injection se ilaaj nahi hota! 💉🙈",
    "Dil ka operation toh kar diya humne,\nPar marz yeh nikla ki tum par hi fida ho gaye! ❤️💋",
    "Nazar mili toh bukhar chadha diya tumne,\nBolo ab dawa kya dega yeh haseen doctor? 🥺🩺",
    "Hum toh aate the tumhari nabz check karne,\nTumne toh seene ki dhadkan hi chura li! 🙈❤️"
]

RANDOM_TAG_WORDS = [
    "Oye zinda hai ya upar bula loon? 💀😈", 
    "Doctor saab ke darr se chup ke baitha hai kya? 🩺🔥",
    "Online aa ja warna tera system crash kar doongi! ⚡🩸", 
    "Kahan gayab ho gaye janab, thoda dard aur chahiye? 🖤😈",
    "Bina meri ijazat ke offline jane ki himmat kaise hui? 😤🥀"
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
        bot.reply_to(message, "⚠️ *Khabardaar!* Sir @itz_rohit_rss ka territory hai yeh, unke kaam me dakhal mat do! 💀⚡", parse_mode="Markdown")
        return

    # 3. /start Command
    if text.startswith("/start"):
        devil_welcome = (
            "╭━━━〔 𝕯𝕰𝖁𝕴𝕷 𝕮𝕷𝕴𝕹𝕴𝕮 〕━━━╮\n"
            "🕷️ **𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐓𝐨 𝐓𝐡𝐞 𝐃𝐚𝐫𝐤 𝐃𝐨𝐦𝐚𝐢𝐧** 🕷️\n\n"
            f"👤 **Hey Mortal:** `{user_name}`\n"
            "🩺 **Name:** `MISS DOCTOR` (Devil Edition 😈)\n"
            "👑 **Architect & Lord:** `@itz_rohit_rss`\n\n"
            "⚡ *Dawa bhi main doongi aur dard bhi...*\n"
            "Maut ka ilaaj dhoondhne aaye ho ya dil haarne? Sambhal kar rehna, yahan har saans par mera pehra hai. 🩸🖤\n\n"
            "⚔️ **DEADLY WEAPONS / COMMANDS:**\n"
            "├ 💬 Direct AI Chat (Flirt ya Khatra)\n"
            "├ 🧩 `/q` - Dimag hilane wali Paheliyan\n"
            "├ 💰 `/rob` - Tijori Looto ya fine bharo\n"
            "├ 🩸 `/shayari` - Deadly Romantic Shayari\n"
            "├ 🎙️ `/vc` - Devil Voice Call Alert\n"
            "├ 💋 `/kiss` | 👋 `/slap` - Fun Torment\n"
            "├ 📢 `/tagall` | 🎯 `/rtag` - Group Terror\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯"
        )
        bot.reply_to(message, devil_welcome, parse_mode="Markdown")
        return

    # 4. /owner Command
    if text_lower in ["/owner", "owner kaun hai", "who is owner", "owner", "admin"]:
        bot.reply_to(message, f"⚡ Mere ek laute Baap aur Creator **@{OWNER_USERNAME}** hain! Unke samne sab jhukte hain. 👑💀", parse_mode="Markdown")
        return

    # 5. /q Command
    if text.startswith("/q") or text.startswith("/Q"):
        asked_data = load_json(RIDDLES_TRACK_FILE)
        asked_indices = asked_data.get(chat_id, [])

        remaining_indices = [i for i in range(len(RIDDLES_LIST)) if i not in asked_indices]

        if not remaining_indices:
            asked_indices = []
            remaining_indices = list(range(len(RIDDLES_LIST)))

        selected_idx = random.choice(remaining_indices)
        asked_indices.append(selected_idx)

        asked_data[chat_id] = asked_indices
        save_json(RIDDLES_TRACK_FILE, asked_data)

        bot.reply_to(message, f"🧩 **Devil Miss Doctor ka Sawal:**\n\n{RIDDLES_LIST[selected_idx]}\n\n_Agar jawab nahi pata toh surrender kar do babu! 😈💀_", parse_mode="Markdown")
        return

    # 6. /shayari Command
    if text.startswith("/shayari"):
        bot.reply_to(message, random.choice(SHAYARIS))
        return

    # 7. /vc Command
    if text.startswith("/vc"):
        vc_quotes = [
            "🔊 Aao sab Voice Chat par aa jao, main injection le kar baithi hoon! 💉😈",
            "🎙️ VC start ho chuki hai baby, aao thodi tabahi machayein! ⚡🎧",
            "📞 Sab log fatfat VC join karo, Doctor saab live operation karenge! 🩸💀"
        ]
        bot.reply_to(message, random.choice(vc_quotes))
        return

    # 8. /rob Command
    if text.startswith("/rob"):
        users_data = load_json(USERS_FILE)
        if user_id not in users_data:
            users_data[user_id] = {"coins": 100, "last_rob": 0}

        current_time = time.time()
        if current_time - users_data[user_id].get("last_rob", 0) < 60:
            remaining = int(60 - (current_time - users_data[user_id].get("last_rob", 0)))
            bot.reply_to(message, f"⏳ Sabar kar chor! Agla daka {remaining}s baad daalna, police peeche lagi hai. 🚔💀")
            return

        users_data[user_id]["last_rob"] = current_time
        outcome = random.choice(["success", "caught", "lucky"])

        if outcome == "success":
            stolen = random.randint(30, 150)
            users_data[user_id]["coins"] += stolen
            bot.reply_to(message, f"💰 Shabaash! Dark bank loot kar **{stolen} coins** chura liye! Total: {users_data[user_id]['coins']} 🪙", parse_mode="Markdown")
        elif outcome == "lucky":
            jackpot = random.randint(200, 400)
            users_data[user_id]["coins"] += jackpot
            bot.reply_to(message, f"🎉 JACKPOT! Devil ki secret tijori tod di aur **{jackpot} coins** uda le gaye! Total: {users_data[user_id]['coins']} 🪙", parse_mode="Markdown")
        else:
            fine = random.randint(20, 60)
            users_data[user_id]["coins"] = max(0, users_data[user_id]["coins"] - fine)
            bot.reply_to(message, f"🚔 Pakde gaye badmash! Doctor ne **{fine} coins** ka jurmana thonk diya! Bacha: {users_data[user_id]['coins']} 🪙", parse_mode="Markdown")

        save_json(USERS_FILE, users_data)
        return

    # 9. /kiss and /slap
    if text.startswith("/kiss"):
        if message.reply_to_message:
            target_name = message.reply_to_message.from_user.first_name
            bot.reply_to(message, f"💋 {user_name} ne {target_name} ko ek deadly toxic pappi de di! 😈🖤")
        else:
            bot.reply_to(message, f"💋 Miss Doctor ne {user_name} ko ek dark and sweet kiss di... nasha chadhega ab! 😘🥀")
        return

    if text.startswith("/slap"):
        if message.reply_to_message:
            target_name = message.reply_to_message.from_user.first_name
            bot.reply_to(message, f"👋 {user_name} ne {target_name} ke gaal par 440 volt ka thappad mara! ⚡💀")
        else:
            bot.reply_to(message, "Kis azaad panchi ko zameen par lana hai? Reply karke bolo! 😡👊")
        return

    # 10. /filter and /stopfilter
    if text.startswith("/filter"):
        parts = text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(message, "⚠️ Format:\n`/filter word reply_message`\nJaise: `/filter hi hello devil`", parse_mode="Markdown")
            return
        keyword = parts[1].lower()
        reply_content = parts[2]
        if chat_id not in filters_data:
            filters_data[chat_id] = {}
        filters_data[chat_id][keyword] = reply_content
        save_json(FILTERS_FILE, filters_data)
        bot.reply_to(message, f"✅ Target set: `{keyword}` trigger hone par tabahi machegi!", parse_mode="Markdown")
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
            bot.reply_to(message, f"🗑️ Trigger `{keyword}` ko mitaya gaya!", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Aisa koi target exist nahi karta!")
        return

    # 11. /tagall Command
    if text.startswith("/tagall"):
        if message.chat.type in ["group", "supergroup"]:
            custom_msg = text.replace("/tagall", "").strip() or "Hajiri lagao sabhi ke sabhi warna sabka system hang hoga!"
            try:
                admins = bot.get_chat_administrators(message.chat.id)
                tag_list = []
                for admin in admins:
                    u = admin.user
                    tag_list.append(f"[{u.first_name}](tg://user?id={u.id})")
                tag_chunk = " ".join(tag_list)
                bot.send_message(message.chat.id, f"⚠️ **ALERT FROM MISS DOCTOR** ⚠️\n\n📢 {custom_msg}\n\n{tag_chunk}", parse_mode="Markdown")
            except Exception as e:
                bot.reply_to(message, f"Target track nahi ho pa rahe: {e}")
        else:
            bot.reply_to(message, "Yeh command sirf group ke liye bani hai! 🩺")
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
                bot.reply_to(message, f"Oye badmash {tag_quote}")
        else:
            bot.reply_to(message, "Group me aao tab shikaar chunungi! 😈")
        return

    # 13. /broadcast Command (Owner Only)
    if text.startswith("/broadcast") or text.startswith("/Broadcast"):
        sender_username = (message.from_user.username or "").lower()
        if sender_username != OWNER_USERNAME.lower():
            bot.reply_to(message, f"❌ Ye command sirf mere Lord @{OWNER_USERNAME} ke liye reserved hai! 💀")
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
                bot.send_message(cid, f"⚡ **SUPREME NOTICE FROM DEVIL CREATOR** ⚡\n\n{broadcast_msg}", parse_mode="Markdown")
                success_count += 1
            except Exception:
                pass

        bot.edit_message_text(
            f"✅ Tabahi broadcast mukammal hui! Sent to {success_count} chats.",
            chat_id=message.chat.id,
            message_id=status_msg.message_id
        )
        return

    # 14. AI Chatting
    is_private = message.chat.type == "private"
    is_reply_to_bot = bool(message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)
    bot_called = any(name in text_lower for name in ["doctor", "miss doctor", "bot", "babu", "baby", "devil"])

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

    print("Miss Doctor Engine running 100% active...")
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
