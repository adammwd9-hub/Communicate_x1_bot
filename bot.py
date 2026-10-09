import logging
import re
import os
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# إنشاء سيرفر وهمي لتشغيل البوت مجاناً على Render Web Service
web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    web_app.run(host='0.0.0.0', port=port)

TOKEN = "8496631614:AAHUC28QCGPDEiNUXy9gnPjAYKFkse8cdy0"
ADMIN_ID = 8524156612
CHANNEL_USERNAME = "@apps_store_x1"

logging.basicConfig(level=logging.WARNING)

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['creator', 'administrator', 'member']
    except Exception:
        return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        is_sub = await check_subscription(user_id, context)
        if not is_sub:
            keyboard = [[InlineKeyboardButton("📢 اشترك في القناة هنا", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")]]
            await update.message.reply_text(
                f"⚠️ **يجب عليك الاشتراك في القناة أولاً لاستخدام البوت:**\n\n{CHANNEL_USERNAME}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

    await update.message.reply_text("أهلاً بك! 👋\n\nاكتب رسالتك أو استفسارك وسيقوم الأدمن بالرد عليك قريباً.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # 1. رد الأدمن على المستخدمين
    if user_id == ADMIN_ID:
        if update.message.reply_to_message:
            reply_msg = update.message.reply_to_message
            target_text = reply_msg.text or reply_msg.caption or ""
            
            match = re.search(r"ID:\s*(\d+)", target_text)
            if match:
                target_user_id = int(match.group(1))
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=f"💬 **رد من الإدارة:**\n\n{update.message.text}"
                    )
                    await update.message.reply_text("✅ تم إرسال الرد بنجاح.")
                except Exception:
                    await update.message.reply_text("❌ لم يتم الإرسال، غالباً المستخدم قام بحظر البوت.")
            else:
                await update.message.reply_text("⚠️ اعمل Reply على رسالة التوجيه التي تحتوي على ID المستخدم.")
        else:
            await update.message.reply_text("💡 للرد على مستخدم، اعمل Reply (رد) على الرسالة القادمة من البوت.")
        return

    # 2. استقبال الرسالة من المستخدم وتوجيهها للأدمن
    is_sub = await check_subscription(user_id, context)
    if not is_sub:
        keyboard = [[InlineKeyboardButton("📢 اشترك في القناة هنا", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")]]
        await update.message.reply_text(
            f"⚠️ **يجب عليك الاشتراك في القناة أولاً:**\n\n{CHANNEL_USERNAME}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    text = update.message.text or update.message.caption or "[ملف / ميديا]"
    forward_text = f"📩 **رسالة جديدة:**\n\n👤 **الاسم:** {user.full_name}\n🆔 **ID:** {user_id}\n🔗 **اليوزر:** @{user.username if user.username else 'لا يوجد'}\n\n💬 **الرسالة:**\n{text}"

    await context.bot.send_message(chat_id=ADMIN_ID, text=forward_text)
    await update.message.reply_text("✅ تم استلام رسالتك بنجاح.")

def main():
    # تشغيل السيرفر في الخلفية
    Thread(target=run_flask).start()
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
