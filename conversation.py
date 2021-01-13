from __future__ import division
# import socketclient
import threading
import queue
import time
import socket
import sys, signal

import re
import sys

from google.cloud import speech

import pyaudio
from six.moves import queue

RATE = 16000
CHUNK = int(RATE / 10)
language_code = "en-US"

class Conversation:

  def listen_print_loop(self,responses):

    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:

            return transcript + overwrite_chars

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                break

            num_chars_printed = 0

  def _speech_to_text(self, content):
    print("speech to text...")
    self.content = content

    self.requests = ( speech.StreamingRecognizeRequest(audio_content=self.content))
    print(self.requests)
    self.responses = self.client.streaming_recognize(self.streaming_config, self.requests)
    print(self.responses)
    print("I will print responses")

    # Now, put the transcription responses to use.
    
    return self.listen_print_loop(self.responses)


  def __init__(self, conn, s):
    self.conn =  conn
    self.s = s
    #self._asr =  Asr()
    #self._tts = TTS()
    self._q = queue.Queue()
    self.client = speech.SpeechClient()
    self.config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )

    self.streaming_config = speech.StreamingRecognitionConfig(
        config=self.config, interim_results=True
    ) # ASR + TTS pipeline
    # threading.Thread(target=self.__send).start()
    # self.__recv()
    print(s)


  def __start(self):
    self.running_flag = True


  def __stop(self):
    try:
      time.sleep(5)
      # self._q.put(None)
    except KeyboardInterrupt:
      self.running_flag = False
    

  def __call__(self):
    # self._asr.Start()
    threading.Thread(target=self.__send).start()
    self.__recv()


  def __recv(self):
    while True:
     
      data = self.conn.recv(4096)
      print("Here is the above data")
      data = self._speech_to_text(data)
      self._q.put(data)
      print(data , "Received data...")
      if data is None:
        break
    

    # self.__stop()

  def __send(self):
    while True:
      data =  self._q.get()
      if data is None:
        self.conn.send(data)
        break
      self.conn.send(data)
      print("sent data:", data)
      
      
      