import socket
import sys
import threading
from conversation import Conversation
import sys, signal
import time



HOST = ''	
PORT = 8888	
running_flag = True
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

try:
	s.bind((HOST, PORT))
except socket.error as e:
	print('Bind failed. Error Code : ' + str(e[0]) + ' Message ' + e[1])
	sys.exit()
	
print('Socket bind complete')

s.listen(20)
print('Socket now listening')

# wait to accept a connection - blocking call


def terminate():
		global running_flag
		try:
			time.sleep(5)
			# self._q.put(None)
		except KeyboardInterrupt:
			print("Program Exited Gracefully...")
			running_flag = False


while(1):
	try:
		s.settimeout(5)
		try:
			conn, addr = s.accept()
			print("Connected with" + addr[0] + ':' + str(addr[1]))
			c = Conversation(conn, s)
			threading.Thread(target=c, daemon=True).start()

		except socket.timeout:
			terminate()
			if not running_flag:
				break

	except KeyboardInterrupt as e:
		print("Server has stopped...")
		break
	
s.close()
