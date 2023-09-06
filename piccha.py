import numpy as np
import random
from selenium.webdriver import ActionChains
import time

from PIL import Image
import os
from selenium.webdriver.support.ui import WebDriverWait
import cv2
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


class Login(object):

    def __init__(self, driver):
        self.driver = driver

    @staticmethod
    def show(name):
        cv2.imshow('Show', name)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def webdriverwait_send_keys(dri, element, value):

        WebDriverWait(dri, 10, 5).until(lambda dr: element).send_keys(value)

    @staticmethod
    def webdriverwait_click(dri, element):

        WebDriverWait(dri, 10, 5).until(lambda dr: element).click()

    @staticmethod
    def get_postion(chunk, canves):

        otemp = chunk
        oblk = canves
        target = cv2.imread(otemp, 0)
        template = cv2.imread(oblk, 0)

        template = template[500:600, 150:250]
        w, h = template.shape[::-1]
        temp = 'temp.jpg'
        targ = 'targ.jpg'
        cv2.imwrite(temp, template)
        cv2.imwrite(targ, target)
        target = cv2.imread(targ)
        target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        target = abs(255 - target)
        cv2.imwrite(targ, target)
        target = cv2.imread(targ)
        template = cv2.imread(temp)
        # приколы
        target = cv2.Canny(target, 400, 400)
        template = cv2.Canny(template, 300, 300)

        result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        x1, y1 = max_loc
        x2, y2 = (x1 + w, y1 + h)
        cv2.rectangle(target, (x1, y1), (x2, y2), 255, 1)

        cv2.waitKey(0)

        x, y = np.unravel_index(result.argmax(), result.shape)
        return x, y

    @staticmethod
    def get_track(distance):

        # 初速度
        v = 0
        t = 0.2
        tracks = []
        current = 0
        mid = distance * 7 / 8

        distance += 10
        while current < distance:
            if current < mid:
                a = random.randint(2, 4)
            else:
                a = -random.randint(3, 5)

            v0 = v
            s = v0 * t + 0.5 * a * (t ** 2)
            current += s
            tracks.append(round(s))

            v = v0 + a * t

        for i in range(4):
            tracks.append(-random.randint(2, 3))
        for i in range(4):
            tracks.append(-random.randint(1, 3))
        return tracks

    @staticmethod
    def urllib_download(imgurl, imgsavepath):

        from urllib.request import urlretrieve
        # print(imgurl, imgsavepath)
        urlretrieve(imgurl, imgsavepath)

    def after_quit(self):

        self.driver.quit()

    def login_main(self, name, phone, mail, visa):
        # Эта функция login_main используется для авторизации на веб - сайте.
        # 1.Разбивает строку visa на отдельные  слова, используя пробел в  качестве разделителя.Это нужно  если id_viza будет несколько значении

        # 2. Находит элементы на странице по указанным  xPath и вводит значения для полей "name", "phone", "mail" и "visa".
        # 3 ломает пикчу
        # 4.Переключается на фрейм со специальным инструментом подтверждения, который
        # ищется
        # по
        # xPath: // *[ @ id = "tcaptcha_iframe_dy"]
        driver = self.driver
        words = visa.split()
        print("id viza:", words)
        num_visa = len(words)
        print(num_visa)
        time.sleep(3)

        xpath_name = "//*[@id=\"linkname\"]"
        driver.find_element("xpath", xpath_name).send_keys(name)

        xpath_phone_number = "/html/body/div[4]/form/div[2]/div[2]/div[2]/input"
        driver.find_element("xpath", xpath_phone_number).send_keys(phone)

        xpath_mail = "/html/body/div[4]/form/div[2]/div[2]/div[3]/input"
        driver.find_element("xpath", xpath_mail).send_keys(mail)
        if num_visa == 1: # если  только одна viza
            xpath_visa_number = "/html/body/div[4]/form/div[3]/div[2]/div[4]/div/input"
            driver.find_element("xpath", xpath_visa_number).send_keys(visa)
        else:
            for i in range(num_visa ):
                if i == 0:# если  2  viza


                    xpath_visa_number = "/html/body/div[4]/form/div[3]/div[2]/div[4]/ div[1] /input"
                    driver.find_element("xpath", xpath_visa_number).send_keys(words[i])
                else:  # если   viza >2
                    driver.find_element("xpath",
                                        f"/ html / body / div[4] / form / div[3] / div[2] / div[4] / div[{i}] / div[1] / span[2]").click()
                    time.sleep(3)

                    xpath_visa_number = f"/html/body/div[4]/form/div[3]/div[2]/div[4]/ div[{1 + i}] /input"
                    time.sleep(3)

                    driver.find_element("xpath", xpath_visa_number).send_keys(words[i])

        xpath_button = "/html/body/div[4]/form/div[4]/div/div[2]/button"
        driver.find_element("xpath", xpath_button).click()

        time.sleep(8)

        driver.switch_to.frame(driver.find_element("xpath", '//*[@id="tcaptcha_iframe_dy"]'))  # switch 到 滑块frame
        time.sleep(0.5)
        bk_block = driver.find_element("xpath", '//*[@id="slideBg"]')  # 大图
        web_image_width = bk_block.size
        web_image_width = web_image_width['width']
        bk_block_x = bk_block.location['x']

        try:
            slide_block = driver.find_element("xpath", '/html/body/div/div[3]/div[2]/div[8]')  # для локальной машины
        except:
            slide_block = driver.find_element("xpath",
                                              '/html/body/div/div[3]/div[2]/div[7]')  # для прокси,при смене ip,путь меняется
        slide_block_x = slide_block.location['x']
        pattern = r"\"\S+\""
        string = bk_block.get_attribute("style")
        string = re.search(pattern, string)[0]
        string = string[1:len(string) - 1]
        bk_block = string
        # print(bk_block)

        pattern = r"\"\S+\""
        string = slide_block.get_attribute("style")
        string = re.search(pattern, string)[0]
        string = string[1:len(string) - 1]
        slide_block = string

        slid_ing = driver.find_element("xpath", '/html/body/div/div[3]/div[2]/div[6]')
        os.makedirs('./image/', exist_ok=True)
        self.urllib_download(bk_block, './image/bkBlock.png')
        self.urllib_download(slide_block, './image/slideBlock.png')
        time.sleep(0.5)
        img_bkblock = Image.open('./image/bkBlock.png')
        real_width = img_bkblock.size[0]
        width_scale = float(real_width) / float(web_image_width)
        position = self.get_postion('./image/bkBlock.png', './image/slideBlock.png')
        real_position = position[1] / width_scale
        real_position = real_position - (slide_block_x - bk_block_x)
        track_list = self.get_track(real_position + 4)
        # real_position = (real_position+4)*7/8


        ActionChains(driver).click_and_hold(on_element=slid_ing).perform()
        time.sleep(0.2)
        ActionChains(driver).move_by_offset(xoffset=real_position, yoffset=0).perform()

        time.sleep(1)
        ActionChains(driver).release(on_element=slid_ing).perform()
        time.sleep(1)

        driver.switch_to.default_content()

        return driver


def start():
    urls = "https://avas.mfa.gov.cn/qzyyCoCommonController.do?yyindex&locale=en_US"
    driver = connect_proxy()

    # Откройте сайт
    driver.get(urls)
    city = []
    time.sleep(3)

    button = driver.find_element("xpath", '//*[@id="EU"]')
    button.click()
    time.sleep(3)

    elements = driver.find_elements("xpath", '//*[@id="RUS"]')# пойск Ru городов
    # print(elements)
    time.sleep(3)
    for element in elements:
        cities = element.text.split('\n')
        city.extend(cities)
    return city, driver


def connect_proxy():
    proxys = ["45.139.125.208:1050"]
    len_proxys = len(proxys)

    # for i in range(len_proxys):
    options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # options.add_argument("--disable-dev-shm-usage")
                #
                # if i > 0:
                #     proxy_server_url = proxys[i - 1]
                #     options.add_argument(f'--proxy-server={proxy_server_url}')
    driver = webdriver.Chrome( options=options)

    return driver
