# import serial
import time

def xor_and_add(data):
    result = data[2]
    for i in range(3, 7):
        result ^= data[i]
    return result + 1


class Motion:
  def __init__(self):
    pass

  def send_smooth_motion(self, start_motion, goal_motion):
      # x y z
      delta_p = [0, 0, 0]
      
      for i in range(3):
        if goal_motion[2 + i] > start_motion[2 + i]:
            delta_p[i] = 5
        elif goal_motion[2 + i] < start_motion[2 + i]:
            delta_p[i] = -5
      send_data = start_motion[:]

      while True:
          if send_data[2] == goal_motion[2] and send_data[3] == goal_motion[3] and send_data[4] == goal_motion[4]:
              break
          send_data[2] += delta_p[0]
          send_data[3] += delta_p[1]
          send_data[4] += delta_p[2]
          print(send_data[2], send_data[3], send_data[4])
          send_data[7] = xor_and_add(send_data)
          self.ser.write(send_data)
          time.sleep(0.1)
      goal_motion[7] = xor_and_add(goal_motion)
      self.ser.write(goal_motion)  

  def run(self, motions):
      pass

if __name__ == "__main__":
    motion = Motion()
    motion.run(["L", "R", "U", "D", "L_E", "R_E"])

