import re

# 1. Fix SCTT.py
with open('SCTT.py', 'r', encoding='utf-8') as f:
    sctt_content = f.read()

# Make background effects run everywhere
old_loop = """        if state == "game":
            update_ghost_trails()
            update_background_effects()
        else:
            clear_ghost_trail_history()
            screen.update()"""
new_loop = """        update_background_effects()
        if state == "game":
            update_ghost_trails()
        else:
            clear_ghost_trail_history()
            screen.update()"""
sctt_content = sctt_content.replace(old_loop, new_loop)

# Change font from "Courier New" to "Fixedsys" (a very retro DOS/arcade looking font built into Windows)
sctt_content = sctt_content.replace('"Courier New"', '"Fixedsys"')
sctt_content = sctt_content.replace("'Courier New'", "'Fixedsys'")

with open('SCTT.py', 'w', encoding='utf-8') as f:
    f.write(sctt_content)


# 2. Fix audio.py
with open('audio.py', 'r', encoding='utf-8') as f:
    audio_content = f.read()

# Remove threading and call init directly to ensure MCI works on the main thread
old_thread = "threading.Thread(target=init_audio_system, daemon=True).start()"
new_init = "init_audio_system()"
audio_content = audio_content.replace(old_thread, new_init)

with open('audio.py', 'w', encoding='utf-8') as f:
    f.write(audio_content)

print("Patched SCTT.py and audio.py")
