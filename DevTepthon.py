import telebot
from telebot import types
import os

ADMINS = [6217649891, 6217649891]

def is_admin(user_id):
    return user_id in ADMINS

def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("ايقاف البوت 🛑", "تشغيل البوت ✅")
    markup.row("الغاء صلاحيه ❌", "اعطاء صلاحيه ✅")
    markup.row("تحديد النجوم ⭐️")
    return markup

IS_SHUTTING_DOWN = False

def handle_admin_commands(bot, message):
    global IS_SHUTTING_DOWN
    if not is_admin(message.from_user.id):
        return
    
    if message.text == "/XAR":
        bot.send_message(message.chat.id, "❈| أهلاً بك في لوحة تحكم المطور", reply_markup=admin_keyboard())
    elif message.text == "اعطاء صلاحيه ✅":
        msg = bot.send_message(message.chat.id, "❈| أرسل أيدي الشخص لإعطائه صلاحية VIP:")
        bot.register_next_step_handler(msg, lambda m: give_vip_step(bot, m))
    elif message.text == "الغاء صلاحيه ❌":
        msg = bot.send_message(message.chat.id, "❈| ارسل ايدي الشخص لإلغاء صلاحية VIP :")
        bot.register_next_step_handler(msg, lambda m: remove_vip_step(bot, m))
    elif message.text == "تحديد النجوم ⭐️":
        msg = bot.send_message(message.chat.id, "❈| أرسل عدد النجوم الجديد مثلاً 50 :")
        bot.register_next_step_handler(msg, lambda m: set_stars_step(bot, m))
    elif message.text == "ايقاف البوت 🛑":
        if IS_SHUTTING_DOWN:
            bot.send_message(message.chat.id, "❈| تم إيقاف البوت سابقا ⚠️")
            return
        IS_SHUTTING_DOWN = True
        bot.send_message(message.chat.id, "❈| تم إيقاف استقبال الأوامر مؤقتاً 🛑.")
        # Logic to stop sessions could go here if needed
    elif message.text == "تشغيل البوت ✅":
        IS_SHUTTING_DOWN = False
        bot.send_message(message.chat.id, "❈| تم تشغيل البوت بنجاح ✅.")

def give_vip_step(bot, message):
    try:
        target_id = message.text
        from database import get_db, User
        db = get_db()
        user = db.query(User).filter(User.user_id == str(target_id)).first()
        try:
            target_chat = bot.get_chat(target_id)
            name = target_chat.first_name or target_chat.username or target_id
        except:
            name = target_id
        if not user:
            user = User(user_id=str(target_id))
            db.add(user)
        user.is_vip = True
        db.commit()
        db.close()
        bot.send_message(message.chat.id, f"❈| تم إعطاء صلاحية الـ Vip للمستخدم : {name} ✅.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ حدث خطأ: {e}")

def remove_vip_step(bot, message):
    try:
        target_id = message.text
        from database import get_db, User
        db = get_db()
        user = db.query(User).filter(User.user_id == str(target_id)).first()
        try:
            target_chat = bot.get_chat(target_id)
            name = target_chat.first_name or target_chat.username or target_id
        except:
            name = target_id
        if user:
            user.is_vip = False
            db.commit()
            bot.send_message(message.chat.id, f"❈| تم إلغاء صلاحية VIP للمستخدم : {name} 💢.")
        else:
            bot.send_message(message.chat.id, "❈| المستخدم غير موجود في قاعدة البيانات ❌")
        db.close()
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ حدث خطأ: {e}")

def set_stars_step(bot, message):
    try:
        new_count = int(message.text)
        from database import get_db, User
        db = get_db()
        db.query(User).update({User.star_count: new_count})
        db.commit()
        db.close()
        bot.send_message(message.chat.id, f"❈| تم تحديث عدد النجوم المطلوب إلي : {new_count} 🤭")
    except ValueError:
        bot.send_message(message.chat.id, "❈| يرجى إرسال رقم صحيح ❌.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ حدث خطأ: {e}")
