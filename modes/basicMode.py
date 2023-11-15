import queue

class BasicMode():
  def __init__(self, default_chats, enter_message, exit_message, maximum_history_size = 100):
    self.chats = queue.Queue(maxsize=maximum_history_size)
    self.maximum_history_size = maximum_history_size
    self.default_chats = default_chats
    self.enter_message = enter_message
    self.exit_message = exit_message

  def create_chat(text, role):
    return {"role": role, "content": text}

  def add_chat(self, text, role):
    self.chats.put({"role": role, "content": text})

  def get_history(self):
    return self.default_chats + list(self.chats.queue)
  
  def get_enter_message(self):
    return self.enter_message
  
  def get_exit_message(self):
    return self.exit_message