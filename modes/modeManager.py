from enum import Enum

from modes.defaultMode import DefaultMode
from modes.diaryMode import DiaryMode
from modes.englishMode import EnglishMode


class Mode(Enum):
    DEFAULT = 0
    ENGLISH = 1
    DIARY = 2
    COUNSEL = 3
    MORNING = 4
    CODING = 5


class ModeManager():
    def __init__(self):
      self.modes = dict()
      self.modes[Mode.DEFAULT] = DefaultMode()
      self.modes[Mode.ENGLISH] = EnglishMode()
      self.modes[Mode.DIARY] = DiaryMode()
      self.modes[Mode.COUNSEL] = None
      self.modes[Mode.MORNING] = None
      self.modes[Mode.CODING] = None

      self.current_mode = Mode.DEFAULT
      self.current_mode_modules = self.modes[self.current_mode]

    def change_mode(self, mode):
       if mode in self.modes:
        self.current_mode_modules = self.modes[mode]
        self.current_mode = mode

    def add_chat(self, text, role):
       self.current_mode_modules.add_chat(text, role)

    def get_mode_id(self):
       return self.current_mode
    
    def get_chats(self):
       return self.current_mode_modules.get_history()
    
    def get_exit_message(self):
       return self.current_mode_modules.get_exit_message()

    def get_enter_message(self):
       return self.current_mode_modules.get_enter_message()