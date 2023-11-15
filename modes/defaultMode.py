
from modes.basicMode import BasicMode


class DefaultMode(BasicMode):
  def __init__(self, maximum_history_size = 100):
    enter_message = "기본모드 전환"
    exit_message = "기본모드 종료"
    default_chats = []
    super().__init__(default_chats, enter_message, exit_message, maximum_history_size)