    # !/usr/bin/python
# -*- coding: utf8 -*-
import telebot
import config
from bs4 import BeautifulSoup
import requests as req
import os
import subprocess
import pandas as pd
import shutil

from threading import Thread


def upd():
    url = 'http://wikimipt.org/index.php?title=%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%9F%D1%80%D0%B5%D0%BF%D0%BE%D0%B4%D0%B0%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D0%B8_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D0%B8%D1%82%D1%83&from=%D0%91'
    main_resp = req.get(url)
    try:
        os.remove('card_database_upd.csv')
    except FileNotFoundError:
        pass
    g = open('card_database_upd.txt', 'a')
    g.write("name| department| Expert_level| Instructor_level| Comm_level| Freebie_level\n")
    g.close()
    main_soup = BeautifulSoup(main_resp.text, 'lxml')
    lib = main_soup.find_all(class_="external text")
    list_lib = list()
    for i in lib:
        list_lib.append(i['href'])
    for i in range(1, len(list_lib)):
        parse_page(str(list_lib[i]))
    try:
        my_file = 'card_database_upd.txt'
        base = os.path.splitext(my_file)[0]
        os.rename(my_file, base + '.csv')
    except FileExistsError:
        pass


class ThreadingUPD(object):
    flag = True

    def __init__(self, interval=1):
        self.interval = interval
        thread = Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        upd()
        shutil.copy(r'card_database_upd.csv', r'card_database.csv')


thread_upd = ThreadingUPD()

bot = telebot.TeleBot(config.TOKEN)
base = object


@bot.message_handler(commands=['update'])
def update_base(message):
    thread_upd.run()
    pass


@bot.message_handler(commands=['start', 'help'])
def send_start(message):
    bot.send_message(message.chat.id,
                     "Напиши ФИО препода в формате --- --- ---,\n я выведу информацию о нём,\n стартуем командой /prep")


def Insert_Unit(url, N):
    resp = req.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    name = soup.find('h1', id='firstHeading')
    dep = soup.find('li')
    param = soup.find_all('span', class_='starrating-avg')
    image_param = soup.find_all('tr')
    links = list()
    for i in image_param:
        links.append(i)

    global_values = list()
    global_name = str()
    global_departament = str()

    for i in name:
        global_name = str(i)

    if global_name[0] == N:
        mask = str()

        for i in dep:
            for j in i:
                tit = str(j.title()).strip()
                mask += tit

        global_departament = mask

        for attr in param:
            for i in attr:
                str_exc = str("( нет голосов )")
                if str(i) != str_exc:
                    global_values.append(str(i).split(' (')[0])
                else:
                    return False
        g = open('card_database_upd.txt', 'a')
        for i in name:
            g.write(global_name + "| ")
        g.write(global_departament + "| ")
        for i in range(len(global_values) - 1):
            g.write(global_values[i])
            if i != len(global_values) - 2:
                g.write('| ')
        g.write('\n')
        g.close()
        # download_image(links[1])
    else:
        return -3


def download_image(site):
    try:
        if str(site).split('"')[13][-3:len(str(site).split('"')[13])] != 'gif':
            link = str(site).split('"')[13]
            link = "http://wikimipt.org" + link + ""
            cmd = ['wget', link]
            subprocess.Popen(cmd).communicate()
    except IndexError:
        pass


def parse_page(url):
    resp_global = req.get(url)
    soup_global = BeautifulSoup(resp_global.text, 'lxml')
    lib_names = soup_global.find(class_='mw-category').find_all('li')
    links = list()
    for i in lib_names:
        for j in i:
            links.append((str(j).split('"')[1]))
    N = url[-1]
    k = 1
    for i in range(2, len(links)):
        s = str(links[i])
        if not s.startswith('H'):
            s = "http://wikimipt.org" + s + ""
            k += 1
            if Insert_Unit(s, N) == -3:
                return True


@bot.message_handler(commands=['prep'])
def send_prep(message):
    global base
    file = open('card_database.csv', encoding='windows-1251')
    base = pd.read_csv(file, sep='|')
    m = bot.send_message(message.chat.id, "Введите ФИО препода")
    bot.register_next_step_handler(m, set_prep)


# ok
def set_prep(message):
    global base
    if not (base.loc[base['name'].str.find(message.text) != -1]).empty:
        bot.send_message(message.chat.id, base.loc[base['name'].str.find(message.text) != -1].T.to_string())
    else:
        bot.send_message(message.chat.id, "Неправильное имя препода, попробуйте ещё раз.")


# RUN
bot.polling(none_stop=True)
