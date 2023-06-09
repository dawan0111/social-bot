from __future__ import division # 파이썬3 스타일의 나누기 지원
import time
import queue
import sys
from google.cloud import speech
import pyaudio

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
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
    
        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        print("exit??")
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
            self._buff.put(in_data)
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
                                          speech_contexts=[{"phrases":phrases}]
        )

        self.streaming_config = speech.StreamingRecognitionConfig(config=self.config,
                                                             single_utterance=False,
                                                             interim_results=True,
                                                             enable_voice_activity_events=False,
        )
        self.listen_callback = listen_callback
        self.text_buffer = queue.Queue()

    def run(self):
        with self.stream as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            responses = self.client.streaming_recognize(self.streaming_config, requests)
            self.listen_audio(responses)

    def listen_audio(self, responses):
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript
            overwrite_chars = " " * (num_chars_printed - len(transcript))

            if not result.is_final:
                self.text_buffer.put((transcript + overwrite_chars, time.time()))
                sys.stdout.write(transcript + overwrite_chars + "\r")
                sys.stdout.flush()
                num_chars_printed = len(transcript)
            else:
                response = []
                while not self.text_buffer.empty():
                    response.append(self.text_buffer.get())
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