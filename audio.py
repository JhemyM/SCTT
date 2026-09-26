import ctypes
import winsound
import os
import sys
import subprocess
import tempfile
import wave
import math
import random
import threading
from functools import lru_cache

class AudioConfig:
    enabled = True
    music_enabled = True

_mci_aliases = set()
_mci_counter = 0

def _play_mci(wav_path, loop=False, volume=1.0):
    global _mci_counter
    try:
        alias = f"track_{_mci_counter}"
        _mci_counter += 1
        cmd_open = f'open "{wav_path}" type waveaudio alias {alias}'
        ctypes.windll.winmm.mciSendStringW(cmd_open, None, 0, None)
        vol_int = int(min(1.0, max(0.0, volume)) * 1000)
        ctypes.windll.winmm.mciSendStringW(f'setaudio {alias} volume to {vol_int}', None, 0, None)
        cmd_play = f'play {alias} {"repeat" if loop else ""}'
        ctypes.windll.winmm.mciSendStringW(cmd_play, None, 0, None)
        if not loop:
            _mci_aliases.add(alias)
        return alias
    except Exception:
        pass
    return None

def _stop_mci(alias):
    try:
        ctypes.windll.winmm.mciSendStringW(f'stop {alias}', None, 0, None)
        ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
    except Exception:
        pass

# 8-BIT CHIPTUNE GENERATOR
def _sq(phase, duty=0.5):
    return 1.0 if (phase % (2 * math.pi)) < (2 * math.pi * duty) else -1.0

def _tri(phase):
    p = phase / (2 * math.pi)
    return 2 * abs(2 * (p - math.floor(p + 0.5))) - 1

def _synth_kick(t):
    freq = 150 * math.exp(-40 * t) + 40
    phase = 2 * math.pi * freq * t
    wave = _tri(phase)
    env = math.exp(-15 * t)
    return wave * env * 0.9

def _synth_snare(t):
    noise = random.choice([-1.0, 1.0])
    env = math.exp(-30 * t)
    return noise * env * 0.8

def _synth_hihat(t):
    noise = random.choice([-1.0, 1.0])
    env = math.exp(-40 * t)
    return noise * env * 0.3

def _synth_bass(t, note_freq):
    phase = 2 * math.pi * note_freq * t
    wave = _sq(phase, 0.25)
    env = math.exp(-8 * t)
    return wave * env * 0.6

def _synth_arp(t, note_freq):
    phase = 2 * math.pi * note_freq * t
    wave = _sq(phase, 0.5)
    env = math.exp(-15 * t)
    return wave * env * 0.4

def build_bgm_track(bpm=130.0, bass_notes=None, arp_chords=None, drum_style="synthwave"):
    sample_rate = 22050
    duration = 16.0
    total_samples = int(sample_rate * duration)
    samples = []
    
    sec_per_beat = 60.0 / bpm
    sec_per_16th = sec_per_beat / 4.0
    
    if bass_notes is None:
        bass_notes = [65.41, 51.91, 87.31, 98.00] 
    if arp_chords is None:
        arp_chords = [
            [130.81, 155.56, 196.00], # Cm
            [103.83, 130.81, 155.56], # Ab
            [174.61, 207.65, 261.63], # Fm
            [196.00, 246.94, 293.66], # G
        ]
    
    for i in range(total_samples):
        t = i / sample_rate
        beat_time = t % sec_per_beat
        total_beats = int(t / sec_per_beat)
        sixteenth_time = t % sec_per_16th
        total_16ths = int(t / sec_per_16th)
        bar_idx = int(t / (sec_per_beat * 4))
        
        mix = 0.0
        if drum_style == "synthwave":
            mix += _synth_kick(beat_time)
            if total_beats % 2 == 1:
                mix += _synth_snare(beat_time)
            hh_vol = 1.0 if total_16ths % 2 != 0 else 0.5
            mix += _synth_hihat(sixteenth_time) * hh_vol
        elif drum_style == "kavinsky": # driving
            if total_16ths % 4 in [0, 2]:
                mix += _synth_kick(beat_time)
            if total_beats % 2 == 1:
                mix += _synth_snare(beat_time)
            mix += _synth_hihat(sixteenth_time) * 0.8
        elif drum_style == "molchat": # minimal post-punk
            mix += _synth_kick(beat_time)
            if total_beats % 2 == 1 and total_16ths % 4 == 0:
                mix += _synth_snare(beat_time)
            if total_16ths % 2 != 0:
                mix += _synth_hihat(sixteenth_time) * 0.4
        
        eighth_time = t % (sec_per_beat / 2.0)
        current_bass_note = bass_notes[bar_idx % 4]
        mix += _synth_bass(eighth_time, current_bass_note)
        
        current_chord = arp_chords[bar_idx % 4]
        arp_note = current_chord[total_16ths % 3]
        mix += _synth_arp(sixteenth_time, arp_note)
        
        # 8-bit Quantization (reduce bit depth to 8-bit artificially)
        val = max(-1.0, min(1.0, mix * 0.2))
        quantized = round(val * 127) / 127.0
        samples.append(int(quantized * 32767))
        
    return sample_rate, tuple(samples)


