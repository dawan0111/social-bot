from middlewares.abstractMiddleware import AbstractMiddleware
from enum import Enum

from modes.modeManager import Mode, ModeManager

class Command(Enum):
    MODE_CHANGE = 1
    COMMUNITY = 2

class ModeMiddleware(AbstractMiddleware):
    
    def __init__(self, modeManager: ModeManager) -> None:
        super().__init__()
        self.modeManager = modeManager

    def run(self, response):
        _, input_text, is_direct, chats, direct_message, motion = response
        command_type, mode = self.classify_command_type(input_text)

        if command_type == Command.MODE_CHANGE:
            exit_message = self.modeManager.get_exit_message()
            self.modeManager.change_mode(mode)
            direct_message = self.modeManager.get_enter_message()

            if mode == Mode.DEFAULT:
                direct_message = exit_message

            return (True, input_text, True, self.modeManager.get_chats(), direct_message, motion)
            
        self.modeManager.add_chat(input_text, 'user')
        return (False, input_text, False, self.modeManager.get_chats(), direct_message, motion)
    
    def classify_command_type(self, input_text):
        if '영어' in input_text:
            return (Command.MODE_CHANGE, Mode.ENGLISH)
        elif '일반' in input_text:
            return (Command.MODE_CHANGE, Mode.DEFAULT)
        elif '다이어리' in input_text:
            return (Command.MODE_CHANGE, Mode.DIARY)
        elif '단어 모드' in input_text:
            return (Command.MODE_CHANGE, Mode.CODING)
        else:
            return (Command.COMMUNITY, self.modeManager.get_mode_id())
