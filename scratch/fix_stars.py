import re

with open('SCTT.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace star initialization
old_star_init = """stars.append({
        "x": random.uniform(-400, 400),
        "y": random.uniform(20, 280),
        "speed": random.uniform(0.5, 2.0),
        "size": random.uniform(1, 3)
    })"""
new_star_init = """stars.append({
        "x": random.uniform(-400, 400),
        "y": random.uniform(-280, 280),
        "speed": random.uniform(1.0, 4.0),
        "size": random.uniform(1, 3)
    })"""
content = content.replace(old_star_init, new_star_init)

# Replace star update loop (reset position)
old_star_update = """        if star["x"] < -400:
            star["x"] = 400
            star["y"] = random.uniform(20, 280)"""
new_star_update = """        if star["x"] < -400:
            star["x"] = 400
            star["y"] = random.uniform(-280, 280)"""
content = content.replace(old_star_update, new_star_update)

# Replace laser logic
old_laser_logic = """    if random.random() < 0.02: # 2% chance per frame to spawn a laser
        lasers.append({
            "x": 400,
            "y": random.uniform(-250, 250),
            "speed": random.uniform(15, 25),"""
new_laser_logic = """    if random.random() < 0.05: # 5% chance per frame to spawn a laser
        lasers.append({
            "x": 400,
            "y": random.uniform(-250, 250),
            "speed": random.uniform(30, 50),"""
content = content.replace(old_laser_logic, new_laser_logic)

with open('SCTT.py', 'w', encoding='utf-8') as f:
    f.write(content)
