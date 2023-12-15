
import time


class Motion:
  def __init__(self):
    self.servo = None

  def run(self, motion):
    print(motion)
    print("motion start!!")
    time.sleep(3)
    print("motion end!!")
  