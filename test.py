#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import news_2_pdf
import channel2pdf
import os
import sys

def test():
	# news_2_pdf.gen(news_source='bbc')
	# news_2_pdf.gen(news_source='nyt')
	channel2pdf.gen('opinion_feed')
	
if __name__ == "__main__":
	test()