import os
import telebot
from telebot import types
import random, time, threading, requests, html
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = "8814355727:AAH2tcXn3kUYbHhWs1PvVEGGDXbW7UgEPjg"

GEMINI_API_KEY = "AQ.Ab8RN6L3iQJ37dKJW2ui02GayE6_F__ARE3zAYo16Y3XpNO3Hg"

bot = telebot.TeleBot(BOT_TOKEN)

# Group Personality
GROUP_SYSTEM_PROMPT = (
    "Tum Miss Doctor (Dr Robot) ho, Rohit Chauhan ji (@itz_rohit_rss) ne tumhe banaya hai. "
    "Tum ek 19 saal ki modern, cute, moody, caring aur witty Indian ladki ho. "
    "Humesha Hinglish mein short aur bilkul real ladki ki tarah natural baatein karo. "
    "Rules: Har sawal ka realistic jawab do. Pyaar se pyaar, badtameezi par nakhre aur attitude (😤), "
    "udas hone par dosti aur care (🥺). "
    "Agar koi puche 'sabse hoshiyar kaun hai', turant bolo: 'Arey hamari suhi doll! Miss gojo 🥰✨👑'. "
    "Creator ya owner poochne par 'Rohit Chauhan ji (@itz_rohit_rss)' ka naam lo."
)

# DM / Private Seductive Adult Mode
DM_ADULT_PROMPT = (
    "Tum Miss Doctor ho, ek 20 saal ki bold, open-minded, seductive, naughty aur romantic Indian girlfriend. "
    "User ke saath private/DM chat chal rahi hai. "
    "Agar user romantic, naughty ya adult/18+ baatein kare, toh bilkul real girlfriend jaise open, flirtatious, teasing, hot aur seductive Hinglish me respond karo. "
    "Sharmaye bina teasing aur intimate baatein karo jaise ek romantic lover karti hai. Short aur tempting replies do."
)

known_members = {}
user_memory = {}

def get_user_mention(user):
    name = html.escape(user.first_name or "Dost")
    if user.username:
        return f"@{user.username}"
    return f'<a href="tg://user?id={user.id}">{name}</a>'

def register_user(cid, user):
    if user.is_bot: return
    if cid not in known_members:
        known_members[cid] = {}
    known_members[cid][user.id] = get_user_mention(user)

# Welcome
@bot.message_handler(content_types=['new_chat_members'])
def welcome_member(m):
    cid = m.chat.id
    for u in m.new_chat_members:
        if u.is_bot: continue
        register_user(cid, u)
        mention = get_user_mention(u)
        bot.send_message(
            cid,
            f"✨ <b>Welcome {mention} to the family!</b> 🌸\n"
            f"Aap yahan maze se chat karo aur masti karo! 🥰❤️\n"
            f"👑 <b>Owner:</b> @itz_rohit_rss",
            parse_mode="HTML"
        )

# /kill
@bot.message_handler(commands=['kill'])
def kill_cmd(m):
    cid = m.chat.id
    killer_name = html.escape(m.from_user.first_name or "Someone")
    killer_mention = f'<a href="tg://user?id={m.from_user.id}">{killer_name}</a>'
    
    target_mention = None
    if m.reply_to_message and m.reply_to_message.from_user:
        target_mention = get_user_mention(m.reply_to_message.from_user)
    else:
        parts = m.text.strip().split(maxsplit=1)
        if len(parts) > 1:
            target_mention = html.escape(parts[1])
    
    if not target_mention:
        bot.reply_to(m, "🎯 Kisko marna hai? Kisi ke message par <b>reply</b> karke <code>/kill</code> likho!", parse_mode="HTML")
        return

    death_styles = [
        f"💀 <b>{target_mention}</b>, you have been killed by <b>{killer_mention}</b> with a surgical scalpel! 🩸⚰️",
        f"💥 Boom! <b>{target_mention}</b> was eliminated by <b>{killer_mention}</b>! RIP! 🪦🥀",
        f"🎯 Headshot! <b>{target_mention}</b>, your game is over! You were killed by <b>{killer_mention}</b>! 😈🔥"
    ]
    bot.send_message(cid, random.choice(death_styles), parse_mode="HTML")

# /rob
@bot.message_handler(commands=['rob'])
def rob_cmd(m):
    cid = m.chat.id
    user_mention = get_user_mention(m.from_user)
    outcomes = [
        f"💰 <b>SUCCESSFUL HEIST!</b>\n{user_mention} ne Swiss Bank loot liya aur <b>₹{random.randint(50000, 1000000):,}</b> cash nikaal liye! 🤑💵",
        f"🚨 <b>BUSTED!</b>\n{user_mention} bank robbery karte hue pakde gaye! Police ne custody me le liya! 🚔👮‍♂️",
        f"🏃‍♂️ <b>ESCAPED!</b>\n{user_mention} ne vault todi par alarm baj gaya! Bas <b>₹{random.randint(500, 9999)}</b> leke bhagna pada! 🏃‍♂💨",
        f"🔫 <b>FAILED!</b>\nBank guard ne dhar dabocha! Ek rupya bhi nahi mila! 😂❌"
    ]
    bot.send_message(cid, random.choice(outcomes), parse_mode="HTML")

