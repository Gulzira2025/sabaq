import telebot
from telebot.types import InputMediaPhoto
import threading, time, json, os

TOKEN = "7952076738:AAHasUTMOQsmvTR_ta12JbaZe0pmtXNH2ig"

# Manba guruhlar
SOURCE_GROUP_IDS = [
    -1003115649489,  # Sinaq
    -1002516714486,  # Turizm
    -1001944640593,  # Onerment
    -1001181053413   # Texnik
]

TARGET_GROUP_ID = -4856640813  # Sabaq

bot = telebot.TeleBot(TOKEN)

# JSON bazani yuklash
def load_users():
    if not os.path.exists("users.json"):
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
    with open("users.json", "r", encoding="utf-8") as f:
        return json.load(f)

# JSON bazani saqlash
def save_users():
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users_db, f, ensure_ascii=False, indent=4)

users_db = load_users()

# Albomlarni vaqtincha saqlash
albums = {}

# Asosiy caption shabloni
BASE_CAPTION = """Taxtakópir rayonı "Bárkamal áwlad" balalar mektebiniń 13-sanlı ulıwma bilim beriw mektebinde shólkemlestirilgen Mini futbol dógereginiń sabaq waqtınan kórinis.
Dògerek basshısı    B.Qudaybergenov

Taxtakópir rayonı "Bárkamal áwlad" balalar mektebi Málimleme xizmeti
<a href="https://t.me/taxta_babm_rasmiy">Telegram</a> | <a href="https://www.instagram.com/barkamalawladtaxtakopir/">Instagram</a> | <a href="https://www.facebook.com/profile.php?id=61554016337487">Facebook</a> | <a href="https://www.youtube.com/channel/UCdOxRcd0w1GD8R2rm9H0oBg">YouTube</a> | <a href="https://tiktok.com/@barkamalawladtaxtakopir">TikTok</a>"""

# Matnni foydalanuvchiga qarab almashtirish
def generate_caption(user_id: str):
    caption = BASE_CAPTION

    # Agar yangi user bo‘lsa – bazaga qo‘shib qo‘yamiz
    if user_id not in users_db:
        users_db[user_id] = {
            "mektebiniń 13-sanlı ulıwma bilim beriw": "mektebiniń 13-sanlı ulıwma bilim beriw",
            "Mini futbol": "Mini futbol",
            "B.Qudaybergenov": "B.Qudaybergenov"
        }
        save_users()
        print(f"[INFO] Yangi foydalanuvchi qo‘shildi: {user_id}")

    # Replacements ishlatish
    replacements = users_db[user_id]
    for old, new in replacements.items():
        if old != "name":
            caption = caption.replace(old, new)

    return caption

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.chat.id not in SOURCE_GROUP_IDS:
        return

    media_group_id = message.media_group_id
    file_id = message.photo[-1].file_id

    # Foydalanuvchi ID ni string ko‘rinishda olish
    user_id = str(message.from_user.id)
    caption = generate_caption(user_id)

    if media_group_id:  # bir nechta rasm
        if media_group_id not in albums:
            albums[media_group_id] = []
            threading.Thread(target=send_album, args=(media_group_id, user_id)).start()
        albums[media_group_id].append(file_id)
    else:  # bitta rasm
        bot.send_photo(TARGET_GROUP_ID, file_id, caption=caption, parse_mode="HTML")

def send_album(group_id, user_id):
    time.sleep(2)
    if group_id in albums:
        photos = albums.pop(group_id)
        caption = generate_caption(user_id)
        media = []
        for i, file_id in enumerate(photos):
            if i == 0:
                media.append(InputMediaPhoto(media=file_id, caption=caption, parse_mode="HTML"))
            else:
                media.append(InputMediaPhoto(media=file_id))
        bot.send_media_group(TARGET_GROUP_ID, media)

print("✅ Bot ishga tushdi...")
bot.polling(none_stop=True)
