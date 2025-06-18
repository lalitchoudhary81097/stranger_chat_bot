from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot_utils import Telebot_utils

bot_class = Telebot_utils()
bot = bot_class.bot

@bot.message_handler(commands=["start"])
def start_handler(message):
    chat_id = message.chat.id
    user = message.from_user
    bot_class.log_user(chat_id, user.username, user.first_name, user.last_name)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("▶ Start Chat", callback_data="start_chat"))

    bot.send_message(chat_id, "👋 Welcome to Stranger Chat!\n\nPress the button below to connect with a stranger.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id

    if call.data == "start_chat":
        found = bot_class.matchmake(chat_id)
        if found:
            bot.edit_message_text("✅ Connecting you to a stranger...", chat_id, call.message.message_id)
            if chat_id in bot_class.pairs:
                partner_id = bot_class.pairs[chat_id]

                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("❌ Leave Chat", callback_data="leave_chat"))

                bot.send_message(chat_id, "🔗 Connected to a stranger. Say hi!", reply_markup=markup)
                bot.send_message(partner_id, "🔗 Connected to a stranger. Say hi!", reply_markup=markup)
        else:
            bot.edit_message_text("⏳ Please wait while we find someone to chat with...", chat_id, call.message.message_id)

    elif call.data == "leave_chat":
        if chat_id in bot_class.pairs:
            partner_id = bot_class.getid(chat_id)
            bot_class.exit(chat_id, partner_id)
            bot_class.requeue(chat_id)
            bot_class.requeue(partner_id)

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("▶ Start Chat Again", callback_data="start_chat"))

            bot.send_message(chat_id, "❌ You have left the chat.", reply_markup=markup)
            bot.send_message(partner_id, "❌ The other user has left the chat.", reply_markup=markup)
        else:
            bot.send_message(chat_id, "⚠️ You're not in a chat.")

@bot.message_handler(commands=["stop"])
def stop_handler(message):
    chat_id = message.chat.id
    if chat_id in bot_class.pairs:
        partner_id = bot_class.getid(chat_id)
        bot_class.exit(chat_id, partner_id)
        bot_class.requeue(chat_id)
        bot_class.requeue(partner_id)

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("▶ Start Chat Again", callback_data="start_chat"))

        bot.send_message(chat_id, "❌ You have left the chat.", reply_markup=markup)
        bot.send_message(partner_id, "❌ The other user has left the chat.", reply_markup=markup)
    else:
        bot.send_message(chat_id, "⚠️ You're not chatting with anyone.")

@bot.message_handler(commands=["report"])
def report_handler(message):
    chat_id = message.chat.id
    result = bot_class.report1(chat_id)
    if result:
        bot.send_message(chat_id, "🚨 User reported successfully.")
    else:
        bot.send_message(chat_id, "⚠️ You are not in a chat to report.")

@bot.message_handler(commands=["get_users"])
def get_users(message):
    chat_id = message.chat.id
    users = bot_class.returnall(chat_id)
    if users:
        bot.send_message(chat_id, f"👤 All users:\n{users}")
    else:
        bot.send_message(chat_id, "⛔ Unauthorized")

@bot.message_handler(commands=["get_reports"])
def get_reports(message):
    chat_id = message.chat.id
    reports = bot_class.returnreported(chat_id)
    if reports:
        bot.send_message(chat_id, f"🚩 Reports:\n{reports}")
    else:
        bot.send_message(chat_id, "⛔ Unauthorized")

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    chat_id = message.chat.id
    if chat_id in bot_class.pairs:
        partner_id = bot_class.getid(chat_id)
        try:
            bot.send_message(partner_id, message.text)
        except Exception as e:
            bot.send_message(chat_id, "⚠️ Error delivering your message.")
            bot.send_message(bot_class.admin_id, f"Error: {e}")
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("▶ Start Chat", callback_data="start_chat"))
        bot.send_message(chat_id, "❗ You're not in a chat. Press below to start chatting.", reply_markup=markup)

print("🤖 Bot is running...")
bot.infinity_polling()
