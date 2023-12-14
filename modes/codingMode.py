
from modes.basicMode import BasicMode


class CodingMode(BasicMode):
  def __init__(self, maximum_history_size = 100):
    enter_message = "단어동작 모드로 변경되었습니다."
    exit_message = "코딩모드 종료"
    default_chats = []
    super().__init__(default_chats, enter_message, exit_message, maximum_history_size)