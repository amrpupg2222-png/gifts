import os
import re
import asyncio
import telebot
from telebot import types
import telethon
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import threading

# Import local modules
import DevTepthon
import must_join
import database
from keep_alive import keep_alive

# --- Configuration ---
from config import (
    API_ID,
    API_HASH,
    SESSION_STRING,
    BOT_TOKEN,
    SOURCE_CHANNEL,
    TARGET_CHANNEL
)

SOURCE_CHANNEL = "ResellGifts1","recalegift","Sandoooo_124","yyong2504"
TARGET_CHANNEL = "xxx_gifts_1"

# --- Clients Setup ---
bot = telebot.TeleBot(BOT_TOKEN)
assistant = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, device_model="AMRGIFTBot", system_version="Linux")

def parse_gift_message(text):
    # Search for price (can be ⭐ Price: 420 or Price: 420)
    price_match = re.search(r"Price:\s*(\d+)", text, re.IGNORECASE)
    
    # Search for gift name (🎁 XmasStocking-171781 or similar)
    # We look for 🎁 followed by text, but skip "Gift Found!" if it's the first line
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    name = "هدية"
    for line in lines:
        if "🎁" in line and "Gift Found!" not in line:
            name = line.replace("🎁", "").strip()
            break
    
    # Search for backdrop (🎨 Backdrop: Name or Backdrop: Name)
    backdrop_match = re.search(r"Backdrop:\s*([^\n]+)", text, re.IGNORECASE)
    
    # Search for any t.me/nft link
    link_match = re.search(r"t\.me/nft/[^\s]+", text)
    
    # Check for direct link in text first, then fallback to markdown style [Link](url)
    if not link_match:
        link_match = re.search(r"\(?(https?://t\.me/nft/[^\s\)]+)\)?", text)

    price = price_match.group(1) if price_match else "غير معروف"
    backdrop = backdrop_match.group(1).strip() if backdrop_match else "تلقائي"
    
    raw_link = link_match.group(1) if link_match and "(" in link_match.group(0) else (link_match.group(0) if link_match else None)
    
    if raw_link:
        link = raw_link if raw_link.startswith("http") else "https://" + raw_link
    else:
        link = "الرابط غير متوفر"

    translated = (
        "هدية مطورة جديدة 🧝‍♀\n\n"
        f"⇜ الاسم : {name}\n"
        f"⇜ الخلفية : {backdrop}\n"
        f"⇜ السعر : {price}\n\n"
        f"⇜ الرابط : {link}"
    )
    return translated

@bot.message_handler(commands=['start'])
def start_cmd(message):
    if not must_join.check_must_join(bot, message.from_user.id):
        bot.send_message(message.chat.id, "❈╎يرجي الاشتراك بقناة السورس لاستخدام البوت 👩‍⚖", reply_markup=must_join.must_join_markup())
        return
    
    welcome_text = (
        "❈╎اهـلا - {}\n"
        "❈╎اعمل علي نشر الهدايا بسعر أقل \n"
        "❈╎المشروع تـابع لـ @Tepthon\n"
        "❈╎قم باضافتي لقناتك وسيتم تفعيلي 🫆"
    ).format(message.from_user.first_name)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ســورس تيبثون 🩶", url="https://t.me/Tepthon"))
    markup.add(types.InlineKeyboardButton("اضـف البوت لقنـاتك 👩‍💻", url=f"https://t.me/{bot.get_me().username}?startchannel=true"))
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def all_messages(message):
    if DevTepthon.is_admin(message.from_user.id):
        DevTepthon.handle_admin_commands(bot, message)

async def assistant_loop():
    while not DevTepthon.IS_SHUTTING_DOWN:
        try:
            if not assistant.is_connected():
                await assistant.connect()
            
            if not await assistant.is_user_authorized():
                print("SESSION_ERROR: Session is invalid, expired, or revoked. Please update TG_SESSION_STRING.")
                # Wait longer before retrying to avoid spamming logs
                await asyncio.sleep(300) 
                continue

            print(f"SUCCESS: Monitoring {SOURCE_CHANNEL}...")
            
            @assistant.on(events.NewMessage(chats=SOURCE_CHANNEL))
            async def handler(event):
                try:
                    raw_text = event.message.message or ""
                    print(f"--- MESSAGE RECEIVED: {raw_text[:50]}... ---")
                    
                    link = None
                    if event.message.media and hasattr(event.message.media, 'webpage') and hasattr(event.message.media.webpage, 'url'):
                        if "t.me/nft/" in event.message.media.webpage.url:
                            link = event.message.media.webpage.url

                    is_gift = any(x in raw_text.lower() for x in ["t.me/nft/", "🎁", "price", "backdrop", "nft", "stars", "هدية", "الخلفية"]) or link is not None
                    
                    if is_gift:
                        print("Match found, parsing...")
                        translated_text = parse_gift_message(raw_text)
                        if link and "الرابط غير متوفر" in translated_text:
                            translated_text = translated_text.replace("الرابط غير متوفر", link)

                        target = "@TepthonGifts"
                        try:
                            bot.send_message(target, translated_text)
                            print(f"SUCCESS: Sent to {target}")
                        except Exception as e:
                            print(f"ERROR: Bot failed to send: {e}")
                    else:
                        print("Message ignored (not a gift).")
                except Exception as e:
                    print(f"Handler Error: {e}")
            
            await assistant.run_until_disconnected()
        except telethon.errors.rpcerrorlist.AuthKeyDuplicatedError:
            print("SESSION_ERROR: AuthKeyDuplicated (Session used elsewhere). Retrying in 60s...")
            await asyncio.sleep(60)
        except Exception as e:
            print(f"Assistant Loop Error: {e}")
            await asyncio.sleep(20)

def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # Start keep alive server
    keep_alive()
    # Start bot in a separate thread
    threading.Thread(target=run_bot, daemon=True).start()
    # Start assistant in the main thread (async loop)
    asyncio.run(assistant_loop())
