import os
import telebot
from telebot import types

# Получаем токен из переменных окружения
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# Простая база данных в памяти
users = {}
orders = []

# ------------------------------
# СТАРТ
# ------------------------------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    users[user_id] = {"role": None, "verified": False, "balance": 0}
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Модель", callback_data="role_model"),
        types.InlineKeyboardButton("Менеджер", callback_data="role_manager"),
        types.InlineKeyboardButton("Клиент", callback_data="role_client")
    )
    bot.send_message(user_id, "Привет! Выберите свою роль:", reply_markup=markup)

# ------------------------------
# ВЫБОР РОЛИ
# ------------------------------
@bot.callback_query_handler(func=lambda c: c.data.startswith("role_"))
def choose_role(callback):
    role = callback.data.replace("role_", "")
    users[callback.message.chat.id]["role"] = role

    if role == "model":
        bot.send_message(callback.message.chat.id,
                         "Вы выбрали МОДЕЛЬ. Отправьте фото/видео и данные для верификации. Модератор проверит.")
    elif role == "manager":
        send_manager_verification_options(callback.message.chat.id)
    else:
        bot.send_message(callback.message.chat.id, "Вы выбрали КЛИЕНТ. Верификация не нужна.")

# ------------------------------
# ВЕРИФИКАЦИЯ МЕНЕДЖЕРА
# ------------------------------
def send_manager_verification_options(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Контакт реферала", callback_data="ver_manager_ref"),
        types.InlineKeyboardButton("Отзывы о сделках с моделями", callback_data="ver_manager_models"),
        types.InlineKeyboardButton("Отзывы о сделках с клиентами", callback_data="ver_manager_clients")
    )
    bot.send_message(user_id, "Выберите способ верификации (проверка вручную):", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("ver_manager_"))
def verify_manager(callback):
    type_ver = callback.data.replace("ver_manager_", "")
    users[callback.message.chat.id]["verification_waiting"] = type_ver
    bot.send_message(callback.message.chat.id,
                     f"Отправьте данные для варианта '{type_ver}'. Модератор проверит вручную.")

# ------------------------------
# СОЗДАНИЕ ЗАКАЗА
# ------------------------------
@bot.message_handler(commands=['neworder'])
def new_order(message):
    user_id = message.chat.id
    if users.get(user_id, {}).get("role") != "manager":
        return bot.send_message(user_id, "Команда доступна только менеджерам.")
    bot.send_message(user_id, "Опишите заказ: город, дата, сумма, условия, сколько получает модель.")
    bot.register_next_step_handler(message, save_order)

def save_order(message):
    orders.append(message.text)
    bot.send_message(message.chat.id, "Заказ опубликован на RUMUS бирже!")

# ------------------------------
# RUMUS Биржа (для моделей)
# ------------------------------
@bot.message_handler(commands=['market'])
def market(message):
    user = users.get(message.chat.id)
    if not user or user.get("role") != "model":
        return bot.send_message(message.chat.id, "Биржа доступна только моделям.")
    if not orders:
        return bot.send_message(message.chat.id, "Пока заказов нет.")
    text = "📌 RUMUS Биржа — доступные заказы:\n\n"
    for i, order in enumerate(orders, 1):
        text += f"{i}. {order}\n"
    bot.send_message(message.chat.id, text)

# ------------------------------
# БАЛАНС
# ------------------------------
@bot.message_handler(commands=['balance'])
def balance(message):
    user = users.get(message.chat.id)
    if user:
        bot.send_message(message.chat.id, f"Ваш баланс: {user['balance']} USD")

# ------------------------------
# ВЫВОД ДЕНЕГ
# ------------------------------
@bot.message_handler(commands=['withdraw'])
def withdraw(message):
    bot.send_message(message.chat.id,
                     "Для вывода средств обратитесь в поддержку. Оператор обработает заявку вручную.")
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

def run_server():
    server = HTTPServer(("0.0.0.0", 10000), BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server).start()

bot.polling()
