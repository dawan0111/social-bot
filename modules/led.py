#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import board
import neopixel
import time

class Neo:
  def __init__(self) -> None:
    self.neo = neopixel.NeoPixel(board.D10, 100, auto_write=False)
    self.neo.fill((255, 0, 0))
    self.neo.show()
    self.count = 0
    self.on = True
    self.mode = False

  def __del__(self) -> None:
    self.neo.fill((0, 0, 0))
    self.neo.show()
    del self.neo

  def changeMode(self) -> None:
    if self.mode:
      self.count = 0
      self.on = True
      self.mode = False
    else:
      self.count = 0
      self.on = True
      self.mode = True
    print(self.mode)

  def voiceMode(self) -> None:
    if self.on:
      #for k in range(61, 69, 1):
        #self.neo[j] = (0, 20, 20)
      for i in range(0, 110, 10):
        if self.count == 0:
          for j in range(61, 69, 1):    #(52, 60, 1)
            self.neo[j] = (0, 0, 20)
        elif self.count == 1:
          for j in range(49, 61, 1):    #(40, 52, 1)
            self.neo[j] = (0, 0, i)
        elif self.count == 2:
          for j in range(33, 49, 1):    #(24, 40, 1)
            self.neo[j] = (0, 0, i)
        elif self.count == 3:
          for j in range(9, 33, 1):     #(0, 24, 1)
            self.neo[j] = (0, 0, i)
        self.neo.show()
        time.sleep(0.005)
        if self.mode:
          break
      if self.count == 3:
        self.on = False
      else:
        self.count += 1
    else:
      #for k in range(61, 69, 1):
        #self.neo[j] = (0, 20, 20)
      for i in range(200, -10, -10):
        if self.count == 0:
          for j in range(61, 69, 1):    #(52, 60, 1)
            self.neo[j] = (0, 0, 20)
        elif self.count == 1:
          for j in range(49, 61, 1):    #(40, 52, 1)
            self.neo[j] = (0, 0, i)
        elif self.count == 2:
          for j in range(33, 49, 1):    #(24, 40, 1)
            self.neo[j] = (0, 0, i)
        elif self.count == 3:
          for j in range(9, 33, 1):     #(0, 24, 1)
            self.neo[j] = (0, 0, i)
        self.neo.show()
        time.sleep(0.005)
        if self.mode:
          break
      if self.count == 0:
        self.on = True
      else:
        self.count -= 1

  def listenMode(self) -> None:
    self.neo.fill((255, 0, 0))
    self.neo.show()
    time.sleep(0.005)

if __name__ == "__main__":
    neo = Neo()
    while True:
      neo.listenMode()
