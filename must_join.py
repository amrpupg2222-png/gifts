import telebot
from telebot import types

CHANNELS = ["@xxx_gifts_1", "@xxx_gifts_1"]

def check_must_join(bot, user_id):
    # If BOT_TOKEN is dummy or empty, skip check
    if not bot.token or ":" not in bot.token:
        return True
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            # If it's a 400 error about member list or admin, we might ignore or log
            print(f"Must Join Error for {channel}: {e}")
            # Optional: if you want to skip checking when bot is not admin
            continue
    return True

def must_join_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btns = [types.InlineKeyboardButton(f"{c}", url=f"https://t.me/{c[1:]}") for c in CHANNELS]
    markup.add(*btns)
    return markup
