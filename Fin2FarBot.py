#!/usr/bin/python2
from __future__ import print_function
import telebot
import requests
import enchant
import time
import urllib3
import certifi
import logging
import re

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',  # Force certificate check.
    ca_certs=certifi.where(),  # Path to the Certifi bundle.
)
urllib3.disable_warnings()

en_dict = enchant.Dict('en')
alphabet = set([i for i in 'abcdefghijklmnopqrstuvwxyz'])

logging.basicConfig(filename='Fin2FarBotLog.log', filemode='a', level=logging.INFO)

base_chat_id = None


def transliterate(text):
    url = 'http://www.behnevis.com/php/convert.php'
    headers = {'Accept-Charset': 'UTF-8'}

    r = http.request(
        'POST',
        url,  # + 'farsi=salam&responsetime=-1&resulttype=json',
        fields={
            'farsi': text,
            'responsetime': -1
        },
        headers=headers
    )

    return r.data


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
    global base_chat_id
    for m in messages:
        chatid = m.chat.id
        if m.content_type == 'text':
            print("[%s] %s %s (%s), %s: %s" %(time.ctime(), m.from_user.first_name, m.from_user.last_name, m.from_user.username, chatid, m.text))
            logging.info("[%s] %s %s (%s), %s: %s\n" %(time.ctime(), m.from_user.first_name, m.from_user.last_name, m.from_user.username, chatid, m.text))
            if is_finglish(m.text.lower()):
               bot.reply_to(
                    m,
                    transliterate(m.text.lower())
                )


log = open('Fin2FarBotLog.log', 'w')
bot = telebot.TeleBot('TOKEN')
bot.set_update_listener(listener)
bot.polling()
#Use none_stop flag let polling will not stop when get new message occur error.
bot.polling(none_stop=True)
# Interval setup. Sleep 3 secs between request new message.
bot.polling(interval=0)

while True: # Don't let the main Thread end.
    pass
