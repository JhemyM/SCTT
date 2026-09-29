import re

with open('audio.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure winsound is imported
if 'import winsound' not in content:
    content = content.replace('import ctypes', 'import ctypes\nimport winsound')

# Replace start_music / stop_music logic
old_music = """def start_music():
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
        _bgm_alias = None"""

new_music = """def start_music():
    if not AudioConfig.music_enabled or not _system_ready:
        return
    if os.name == "nt":
        # Using winsound for background music ensures it plays reliably on Windows without threading/MCI issues
        winsound.PlaySound(_bgm_file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)

def stop_music():
    if os.name == "nt":
        # Passing None stops any currently playing asynchronous winsound
        winsound.PlaySound(None, winsound.SND_PURGE)"""

content = content.replace(old_music, new_music)

# Scale down music volume in build_bgm_track so winsound doesn't blast
# It was: val = max(-1.0, min(1.0, mix * 0.6))
content = content.replace('val = max(-1.0, min(1.0, mix * 0.6))', 'val = max(-1.0, min(1.0, mix * 0.2))')

with open('audio.py', 'w', encoding='utf-8') as f:
    f.write(content)
