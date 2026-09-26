import ctypes
import os
import sys
import subprocess
import tempfile
import wave
import math
import random
import threading
import time
from functools import lru_cache

class AudioConfig:
    enabled = True
    music_enabled = True

# MCI Audio Player (Windows only, multi-channel)
_mci_aliases = set()
_mci_counter = 0

def _play_mci(wav_path, loop=False, volume=1.0):
    global _mci_counter
    try:
        alias = f"track_{_mci_counter}"
        _mci_counter += 1
        
        # Windows API to play multiple overlapping sounds
        cmd_open = f'open "{wav_path}" type waveaudio alias {alias}'
        ctypes.windll.winmm.mciSendStringW(cmd_open, None, 0, None)
        
        # Set volume (1000 is max)
        vol_int = int(min(1.0, max(0.0, volume)) * 1000)
        ctypes.windll.winmm.mciSendStringW(f'setaudio {alias} volume to {vol_int}', None, 0, None)
        
        cmd_play = f'play {alias} {"repeat" if loop else ""}'
        ctypes.windll.winmm.mciSendStringW(cmd_play, None, 0, None)
        
        # Auto-cleanup for non-looping sounds
        if not loop:
            _mci_aliases.add(alias)
            # We don't close immediately so it can play
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

# ----- MUSIC GENERATOR -----
# We generate a 16-second looping synthwave track (Molchat Doma / Kavinsky style)
# Tempo: 120 BPM -> 0.5 sec per beat. 16 seconds = 32 beats = 8 bars.

def _synth_kick(t):
    # Punchy kick drum
    freq = 150 * math.exp(-40 * t) + 40
    phase = 2 * math.pi * freq * t
    env = math.exp(-15 * t)
    return math.sin(phase) * env * 0.9

def _synth_snare(t):
    # White noise snare
    noise = random.uniform(-1.0, 1.0)
    # Body
    freq = 200 * math.exp(-30 * t)
    body = math.sin(2 * math.pi * freq * t)
    env = math.exp(-25 * t)
    return (noise * 0.6 + body * 0.4) * env * 0.7

def _synth_hihat(t):
    # Ticking hi-hat
    noise = random.uniform(-1.0, 1.0)
    env = math.exp(-40 * t)
    return noise * env * 0.3

def _synth_bass(t, note_freq):
    # Driving sawtooth bass
    phase = 2 * math.pi * note_freq * t
    # Sawtooth approximation
    wave = 2 * (t * note_freq - math.floor(t * note_freq + 0.5))
    env = math.exp(-5 * t)
    # Lowpass filter effect via simple smoothing could be done, but we'll keep it raw
    return wave * env * 0.5

def _synth_arp(t, note_freq):
    # Plucky square wave arpeggio
    phase = 2 * math.pi * note_freq * t
    wave = 1.0 if math.sin(phase) > 0 else -1.0
    env = math.exp(-12 * t)
    return wave * env * 0.35

def build_bgm_track():
    sample_rate = 22050 # Lower sample rate for faster generation & retro feel
    duration = 16.0
    total_samples = int(sample_rate * duration)
    samples = []
    
    bpm = 120.0
    sec_per_beat = 60.0 / bpm
    sec_per_16th = sec_per_beat / 4.0
    
    # Bassline sequence (A minor: A2, F2, C3, G2)
    bass_notes = [110.0, 87.31, 130.81, 98.00] 
    arp_chords = [
        [220.0, 261.63, 329.63], # Am
        [174.61, 220.0, 261.63], # F
        [261.63, 329.63, 392.00], # C
        [196.00, 246.94, 293.66], # G
    ]
    
    for i in range(total_samples):
        t = i / sample_rate
        
        # Timeline positions
        beat_time = t % sec_per_beat
        bar_time = t % (sec_per_beat * 4)
        total_beats = int(t / sec_per_beat)
        sixteenth_time = t % sec_per_16th
        total_16ths = int(t / sec_per_16th)
        bar_idx = int(t / (sec_per_beat * 4))
        
        mix = 0.0
        
        # 1. KICK (Every beat)
        mix += _synth_kick(beat_time)
        
        # 2. SNARE (Beats 2 and 4)
        if total_beats % 2 == 1:
            mix += _synth_snare(beat_time)
            
        # 3. HI-HAT (Every 16th, slightly quieter on downbeats)
        hh_vol = 1.0 if total_16ths % 2 != 0 else 0.5
        mix += _synth_hihat(sixteenth_time) * hh_vol
        
        # 4. BASSLINE (Driving 8th notes)
        eighth_time = t % (sec_per_beat / 2.0)
        current_bass_note = bass_notes[bar_idx % 4]
        mix += _synth_bass(eighth_time, current_bass_note)
        
        # 5. ARPEGGIO (16th notes playing chord tones)
        current_chord = arp_chords[bar_idx % 4]
        arp_note = current_chord[total_16ths % 3]
        mix += _synth_arp(sixteenth_time, arp_note)
        
        # Soft clipping limiter
        val = max(-1.0, min(1.0, mix * 0.6))
        samples.append(int(val * 32767))
        
    return sample_rate, tuple(samples)


