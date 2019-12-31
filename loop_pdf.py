#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import threading
from telegram.ext import Updater
from telegram_util import log_on_fail
import news_2_pdf

DAY = 60 * 60 * 24
TIMEOUT = 10 * 60

with open('CREDENTIALS') as f:
    CREDENTIALS = yaml.load(f, Loader=yaml.FullLoader)

tele = Updater(CREDENTIALS['bot_token'], use_context=True)
debug_group = tele.bot.get_chat(-1001198682178)
channel = tele.bot.get_chat(-1001371029868)

@log_on_fail(debug_group)
def loopImp():
    file1 = news_2_pdf.gen(news_source='bbc')
    channel.send_document(document=open(file1, 'rb'), timeout=TIMEOUT)
    file2 = news_2_pdf.gen(news_source='nyt')
    channel.send_document(document=open(file2, 'rb'), timeout=TIMEOUT)

def loop():
    loopImp()
    threading.Timer(DAY, loop).start() 

threading.Timer(1, loop).start()