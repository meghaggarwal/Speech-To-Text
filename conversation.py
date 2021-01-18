# import socketclient
import threading
import queue
import time
import socket
import sys, signal
import logging
import re
import sys
import wave

from google.cloud import speech

import pyaudio
import queue

class Conversation:

  def __init__(self, conn, s):
    self.conn =  conn
    self.s = s
    self._q = queue.Queue()
    self.client = speech.SpeechClient()
    
  def __start(self):
    self.running_flag = True

  def __stop(self):
    self._q.put(None)

  def __call__(self):
    threading.Thread(target=self.__send).start()
    self.__recv()

  def __recv(self):
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    recognition_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)
    try:                                                              
      for resp in self.client.streaming_recognize(recognition_config , self.read_soc()):
        print("Receiving....")
        print(resp)

    except Exception as e:
      print("Receivinf from client..", e)
        # self._q.put(self.__process_response(resp))
        
    self.__stop()
    
  def __process_response(self, response):
      
        # response list is empty
    if not response.results:
      return
    
    result = response.results[0]
    if not result.alternatives:
      return

    print(result.is_final, result.alternatives[0])
    return result.alternatives[0].transcript

  def read_soc(self):
    try:
      flag = False
      while True:
        # buffer = self.conn.recv(4096)
        buffer = b''
        while(len(buffer) < 1600):
          buffer+=self.conn.recv(1600 - len(buffer))
          print("Writing on buffer")
          if not buffer:
            print("No client data received..")
            break

        if not flag:
          s =  wave.open("file_audio.wav", "wb")
          s.setnchannels(1)
          s.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
          s.setframerate(16000)
          s.writeframes(buffer)
          flag = True

        else:
          # print("Writing....")
          s.writeframes(buffer)
        if buffer is None:
          break
        # print("Generatig req..", len(buffer))
        yield speech.StreamingRecognizeRequest(audio_content=buffer)
    except Exception as e:
      print("Error on read...", e)

    
  def __send(self):
    while True:
      data =  self._q.get()
      if data is None:
        break
      self.conn.send(data)
      print("sent data:", data)