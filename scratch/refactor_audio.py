import re

with open('audio.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Refactor build_bgm_track to take parameters
old_build_bgm = """def build_bgm_track():
    sample_rate = 22050
    duration = 16.0
    total_samples = int(sample_rate * duration)
    samples = []
    
    bpm = 130.0
    sec_per_beat = 60.0 / bpm
    sec_per_16th = sec_per_beat / 4.0
    
    # 8-bit Synthwave Chords (Cm, Ab, Fm, G)
    bass_notes = [65.41, 51.91, 87.31, 98.00] 
    arp_chords = [
        [130.81, 155.56, 196.00], # Cm
        [103.83, 130.81, 155.56], # Ab
        [174.61, 207.65, 261.63], # Fm
        [196.00, 246.94, 293.66], # G
    ]"""

new_build_bgm = """def build_bgm_track(bpm=130.0, bass_notes=None, arp_chords=None, drum_style="synthwave"):
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
        ]"""

content = content.replace(old_build_bgm, new_build_bgm)

# Update drum logic based on style
old_drums = """        mix += _synth_kick(beat_time)
        if total_beats % 2 == 1:
            mix += _synth_snare(beat_time)
        
        hh_vol = 1.0 if total_16ths % 2 != 0 else 0.5
        mix += _synth_hihat(sixteenth_time) * hh_vol"""

new_drums = """        if drum_style == "synthwave":
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
                mix += _synth_hihat(sixteenth_time) * 0.4"""

content = content.replace(old_drums, new_drums)

# Update init system to generate multiple tracks
old_init = """def init_audio_system():
    global _bgm_file, _system_ready
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
    if not AudioConfig.music_enabled or not _system_ready:
        return
    if os.name == "nt":
        # Using winsound for background music ensures it plays reliably on Windows without threading/MCI issues
        winsound.PlaySound(_bgm_file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)"""

new_init = """
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
        winsound.PlaySound(_bgm_files[_current_track], winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)"""

content = content.replace(old_init, new_init)

with open('audio.py', 'w', encoding='utf-8') as f:
    f.write(content)