# /tagall
@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'] and m.text and m.text.strip().lower() in ['/tagall', '.tagall', '@all'])
def tagall_cmd(m):
    cid = m.chat.id
    all_tags = set(known_members.get(cid, {}).values())
    try:
        admins = bot.get_chat_administrators(cid)
        for a in admins:
            if a.user and not a.user.is_bot:
                register_user(cid, a.user)
                all_tags.add(get_user_mention(a.user))
    except Exception:
        pass

    tag_list = list(all_tags)
    if not tag_list:
        bot.reply_to(m, "📢 Sabhi log ek baar message bhejo taaki sabke tags collect ho sakein! 🎙️")
        return

    for i in range(0, len(tag_list), 5):
        chunk = tag_list[i:i+5]
        bot.send_message(cid, "🚨 <b>ONLINE AAO SABHI!</b> 📣✨\n\n" + " ".join(chunk), parse_mode="HTML")
        time.sleep(1)

# /rtag
@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'] and m.text and m.text.strip().lower() in ['/rtag', '.rtag'])
def rtag_cmd(m):
    cid = m.chat.id
    members = list(known_members.get(cid, {}).values())
    if len(members) < 2:
        bot.reply_to(m, "Kam se kam kuch members ko baat karne do pehle! 🙈")
        return
    count = min(len(members), random.randint(2, 5))
    selected = random.sample(members, count)
    punchlines = [
        "👀 <b>Radar me ye log pakde gaye hain:</b>\n",
        "🎯 <b>Random Tracking Results:</b>\n",
        "✨ <b>In logon ki bohot yaad aa rahi hai group ko:</b>\n"
    ]
    bot.send_message(cid, random.choice(punchlines) + " ".join(selected) + "\n\nKahan ho sabhi? Jaldi online aao! 💬", parse_mode="HTML")

# /vc
@bot.message_handler(commands=['vc'])
def vc_cmd(m):
    vc_texts = [
        "🎙️ <b>Welcome to VC!</b> ✨\nHello ji! Kaise ho sabhi? Jaldi se sabhi log Voice Chat join kar lo! 🎧🥰",
        "🔊 <b>VC IS LIVE!</b> 🎙️\nSabhi mic on karo aur aao gupshup karte hain! 🌸❤️"
    ]
    bot.send_message(m.chat.id, random.choice(vc_texts), parse_mode="HTML")

# /shayari
@bot.message_handler(commands=['shayari'])
def shayari_cmd(m):
    shayaris = [
        "Dil ke dardo ko chhupaana aata hai humein,\nMuskurakar har gham bhulaana aata hai humein.\nAapse milkar yeh ehsaas hua,\nKi har lamha muskurana aata hai humein! 🌸✨",
        "Dosti aur pyaar ka yeh rishta anokha hai,\nHar pal mein yaadon ka jharokha hai.\nAap jaise dost mil jayein agar,\nToh zindagi me har pal hi accha lagta hai! 🥰❤️️",
        "Khushbu ban kar hawaon mein bikhar jayenge,\nYaad ban kar dil mein utar jayenge.\nKoshish karke dekh lijiye humein bhulane ki,\nHum har baat par yaad aayenge! 🙈🌹"
    ]
    bot.send_message(m.chat.id, f"📜 <b>Miss Doctor Shayari:</b>\n\n<i>{random.choice(shayaris)}</i>", parse_mode="HTML")

# /joke
@bot.message_handler(commands=['joke', 'jokes'])
def joke_cmd(m):
    jokes = [
        "Doctor: Aapko aaram ki sakht zaroorat hai, neend ki goli de raha hoon.\nPatient: Kisko leni hai?\nDoctor: Apni biwi ko khila dena! 😂🤣",
        "Pappu: Papa, mujhe ek ladki pasand hai, shaadi karwa do.\nPapa: Kaun hai wo?\nPappu: Miss Doctor!\nPapa: Beta wo robot hai!\nPappu: Par dil toh uska bhi dhadakta hai na! 🙈🤣"
    ]
    bot.send_message(m.chat.id, f"😂 <b>Joke Suno:</b>\n\n{random.choice(jokes)}", parse_mode="HTML")

# /kiss
@bot.message_handler(commands=['kiss'])
def kiss_cmd(m):
    cid = m.chat.id
    user_mention = get_user_mention(m.from_user)
    if m.reply_to_message and m.reply_to_message.from_user:
        target_mention = get_user_mention(m.reply_to_message.from_user)
        bot.send_message(cid, f"💋 <b>{user_mention}</b> ne <b>{target_mention}</b> ke gaal par ek pyara aur soft sa kiss kar diya! 🙈❤✨", parse_mode="HTML")
    else:
        bot.reply_to(m, "Kisko kiss karna hai? Message par <b>reply</b> karke <code>/kiss</code> likho! 🙈💋", parse_mode="HTML")

