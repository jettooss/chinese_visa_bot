import os
import time

from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import telebot

from piccha import start, Login
from additional_functions import connect_to_mysql, check_info_values

TOKEN = "6354582076:AAG9klTTcmIiCtHuRI48t8XcV4bWrC0g0xs"

bot = telebot.TeleBot(TOKEN)


def parse_data():
    id_html = 0
    while True:
        connection, cursor = connect_to_mysql()
        cursor.execute("SELECT * FROM users where active =1")

        # Получение результатов SQL-запроса
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        # print(results)
        # Вывод результатов
        for row in results:
            user_id = row[0]
            fio = row[1]
            city_name = row[6]

            for popitka in range(3):
                # Получение результатов SQL-запроса
                print(f"Проверка {fio}  ")

                try:
                    city, driver = start()

                    print(city_name)
                    time.sleep(5)
                    if city_name in city:
                        index = city.index(city_name)
                        xpath = f' / html / body / div[2] / div[1] / div[1] / ul / li[2] / div[11] / ul / li[{index + 1}]'
                        s = driver.find_element("xpath", xpath)
                        s.click()
                    button = driver.find_element("xpath", '// *[ @ id = "first-info"] / div[2] / div / button').click()
                    authorization = Login(driver)
                    time.sleep(3)

                    time.sleep(3)
                    authorization.login_main(row[1], row[2], row[3], row[4])
                    time.sleep(13)

                    driver = authorization.driver

                    element = driver.find_elements("xpath", '/ html / body / div[4] / div[1]')
                    if element != []:
                        bot.send_message(
                            row[0],
                            "МЕСТА ЕСТЬ!!! ")

                    os.makedirs('./important_information/', exist_ok=True)
                    page_source = driver.page_source

                    with open(f'important_information/saved_page{id_html}.html', "w", encoding="utf-8") as file:
                        file.write(page_source)
                    id_html += 1
                except:
                    print("ошибка_1")

                try:
                    element = WebDriverWait(driver, 30).until(ec.presence_of_element_located(
                        (By.XPATH, "/html/body/div[1]/div/table/tbody/tr[2]/td[2]/div/table/tbody/tr[2]/td[2]/div")))
                    # фун check_info_values находится в additional_functions . Функция check_info_values принимает элемент в качестве входного параметра и проверяет его текстовое значение на соответствие различным условиям.

                    reply__user = check_info_values(element)

                    element1 = WebDriverWait(driver, 30).until(ec.presence_of_element_located(
                        (By.XPATH, "/ html / body / div[4] / form / div[3] / div[2] / div[4] / div[1] / span")))

                    #         / html / body / div[4] / div[1] / div[2] / span
                    #         / html / body / div[4] / div[2] / div[1]
                    #         / html / body / div[4] / div[2]

                    reply__user1 = check_info_values(element1)

                    if reply__user == False:
                        cursor.execute(f"UPDATE users SET active=0 where FIO = '{row[1]}'")
                        connection.commit()

                        bot.send_message(
                            row[0],
                            "ID больше недействительное "
                        )
                    elif reply__user1 == True:
                        bot.send_message(
                            row[0],
                            "Вы забронировали номер "
                        )
                    elif reply__user == 2:
                        bot.send_message(
                            row[0],
                            "Проверка....,мест пока нет "
                        )

                    elif reply__user == 3:
                        cursor.execute(f"UPDATE users SET active=0 where FIO = '{row[1]}'")
                        connection.commit()
                        bot.send_message(
                            row[0],
                            "данные устарели или неправильные "
                        )
                    elif reply__user == 4:
                        bot.send_message(row[0], "вы зарегистрированы уже")
                        cursor.execute(f"UPDATE users SET active=0 where FIO = '{row[1]}'")
                        connection.commit()

                    else:
                        page_source = driver.page_source
                        os.makedirs('./html_path/', exist_ok=True)

                        with open(f'html_path/saved_page{id_html}.html', "w", encoding="utf-8") as file:
                            file.write(page_source)
                        id_html += 1
                        bot.send_message(
                            row[0],
                            reply__user
                        )
                    driver.quit()
                except:
                           print("ошибка_2")
            cursor.close()
            connection.close()


            time.sleep(240)

# parse_data()
