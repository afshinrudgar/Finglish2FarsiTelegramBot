#!/usr/bin/python2
from __future__ import print_function
import telebot
import requests
import enchant
import time


en_dict = enchant.Dict('en')
alphabet = set([i for i in 'abcdefghijklmnopqrstuvwxyz'])

def transliterate(text):
    url = 'http://www.behnevis.com/php/convert.php'
    headers = {'Accept-Charset': 'UTF-8'}

    r = requests.post(
        url,  # + 'farsi=salam&responsetime=-1&resulttype=json',
        data={
            'farsi': text,
            'responsetime': -1
        },
        headers=headers
    )

    return r.text


def is_finglish(text):
    flag = True
    s_t = text.split(' ')
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
        if m.content_type == 'text' and is_finglish(m.text):
            print("[%s] %s, %s" %(time.ctime(), chatid, m.text))
            bot.reply_to(
                m,
                transliterate(m.text)
            )


bot = telebot.TeleBot('122159953:AAGAxAZhIRki8J0vEKd8II9zQCqXV0UV67M')
bot.set_update_listener(listener)
bot.polling()
#Use none_stop flag let polling will not stop when get new message occur error.
bot.polling(none_stop=True)
# Interval setup. Sleep 3 secs between request new message.
bot.polling(interval=0)

while True: # Don't let the main Thread end.
    pass
