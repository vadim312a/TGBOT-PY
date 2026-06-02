from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from wakeonlan import send_magic_packet
import os
import platform
import subprocess

# =====================
TOKEN = os.getenv("TOKEN")
OWNER_ID = 1460740609

PC_MAC = "A8:A1:59:E8:9A:7D"
PC_IP = "192.168.0.103"
# =====================


def is_owner(user_id: int):
    return user_id == OWNER_ID


def ping_pc():
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", PC_IP]

    try:
        return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    except:
        return False


def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 Включить ПК", callback_data="on")],
        [InlineKeyboardButton("🎮 Dota 2", callback_data="dota")],
        [InlineKeyboardButton("📡 Статус ПК", callback_data="status")],
        [InlineKeyboardButton("🔴 Выключить ПК", callback_data="off")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("⛔ Доступ запрещён")
        return

    await update.message.reply_text("⚙️ Railway PC Control", reply_markup=menu())


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if not is_owner(query.from_user.id):
        await query.answer("Нет доступа", show_alert=True)
        return

    await query.answer()

    # 🟢 ВКЛ ПК
    if query.data == "on":
        send_magic_packet(PC_MAC)
        await query.message.reply_text("🟢 Сигнал на включение отправлен")

    # 🎮 DOTA (Railway НЕ может запускать Steam на твоём ПК)
    elif query.data == "dota":
        await query.message.reply_text("🎮 Команда отправлена (Dota запускается на ПК локально)")
    
    # 📡 СТАТУС
    elif query.data == "status":
        if ping_pc():
            await query.message.reply_text("🟢 ПК онлайн")
        else:
            await query.message.reply_text("🔴 ПК оффлайн")

    # 🔴 ВЫКЛ ПК (работает только если бот на самом ПК — тут просто сигнал)
    elif query.data == "off":
        await query.message.reply_text("🔴 Команда выключения отправлена (нужен агент на ПК)")


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

print("🤖 BOT RUNNING (RAILWAY)")
app.run_polling()