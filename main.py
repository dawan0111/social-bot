import sys
import os
import argparse
import queue
import yaml
import time
import threading

from modules.TTS import TTS
from modules.STT import STT
from modules.openAI import OpenAI

def parse_args():
    parser = argparse.ArgumentParser(description="EMOTIBOT Parameter description")
    parser.add_argument("--config", type=str, default=os.environ.get("GCP_KEY_PATH", "./config.yaml"), help="emoti config yaml file path")

    args = parser.parse_args()
    return args

class InputProcesser:
    def __init__(self, stt):
        self.stt = stt

    def output_start_callback(self):
        audio_stream = self.stt.get_stream()
        audio_stream.paused = True
        print("InputProcesser) output start callback!!")

    def output_end_callback(self):
        audio_stream = self.stt.get_stream()
        audio_stream.paused = False
        print("InputProcesser) output end callback!!")

    def run(self):
        self.stt.run()

class OutputProcesser:
    def __init__(self, tts: TTS, openAI: OpenAI, delay_s = 0.1):
        self.tts = tts
        self.openAI = openAI
        self.delay_s = delay_s
        self.latest_speak = None
        self.input_queue = queue.Queue()

        self.output_start_callback = None
        self.output_end_callback = None

    def speak_callback(self, responses):
        self.input_queue.put(responses)
        return True

    def register_output_start_callback(self, callback):
        self.output_start_callback = callback 

    def register_output_end_callback(self, callback):
        self.output_end_callback = callback

    def run(self):
        while True:
            if not self.input_queue.empty():
                if self.output_start_callback is not None:
                    self.output_start_callback()

                response = self.input_queue.get()
                print(response)
                final_text, final_time = response[-1]

                response_text = self.openAI.run(final_text)
                self.tts.run(response_text)
                self.latest_answer = time.time()

                if self.output_end_callback is not None:
                    self.output_end_callback()
            else:
                pass
            time.sleep(self.delay_s)


if __name__ == "__main__":
    args = parse_args()

    if not os.path.isfile(args.config):
        print(f"unlocate config file path: {args.config}")
        sys.exit(1)

    with open(args.config, encoding='UTF-8') as f:
        _cfg = yaml.load(f, Loader=yaml.FullLoader)

    GCP_AUTH_PATH = _cfg["GCP"]["auth_key_path"]
    GCP_LANG_CODE = _cfg["GCP"]["language_code"]
    OPENAI = _cfg["openAI"]

    if not os.path.isfile(GCP_AUTH_PATH):
        print(f"unlocate gcp auth file path: {GCP_AUTH_PATH}")
        sys.exit(1)

    tts = TTS(GCP_AUTH_PATH, GCP_LANG_CODE)
    openAI = OpenAI(OPENAI['API_KEY'], OPENAI['model'])

    output_processer = OutputProcesser(tts=tts, openAI=openAI)

    stt = STT(GCP_AUTH_PATH, GCP_LANG_CODE, _cfg["STT"]["rate"], _cfg["STT"]["chunk"], output_processer.speak_callback)
    input_processer = InputProcesser(stt=stt)

    output_processer.register_output_start_callback(input_processer.output_start_callback)
    output_processer.register_output_end_callback(input_processer.output_end_callback)

    input_thread = threading.Thread(target=input_processer.run)
    output_thread = threading.Thread(target=output_processer.run)

    threads = [input_thread, output_thread]
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()

    print("program end!")
    # success = tts.run("hello world!")