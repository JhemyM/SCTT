import ctypes
import time
import math
import wave
import tempfile

def generate_wav(freq, duration, filename):
    sample_rate = 44100
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        samples = bytearray()
        total_samples = int(sample_rate * duration)
        for i in range(total_samples):
            t = i / sample_rate
            val = int(math.sin(2 * math.pi * freq * t) * 10000)
            samples.extend(val.to_bytes(2, byteorder='little', signed=True))
        wav_file.writeframes(samples)

temp_music = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
temp_sfx = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name

generate_wav(400, 5.0, temp_music) # 5 sec music
generate_wav(1200, 0.5, temp_sfx) # 0.5 sec sfx

# Play music in loop
ctypes.windll.winmm.mciSendStringW(f'open "{temp_music}" alias bgm', None, 0, None)
ctypes.windll.winmm.mciSendStringW('play bgm repeat', None, 0, None)

time.sleep(1)

# Play SFX without stopping music
ctypes.windll.winmm.mciSendStringW(f'open "{temp_sfx}" alias sfx1', None, 0, None)
ctypes.windll.winmm.mciSendStringW('play sfx1', None, 0, None)

time.sleep(2)
print("Done")