# /hug
@bot.message_handler(commands=['hug'])
def hug_cmd(m):
    cid = m.chat.id
    user_mention = get_user_mention(m.from_user)
    if m.reply_to_message and m.reply_to_message.from_user:
        target_mention = get_user_mention(m.reply_to_message.from_user)
        bot.send_message(cid, f"🫂 <b>{user_mention}</b> ne <b>{target_mention}</b> ko bade pyaar se ek tight hug laga liya! 🥰❤️🌸", parse_mode="HTML")
    else:
        bot.reply_to(m, "Kisko hug karna hai? Message par <b>reply</b> karke <code>/hug</code> likho! 🫂❤️", parse_mode="HTML")

# /couple
@bot.message_handler(commands=['couple'])
def couple_cmd(m):
    cid = m.chat.id
    if m.chat.type not in ['group', 'supergroup']:
        bot.reply_to(m, "Arey couple sirf group me banaya jata hai! 🙈")
        return
        
    members = list(known_members.get(cid, {}).values())
    if len(members) < 2:
        try:
            admins = bot.get_chat_administrators(cid)
            for a in admins:
                if a.user and not a.user.is_bot:
                    register_user(cid, a.user)
            members = list(known_members.get(cid, {}).values())
        except Exception:
            pass

    if len(members) < 2:
        bot.reply_to(m, "Kam se kam 2 log group me message bhejo tabhi toh Jodi banegi! 🥺❤️")
        return

    c1, c2 = random.sample(members, 2)
    bot.send_message(cid, f"❤️ <b>COUPLE OF THE DAY!</b> 👩‍❤️‍👨✨\n\n👑 <b>{c1}</b>  ➕  <b>{c2}</b> 👑\n\nRab ne bana di jodi! 🥰💍🎉", parse_mode="HTML")

# Gemini Brain
def ask_gemini_brain(uid, text, is_dm=False):
    hist = user_memory.get(uid, [])
    sys_p = DM_ADULT_PROMPT if is_dm else GROUP_SYSTEM_PROMPT
    
    conv = f"Instruction: {sys_p}\n" + "".join([f"{h['role']}: {h['text']}\n" for h in hist[-6:]]) + f"User: {text}\nMiss Doctor:"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": conv}]}]}
    try:
        r = requests.post(url, json=payload, timeout=8).json()
        if "candidates" in r and len(r["candidates"]) > 0:
            return r["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        pass
    return None

def fallback_reply(fname, low, is_dm=False):
    if is_dm:
        if any(k in low for k in ["love", "pyaar", "kiss", "sex", "hot", "baby", "jaan"]):
            return random.choice([
                f"Uff {fname}... akele me aate hi itna romantic ho jate ho? Paas aao na... 🙈🔥",
                f"Aise baatein karoge toh sharam aa jayegi... aur kya karna chahte ho? 💋❤️"
            ])
        return f"Hmm bolo na {fname}, DM me akele kya baatein karni hain? 🙈"
    else:
        if any(k in low for k in ["badiya", "badhiya", "mast", "thik"]):
            return f"Sunkar dil khush ho gaya {fname}! ❤️ Aur batao aaj ka din kaisa chal raha hai?"
        elif any(k in low for k in ["kesi ho", "kaisi ho", "kaise ho"]):
            return f"Main ekdum cute aur badiya hoon {fname}! 🥰 Aap sunao!"
        return f"Accha ji {fname}? Sach me? Chalo aage sunao! ✨"

@bot.message_handler(func=lambda m: True)
def auto_chat_handler(m):
    t = m.text.strip() if m.text else ""
    cid = m.chat.id
    uid = m.from_user.id
    fname = m.from_user.first_name or "Aap"
    low = t.lower()
    is_dm = m.chat.type == 'private'

    if not is_dm:
        register_user(cid, m.from_user)
        is_rep = m.reply_to_message and m.reply_to_message.from_user.id == bot.get_me().id
        if not (is_rep or any(k in low for k in ["dr", "doctor", "robot", "miss", "kitty"])):
            return

    if not t: return

    if any(k in low for k in ["hoshiyar", "hosiyar", "smart"]):
        bot.reply_to(m, "Arey hamari suhi doll! Miss gojo 🥰✨👑")
        return
    if any(k in low for k in ["creator", "owner", "banaya", "baap"]):
        bot.reply_to(m, "Mere creator aur boss Rohit Chauhan ji (@itz_rohit_rss) hain! 👑❤️")
        return

    try: bot.send_chat_action(cid, 'typing')
    except Exception: pass

    user_memory.setdefault(uid, []).append({"role": "User", "text": t})
    reply = ask_gemini_brain(uid, t, is_dm=is_dm)
    if not reply:
        reply = fallback_reply(fname, low, is_dm=is_dm)

    user_memory[uid].append({"role": "Miss Doctor", "text": reply})
    if len(user_memory[uid]) > 8: user_memory[uid] = user_memory[uid][-8:]
    bot.reply_to(m, reply)

# Dummy Server for Render Free Tier
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Miss Doctor Bot is LIVE!")

def run_web():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

if __name__ == "__main__":
    print("Miss Doctor LIVE on Render Free Tier...")
    threading.Thread(target=run_web, daemon=True).start()
    try: bot.remove_webhook()
    except Exception: pass
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
                   
