import re

with open('SCTT.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Terminator error
old_except = """    except Exception as exc:
        if "invalid command name" in str(exc) or "!canvas" in str(exc):
            break
        raise"""

new_except = """    except turtle.Terminator:
        break
    except Exception as exc:
        if "invalid command name" in str(exc) or "!canvas" in str(exc) or "application has been destroyed" in str(exc):
            break
        raise"""

content = content.replace(old_except, new_except)

with open('SCTT.py', 'w', encoding='utf-8') as f:
    f.write(content)
