from __future__ import division # 파이썬3 스타일의 나누기 지원
import time
import queue
import sys
import threading
import numpy as np
from google.cloud import speech
import pyaudio

p = pyaudio.PyAudio()
device_number = 0
for i in range(p.get_device_count()):
    device = p.get_device_info_by_index(i)
    print(device)
    if "snd_rpi_i2s_card" in device["name"]:
        device_number = device["index"]
        break

print("len: ", p.get_device_count())
class MicrophoneStream(object):

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True
        self.paused = False

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt32,
            channels=1,
            rate=self._rate,
            input=True,
            input_device_index=device_number,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
    
        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        print(type, value, traceback)
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()
        self.paused = False

        return self

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        if self.paused:
            self._buff.put(b'\x00' * 3200)
        else:
            data_int32 = np.frombuffer(in_data, dtype=np.int32)
            data_int32 = ((data_int32 / (2 ** 31 - 1)) * 32767).astype(np.int16)
            data_len = data_int32.size // 2
            data_int16_1 = data_int32[:data_len]
            data_int16_2 = data_int32[data_len:]

            self._buff.put(data_int16_1.tobytes())
            self._buff.put(data_int16_2.tobytes())

            # data_int16 = data_int32.astype(np.int16)

            # self._buff.put(in_data)
            # ndarray = np.fromstring(in_data, dtype=np.int16)
            # max_volume = np.max(ndarray)
            
            # if max_volume > 6000:
            #     self._buff.put(in_data)
            # else:
            #     self._buff.put(b'\x00' * 3200)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        print('\n---while chunk is none---\n')
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

class STT:
    def __init__(self, auth_filepath, language_code, rate, chunk, listen_callback, phrases = []):
        self.rate = rate
        self.chunk = chunk
        self.stream = MicrophoneStream(self.rate, self.chunk)
        self.client = speech.SpeechClient.from_service_account_file(auth_filepath)
        self.config = speech.RecognitionConfig(encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                                          sample_rate_hertz=rate,
                                          language_code=language_code,
                                          max_alternatives=0,
                                          # alternative_language_codes=["en-US"],
                                          speech_contexts=[{"phrases":phrases}]
        )

        self.streaming_config = speech.StreamingRecognitionConfig(config=self.config,
                                                             single_utterance=False,
                                                             interim_results=True,
                                                             enable_voice_activity_events=False,
        )

        self.auth_filepath = auth_filepath
        self.latest_time = time.time()
        self.listen_callback = listen_callback
        self.detecting_text = ""
        self.text_start_index = 0
        self.timeout = False
        self.spacking_mutex = threading.Lock()
        self.text_buffer = queue.Queue()

    def speaking_timeout(self):
        while True:
            diff_time = time.time() - self.latest_time
            if diff_time >= 2 and self.detecting_text.strip() != "":
                print("time out: {}".format(self.detecting_text))
                self.spacking_mutex.acquire()
                self.listen_callback([(self.detecting_text, time.time())])
                if self.text_start_index > 0:
                    self.text_start_index += 1
                self.text_start_index += len(self.detecting_text)
                self.detecting_text = ""
                self.timeout = True
                self.spacking_mutex.release()
                pass
            time.sleep(0.5)
        pass

    def run(self):
        speacking_thread = threading.Thread(target=self.speaking_timeout)
        speacking_thread.start()
        
        with self.stream as stream:
            while True:
                try:
                    audio_generator = stream.generator()
                    requests = (
                        speech.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator
                    )
                    responses = self.client.streaming_recognize(self.streaming_config, requests)
                    self.listen_audio(responses)
                except Exception as exception:
                    print("Excption handle : Exceeded maximum allowed stream duration of 65 seconds")

        speacking_thread.join()

    def listen_audio(self, responses):
        num_chars_printed = 0
        print("listen_audio")
        for response in responses:
            self.latest_time = time.time()
            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript[self.text_start_index:]
            overwrite_chars = " " * (num_chars_printed - len(transcript))

            if not result.is_final:
                self.text_buffer.put((transcript + overwrite_chars, time.time()))
                sys.stdout.write(transcript + overwrite_chars + "\r")
                sys.stdout.flush()
                num_chars_printed = len(transcript)

                self.spacking_mutex.acquire()
                self.detecting_text = transcript + overwrite_chars
                self.spacking_mutex.release()
            else:
                response = []                
                print(result.alternatives[0].transcript, self.text_start_index)

                while not self.text_buffer.empty():
                    response.append(self.text_buffer.get())

                response.append((transcript + overwrite_chars, time.time()))

                self.spacking_mutex.acquire()
                self.text_start_index = 0
                self.detecting_text = ""
                self.spacking_mutex.release()

                if response[-1][0].strip() != "" and not self.stream.paused:
                    self.listen_callback(response)
                    print("finish]", transcript + overwrite_chars)
                
                num_chars_printed = 0
    
    def empty(self):
        self.text_buffer.empty()

    def get_stream(self):
        return self.stream

if __name__ == "__main__":
    def callback(text):
        print("callback: ", text)

    stt = STT("./gcp.json", "ko-KR", 16000, 1600, callback)
    stt.run()
