import sys
import os
import argparse
import queue
import yaml
import time
import threading
from middlewares.modeMiddleware import ModeMiddleware
from modes.modeManager import ModeManager
from modules.API import API, PostChatEntity

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
    def __init__(self, tts: TTS, openAI: OpenAI, modeManager: ModeManager, APIModule: API, delay_s = 0.1):
        self.tts = tts
        self.openAI = openAI
        self.delay_s = delay_s
        self.latest_speak = None
        self.input_queue = queue.Queue()
        self.modeManager = modeManager
        self.APIModule = APIModule

        self.middlewares = []

        self.output_start_callback = None
        self.output_end_callback = None

    def speak_callback(self, responses):
        final_text, final_time = responses[-1]

        entity = PostChatEntity(robot_id=1, mode=self.modeManager.get_mode_id(), message=final_text)
        response = self.APIModule.post_chat_message(entity)
        
        _, input_text, is_direct, chats, direct_message = self.run_middlewares(final_text)
        self.input_queue.put((is_direct, chats, direct_message))
        return True

    def register_output_start_callback(self, callback):
        self.output_start_callback = callback 

    def register_output_end_callback(self, callback):
        self.output_end_callback = callback

    def regitser_middleware(self, name, middleware):
        self.remove_middleware(name)
        self.middlewares.append((name, middleware))

    def remove_middleware(self, name):
        delete_index = None
        for i, middleware in enumerate(self.middlewares):
            if middleware[0] == name:
                delete_index = i
                break
        
        if delete_index:
            del self.middlewares[delete_index]
            return True
        
        return False
    
    def run_middlewares(self, input_text):
        response = (False, input_text, False, [], "")

        for middleware in self.middlewares:
            response = middleware[1].run(response)
            if response[0]:
                break

        return response


    def run(self):
        while True:
            if not self.input_queue.empty():
                if self.output_start_callback is not None:
                    self.output_start_callback()

                is_direct, chats, direct_message = self.input_queue.get()
                
                if is_direct:
                    self.tts.run(direct_message)
                    self.latest_answer = time.time()
                else:
                    response_text = self.openAI.run(chats)
                    self.modeManager.add_chat(response_text, 'assistant')
                    self.tts.run(response_text)
                    self.latest_answer = time.time()

                if self.output_end_callback is not None:
                    self.output_end_callback()
            else:
                pass
            time.sleep(self.delay_s)


if __name__ == "__main__":
    print("program start!")

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

    modeManager = ModeManager()
    tts = TTS(GCP_AUTH_PATH, GCP_LANG_CODE)
    openAI = OpenAI(OPENAI['API_KEY'], OPENAI['model'])
    API_module = API(api_endpoint="http://127.0.0.1:8000")

    modeMiddleware = ModeMiddleware(modeManager)

    output_processer = OutputProcesser(tts=tts, openAI=openAI, modeManager=modeManager, APIModule=API_module)

    stt = STT(GCP_AUTH_PATH, GCP_LANG_CODE, _cfg["STT"]["rate"], _cfg["STT"]["chunk"], output_processer.speak_callback)
    input_processer = InputProcesser(stt=stt)

    output_processer.register_output_start_callback(input_processer.output_start_callback)
    output_processer.register_output_end_callback(input_processer.output_end_callback)
    output_processer.regitser_middleware('mode', modeMiddleware)

    input_thread = threading.Thread(target=input_processer.run)
    output_thread = threading.Thread(target=output_processer.run)

    threads = [input_thread, output_thread]
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()

    print("program end!")
    # success = tts.run("hello world!")