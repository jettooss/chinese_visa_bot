import re
import threading

import requests
import telebot
from additional_functions import connect_to_mysql, check_info_values
from telebot import types
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import piccha
from parsers import parse_data

TOKEN = ""

bot = telebot.TeleBot(TOKEN)
# connection, cursor = connect_to_mysql()
start_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
start_markup.add(types.KeyboardButton('Добавить аккаунт'), types.KeyboardButton('Просмотр заявок'), types.KeyboardButton('Узнать о боте'))

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    itembtn1 = telebot.types.KeyboardButton('Добавить аккаунт')
    itembtn2 = telebot.types.KeyboardButton('Просмотр заявок')

    itembtn3 = telebot.types.KeyboardButton('Узнать о боте')
    markup.add(itembtn1,itembtn2, itembtn3)

    bot.send_message(
        message.chat.id,
        "Привет! Чем я могу тебе помочь?",
        reply_markup=markup
    )


@bot.message_handler(commands=['addinfo'])
def add_info(message):
    bot.send_message(message.chat.id, "Давайте начнем: введите ваше полное имя. Например, Ivanov Ivan Ivanovich.")
    bot.register_next_step_handler(message, full_name_handler)


def full_name_handler(message):
    full_name = message.text
    print(message.chat.id)
    # Проверка на корректность имени
    if not re.match(r"^[A-Za-z\s]+$", full_name):
        bot.send_message(message.chat.id,
                         "Некорректное имя. Имя должно содержать только английские буквы. Пожалуйста, введите корректное имя.")
        return

    bot.send_message(message.chat.id, "Введите номер телефона")
    bot.register_next_step_handler(message, phone_number_handler, full_name)


def phone_number_handler(message, full_name):
    phone_number = message.text

    # Проверка правильности формата номера телефона с помощью регулярного выражения
    pattern = r'^\+?[1-9]\d{1,10}$'  # Пример паттерна для проверки формата
    if not re.match(pattern, phone_number):
        bot.send_message(message.chat.id, "Неправильный формат номера телефона. Попробуйте еще раз.")
        return

    bot.send_message(message.chat.id, "Введите адрес электронной почты")
    bot.register_next_step_handler(message, email_handler, full_name, phone_number)


def email_handler(message, full_name, phone_number):
    email = message.text

    # Проверка на корректность email адреса
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        bot.send_message(message.chat.id, "Некорректный email адрес. Пожалуйста, введите корректный email адрес.")
        return

    bot.send_message(message.chat.id, "Пожалуйста, введите номер(а) визы. Учтите, что количество виз не должно превышать шести. Если у вас есть более одной визы, пожалуйста, введите номера, разделяя их пробелом. Например, 54545454302 424234234 5425252. Спасибо!")


    bot.register_next_step_handler(message, visa_id_handler, full_name, phone_number, email)


def visa_id_handler(message, full_name, phone_number, email):
    visa_id = message.text
    city, driver = piccha.start()
    id = visa_id.split()
    num_visa = len(id)
    print(city)

    if num_visa < 6:
        keyboard = types.ReplyKeyboardMarkup(row_width=2)
        for city_name in city:
            if city_name not in ['MOSCOW', 'ST.PETERSBURG']:
                keyboard.add(types.KeyboardButton(city_name))
        keyboard.add(types.KeyboardButton("Вернуться"))

        bot.send_message(message.chat.id, "Выберите город:", reply_markup=keyboard)
        bot.register_next_step_handler(message, end, driver, city, full_name, phone_number, email, visa_id)
    else:
        bot.send_message(message.chat.id, "id < 6")


