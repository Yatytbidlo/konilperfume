import telebot
import mysql.connector
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests

# Токен Telegram бота
token = "7147082487:AAEmEkwViX_PsW-2_Rz5U6arDNE6H-S2v7I"
bot = telebot.TeleBot(token)

try:
    bot_info = bot.get_me()
    print(f"Бот успешно авторизован: {bot_info}")
except Exception as e:
    print(f"Ошибка авторизации бота: {e}")

# Конфигурация базы данных
db_config = {
    'host': 'localhost',
    'user': 'root',
    'database': 'konil',
    'password': '',
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    print("Успешное подключение к базе данных")   
except mysql.connector.Error as err:
    print(f"Ошибка подключения к базе данных: {err}")

# Словарь для хранения состояния пользователей
user_states = {}

# Функция для получения состояния пользователя
def get_user_state(user_id):
    return user_states.get(user_id, [])

# Функция для установки состояния пользователя
def set_user_state(user_id, state):
    user_states[user_id] = state

def is_url_accessible(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Ошибка при проверке URL: {e}")
        return False

# Кнопки меню
buttons_menu = InlineKeyboardMarkup()
buttons_menu.row_width = 1
buttons_menu.add(InlineKeyboardButton("Поиск по духам", callback_data="search"),
                 InlineKeyboardButton("Подобрать парфюм c помощью ИИ", callback_data="AI"),
                 InlineKeyboardButton("Комбо предложения", callback_data="kombo"),
                 InlineKeyboardButton("О компании", callback_data="about"))

# Кнопки поиска по духам
buttons_search = InlineKeyboardMarkup()
buttons_search.row_width = 2
buttons_search.add(InlineKeyboardButton("По названию", callback_data="name"),
                   InlineKeyboardButton("По ощущениям", callback_data="feelings"),
                   InlineKeyboardButton("По мотиву", callback_data="motive"))

# Кнопки о компании
buttons_about = InlineKeyboardMarkup()
buttons_about.row_width = 1
buttons_about.add(InlineKeyboardButton("Контакты", callback_data="contacts"),
                  InlineKeyboardButton("Сертификат", callback_data="certificates"),
                  InlineKeyboardButton("Условия доставки", callback_data="delivery"))

# Добавление кнопки "Назад"
def add_back_button(buttons, callback_data):
    if not any(button.callback_data == callback_data for row in buttons.keyboard for button in row):
        buttons.add(InlineKeyboardButton("Назад", callback_data=callback_data))

about_text = "Добро пожаловать в нашего телеграм-бота, который поможет вам открыть новые ароматические горизонты. Здесь вы сможете узнать о наших последних коллекциях, получить рекомендации по подбору идеального аромата, а также узнать о специальных предложениях и акциях. Для нас парфюмерия - это искусство, и мы стремимся подарить вам неповторимые впечатления с помощью наших уникальных композиций. Будьте в курсе последних трендов, узнавайте первыми о новинках и наслаждайтесь каждой нотой, которую мы тщательно подбираем. Не стесняйтесь обращаться к нам с любыми вопросами или запросами. Мы всегда здесь, чтобы помочь вам найти тот самый аромат, который отражает вашу индивидуальность и подчеркивает вашу уникальность. Спасибо, что выбрали компанию Konil Perfume. Давайте вместе откроем мир чувственных ароматов!"


@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f"Получена команда /start от {message.chat.id}")
    set_user_state(message.chat.id, ['menu'])
    bot.send_message(message.chat.id, f"Здравствуйте! Рады приветствовать вас {message.chat.username} в мире парфюмерии от компании Konil Perfume!", reply_markup=buttons_menu)

@bot.message_handler(commands=['menu'])
def send_meassage(message):
    print(f"Получена команда /menu от {message.chat.id}")
    set_user_state(message.chat.id, ['menu'])
    bot.send_message(message.chat.id, "Выбирайте то что подходит именно вам!", reply_markup=buttons_menu)

# Функция для выполнения запросов к базе данных
def get_data_from_db(column_name):
    try:
        cursor.execute(f"SELECT DISTINCT {column_name} FROM parfumes")
        results = cursor.fetchall()
        print(f"Данные из колонки {column_name}: {results}")  # Отладочное сообщение
        return [row[column_name].strip() for row in results]
    except mysql.connector.Error as err:
        print(f"Ошибка выполнения запроса: {err}")
        return []

# Функция для получения полной информации о продукте по указанной колонке и значению
def get_product_info(column_name, value):
    try:
        query = f"SELECT * FROM parfumes WHERE {column_name} = %s"
        cursor.execute(query, (value,))
        result = cursor.fetchone()
        print(f"Результат запроса для {column_name} = {value}: {result}")  # Отладочное сообщение
        return result
    except mysql.connector.Error as err:
        print(f"Ошибка выполнения запроса: {err}")
        return None

def get_parfumes_from_kombo(category):
    try:
        query = "SELECT parfume FROM kombo WHERE name = %s"
        cursor.execute(query, (category,))
        results = cursor.fetchall()
        print(f"Духи для категории {category}: {results}")  # Отладочное сообщение
        return [row['parfume'].strip() for row in results]
    except mysql.connector.Error as err:
        print(f"Ошибка выполнения запроса: {err}")
        return []

# Обработчик callback_query
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    print(f"Callback data: {call.data}")  # Отладочное сообщение
    user_state = get_user_state(call.from_user.id)

    if call.data == "back":
        if user_state:
            user_state.pop()  # Удаляем последнее состояние
            set_user_state(call.from_user.id, user_state)
            previous_state = user_state[-1] if user_state else 'menu'
            if previous_state == 'menu':
                bot.send_message(call.from_user.id, "Выбирайте то что подходит именно вам!", reply_markup=buttons_menu)
            elif previous_state == 'search':
                bot.send_message(call.from_user.id, "Поиск по духам:", reply_markup=buttons_search)
            elif previous_state == 'about':
                bot.send_message(call.from_user.id, about_text, reply_markup=buttons_about)
            elif previous_state == 'kombo':
                buttons_kombo = InlineKeyboardMarkup()
                buttons_kombo.row_width = 1
                buttons_kombo.add(
                    InlineKeyboardButton("Цитрус", callback_data="kombo_citrus"),
                    InlineKeyboardButton("Океан", callback_data="kombo_ocean"),
                    InlineKeyboardButton("Оазис", callback_data="kombo_oasis")
                )
                add_back_button(buttons_kombo, "back")
                bot.send_message(call.from_user.id, "Выберите категорию:", reply_markup=buttons_kombo)
        else:
            bot.send_message(call.from_user.id, "Вы находитесь в главном меню.", reply_markup=buttons_menu)

    elif call.data == "search":
        user_state.append("search")
        set_user_state(call.from_user.id, user_state)
        add_back_button(buttons_search, "back")
        bot.send_message(call.from_user.id, "Поиск по духам:", reply_markup=buttons_search)

    elif call.data == "AI":
        bot.answer_callback_query(call.id, text='Эта функция еще в разработке.', show_alert=True)

    elif call.data == "kombo":
        # Кнопки для категорий комбо предложений
        buttons_kombo = InlineKeyboardMarkup()
        buttons_kombo.row_width = 1
        buttons_kombo.add(
            InlineKeyboardButton("Цитрус", callback_data="kombo_citrus"),
            InlineKeyboardButton("Океан", callback_data="kombo_ocean"),
            InlineKeyboardButton("Оазис", callback_data="kombo_oasis")
        )
        add_back_button(buttons_kombo, "back")
        user_state.append("kombo")
        set_user_state(call.from_user.id, user_state)
        bot.send_message(call.from_user.id, "Выберите категорию:", reply_markup=buttons_kombo)

    elif call.data == "about":
        user_state.append("about")
        set_user_state(call.from_user.id, user_state)
        add_back_button(buttons_about, "back")
        bot.send_message(call.from_user.id, about_text, reply_markup=buttons_about)

    elif call.data == "contacts":
        phone_number = "+7 707 601 7555"
        bot.answer_callback_query(call.id, text=f"Номер телефона скопирован: {phone_number}", show_alert=True)

    elif call.data == "certificates":
        certificate = "https://i.postimg.cc/25zW8qTC/certificate.jpg"
        bot.send_photo(call.from_user.id, photo=certificate, caption="Сертификат о подтверждение оригинальности")

    elif call.data == "delivery":
        user_state.append("delivery")
        set_user_state(call.from_user.id, user_state)
        add_back_button(buttons_about, "back")
        bot.send_message(call.from_user.id, "Доставка бесплатная. Отправка товара начинается после заполнения всех полей в форме. Доставка приходит в день заказа не позже 5 часов вечера. Если заказ после 5 вечера, то переносится на следующий день. С понедельника по субботу!", reply_markup=buttons_about)

    elif call.data in ["name", "feelings", "motive"]:
        column_map = {
            "name": "name",
            "feelings": "accociation",
            "motive": "similar"
        }
        column_name = column_map[call.data]
        data = get_data_from_db(column_name)

        if data:
            buttons = InlineKeyboardMarkup(row_width=1)
            for item in data:
                callback_data = f"{call.data}_{item[:21]}".replace(' ', '_').replace('.', '')
                buttons.add(InlineKeyboardButton(item, callback_data=callback_data))
            add_back_button(buttons, "back")
            bot.send_message(call.from_user.id, "Выберите опцию:", reply_markup=buttons)
        else:
            bot.send_message(call.from_user.id, "Извините, данные не найдены.")

    elif call.data.startswith("kombo_"):
        category = call.data.split("_")[1]
        parfumes = get_parfumes_from_kombo(category)

        if parfumes:
            buttons_parfumes = InlineKeyboardMarkup()
            buttons_parfumes.row_width = 1
            for parfume in parfumes:
                callback_data = f"name_{parfume[:21]}".replace(' ', '_').replace('.', '')
                buttons_parfumes.add(InlineKeyboardButton(parfume, callback_data=callback_data))
            add_back_button(buttons_parfumes, "back")
            user_state.append("kombo")
            set_user_state(call.from_user.id, user_state)
            bot.send_message(call.from_user.id, "Выберите духи:", reply_markup=buttons_parfumes)
        else:
            bot.send_message(call.from_user.id, "Извините, духи не найдены.")

    else:
        if call.data.startswith("name_"):
            column_name = "name"
            value = call.data[5:].replace('_', ' ')
        elif call.data.startswith("feelings_"):
            column_name = "accociation"
            value = call.data[9:].replace('_', ' ')
        elif call.data.startswith("motive_"):
            column_name = "similar"
            value = call.data[7:].replace('_', ' ')
        else:
            bot.answer_callback_query(call.id, text="Неверный запрос", show_alert=True)
            return

        product_info = get_product_info(column_name, value)

        if product_info:
            info_text = (f"Название: {product_info['name']}\n"
                         f"Тип: {product_info['type']}\n"
                         f"Верхние ноты: {product_info['top_notes']}\n"
                         f"Средние ноты: {product_info['medium_notes']}\n"
                         f"Базовые ноты: {product_info['main_notes']}\n"
                         f"Сезон: {product_info['season']}\n"
                         f"Время суток: {product_info['day_night']}\n"
                         f"Ассоциации: {product_info['accociation']}\n"
                         f"Стиль: {product_info['style']}\n"
                         f"Похожие: {product_info['similar']}\n"
                         f"5 мл: {product_info['five_ml']} тг\n"
                         f"10 мл: {product_info['ten_ml']} тг\n"
                         f"30 мл: {product_info['thirty_ml']} тг\n"
                         f"50 мл: {product_info['fifty_ml']} тг")
            user_state.append("product_info")
            set_user_state(call.from_user.id, user_state)
            buttons_info = InlineKeyboardMarkup(row_width=1)
            add_back_button(buttons_info, "back")

            if product_info['image'] and is_url_accessible(product_info['image']):
                bot.send_photo(call.from_user.id, photo=product_info['image'], caption=info_text, reply_markup=buttons_info)
            else:
                bot.send_message(call.from_user.id, info_text, reply_markup=buttons_info)
        else:
            bot.answer_callback_query(call.id, text="Информация о продукте не найдена", show_alert=True)

bot.polling(none_stop=True)
