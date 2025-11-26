import telebot
from telebot import types
import os
import random

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# -----------------------------
# Простая база данных
# -----------------------------
users = {}  # user_id: {"role":..., "verified": False, "balance":0, "trust":0}
orders = {}  # order_id: {"manager":..., "params":..., "status":"open", "taken_by":None}

# -----------------------------
# Главная страница
# -----------------------------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    bot.send_message(
        user_id,
        "Добро пожаловать в RUMUS BOT!\n"
        "⚠ Верификация проходит через администрацию @RUMUSSUP.\n"
        "Баланс виртуальный, вывод через поддержку."
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("👩 Модель", "👨‍💼 Менеджер", "🧔 Клиент")
    bot.send_message(user_id, "Выберите кто вы:", reply_markup=markup)

# -----------------------------
# Выбор роли
# -----------------------------
@bot.message_handler(func=lambda m: m.text in ["👩 Модель", "👨‍💼 Менеджер", "🧔 Клиент"])
def select_role(message):
    user_id = message.chat.id
    role = message.text
    users[user_id] = {"role": role, "verified": False, "balance": 0, "trust": 0}

    if role == "👩 Модель":
        bot.send_message(
            user_id,
            "🔍 Для моделей требуется верификация.\n"
            "Запишите видео-кружок, где произносите: **RUMUS.ESC**\n"
            "Отправьте видео сюда для проверки через @RUMUSSUP."
        )
        bot.register_next_step_handler(message, model_verification)

    elif role == "👨‍💼 Менеджер":
        bot.send_message(
            user_id,
            "⚠ Для менеджеров верификация через @RUMUSSUP. Выберите способ:"
        )
        send_manager_verification(user_id)

    elif role == "🧔 Клиент":
        users[user_id]["verified"] = True
        send_client_menu(user_id)

# -----------------------------
# Верификация модели
# -----------------------------
def model_verification(message):
    user_id = message.chat.id
    if not message.video_note:
        bot.send_message(user_id, "Это не видео-кружок. Попробуйте снова.")
        bot.register_next_step_handler(message, model_verification)
        return

    bot.send_message(
        user_id,
        "Видео отправлено на ручную проверку администратору @RUMUSSUP.\n"
        "После подтверждения вы получите доступ к функциям."
    )
    users[user_id]["verified"] = False

# -----------------------------
# Верификация менеджера
# -----------------------------
def send_manager_verification(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("🔗 Реферальный менеджер", "💬 Отзывы от моделей", "📨 Отзывы от клиентов", "↩️ Назад")
    bot.send_message(user_id, "Выберите способ верификации и отправьте данные администратору:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["🔗 Реферальный менеджер", "💬 Отзывы от моделей", "📨 Отзывы от клиентов"])
def manager_verification(message):
    user_id = message.chat.id
    bot.send_message(
        user_id,
        "Отправьте выбранный способ подтверждения администратору @RUMUSSUP.\n"
        "После проверки вы получите доступ к меню менеджера."
    )
    users[user_id]["verified"] = False

# -----------------------------
# Проверка и открытие меню
# -----------------------------
@bot.message_handler(func=lambda m: m.text in ["Меню"])
def open_menu(message):
    user_id = message.chat.id
    if not users[user_id]["verified"]:
        bot.send_message(user_id, "Верификация не пройдена. Свяжитесь с @RUMUSSUP.")
        return

    role = users[user_id]["role"]
    if role == "👨‍💼 Менеджер":
        send_manager_menu(user_id)
    elif role == "👩 Модель":
        send_model_menu(user_id)
    elif role == "🧔 Клиент":
        send_client_menu(user_id)

# -----------------------------
# Меню менеджера
# -----------------------------
def send_manager_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        "📦 Создать заказ",
        "❌ Отменить заказ",
        "💬 Оставить отзыв",
        "⚠ Поддержка",
        "📝 Диспут",
        "📊 Биржа RUMUS",
        "💰 Баланс"
    )
    bot.send_message(user_id, "Выберите действие:", reply_markup=markup)

# -----------------------------
# Меню модели
# -----------------------------
def send_model_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        "📊 Биржа RUMUS",
        "💰 Баланс",
        "⚠ Поддержка"
    )
    bot.send_message(user_id, "Выберите действие:", reply_markup=markup)

