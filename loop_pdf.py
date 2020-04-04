#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import threading
from telegram.ext import Updater, MessageHandler, Filters
from telegram_util import log_on_fail
import news_2_pdf
import channel2pdf
import time
import os
import datetime
import sendgrid
import sys
from retrying import retry

channel_sources = [
	'equality_and_rights', 
	'freedom_watch',
	'equality_and_rights', 
	'social_justice_watch', 
	'pincongessence',
]

news_sources = ['bbc', 'nyt', 'bbc英文', 'nyt英文']

TIMEOUT = 20 * 60
excuted = set()
last_excute = {'taiwan': time.time(), 'douban': time.time()}

big_font_setting = '--paper-size b6 --pdf-page-margin-left 15 ' + \
	'--pdf-page-margin-right 15 --pdf-page-margin-top 15 ' + \
	'--pdf-page-margin-bottom 15'

if 'skip' in str(sys.argv):
	now = datetime.datetime.now()
	excuted.add((now.month, now.day))

with open('CREDENTIALS') as f:
	CREDENTIALS = yaml.load(f, Loader=yaml.FullLoader)

tele = Updater(CREDENTIALS['bot_token'], use_context=True)
debug_group = tele.bot.get_chat(-1001198682178)
channel_pdf = tele.bot.get_chat(-1001371029868)
channel_en = tele.bot.get_chat(-1001414226421)

@retry(stop_max_attempt_number=2)
def sendSingle(c, f):
	try:
		c.send_document(document=open(f, 'rb'), timeout=TIMEOUT)
	except Exception as e:
		debug_group.send_message(str(e))
		raise e

def sendAll(c, files):
	for f in files:
		try:
			sendSingle(c, f)
		except:
			pass

def gen_files():
	files = []
	files_en = []
	for s in news_sources:
		news_2_pdf.gen(news_source=s, filename_suffix='_大字版', additional_setting=big_font_setting)
		f = news_2_pdf.gen(news_source=s)
		files.append(f)
		if '英文' in s:
			files_en.append(f)
	day = int(time.time() / 24 / 60 / 60)
	for s in set(channel_sources):
		f = channel2pdf.gen(s)
		if s == channel_sources[day % len(channel_sources)]:
			files.append(f)
			if 'social_justice_watch' == s:
				files_en.append(f)
		channel2pdf.gen(s, filename_suffix='_大字版', additional_setting=big_font_setting)
	return files, files_en

def log(text):
	with open('nohup.out', 'a') as f:
		f.write('%d:%d %s\n' % (datetime.datetime.now().hour, datetime.datetime.now().minute, text))

def send_pdf():
	now = datetime.datetime.now()
	if (now.month, now.day) in excuted:
		return
	log('generating file')
	files, files_en = gen_files()
	log('removing old file')
	for x in os.listdir('pdf_result'):
		if os.path.getmtime('pdf_result/' + x) < time.time() - 60 * 60 * 72:
			os.system('rm pdf_result/' + x + ' > /dev/null 2>&1')
	log('commiting github')
	os.system('git add . > /dev/null 2>&1 && git commit -m commit > /dev/null 2>&1 && nohup git push -u -f &')
	log('sending pdf')
	sendAll(channel_pdf, files[::-1])
	sendAll(channel_en, files_en)
	log('pdf execution end')
	excuted.add((now.month, now.day))

def send_telegram():
	if time.time() - last_excute['taiwan'] > 60 * 60 * 12:
		os.system('cd ~/Documents/projects/douban && nohup python3 aggregate.py &')
		os.system('cd ~/Documents/projects/taiwan && nohup python3 aggregate.py &')
		last_excute['taiwan'] = time.time()
		last_excute['douban'] = time.time()
	if time.time() - last_excute['douban'] > 60 * 60 * 2:
		os.system('cd ~/Documents/projects/douban && nohup python3 aggregate.py &')
		last_excute['douban'] = time.time()

@log_on_fail(debug_group)
def loopImp():
	send_telegram()
	send_pdf()

def loop():
	loopImp()
	threading.Timer(60 * 10, loop).start() 

threading.Timer(1, loop).start()

@log_on_fail(debug_group)
def export(update, context):
	channel_name = update.message.text
	if not channel_name:
		return
	channel_name = channel_name.split('/')[-1]
	f = channel2pdf.gen(channel_name)
	update.message.reply_document(document=open(f, 'rb'), timeout=TIMEOUT)

tele.dispatcher.add_handler(MessageHandler(Filters.text & Filters.private, export))

tele.start_polling()
tele.idle()
