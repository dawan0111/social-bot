import serial
import time

def xor_and_add(data):
    result = data[2]
    for i in range(3, 7):
        result ^= data[i]
    return result + 1


class Motion:
  def __init__(self):
    self.servo = None
    self.safety_thr = 12
    self.ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)

  def send_smooth_motion(self, start_motion, goal_motion):
      # x y z
      delta_p = [0, 0, 0]
      
      for i in range(3):
        if goal_motion[2 + i] > start_motion[2 + i]:
            delta_p[i] = 4
        elif goal_motion[2 + i] < start_motion[2 + i]:
            delta_p[i] = -4
      send_data = start_motion[:]

      while True:
          if send_data[2] == goal_motion[2] and send_data[3] == goal_motion[3] and send_data[4] == goal_motion[4]:
              break
          send_data[2] += delta_p[0]
          send_data[3] += delta_p[1]
          send_data[4] += delta_p[2]
          send_data[7] = xor_and_add(send_data)
          self.ser.write(send_data)
          time.sleep(0.05)
      goal_motion[7] = xor_and_add(goal_motion)
      self.ser.write(goal_motion)  

  def run(self, motions):
      for motion in motions:
          print("motion: {}".format(motion))
          motion_data = bytearray([0xFF, 0xFF, 85, 90, 95, 0x00, 0x00, 0x00])
          reset_data = bytearray([0xFF, 0xFF, 85, 90, 95, 0x00, 0x00, 0x00])
          if motion == "L":
              motion_data[2] += self.safety_thr
          elif motion == "R":
              motion_data[2] -= self.safety_thr
          elif motion == "D":
              motion_data[3] += self.safety_thr
          elif motion == "U":
              motion_data[3] -= self.safety_thr
          elif motion == "L_E":
              motion_data[5] = 0x01
          elif motion == "R_E":
              motion_data[6] = 0x01
          
          print("motion_data start!!")
          self.send_smooth_motion(reset_data, motion_data)
          time.sleep(1)
          self.send_smooth_motion(motion_data, reset_data)
          time.sleep(1)

if __name__ == "__main__":
    motion = Motion()
    motion.run(["L", "R", "U", "D", "L_E", "R_E"])