# -----------------------------
# Меню клиента
# -----------------------------
def send_client_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        "📊 Биржа RUMUS",
        "💰 Баланс",
        "⚠ Поддержка"
    )
    bot.send_message(user_id, "Выберите действие:", reply_markup=markup)

# -----------------------------
# Создание заказа (упрощённо)
# -----------------------------
@bot.message_handler(func=lambda m: m.text == "📦 Создать заказ")
def create_order_step1(message):
    user_id = message.chat.id
    if not users[user_id]["verified"]:
        bot.send_message(user_id, "Верификация не пройдена. Свяжитесь с @RUMUSSUP.")
        return
    msg = bot.send_message(user_id, "Введите город для заказа:")
    bot.register_next_step_handler(msg, create_order_step2)

def create_order_step2(message):
    user_id = message.chat.id
    city = message.text
    msg = bot.send_message(user_id, "Введите дату и время встречи (пример: 25.11 18:00):")
    bot.register_next_step_handler(msg, create_order_step3, city)

def create_order_step3(message, city):
    user_id = message.chat.id
    datetime = message.text
    msg = bot.send_message(user_id, "Введите общую сумму заказа (виртуальная валюта):")
    bot.register_next_step_handler(msg, create_order_step4, city, datetime)

def create_order_step4(message, city, datetime):
    user_id = message.chat.id
    total_sum = message.text
    msg = bot.send_message(user_id, "Введите сумму для модели:")
    bot.register_next_step_handler(msg, create_order_step5, city, datetime, total_sum)

def create_order_step5(message, city, datetime, total_sum):
    user_id = message.chat.id
    model_sum = message.text
    msg = bot.send_message(user_id, "Введите длительность встречи (например, 2 часа):")
    bot.register_next_step_handler(msg, create_order_step6, city, datetime, total_sum, model_sum)

def create_order_step6(message, city, datetime, total_sum, model_sum):
    user_id = message.chat.id
    duration = message.text
    msg = bot.send_message(user_id, "Введите комментарий или пожелания:")
    bot.register_next_step_handler(msg, create_order_step7, city, datetime, total_sum, model_sum, duration)

def create_order_step7(message, city, datetime, total_sum, model_sum, duration):
    user_id = message.chat.id
    comment = message.text
    order_id = random.randint(1000, 9999)
    orders[order_id] = {
        "manager": user_id,
        "params": {
            "city": city,
            "datetime": datetime,
            "total_sum": total_sum,
            "model_sum": model_sum,
            "duration": duration,
            "comment": comment
        },
        "status": "open",
        "taken_by": None
    }
    bot.send_message(user_id, f"✅ Заказ создан! Номер заказа: {order_id}\n"
                              "Он добавлен на биржу RUMUS, модели могут его принять.")

# -----------------------------
# Биржа заказов
# -----------------------------
@bot.message_handler(func=lambda m: m.text == "📊 Биржа RUMUS")
def show_exchange(message):
    user_id = message.chat.id
    text = "📋 Биржа заказов:\n"
    for oid, odata in orders.items():
        if odata["status"] == "open":
            text += (f"Номер {oid}: {odata['params']['city']}, {odata['params']['datetime']}, "f"Сумма: {odata['params']['total_sum']}, Модель получает: {odata['params']['model_sum']}\n")
    bot.send_message(user_id, text if text != "📋 Биржа заказов:\n" else "Нет открытых заказов.")

# -----------------------------
# Баланс
# -----------------------------
@bot.message_handler(func=lambda m: m.text == "💰 Баланс")
def show_balance(message):
    user_id = message.chat.id
    bal = users[user_id]["balance"]
    bot.send_message(user_id, f"Ваш виртуальный баланс: {bal}\nВывод через поддержку @RUMUSSUP")

# -----------------------------
# Поддержка
# -----------------------------
@bot.message_handler(func=lambda m: m.text == "⚠ Поддержка")
def support(message):
    bot.send_message(message.chat.id, "Свяжитесь с поддержкой @RUMUSSUP для вопросов и вывода баланса.")

# -----------------------------
# Запуск бота
# -----------------------------
print("Bot started!")

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
