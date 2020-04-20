import os
import sys

def kill():
	os.system("ps aux | grep ython | grep loop_pdf | awk '{print $2}' | xargs kill -9")

def setup():
	kill()
	if 'kill' in str(sys.argv):
		return 

	if 'debug' in str(sys.argv):
		os.system('python3 -u loop_pdf.py')
	elif 'skip' in str(sys.argv):
		os.system('nohup python3 -u loop_pdf.py skip &')
	else:
		os.system('touch nohup.out')
		os.system('nohup python3 -u loop_pdf.py & tail -F nohup.out')


if __name__ == '__main__':
	setup()