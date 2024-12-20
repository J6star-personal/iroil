import logging
import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# تنظیمات لاگینگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(name)

# ایجاد و اتصال به دیتابیس SQLite
def create_db():
    conn = sqlite3.connect('wallets.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS wallets
                    (id INTEGER PRIMARY KEY, wallet_address TEXT)''')
    conn.commit()
    conn.close()

# افزودن آدرس کیف پول به دیتابیس
def add_wallet(user_id, wallet_address):
    conn = sqlite3.connect('wallets.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO wallets (id, wallet_address) VALUES (?, ?)', (user_id, wallet_address))
    conn.commit()
    conn.close()

# گرفتن آدرس کیف پول کاربر از دیتابیس
def get_wallet(user_id):
    conn = sqlite3.connect('wallets.db')
    cursor = conn.cursor()
    cursor.execute('SELECT wallet_address FROM wallets WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

# شروع به کار ربات
def start(update: Update, context: CallbackContext):
    update.message.reply_text('سلام! من یک ربات هستم. برای ذخیره آدرس کیف پول خود از دستور /set_wallet استفاده کنید.')

# دستور set_wallet برای ذخیره آدرس کیف پول
def set_wallet(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    wallet_address = " ".join(context.args)
    
    if wallet_address:
        add_wallet(user_id, wallet_address)
        update.message.reply_text(f'آدرس کیف پول شما با موفقیت ذخیره شد: {wallet_address}')
    else:
        update.message.reply_text('لطفاً آدرس کیف پول خود را وارد کنید.\nمثال: /set_wallet 0x1234567890abcdef')

# دستور get_wallet برای دریافت آدرس کیف پول
def get_wallet_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    wallet_address = get_wallet(user_id)
    
    if wallet_address:
        update.message.reply_text(f'آدرس کیف پول شما: {wallet_address}')
    else:
        update.message.reply_text('هیچ آدرس کیف پولی برای شما ذخیره نشده است.')

# دستور خطاها
def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# تابع اصلی برای راه‌اندازی ربات
def main():
    create_db()  # ایجاد دیتابیس SQLite در هنگام شروع ربات

    # توکن ربات خود را از BotFather در تلگرام وارد کنید
    updater = Updater("7902137813:AAHhOmum4nUdiFg1ZjrQGBIsA5YenIB_e84", use_context=True)

    # دریافت دیسپاچر برای ثبت هندلرها
    dispatcher = updater.dispatcher

    # ثبت هندلرهای مختلف
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("set_wallet", set_wallet))
    dispatcher.add_handler(CommandHandler("get_wallet", get_wallet_command))

    # ثبت هندلر برای پیام‌ها (در صورتی که نیاز به دریافت پیام‌های خاص دارید)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, error))

    # شروع ربات
    updater.start_polling()
    updater.idle()

if name == 'main':
    main()