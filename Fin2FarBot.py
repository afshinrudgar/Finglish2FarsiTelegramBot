#!/usr/bin/python2
# coding=utf-8
from __future__ import print_function, unicode_literals
import telebot
import requests
import enchant
import time
import urllib3
import certifi
import logging
import pickle
import re
import sys


reload(sys)
sys.setdefaultencoding("utf-8")

DATA = './data.p'

global data
try:
    data = pickle.load(open(DATA, 'rb'))
except IOError:
    data = {}


transliteration_set = set()

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',  # Force certificate check.
    ca_certs=certifi.where(),  # Path to the Certifi bundle.
)
urllib3.disable_warnings()

en_dict = enchant.Dict('en')
alphabet = set([i for i in 'abcdefghijklmnopqrstuvwxyz'])

logging.basicConfig(
    filename='Fin2FarBotLog.log', filemode='a', level=logging.INFO)

base_chat_id = None


def transliterate(text):
    words = set(re.findall('\w+', text))

    new_finglish = list(words.difference(data.keys()))

    print('new_finglish', new_finglish)

    if new_finglish:
        print("requesting for farsi")

        url = 'http://www.behnevis.com/php/convert.php'
        headers = {'Accept-Charset': 'UTF-8'}

        r = http.request(
            'POST',
            url,  # + 'farsi=salam&responsetime=-1&resulttype=json',
            fields={
                'farsi': ' '.join(new_finglish),
                # 'responsetime': -1
            },
            headers=headers
        )

        new_farsi = r.data.strip().split(' ')
        print(new_finglish)
        print(new_farsi)

        for i, j in zip(new_finglish, new_farsi):
            data[i] = j

    print(data)

    for word in words:
        text = re.sub(word, data[word], text)

    print('text', text)
    return text


def is_finglish(text):
    text = re.sub('\W+', ' ', text)
    s_t = text.split(' ')
    while '' in s_t:
        s_t.remove('')
    for i in range(min(3, len(s_t))):
        if not en_dict.check(s_t[i]) and alphabet.intersection(s_t[i]):
            return True
    return False


def listener(messages):
    """
        When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        chatid = m.chat.id
        if m.content_type == 'text':
            print("[%s] %s %s (%s), %s: %s" % (time.ctime(), m.from_user.first_name,
                                               m.from_user.last_name, m.from_user.username, chatid, m.text))
            logging.info("[%s] %s %s (%s), %s: %s\n" % (time.ctime(
            ), m.from_user.first_name, m.from_user.last_name, m.from_user.username, chatid, m.text))
            if is_finglish(m.text.lower()):
                bot.reply_to(
                    m,
                    transliterate(m.text.lower())
                )


bot = telebot.TeleBot('Token')
bot.set_update_listener(listener)
# Use none_stop flag let polling will not stop when get new message occur
# error.
bot.polling(none_stop=True)

while True:  # Don't let the main Thread end.
    try:
        time.sleep(10)
        bot.get_me()
        pickle.dump(data, open(DATA, 'wb'))
    except:
        bot.polling(none_stop=True)
