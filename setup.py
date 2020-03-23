import os
import sys

def kill():
	os.system("ps aux | grep ython | grep loop_pdf | awk '{print $2}' | xargs kill -9")

def setup():
	if 'kill' in str(sys.argv):
		kill()
		return 
	
	os.system('pip3 install --user -r requirements.txt --upgrade')
	kill()

	if 'debug' in str(sys.argv):
		os.system('python3 loop_pdf.py')
	elif 'skip' in str(sys.argv):
		os.system('nohup python3 loop_pdf.py skip &')
	else:
		os.system('nohup python3 loop_pdf.py &')


if __name__ == '__main__':
	setup()