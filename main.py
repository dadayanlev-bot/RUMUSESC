import telebot
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# -----------------------------
#  ГЛАВНОЕ МЕНЮ С КНОПКАМИ
# -----------------------------
@bot.message_handler(commands=['start'])
def start(message):
    # Создаем клавиатуру
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Кнопки на клавиатуре
    markup.add("👩 Модель", "👨‍💼 Менеджер", "🧔 Клиент")
    bot.send_message(
        message.chat.id,
        "Добро пожаловать в RUMUS BOT.\nВыберите кто вы:",
        reply_markup=markup
    )

# -----------------------------
#  ВЫБОР РОЛИ
# -----------------------------
@bot.message_handler(func=lambda m: m.text in ["👩 Модель", "👨‍💼 Менеджер", "🧔 Клиент"])
def select_role(message):
    role = message.text

    if role == "👩 Модель":
        bot.send_message(
            message.chat.id,
            "🔍 Для моделей требуется верификация.\n"
            "Запишите видео-кружок, где вы произносите:\n\n"
            "**RUMUS.ESC**\n\n"
            "После отправьте видео сюда."
        )
        bot.register_next_step_handler(message, model_verification)

    elif role == "👨‍💼 Менеджер":
        bot.send_message(
            message.chat.id,
            "⚠️ Верификация менеджера.\nВыберите способ подтверждения:"
        )
        send_manager_verification(message.chat.id)

    elif role == "🧔 Клиент":
        bot.send_message(
            message.chat.id,
            "Добро пожаловать, клиент.\nВерификация не требуется."
        )

# -----------------------------
#  ВЕРИФИКАЦИЯ МЕНЕДЖЕРА
# -----------------------------
def send_manager_verification(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        "🔗 Реферальный менеджер",
        "💬 Отзывы от моделей",
        "📨 Отзывы от клиентов",
        "↩️ Назад"
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
#  ВЕРИФИКАЦИЯ МОДЕЛИ
# -----------------------------
def model_verification(message):
    if not message.video_note:
        bot.send_message(message.chat.id, "Это не видео-кружок. Попробуйте снова.")
        return bot.register_next_step_handler(message, model_verification)

    bot.send_message(
        message.chat.id,
        "Спасибо! Видео отправлено на ручную верификацию.\n"
        "Вы получите ответ после проверки администрацией RUMUS."
    )

# -----------------------------
#  ЗАПУСК БОТА
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
