import os
import subprocess

def connect_to_open_wifi():
    networks = subprocess.getoutput("nmcli device wifi list")
    lines = networks.split("\n")[1:]

    for line in lines:
        if "WPA" not in line and "WEP" not in line:
            ssid = line.split()[1]
            os.system(f"nmcli device wifi connect {ssid}")
            break

def check_wifi_connection():
    result = os.popen("nmcli device status").read()
    return "connected" in result


if __name__ == "__main__":
  connect_to_open_wifi()

  if check_wifi_connection():
      print("Wi-Fi 연결됨")
  else:
      print("Wi-Fi 연결 안됨")