import mysql
import sqlite3


from mysql.connector import Error
def check_info_values(element):



    if element.text.startswith("You have already scheduled a visa appointment with this Application ID"):
        # return f"Вы уже записались на прием для получения визы с помощью этого id "
        return 4

    elif element.text == "The visa authority you choose does not correspond with the one you've selected when filling the COVA form. Please check.":
         # return "Выбранный вами город выдачи визы не соответствует тому, который вы выбрали при заполнении формы"
         return 3
    elif element.text=="Invalid application ID. Please check if you have entered the correct one.":
        return 3

    elif element.text == "You have already scheduled a visa appointment with this Application ID":
        # return "ID больше недействительное"
        return False
    elif element.text =="The maximum number of people making appointment at one time is 0. Please make change.":
        return 2
    elif element.text.startswith("You have booked"):
        return True
    else:
        return "    "


def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            database='bot',
            user='root',
            password='0808'
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print("Подключено к серверу MySQL версии ", db_info)
            cursor = connection.cursor()

            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print("Вы подключены к базе данных: ", record)
        return connection,cursor

    except mysql.connector.Error as e:
        print("Ошибка при подключении к MySQL: ", e)
        return None
