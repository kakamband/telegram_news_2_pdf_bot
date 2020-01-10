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
channel_pdf = tele.bot.get_chat(-1001371029868)
channel_en = tele.bot.get_chat(-1001414226421)

@log_on_fail(debug_group)
def loopImp():
	sources = ['bbc', 'nyt', 'bbc英文', 'nyt英文']
	files = []
	files_en = []
	for s in sources:
		f = news_2_pdf.gen(news_source=s)
		files.append(f)
		if '英文' in s:
			files_en.append(f)
	for f in files[::-1]:
		channel_pdf.send_document(document=open(f, 'rb'), timeout=TIMEOUT)
	for f in files_en:
		channel_en.send_document(document=open(f, 'rb'), timeout=TIMEOUT)

def loop():
	loopImp()
	threading.Timer(DAY, loop).start() 

threading.Timer(1, loop).start()