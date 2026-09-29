import winsound
import ctypes
import time
import tempfile
import wave
import math
import sys

def create_wav(filename, freq):
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(44100)
        samples = bytearray()
        for i in range(44100 * 2): # 2 seconds
            t = i / 44100
            val = int(math.sin(2 * math.pi * freq * t) * 10000)
            samples.extend(val.to_bytes(2, byteorder='little', signed=True))
        wav_file.writeframes(samples)

temp_music = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
temp_sfx = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name

create_wav(temp_music, 400)
create_wav(temp_sfx, 1000)

print("Playing BGM via winsound")
winsound.PlaySound(temp_music, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)

time.sleep(1)

print("Playing SFX via MCI")
ctypes.windll.winmm.mciSendStringW(f'open "{temp_sfx}" type waveaudio alias sfx1', None, 0, None)
ctypes.windll.winmm.mciSendStringW('play sfx1', None, 0, None)

time.sleep(2)
print("Done")