@lru_cache(maxsize=32)
def _build_effect_samples(effect_name):
    sample_rate = 44100
    samples = []
    
    if effect_name == "paddle":
        duration = 0.08
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            freq = 1800 * math.exp(-40 * t) + 400
            wave = _sq(2 * math.pi * freq * t, 0.5)
            noise = random.choice([-1.0, 1.0]) * math.exp(-200 * t)
            env = math.exp(-45 * t)
            val = (wave * 0.6 + noise * 0.4) * env
            samples.append(int(max(-1.0, min(1.0, val)) * 32767))

    elif effect_name == "score":
        duration = 0.6
        notes = [523.25, 659.25, 783.99, 1046.50]
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            note_idx = min(len(notes) - 1, int(t / 0.15))
            freq = notes[note_idx]
            local_t = t % 0.15
            wave = _sq(2 * math.pi * freq * t, 0.5)
            env = math.exp(-15 * local_t)
            val = wave * env * 0.8
            samples.append(int(max(-1.0, min(1.0, val)) * 32767))
            
    elif effect_name == "serve":
        duration = 0.15
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            freq = 400 + (1200 * (t / duration))
            wave = _sq(2 * math.pi * freq * t, 0.25)
            env = math.exp(-10 * t)
            val = wave * env * 0.9
            samples.append(int(max(-1.0, min(1.0, val)) * 32767))

    elif effect_name == "win":
        duration = 1.2
        notes = [440, 554, 659, 880]
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            note_idx = min(len(notes) - 1, int(t / 0.3))
            freq = notes[note_idx]
            local_t = t % 0.3
            wave = _sq(2 * math.pi * freq * t, 0.5)
            env = math.exp(-5 * local_t)
            val = wave * env * 0.8
            samples.append(int(max(-1.0, min(1.0, val)) * 32767))

    elif effect_name == "lose":
        duration = 1.0
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            freq = 300 - (150 * (t / duration))
            wave = _tri(2 * math.pi * freq * t)
            env = math.exp(-3 * t)
            val = wave * env * 0.7
            samples.append(int(max(-1.0, min(1.0, val)) * 32767))

    elif effect_name == "menu":
        duration = 0.05
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            wave = _sq(2 * math.pi * 800 * t, 0.5)
            env = math.exp(-60 * t)
            val = wave * env * 0.8
            samples.append(int(max(-1.0, min(1.0, val)) * 32767))

    return sample_rate, tuple(samples)

_effect_files = {}
_bgm_file = None
_bgm_alias = None
_system_ready = False


_bgm_files = {}
_current_track = "menu"

def init_audio_system():
    global _system_ready
    effects = ["paddle", "score", "serve", "win", "lose", "menu"]
    for eff in effects:
        sr, frames = _build_effect_samples(eff)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wf:
            with wave.open(wf.name, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sr)
                wav_file.writeframes(b"".join(int(v).to_bytes(2, byteorder="little", signed=True) for v in frames))
            _effect_files[eff] = wf.name

    # Define 3 different tracks
    tracks = {
        "menu": {"bpm": 120, "drum_style": "molchat", "bass": [55.0, 55.0, 65.41, 73.42], "arp": [[110.0, 130.81, 164.81], [110.0, 130.81, 164.81], [130.81, 155.56, 196.00], [146.83, 174.61, 220.00]]}, # Am, Am, Cm, Dm
        "game1": {"bpm": 140, "drum_style": "synthwave", "bass": [65.41, 51.91, 87.31, 98.00], "arp": [[130.81, 155.56, 196.00], [103.83, 130.81, 155.56], [174.61, 207.65, 261.63], [196.00, 246.94, 293.66]]}, # Original Cm
        "game2": {"bpm": 155, "drum_style": "kavinsky", "bass": [58.27, 58.27, 43.65, 49.00], "arp": [[116.54, 138.59, 174.61], [116.54, 138.59, 174.61], [87.31, 103.83, 130.81], [98.00, 116.54, 146.83]]} # Bbm, Bbm, F, G
    }

    for t_name, t_cfg in tracks.items():
        sr_bgm, frames_bgm = build_bgm_track(bpm=t_cfg["bpm"], bass_notes=t_cfg["bass"], arp_chords=t_cfg["arp"], drum_style=t_cfg["drum_style"])
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wf:
            with wave.open(wf.name, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sr_bgm)
                wav_file.writeframes(b"".join(int(v).to_bytes(2, byteorder="little", signed=True) for v in frames_bgm))
            _bgm_files[t_name] = wf.name

    _system_ready = True
    start_music()

def change_bgm(track_name):
    global _current_track
    if track_name in _bgm_files and _current_track != track_name:
        _current_track = track_name
        start_music()

def start_music():
    if not AudioConfig.music_enabled or not _system_ready:
        return
    if os.name == "nt":
        winsound.PlaySound(_bgm_files[_current_track], winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)

def stop_music():
    if os.name == "nt":
        # Passing None stops any currently playing asynchronous winsound
        winsound.PlaySound(None, winsound.SND_PURGE)

def play_effect(effect_name):
    if not AudioConfig.enabled or not _system_ready:
        return
    if effect_name in _effect_files:
        if os.name == "nt":
            _play_mci(_effect_files[effect_name], volume=1.0)
        else:
            subprocess.Popen(["aplay" if sys.platform.startswith("linux") else "afplay", _effect_files[effect_name]], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def play_paddle_sound(): play_effect("paddle")
def play_score_sound(): play_effect("score")
def play_single_player_result_sound(player_won): play_effect("win" if player_won else "lose")
def play_menu_sound(): play_effect("menu")
def play_serve_sound(): play_effect("serve")

init_audio_system()
