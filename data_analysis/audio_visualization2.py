import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# PyAudio 설정
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# PyAudio 객체 초기화
audio = pyaudio.PyAudio()

# 그래프 설정
fig, ax = plt.subplots()
x = np.linspace(0, RATE / 2, CHUNK // 2)  # Nyquist 주파수까지의 주파수 축 설정
line, = ax.plot(x, np.random.rand(CHUNK // 2))  # x축 데이터 크기 조정
ax.set_ylim(0, 1024)
ax.set_xlim(0, RATE / 2)

# 스트림 콜백 함수
def callback(in_data, frame_count, time_info, status):
    data = np.frombuffer(in_data, dtype=np.int16)
    # FFT 변환
    fft_data = np.abs(np.fft.fft(data)) / CHUNK
    line.set_ydata(fft_data[:CHUNK // 2])  # Nyquist 주파수까지만 사용
    return (in_data, pyaudio.paContinue)

# 스트림 객체 생성
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

# 애니메이션 업데이트 함수
def update_line(num, line):
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
