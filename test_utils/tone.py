import pyaudio
from pyaudio import paFloat32, paContinue
from numpy import pi, sin, arange, float32, zeros
import sys

tones = sys.argv[1:]
rate = 44100
offset = 0.0
def play(in_data, frames, time_info, status):
    global offset
    out = zeros(frames,dtype=float32)
    for t in tones:
        out += sin((arange(frames,dtype=float32)+offset)*2*pi*float(t)/rate)
    out /= len(tones)
    offset += frames
    return (out, paContinue)

p = pyaudio.PyAudio()
s = p.open(format=paFloat32,
           channels=1,
           rate=rate,
           output=True,
           stream_callback=play)

s.start_stream()
input('Press key to stop.')
s.stop_stream()
s.close()
p.terminate()


