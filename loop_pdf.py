#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import threading
from telegram.ext import Updater
from telegram_util import log_on_fail
import news_2_pdf

DAY = 60 * 60 * 24
TIMEOUT = 20 * 60

with open('CREDENTIALS') as f:
	CREDENTIALS = yaml.load(f, Loader=yaml.FullLoader)

tele = Updater(CREDENTIALS['bot_token'], use_context=True)
debug_group = tele.bot.get_chat(-1001198682178)
channel = tele.bot.get_chat(-1001371029868)

@log_on_fail(debug_group)
def loopImp():
	sources = ['bbc', 'nyt', 'bbc英文', 'nyt英文']
	files = []
	for s in sources:
		files.append(news_2_pdf.gen(news_source=s))
	for f in files[::-1]:
		channel.send_document(document=open(f, 'rb'), timeout=TIMEOUT)

def loop():
	loopImp()
	threading.Timer(DAY, loop).start() 

threading.Timer(1, loop).start()