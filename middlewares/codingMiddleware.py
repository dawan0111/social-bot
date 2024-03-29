from middlewares.abstractMiddleware import AbstractMiddleware
from enum import Enum

from modes.modeManager import Mode, ModeManager

class CodingMiddleware(AbstractMiddleware):
    
    def __init__(self, modeManager: ModeManager) -> None:
        super().__init__()
        self.modeManager = modeManager
        self.settings = [
            dict(id="과일", left_command=["딸기"], right_command=["사과"], up_command=["포도"], down_command=["자두"], right_eye_command=["수박"], left_eye_command=["레몬", "멜론"]),
            dict(id="동물", left_command=["여우"], right_command=["사자", "타자"], up_command=["토끼"], down_command=["상어"], right_eye_command=["하마", "삼아"], left_eye_command=["고래", "노래", "오래"]),
            dict(id="음식", left_command=["김밥"], right_command=["만두"], up_command=["피자"], down_command=["치킨"], right_eye_command=["초밥"], left_eye_command=["라면"]),
        ]
        self.setting = self.settings[0]
        

    def run(self, response):
        _, input_text, is_direct, chats, direct_message, motion = response
        
        mode = self.modeManager.get_mode_id()
        
        if mode == Mode.CODING:
            setting = self.get_setting(input_text)
            if setting is not None:
                self.setting = setting
                return (False, input_text, True, [], "{} 문제로 변경했어요.".format(self.setting["id"]), [])

            coding_moton = self.create_motion(input_text)
            text = "동작을 확인해보세요."

            if len(coding_moton) == 0:
                text = ""

            return (False, input_text, True, [], text, coding_moton)
        else:
          return response
        
    def get_setting(self, text):
        command = text.replace(" ", "")
        for setting in self.settings:
            if setting["id"] in command:
                return setting
        return None
        
    def create_motion(self, text):
        motion = []
        start_index = 0
        string_length = 1
        command_names = [["left_command", "L"], ["right_command", "R"], ["up_command", "U"], ["down_command", "D"], ["right_eye_command", "R_E"], ["left_eye_command", "L_E"]]

        while start_index + string_length <= len(text):
            command = text[start_index:start_index + string_length].strip()
            matched_motion = False

            for command_name in command_names:
                for motion_command in self.setting[command_name[0]]:
                    if motion_command in command:
                        matched_motion = True
                        motion.append(command_name[1])
                        break
                if matched_motion:
                    break
              
            if matched_motion:
                start_index += string_length
                string_length = 1
            else:
              string_length += 1

        return motion
