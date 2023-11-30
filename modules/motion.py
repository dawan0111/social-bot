
import time


class Motion:
  def __init__(self):
    self.servo = None

  def run(self, motion):
    print(motion)
    print("hello world!!")
    time.sleep(3)
    print("helloworld end!!")
  