# main.py
# Простой Telegram-bot (pyTelegramBotAPI) для RUMUS.ESC — с реализацией RUMUS Биржи
# pip install pyTelegramBotAPI

import telebot
from telebot import types

TOKEN = os.getenv(8497594070:AAHdh5pdWSJ_Pr4Zjmc0P3zdPA4wIUG2R9A)   # -- Поменяй на токен от BotFather
ADMIN_ID = 123456789               # -- Твой Telegram ID (опционально уведомления админa)

bot = telebot.TeleBot(8497594070:AAHdh5pdWSJ_Pr4Zjmc0P3zdPA4wIUG2R9A)

# В памяти
users = {}         # {tg_id {role modelmanagerclient, verified False, ...}}
verifications = {} # {tg_id bool}
balances = {}      # {tg_id float}
orders = []        # список словарей заказа
next_order_id = 1

# ----- вспомогательные клавиатуры -----
def main_keyboard()
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(Регистрация, Мой профиль)
    kb.row(RUMUS Биржа, Поддержка)
    return kb

def manager_keyboard()
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(Создать заказ, Отменить заказ)
    kb.row(Мои заказы, Биржа (просмотр))
    kb.row(Баланс, Поддержка)
    return kb

def model_keyboard()
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(Моя анкета, RUMUS Биржа)
    kb.row(Отклики, Баланс)
    kb.row(Поддержка)
    return kb

def client_keyboard()
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(Создать заказ, Мои заказы)
    kb.row(RUMUS Биржа, Баланс)
    kb.row(Поддержка)
    return kb

# ----- утилиты -----
def ensure_user(uid)
    if uid not in users
        users[uid] = {role None, verified False, profile None}
    return users[uid]

def get_order_by_id(oid)
    for o in orders
        if o[id] == oid
            return o
    return None

# ----- старт -----
@bot.message_handler(commands=['start'])
def cmd_start(msg)
    ensure_user(msg.from_user.id)
    bot.send_message(msg.chat.id, Добро пожаловать в RUMUS.ESC — выберите действие, reply_markup=main_keyboard())

# ----- регистрация  выбор роли -----
@bot.message_handler(func=lambda m m.text == Регистрация)
def registration(msg)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(Я — Модель, callback_data=role_model))
    kb.add(types.InlineKeyboardButton(Я — Менеджер, callback_data=role_manager))
    kb.add(types.InlineKeyboardButton(Я — Клиент, callback_data=role_client))
    bot.send_message(msg.chat.id, Кем вы являетесь Выберите роль, reply_markup=kb)

@bot.callback_query_handler(func=lambda c c.data and c.data.startswith(role_))
def callback_role(c)
    role = c.data.split(_,1)[1]
    uid = c.from_user.id
    ensure_user(uid)
    users[uid][role] = role
    users[uid][verified] = False if role in [manager,model] else True
    bot.answer_callback_query(c.id, fРоль установлена {role})
    if role == manager
        bot.send_message(uid, Вы — Менеджер. Для доступа необходимо пройти верификацию.nВыберите метод верификации отправьте контакт пригласившего, отзывы или файлы. Всё проверяет админ.,
                         reply_markup=types.ReplyKeyboardRemove())
    elif role == model
        bot.send_message(uid, Вы — Модель. Пожалуйста, создайте анкету и отправьте короткое видео с фразой 'RUMUS.ESC' для верификации. Админ проверит вручную.,
                         reply_markup=types.ReplyKeyboardRemove())
    else
        bot.send_message(uid, Вы — Клиент. Верификация не нужна., reply_markup=client_keyboard())

# ----- получение материалов для верификации -----
@bot.message_handler(content_types=['photo','video','document','text'])
def handle_all(msg)
    uid = msg.from_user.id
    if uid not in users or users[uid][role] is None
        bot.send_message(uid, Сначала нажмите 'Регистрация' и выберите роль., reply_markup=main_keyboard())
        return

    role = users[uid][role]
    # если роль требует верификации и она ещё не пройдена — принимаем материалы и шлём админу
    if role in [manager,model] and not users[uid][verified]
        bot.send_message(uid, Материал получен и отправлен на проверку. Ожидайте результатов от поддержки.)
# переслать админу
        try
            bot.send_message(ADMIN_ID, fНовая верификация @{msg.from_user.username} (role={role}))
            msg.forward(ADMIN_ID)
        except Exception
            pass
        return

    # если уже верифицирован — показать меню по роли
    if users[uid][verified]
        if role == manager
            bot.send_message(uid, Меню менеджера, reply_markup=manager_keyboard())
        elif role == model
            bot.send_message(uid, Меню модели, reply_markup=model_keyboard())
        else
            bot.send_message(uid, Меню клиента, reply_markup=client_keyboard())
        return

    # в остальных случаях
    bot.send_message(uid, Ваш статус ожидается верификация. Отправьте материалы (видеоскринконтакт).)

