
from modes.basicMode import BasicMode


class DiaryMode(BasicMode):
  def __init__(self, maximum_history_size = 100):
    enter_message = "다이어리 전환"
    exit_message = "다이어리 종료"
    default_chats = [
      {"role": 'user', "content": '너와의 대화를 통해 일기를 쓰고 싶어, 내 하루를 되돌아 보고 내일 더 나은 하루를 보낼 수 있도록 하나씩 질문하고 그것에 관해 피드백 해 줄 수 있을까?'}
    ]
    super().__init__(default_chats, enter_message, exit_message, maximum_history_size)