def end(message, driver, city, full_name, phone_number, email, visa_id):
    connection, cursor = connect_to_mysql()
    bot.send_message(message.chat.id, text="Выберите одну из опций:", reply_markup=start_markup)

    if message.text in city:
        xpath = f'//*[@id="RUS"]/li[contains(text(), "{message.text}")]'
        driver.find_element("xpath", xpath).click()  # нажимает на нужный город
        button = driver.find_element("xpath", '// *[ @ id = "first-info"] / div[2] / div / button').click()
        try:
            authorization = piccha.Login(driver)
            authorization.login_main(full_name, phone_number, email, visa_id)
            driver = authorization.driver
            driver.quit()
            # обновляем  driver,это нужно для того,чтобы фрейм обновился
            element = WebDriverWait(driver, 20).until(ec.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div/table/tbody/tr[2]/td[2]/div/table/tbody/tr[2]/td[2]/div")))
            # фун check_info_values находится в additional_functions . Функция check_info_values принимает элемент в качестве входного параметра и проверяет его текстовое значение на соответствие различным условиям.
            reply__user = check_info_values(element)
            print("Пользователь ввел данные в бота ", message.chat.id, full_name, phone_number, email, 1, message.text)

            driver.quit()

            if reply__user == 2:
                bot.send_message(message.chat.id,
                                 "Мы сожалеем, но на данный момент нет доступных мест. Однако, будем рады сообщить Вам, как только появится возможность. ")
                # try:
                try:
                    sql = "INSERT INTO users (id, FIO, phone_number, email, visa_id, active, city) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    values = (message.chat.id, full_name, phone_number, email, 1, message.text)
                    cursor.execute(sql, values)
                    connection.commit()

                except Exception as e:
                    print("Ошибка при выполнении запроса:", e)

                bot.send_message(message.chat.id, "Информация успешно добавлена в базу данных")

            elif reply__user == 3:

                bot.send_message(message.chat.id, "данные неправильные")
                print(f"данные были неправильные :{full_name}")

            elif reply__user == 4:
                bot.send_message(message.chat.id, "вы зарегистрированы уже")


        except:
            sql = "INSERT INTO users (id, FIO, phone_number, email, visa_id, active, city) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (message.chat.id, full_name, phone_number, email,visa_id, 1, message.text)
            cursor.execute(sql, values)
            connection.commit()

            bot.send_message(message.chat.id, "ваши данные сохранены,но непроверенны.Ожидайте ")


@bot.message_handler(commands=['getinfo'])
def get_info(message):
    connection, cursor = connect_to_mysql()

    bot.send_message(
        message.chat.id,
        "Информация из базы данных...",
    )

    # Выполнение SQL-запроса
    cursor.execute("SELECT * FROM users")

    # Получение результатов SQL-запроса
    results = cursor.fetchall()

    # Вывод результатов
    for row in results:
        user_id = row[0]
        fio = row[1]
        phone_number = row[2]
        email = row[3]
        visa_id = row[4]
        active = row[5]
        user_info = f"ID: {user_id}\nFIO: {fio}\nPhone Number: {phone_number}\nEmail: {email}\nVisa ID: {visa_id}\nStatus: {'действительный аккаунт' if active == 1 else 'недействительный аккаунт'}"

        markup = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton('Удалить', callback_data=f'delete_{fio}')
        markup.add(item)

        bot.send_message(
            message.chat.id,
            user_info,
            reply_markup=markup
        )
        cursor.close()
        connection.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith(f'delete_'))
def handle_delete_button(call):
    connection, cursor = connect_to_mysql()

    fio = call.data.split('_')[1]
    print(fio)
    query = "DELETE FROM users WHERE fio = %s"
    cursor.execute(query, (fio,))
    connection.commit()

    cursor.close()
    connection.close()
    bot.answer_callback_query(call.id, text='Пользователь успешно удален')

#         / html / body / div[4] / div[1] / div[2] / span
#         / html / body / div[4] / div[2] / div[1]
#         / html / body / div[4] / div[2]

@bot.message_handler(commands=['info'])
def reset(message):
    bot.send_message(
        message.chat.id,
        "Добро пожаловать в бота!\n\n"
        "Вы можете использовать следующие команды:\n\n"
        "- `/start` - начать работу с ботом или вернуться в главное меню.\n"
        "- `/getinfo` - просмотреть информацию о пользователях.\n"
        "- `/addinfo` - добавить информацию о пользователе.\n\n"
        "В главном меню вы также можете выбрать следующие опции:\n\n"
        "- 'Узнать о боте' для получения информации о боте и его возможностях.\n"
        "- 'Добавить аккаунт' для добавления информации о новом пользователе.\n"
        "- 'Просмотр заявок' для просмотра информации о пользователях (доступно только для администраторов).\n"
        "- 'Вернуться' для возврата в главное меню.\n\n"
        "Если у вас есть какие-либо вопросы или вам нужна помощь, пожалуйста, обратитесь к администратору бота.\n\n"
        "Хорошего использования!"
    )


