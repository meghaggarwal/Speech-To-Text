from __future__ import division

import socket	#for sockets
import sys	#for exit
import threading
import pyaudio
import wave
import time


import re
import sys

from google.cloud import speech

import pyaudio
from six.moves import queue


RATE = 16000
CHUNK = int(RATE / 10)

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue


    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

host = 'localhost'
port = 8888
reply = ''

try:
	#create an AF_INET, STREAM socket (TCP)
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
  print('Failed to create socket')
  sys.exit()

print('Socket Created')

try:
  remote_ip = socket.gethostbyname( host )
  print(remote_ip)
  
except socket.gaierror:
	#could not resolve
  print('Hostname could not be resolved. Exiting')
  sys.exit()
	
print('Ip address of ' + host + ' is ' + remote_ip)

# Connect to remote server
s.connect((remote_ip , port))

print('Socket Connected to ' + host + ' on ip ' + remote_ip)

#Send some data to remote server
print("Record your message...")

def send_client_data(s):
  while True:
    try:
      # message = input()
      try:
        with MicrophoneStream(RATE, CHUNK) as stream:
          audio_generator = stream.generator()
          s.sendall(next(audio_generator))
      except socket.error:
        #Send failed
        print('Sending failed')
        sys.exit()

    except KeyboardInterrupt:
      print("Key Interrupt...Stopping the client side...")
      break
    
 
def recv_client_data(s):
  global reply
  while True:
    try:
      if reply is None:
        break
      reply += s.recv(4).decode('utf-8')
      print(reply)

    except ConnectionError:
      print("Connection has been aborted ...")
      sys.exit()
      break
  
t1 = threading.Thread(target=recv_client_data, args=(s,), daemon=True).start()
send_client_data(s)
s.close()

 


