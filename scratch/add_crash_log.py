import re

with open('SCTT.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_raise = """    except Exception as exc:
        if "invalid command name" in str(exc) or "!canvas" in str(exc) or "application has been destroyed" in str(exc):
            break
        raise"""

new_raise = """    except Exception as exc:
        if "invalid command name" in str(exc) or "!canvas" in str(exc) or "application has been destroyed" in str(exc):
            break
        import traceback
        with open("crash.txt", "w") as crash_file:
            crash_file.write(traceback.format_exc())
        raise"""

content = content.replace(old_raise, new_raise)

# Also wrap the very startup
old_startup = """import sys
import ctypes
import math
import random
import time
import turtle
import audio"""

new_startup = """import sys
import ctypes
import math
import random
import time
import turtle
import traceback

try:
    import audio
except Exception as e:
    with open("crash_startup.txt", "w") as f:
        f.write("Startup error: " + traceback.format_exc())
    raise"""

content = content.replace(old_startup, new_startup)

with open('SCTT.py', 'w', encoding='utf-8') as f:
    f.write(content)
