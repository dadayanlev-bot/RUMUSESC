import telebot
import os
from telebot import types

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# -----------------------------
#  Главное меню — выбор роли
# -----------------------------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id

    # Используем ReplyKeyboardMarkup для больших кнопок-квадратов
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_model = types.KeyboardButton("👩 Модель")
    btn_manager = types.KeyboardButton("👨‍💼 Менеджер")
    btn_client = types.KeyboardButton("🧔 Клиент")
    markup.add(btn_model, btn_manager, btn_client)

    bot.send_message(
        user_id,
        "Добро пожаловать в RUMUS BOT.\nВыберите кто вы:",
        reply_markup=markup
    )

# -----------------------------
#  Обработка выбора роли
# -----------------------------
@bot.message_handler(func=lambda m: m.text in ["👩 Модель", "👨‍💼 Менеджер", "🧔 Клиент"])
def select_role(message):
    user_id = message.chat.id
    role = message.text

    if role == "👩 Модель":
        bot.send_message(
            user_id,
            "🔍 Для моделей требуется верификация.\n"
            "Запишите видео-кружок, где произносите:\n**RUMUS.ESC**\nПосле отправьте сюда."
        )
        bot.register_next_step_handler(message, model_verification)

    elif role == "👨‍💼 Менеджер":
        send_manager_verification(user_id)

    elif role == "🧔 Клиент":
        bot.send_message(
            user_id,
            "Добро пожаловать, клиент.\nВерификация не требуется."
        )

# -----------------------------
# Верификация менеджера (блоки)
# -----------------------------
def send_manager_verification(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🔗 Реферальный менеджер"),
        types.KeyboardButton("💬 Отзывы от моделей"),
        types.KeyboardButton("📨 Отзывы от клиентов"),
        types.KeyboardButton("↩️ Назад")
    )
    bot.send_message(user_id, "Выберите способ верификации:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in [
    "🔗 Реферальный менеджер", "💬 Отзывы от моделей", "📨 Отзывы от клиентов"
])
def manager_verification(message):
    text = message.text
    if text == "🔗 Реферальный менеджер":
        bot.send_message(message.chat.id, "Отправьте контакт менеджера, от которого вы пришли.")
    elif text == "💬 Отзывы от моделей":
        bot.send_message(message.chat.id, "Отправьте скриншоты отзывов моделей.")
    elif text == "📨 Отзывы от клиентов":
        bot.send_message(message.chat.id, "Отправьте скриншоты отзывов клиентов.")

    bot.send_message(
        message.chat.id,
        "После отправки ваши данные уйдут на ручную верификацию администратору RUMUS."
    )

# -----------------------------
# Верификация модели (видео кружок)
# -----------------------------
def model_verification(message):
    if not message.video_note:
        bot.send_message(message.chat.id, "Это не видео-кружок. Попробуйте снова.")
        bot.register_next_step_handler(message, model_verification)
    else:
        bot.send_message(
            message.chat.id,
            "Спасибо! Видео отправлено на ручную верификацию.\n"
            "Вы получите ответ после проверки администрацией RUMUS."
        )

# -----------------------------
# Запуск бота
# -----------------------------
print("Bot started!")

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

def run_server():
    server = HTTPServer(("0.0.0.0", 10000), BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server).start()

import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"RUMUS Bot is running")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server).start()

bot.infinity_polling()