# ----- Менеджер создать заказ (последовательность) -----
creating_order = {}  # tmp state {uid step_index, data {}}

@bot.message_handler(func=lambda m m.text == Создать заказ)
def start_create_order(msg)
    uid = msg.from_user.id
    if uid not in users or users[uid][role] != manager or not users[uid][verified]
        bot.send_message(uid, Только верифицированные менеджеры могут создавать заказы.)
        return
    creating_order[uid] = {step 1, data {}}
    bot.send_message(uid, Создание заказа — шаг 17nВведите город (пример Dubai))

@bot.message_handler(func=lambda m m.from_user.id in creating_order)
def create_order_steps(msg)
    uid = msg.from_user.id
    state = creating_order.get(uid)
    text = msg.text.strip() if msg.text else 
    step = state[step]

    if step == 1
        state[data][city] = text
        state[step] = 2
        bot.send_message(uid, Шаг 27 — Введите дату и время встречи (YYYY-MM-DD HHMM))
        return
    if step == 2
        state[data][time] = text
        state[step] = 3
        bot.send_message(uid, Шаг 37 — Длительность встречи (минуты))
        return
    if step == 3
        try
            state[data][duration] = int(text)
        except
            bot.send_message(uid, Некорректное число, введите длительность в минутах (например 60).)
            return
        state[step] = 4
        bot.send_message(uid, Шаг 47 — Общая сумма (в USDT))
        return
    if step == 4
        try
            state[data][total_amount] = float(text)
        except
            bot.send_message(uid, Некорректная сумма, введите число (например 300).)
            return
        state[step] = 5
        bot.send_message(uid, Шаг 57 — Сумма модели (сколько получит модель, в той же валюте))
        return
    if step == 5
        try
            state[data][model_amount] = float(text)
        except
            bot.send_message(uid, Некорректная сумма, введите число.)
            return
        state[step] = 6
        bot.send_message(uid, Шаг 67 — Процент менеджера от суммы (например 20))
        return
    if step == 6
        try
            state[data][manager_pct] = float(text)
        except
            bot.send_message(uid, Некорректный процент, введите число (например 20).)
            return
        state[step] = 7
        bot.send_message(uid, Шаг 77 — Краткое описание  требования к модели)
        return
    if step == 7
        state[data][requirements] = text
        # создаём заказ
        global next_order_id
        order = {
            id next_order_id,
            manager_id uid,
            city state[data].get(city),
            time state[data].get(time),
            duration state[data].get(duration),
            total_amount state[data].get(total_amount),
            model_amount state[data].get(model_amount),
            manager_pct state[data].get(manager_pct),
            requirements state[data].get(requirements),
            status open,
            model_id None,
            client_id None,
            offer_code fOFF-{next_order_id04d}
        }
        orders.append(order)
