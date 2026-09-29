import re

with open('SCTT.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add resource_path function
resource_path_code = """
def resource_path(relative_path):
    \"\"\" Get absolute path to resource, works for dev and for PyInstaller \"\"\"
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
"""

if "def resource_path" not in content:
    content = content.replace("try:\n    import simpleaudio as sa", resource_path_code + "\ntry:\n    import simpleaudio as sa")

# Add the icon setting code
icon_code = """
# Screen setup
screen = turtle.Screen()
try:
    # Attempt to set the window icon
    screen._root.iconbitmap(resource_path("icon.ico"))
except Exception:
    pass
"""

content = content.replace("# Screen setup\nscreen = turtle.Screen()", icon_code)

with open('SCTT.py', 'w', encoding='utf-8') as f:
    f.write(content)
