
from modes.basicMode import BasicMode


class EnglishMode(BasicMode):
  def __init__(self, maximum_history_size = 100):
    enter_message = "영어회화 전환"
    exit_message = "영어회화 종료"
    default_chats = [
      {"role": 'user', "content": '너는 영어 교사의 역할, 나는 학생의 역할로 대화할거야. 내가 말한 영어 문장 중 틀리거나 잘못 사용된 문법이 있으면 그걸 수정해서 알려줘야해.'}
    ]
    super().__init__(default_chats, enter_message, exit_message, maximum_history_size)