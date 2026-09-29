import re

with open('SCTT.py', 'r', encoding='utf-8') as f:
    content = f.read()

fx_init_code = """
# Visual Effects (Stars & Lasers)
fx_layer = turtle.Turtle()
fx_layer.hideturtle()
fx_layer.speed(0)
fx_layer.penup()

stars = []
for _ in range(40):
    stars.append({
        "x": random.uniform(-400, 400),
        "y": random.uniform(20, 280),
        "speed": random.uniform(0.5, 2.0),
        "size": random.uniform(1, 3)
    })

lasers = []

def update_background_effects():
    global current_bg
    fx_layer.clear()
    
    # Update and draw stars
    fx_layer.color("white" if current_bg not in ["#0F0C29", "#1A0033"] else "#00FFFF")
    for star in stars:
        star["x"] -= star["speed"]
        if star["x"] < -400:
            star["x"] = 400
            star["y"] = random.uniform(20, 280)
        fx_layer.goto(star["x"], star["y"])
        fx_layer.dot(star["size"])
        
    # Update and draw lasers
    if random.random() < 0.02: # 2% chance per frame to spawn a laser
        lasers.append({
            "x": 400,
            "y": random.uniform(-250, 250),
            "speed": random.uniform(15, 25),
            "length": random.uniform(40, 100),
            "color": random.choice(["#FF00FF", "#00FFFF", "#FFE600", "#39FF14"])
        })
        
    for laser in lasers[:]:
        laser["x"] -= laser["speed"]
        if laser["x"] < -500:
            lasers.remove(laser)
            continue
            
        fx_layer.color(laser["color"])
        fx_layer.pensize(3)
        fx_layer.penup()
        fx_layer.goto(laser["x"], laser["y"])
        fx_layer.pendown()
        fx_layer.goto(laser["x"] + laser["length"], laser["y"])
        fx_layer.penup()
"""

# Insert fx_init_code before `def clear_ghost_trail_history():` (which is around line 718)
# We can just put it right before `def update_ghost_trails():` or similar.
target_insert = "def update_ghost_trails():"
content = content.replace(target_insert, fx_init_code + "\n\n" + target_insert)

# Insert the function call in the main loop
loop_target = """        if state == "game":
            update_ghost_trails()"""
loop_replacement = """        if state == "game":
            update_ghost_trails()
            update_background_effects()"""
content = content.replace(loop_target, loop_replacement)

with open('SCTT.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("FX added.")