def check_user_in_db(user_id):
    connection, cursor = connect_to_mysql()

    print("Пользователь выполняет действия", user_id)  # id  пользователя
    # connection, cursor = connect_to_sqlite()

    # Выполнение SQL-запроса
    cursor.execute(f"SELECT * FROM authorization where id={user_id}")
    results = cursor.fetchall()

    cursor.close()
    connection.close()
    try:
        if user_id in results[0]:
            return True
        else:
            return False
    except:
        print("Нет данных")


def admin_function(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1)
    keyboard.add(telebot.types.KeyboardButton('Просмотр заявок'))
    keyboard.add(telebot.types.KeyboardButton('Добавить доступ'))
    keyboard.add(telebot.types.KeyboardButton('Вернуться'))
    bot.send_message(
        message.chat.id,
        "Вы используете админ функцию. Пожалуйста, выберите одну из доступных опций:",
        reply_markup=keyboard
    )


def add_user_access(message):
    bot.send_message(message.chat.id, " id пользователя  ")
    bot.register_next_step_handler(message, add_id)


def add_id(message):
    if re.match(r'^\d{1,11}$', message.text):
        id = message.text
        bot.send_message(message.chat.id, " имя ")
        bot.register_next_step_handler(message, add_end, id)


    else:
        bot.send_message(message.chat.id, "ID пользователя должно состоять из 1-11 цифр. Попробуйте еще раз.")


def add_end(message, id):
    connection, cursor = connect_to_mysql()

    name = message.text

    cursor.execute(
        "INSERT INTO authorization (id, name, admin) VALUES (%s, %s, %s)",
        (id, name, 0))
    connection.commit()

    print("Добавлен:", id, name, 0)

    bot.send_message(message.chat.id, f"{name} добавлен ")


def start_bot():
    # 1. @ bot.message_handler(func=lambda message: True) - это декоратор, который указывает, чтофункция
    # handle_message()будет обрабатывать все сообщения.
    # 2.
    # фун check_info_values находится в additional_functions . Функция check_info_values принимает элемент в качестве входного параметра и проверяет его текстовое значение на соответствие различным условиям.
    #
    # 3.
    # 'Начать', 'Добавить информацию', 'Получить информацию', 'Вернуться', 'Добавить доступ' - это
    # команды, которые ваш бот будет распознавать и вызывать соответствующие  функции для  их обработки.
    #
    # 4.
    # reset(message), add_info(message), get_info(message), start(message), admin_function(message), add_user_access(
    #     message) - это
    # функции, которые  будуn  вызываться для обработки соответствующих  команд.

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        connection, cursor = connect_to_mysql()
        if check_user_in_db(message.from_user.id):

            if message.text == 'Узнать о боте':
                reset(message)
            elif message.text == 'Добавить аккаунт':
                add_info(message)
            elif message.text == 'Просмотр заявок':
                # connection, cursor = connect_to_mysql()
                user_id = message.from_user.id
                cursor.execute(f"SELECT * FROM authorization where id={user_id}")
                results = cursor.fetchall()
                if results[0][2] == 1:
                    get_info(message)

                elif results[0][2] == 0:
                    bot.send_message(
                        message.chat.id,
                        f"отказано в доступе "
                    )

            elif message.text == 'Вернуться':

                start(message)
            elif message.text == '/admin':
                admin_function(message)

            elif message.text == 'Добавить доступ':
                # connection, cursor = connect_to_mysql()
                user_id = message.from_user.id
                cursor.execute(f"SELECT * FROM authorization where id={user_id}")
                results = cursor.fetchall()
                if results[0][2] == 1:
                    add_user_access(message)
                else:
                    bot.send_message(
                        message.chat.id,
                        f"отказано в доступе "
                    )
            else:
                bot.send_message(
                    message.chat.id,
                    "Я не понимаю вашего запроса. Пожалуйста, выберите команду из командного меню."
                )
        else:
            bot.send_message(
                message.chat.id,
                f"отказано в доступе,сообщите администратору свой id:{message.from_user.id} "
            )



    bot.polling()


# start_bot()
bot_thread = threading.Thread(target=start_bot)
parser_thread = threading.Thread(target=parse_data)

bot_thread.start()
parser_thread.start()

bot_thread.join()
parser_thread.join()
