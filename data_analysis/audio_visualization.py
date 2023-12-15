import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# PyAudio 설정
FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 16000
CHUNK = 4096

# PyAudio 객체 초기화
audio = pyaudio.PyAudio()

# 그래프 설정
fig, ax = plt.subplots()
x = np.arange(0, 2 * CHUNK, 2)
line, = ax.plot(x, np.random.rand(CHUNK))
ax.set_ylim(-10000, 10000)
ax.set_xlim(0, CHUNK)

# 스트림 콜백 함수
def callback(in_data, frame_count, time_info, status):
    data = np.frombuffer(in_data, dtype=np.int32)
    ndarray = np.fromstring(in_data, dtype=np.int32)
    scaled = (ndarray).astype(np.int32)

    line.set_ydata(scaled)
    return (scaled.tostring(), pyaudio.paContinue)

# 스트림 객체 생성
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=1,
                    stream_callback=callback)

# 애니메이션 업데이트 함수
def update_line(num, line):
    line.set_ydata(np.random.rand(CHUNK))
    return line,

# 애니메이션 객체 생성
ani = animation.FuncAnimation(fig, update_line, fargs=(line,), interval=50)

# 스트림 시작
stream.start_stream()

# 플로팅 시작
plt.show()

while stream.is_active():
    pass

# 스트림 정지 및 종료
stream.stop_stream()
stream.close()
audio.terminate()
