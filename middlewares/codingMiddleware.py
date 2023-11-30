from middlewares.abstractMiddleware import AbstractMiddleware
from enum import Enum

from modes.modeManager import Mode, ModeManager

class CodingMiddleware(AbstractMiddleware):
    
    def __init__(self, modeManager: ModeManager) -> None:
        super().__init__()
        self.modeManager = modeManager

        self.left_command = "사과"
        self.right_command = "배"
        self.up_command = "포도"
        self.down_command = "바나나"

    def run(self, response):
        _, input_text, is_direct, chats, direct_message, motion = response
        
        mode = self.modeManager.get_mode_id()
        
        if mode == Mode.CODING:
            coding_moton = self.create_motion(input_text)
            return (False, input_text, True, [], "motion start", coding_moton)
        else:
          return response
        
    def create_motion(self, text):
        motion = []
        start_index = 0
        string_length = 1

        while start_index + string_length <= len(text):
            command = text[start_index:start_index + string_length].strip()
            matched_motion = False
            print(command)
            if self.left_command in command:
                motion.append("L")
                matched_motion = True
            elif self.right_command in command:
                motion.append("R")
                matched_motion = True
            elif self.up_command in command:
                motion.append("U")
                matched_motion = True
            elif self.down_command in command:
                motion.append("D")
                matched_motion = True
              
            if matched_motion:
                start_index += string_length
                string_length = 1
            else:
              string_length += 1

        print("motion: ", motion)
        return motion