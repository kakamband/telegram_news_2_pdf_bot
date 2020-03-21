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
from datetime import date
import sendgrid
import sys
from sendgrid.helpers.mail import Content, Email, Mail, Attachment, To

TO_EXPORT = [
	'opinion_feed',
	'equality_and_rights', 
	'freedom_watch',
	'social_justice_watch', 
	'pincongessence',
	'equality_and_rights', 
]

TIMEOUT = 40 * 60
excuted = set()
last_excute = {'taiwan': 0, 'douban': 0}

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

def sendAll(c, files):
	for f in files:
		try:
			c.send_document(document=open(f, 'rb'), timeout=TIMEOUT)
		except Exception as e:
			debug_group.send_message(str(e))

def sendEmail():
	now = datetime.datetime.now()
	sg = sendgrid.SendGridAPIClient(CREDENTIALS['email_key'])
	from_email = Email(CREDENTIALS['sender'])
	to_emails = [To(x) for x in CREDENTIALS['to']]
	content = Content("text/plain", "no content")
	mail = Mail(subject='%s 【新闻播报】' % date.today().strftime("%m%d"),
		html_content='书友好！今天的新闻播报已经生成，请至 https://github.com/gaoyunzhi/telegram_news_2_pdf_bot/tree/master/pdf_result 领取。',
		from_email=from_email,
		to_emails=to_emails,
		)
	sg.send(mail)

def send_pdf():
	now = datetime.datetime.now()
	if (now.month, now.day) in excuted:
		return
	sources = ['bbc', 'nyt', 'bbc英文', 'nyt英文']
	files = []
	files_en = []
	for s in sources:
		news_2_pdf.gen(news_source=s, filename_suffix='_大字版', additional_setting=big_font_setting)
		f = news_2_pdf.gen(news_source=s)
		files.append(f)
		if '英文' in s:
			files_en.append(f)
	day = int(time.time() / 24 / 60 / 60)
	for s in TO_EXPORT:
		channel2pdf.gen(s)
		channel2pdf.gen(s, filename_suffix='_大字版', additional_setting=big_font_setting)
	s = TO_EXPORT[day % len(TO_EXPORT)]
	f = channel2pdf.gen(s)
	files.append(f)
	if 'social_justice_watch' == s:
		files_en.append(f)
	sendAll(channel_pdf, files[::-1])
	sendAll(channel_en, files_en)
	for x in os.listdir('pdf_result'):
		if os.path.getmtime('pdf_result/' + x) < time.time() - 60 * 60 * 72:
			os.system('rm pdf_result/' + x + ' > /dev/null 2>&1')
	os.system('git add . > /dev/null 2>&1 && git commit -m commit > /dev/null 2>&1 && git push -u -f > /dev/null 2>&1')
	sendEmail()
	excuted.add((now.month, now.day))

def send_telegram():
	h = datetime.datetime.now().hour
	if h > 9 or h < 8:
		return

	if time.time() - last_excute['taiwan'] > 10 * 60 * 12:
		os.system('cd ~/Documents/projects/taiwan && python3 aggregate.py')
		os.system('cd ~/Documents/projects/douban && python3 aggregate.py')
		last_excute['taiwan'] = time.time()
		last_excute['douban'] = time.time()
	if time.time() - last_excute['douban'] > 10 * 60 * 2:
		os.system('cd ~/Documents/projects/douban && python3 aggregate.py')
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
	f = channel2pdf.gen(update.message.text)
	update.message.reply_document(document=open(f, 'rb'), timeout=TIMEOUT)

tele.dispatcher.add_handler(MessageHandler(Filters.text & Filters.private, export))

tele.start_polling()
tele.idle()