# ----- SFX GENERATOR -----
@lru_cache(maxsize=32)
def _build_effect_samples(effect_name):
    sample_rate = 44100
    samples = []
    
    if effect_name == "paddle":
        duration = 0.08
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            freq = 1800 * math.exp(-40 * t) + 400
            wave = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            noise = random.uniform(-1.0, 1.0) * math.exp(-200 * t)
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
            phase = 2 * math.pi * freq * t
            wave = (math.sin(phase) + math.sin(2 * phase)*0.5) / 1.5
            env = math.exp(-15 * local_t)
            val = wave * env * 0.8
            samples.append(int(max(-1.0, min(1.0, val)) * 32767))
            
    elif effect_name == "serve":
        duration = 0.15
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            freq = 400 + (1200 * (t / duration))
            wave = math.sin(2 * math.pi * freq * t)
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
            phase = 2 * math.pi * freq * t
            wave = (1.0 if math.sin(phase) > 0 else -1.0) * 0.4 + math.sin(phase) * 0.6
            env = math.exp(-5 * local_t)
            val = wave * env * 0.8
            samples.append(int(max(-1.0, min(1.0, val)) * 32767))

    elif effect_name == "lose":
        duration = 1.0
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            freq = 300 - (150 * (t / duration))
            wave = 2 * (t * freq - math.floor(t * freq + 0.5))
            env = math.exp(-3 * t)
            val = wave * env * 0.7
            samples.append(int(max(-1.0, min(1.0, val)) * 32767))

    elif effect_name == "menu":
        duration = 0.05
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            wave = math.sin(2 * math.pi * 800 * t)
            env = math.exp(-60 * t)
            val = wave * env * 0.8
            samples.append(int(max(-1.0, min(1.0, val)) * 32767))

    return sample_rate, tuple(samples)


# ----- AUDIO SYSTEM -----
_effect_files = {}
_bgm_file = None
_bgm_alias = None
_system_ready = False

def init_audio_system():
    global _bgm_file, _system_ready
    
    # 1. Pre-generate all SFX into temp files
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

    # 2. Pre-generate BGM into a temp file
    sr_bgm, frames_bgm = build_bgm_track()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wf:
        with wave.open(wf.name, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sr_bgm)
            wav_file.writeframes(b"".join(int(v).to_bytes(2, byteorder="little", signed=True) for v in frames_bgm))
        _bgm_file = wf.name

    _system_ready = True
    start_music()

def start_music():
    global _bgm_alias
    if not AudioConfig.music_enabled or not _system_ready:
        return
    if os.name == "nt":
        if _bgm_alias:
            _stop_mci(_bgm_alias)
        _bgm_alias = _play_mci(_bgm_file, loop=True, volume=0.5)

def stop_music():
    global _bgm_alias
    if _bgm_alias and os.name == "nt":
        _stop_mci(_bgm_alias)
        _bgm_alias = None

def play_effect(effect_name):
    if not AudioConfig.enabled or not _system_ready:
        return
    if effect_name in _effect_files:
        if os.name == "nt":
            _play_mci(_effect_files[effect_name], volume=1.0)
        else:
            # Fallback for linux/mac
            subprocess.Popen(["aplay" if sys.platform.startswith("linux") else "afplay", _effect_files[effect_name]], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def play_paddle_sound(): play_effect("paddle")
def play_score_sound(): play_effect("score")
def play_single_player_result_sound(player_won): play_effect("win" if player_won else "lose")
def play_menu_sound(): play_effect("menu")
def play_serve_sound(): play_effect("serve")

# Start generating audio in the background as soon as module is imported!
threading.Thread(target=init_audio_system, daemon=True).start()