next_order_id += 1
        del creating_order[uid]
        bot.send_message(uid, fЗаказ создан и опубликован в RUMUS Бирже! ID #{order['id']}  Код {order['offer_code']})
        # оповестить админов (опционально)
        try
            bot.send_message(ADMIN_ID, fНовый заказ #{order['id']} от менеджера @{msg.from_user.username} ({order['city']}))
        except
            pass
        return

# ----- Менеджер отменить заказ -----
@bot.message_handler(func=lambda m m.text == Отменить заказ)
def cancel_order(msg)
    uid = msg.from_user.id
    if uid not in users or users[uid][role] != manager
        bot.send_message(uid, Только менеджеры.)
        return
    bot.send_message(uid, Введите ID заказа для отмены (например 12))

@bot.message_handler(func=lambda m m.text and m.text.isdigit())
def cancel_by_id(msg)
    uid = msg.from_user.id
    if users.get(uid,{}).get(role) != manager
        return
    oid = int(msg.text.strip())
    o = get_order_by_id(oid)
    if not o
        bot.send_message(uid, Заказ не найден.)
        return
    if o[manager_id] != uid
        bot.send_message(uid, Вы не являетесь создателем этого заказа.)
        return
    if o[status] in [completed,cancelled]
        bot.send_message(uid, fНельзя отменить заказ со статусом {o['status']}.)
        return
    o[status] = cancelled
    bot.send_message(uid, fЗаказ #{oid} отменён.)
    # оповестить модель, если была назначена
    if o.get(model_id)
        try
            bot.send_message(o[model_id], fЗаказ #{oid} был отменён менеджером.)
        except
            pass

# ----- Биржа модели и клиенты просматривают (с фильтром по городу) -----
@bot.message_handler(func=lambda m m.text == RUMUS Биржа or m.text == Биржа (просмотр))
def show_exchange_menu(msg)
    # предложим выбрать город (соберём список городов из открытых заказов)
    cities = sorted({o[city] for o in orders if o[status] == open})
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(Все города, callback_data=city_ALL))
    for c in cities
        kb.add(types.InlineKeyboardButton(c, callback_data=fcity_{c}))
    bot.send_message(msg.chat.id, Выберите город для фильтрации заказов, reply_markup=kb)

@bot.callback_query_handler(func=lambda c c.data and c.data.startswith(city_))
def city_filter(c)
    sel = c.data.split(_,1)[1]
    if sel == ALL
        filtered = [o for o in orders if o[status] == open]
    else
        filtered = [o for o in orders if o[status] == open and o[city].lower() == sel.lower()]

    if not filtered
        bot.send_message(c.from_user.id, Заказы не найдены по выбранному фильтру.)
        return

    for o in filtered
        txt = (fID #{o['id']}  {o['city']}  {o['time']}n
               fДлительность {o['duration']} мин  Сумма {o['total_amount']}  Модель {o['model_amount']}n
               fМенеджер @{bot.get_chat(o['manager_id']).username if bot.get_chat(o['manager_id']).username else 'manager'}n
               fТребования {o['requirements']}n
               fКод оффера {o['offer_code']}n
               fСтатус {o['status']}n)
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(Принять заказ, callback_data=faccept_{o['id']}))
        kb.add(types.InlineKeyboardButton(Подробнее, callback_data=fdetail_{o['id']}))
        bot.send_message(c.from_user.id, txt, reply_markup=kb)

# ----- Принять заказ (модель) -----
@bot.callback_query_handler(func=lambda c c.data and c.data.startswith(accept_))
def accept_order(c)
    uid = c.from_user.id
    if users.get(uid,{}).get(role) != model or not users[uid][verified]
        bot.answer_callback_query(c.id, Только верифицированные модели могут принимать заказы.)
        return
    oid = int(c.data.split(_,1)[1])
    o = get_order_by_id(oid)
    if not o
        bot.answer_callback_query(c.id, Заказ не найден.)
        return
    if o[status] != open
        bot.answer_callback_query(c.
id, fНельзя принять заказ, статус {o['status']})
        return
    o[model_id] = uid
    o[status] = assigned
    bot.answer_callback_query(c.id, fВы приняли заказ #{oid}. Менеджер уведомлён.)
    # уведомить менеджера
    try
        bot.send_message(o[manager_id], fМодель @{c.from_user.username} приняла ваш заказ #{oid}. Для связи используйте бота.)
    except
        pass
    bot.send_message(uid, fВы назначены на заказ #{oid}. Для общения с менеджером используйте 'msg {oid} ТЕКСТ'.)

# ----- Детали заказа -----
@bot.callback_query_handler(func=lambda c c.data and c.data.startswith(detail_))
def detail_order(c)
    oid = int(c.data.split(_,1)[1])
    o = get_order_by_id(oid)
    if not o
        bot.answer_callback_query(c.id, Заказ не найден.)
        return
    txt = (f--- Детали заказа #{o['id']} ---n
           fГород {o['city']}nДатаВремя {o['time']}nДлительность {o['duration']} минn
           fСумма {o['total_amount']}nМодель получает {o['model_amount']}nПроцент менеджера {o['manager_pct']}n
           fТребования {o['requirements']}nСтатус {o['status']}nКод {o['offer_code']})
    bot.send_message(c.from_user.id, txt)

# ----- Команда для общения через бота msg order_id text -----
@bot.message_handler(func=lambda m m.text and m.text.lower().startswith(msg ))
def relay_message(m)
    parts = m.text.split(maxsplit=2)
    if len(parts)  3
        bot.send_message(m.chat.id, Использование msg order_id текст)
        return
    oid = int(parts[1])
    text = parts[2]
    o = get_order_by_id(oid)
    if not o
        bot.send_message(m.chat.id, Заказ не найден.)
        return
    sender = m.from_user.id
    # определяем получателя
    if sender == o[manager_id]
        # отправляем модели (если назначена)
        if not o[model_id]
            bot.send_message(sender, Модель ещё не назначена.)
            return
        try
            bot.send_message(o[model_id], fСообщение от менеджера (order {oid})n{text})
            bot.send_message(sender, Сообщение отправлено модели.)
        except
            bot.send_message(sender, Не удалось отправить сообщение модели.)
    elif sender == o.get(model_id)
        # отправляем менеджеру
        try
            bot.send_message(o[manager_id], fСообщение от модели @{m.from_user.username} (order {oid})n{text})
            bot.send_message(sender, Сообщение отправлено менеджеру.)
        except
            bot.send_message(sender, Не удалось отправить сообщение менеджеру.)
    else
        bot.send_message(sender, Вы не участник этого заказа и не можете отправлять сообщения по нему.)

# ----- Запуск бота -----
if name == __main__
    print(Bot started)
    bot.infinity_polling()
