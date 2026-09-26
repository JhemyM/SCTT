import turtle
import random
import time
import math
import os
import sys
import subprocess
import tempfile
import wave
from functools import lru_cache

try:
    import simpleaudio as sa
except Exception:
    sa = None

# Screen setup
screen = turtle.Screen()
screen.title("SCTT - Super Competitive Table Tennis")
screen.bgcolor("black")
screen.setup(width=800, height=600)
screen.tracer(0)
current_bg = "black"

# Scores
score_a = 0
score_b = 0
POINTS_TO_WIN = 11
WIN_BY = 2
ball_active = False
game_over = False
serve_player = "left"
training_misses = 0
MAX_TRAINING_MISSES = 1
COURT_LEFT = -390
COURT_RIGHT = 390
GOAL_LEFT = -390
GOAL_RIGHT = 390
manual_visible = False
manual_show_time = 0.0
game_screen_state = "menu"
current_bg = "black"
current_court_color = "white"
current_line_width = 2
SETTINGS = {"sound": True, "effects": True, "ghosting": True, "trail_translucent": True}
GHOST_BLOCKINESS = 2
GHOST_BLOCKINESS_OPTIONS = [2, 3, 4, 5, 6, 8]
GHOST_MIN_MOVEMENT = 2

# Smooth movement state
left_move_up = False
left_move_down = False
left_move_front = False
left_move_back = False
right_move_up = False
right_move_down = False
right_move_front = False
right_move_back = False
current_mode = "single"

MODE_SETTINGS = {
    "single": {"ai_right": True, "ai_left": False, "ball_speed": 3, "win_text": "Single Player"},
    "multi": {"ai_right": False, "ai_left": False, "ball_speed": 3, "win_text": "1v1 Match"},
    "training": {"ai_right": False, "ai_left": False, "ball_speed": 4, "win_text": "Training"},
}

BACKGROUND_OPTIONS = [
    ("black", "white", 2),
    ("green", "white", 4),
    ("navy", "cyan", 3),
    ("darkred", "white", 3),
    ("purple", "white", 3),
    ("darkorange", "black", 2),
]

BALL_COLORS = ["white", "#ffd166", "#ff8fab", "#7ae582", "#9fe7ff", "#f5d9ff", "#f6f6f6"]

PADDLE_PALETTES = {
    "black": ("#00E5FF", "#FFD93D"),
    "green": ("#7CFF6B", "#FFB703"),
    "navy": ("#7AF7FF", "#FF66C4"),
    "darkred": ("#F6D365", "#7BF1A8"),
    "purple": ("#C77DFF", "#48CAE4"),
    "darkorange": ("#7BDFF2", "#FF9F1C"),
}

FIELD_CONTRAST = {
    "black": ("#ffffff", "#FFD93D"),
    "green": ("#f1fff2", "#FF5D8F"),
    "navy": ("#dff7ff", "#FFB703"),
    "darkred": ("#fff4f4", "#7BF1A8"),
    "purple": ("#f7ebff", "#FF66C4"),
    "darkorange": ("#fff4d9", "#7CFF6B"),
}

# Court drawing
court = turtle.Turtle()
court.speed(0)
court.hideturtle()
court.penup()
court.color("white")

# Draw table lines
court.goto(-380, -280)
court.pendown()
for _ in range(2):
    court.forward(760)
    court.left(90)
    court.forward(560)
    court.left(90)

court.penup()
court.goto(0, -280)
court.pendown()
court.setheading(90)
court.forward(560)

court.penup()
court.goto(-380, 0)
court.pendown()
court.setheading(0)
for _ in range(2):
    court.forward(760)
    court.left(90)
    court.forward(0)
    court.left(90)

court.penup()

# Paddles
left_paddle = turtle.Turtle()
left_paddle.speed(0)
left_paddle.shape("square")
left_paddle.color("white")
left_paddle.shapesize(stretch_wid=5, stretch_len=1)
left_paddle.penup()
left_paddle.goto(-350, 0)

right_paddle = turtle.Turtle()
right_paddle.speed(0)
right_paddle.shape("square")
right_paddle.color("white")
right_paddle.shapesize(stretch_wid=5, stretch_len=1)
right_paddle.penup()
right_paddle.goto(350, 0)

# Ball
BALL_SPEED = 3
ball = turtle.Turtle()
ball.speed(0)
ball.shape("circle")
ball.color("white")
ball.penup()
ball.goto(0, 0)
ball.dx = BALL_SPEED
ball.dy = BALL_SPEED

# Scoreboard
pen = turtle.Turtle()
pen.speed(0)
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("0   0", align="center", font=("Verdana", 24, "bold"))

# Ghost trail layer
ghost_layer = turtle.Turtle()
ghost_layer.speed(0)
ghost_layer.hideturtle()
ghost_layer.penup()

ghost_layers = {
    "left": turtle.Turtle(),
    "right": turtle.Turtle(),
    "ball": turtle.Turtle(),
}
for layer in ghost_layers.values():
    layer.speed(0)
    layer.hideturtle()
    layer.penup()

# Window title styling (cool display text)
screen._root.title("SCTT - Super Competitive Table Tennis")

# Movement functions

def move_left_paddle_up():
    global left_move_up
    left_move_up = True


def move_left_paddle_down():
    global left_move_down
    left_move_down = True


def stop_left_paddle_up():
    global left_move_up
    left_move_up = False


def stop_left_paddle_down():
    global left_move_down
    left_move_down = False


def move_left_paddle_front():
    global left_move_front
    left_move_front = True


def move_left_paddle_back():
    global left_move_back
    left_move_back = True


def stop_left_paddle_front():
    global left_move_front
    left_move_front = False


def stop_left_paddle_back():
    global left_move_back
    left_move_back = False


def move_right_paddle_up():
    global right_move_up
    right_move_up = True


def move_right_paddle_down():
    global right_move_down
    right_move_down = True


def stop_right_paddle_up():
    global right_move_up
    right_move_up = False


def stop_right_paddle_down():
    global right_move_down
    right_move_down = False


def move_right_paddle_front():
    global right_move_front
    right_move_front = True


def move_right_paddle_back():
    global right_move_back
    right_move_back = True


def stop_right_paddle_front():
    global right_move_front
    right_move_front = False


def stop_right_paddle_back():
    global right_move_back
    right_move_back = False


@lru_cache(maxsize=128)
def _build_tone_samples(frequency, duration_ms, volume=0.7, brightness=1.15):
    sample_rate = 44100
    seconds = max(0.01, duration_ms / 1000.0)
    total_samples = max(1, int(sample_rate * seconds))
    samples = []
    attack_time = min(0.06, seconds * 0.18)
    release_tail = max(0.04, seconds * 0.2)
    amplitude = max(0.0, min(1.25, volume))

    for i in range(total_samples):
        t = i / sample_rate
        sustain = max(0.0, 1.0 - (t / max(0.001, seconds)))
        attack_curve = min(1.0, t / max(0.001, attack_time))
        release_curve = max(0.08, sustain)
        envelope = (attack_curve * 1.1) * (release_curve ** 0.8)

        phase = 2 * math.pi * frequency * t
        waveform = (
            math.sin(phase)
            + 0.8 * math.sin(2 * phase + 0.25)
            + 0.45 * math.sin(3 * phase + 0.55)
            + 0.22 * math.sin(4 * phase + 0.9)
        ) / 1.7

        shimmer = 0.12 * math.sin(2 * math.pi * (frequency * 8.0) * t + 0.7)
        buzz = random.uniform(-0.025, 0.025) * max(0.0, 1.0 - t / max(0.001, seconds))
        value = waveform * brightness + shimmer + buzz
        sample = int(max(-1.0, min(1.0, value)) * 32767 * amplitude * envelope)
        samples.append(sample)

    return sample_rate, tuple(samples)


def _play_os_tone(frequency, duration_ms, volume=0.7):
    try:
        sample_rate, frames = _build_tone_samples(frequency, duration_ms, volume, brightness=1.3)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wave_file:
            temp_path = wave_file.name

        with wave.open(temp_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b"".join(int(v).to_bytes(2, byteorder="little", signed=True) for v in frames))

        if sys.platform.startswith("darwin"):
            subprocess.Popen(["afplay", temp_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif os.name == "nt":
            subprocess.Popen(["powershell", "-c", f"(New-Object Media.SoundPlayer '{temp_path}').PlaySync()"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            for player in ("aplay", "paplay", "play", "ffplay"):
                if subprocess.run(["sh", "-c", f"command -v {player}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                    subprocess.Popen([player, temp_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    break
    except Exception:
        return


def play_tone(frequency, duration_ms, volume=0.7):
    if not SETTINGS["sound"]:
        return
    if sa is not None:
        try:
            sample_rate, samples = _build_tone_samples(frequency, duration_ms, volume, brightness=1.35)
            audio = bytearray()
            for sample in samples:
                audio.extend(sample.to_bytes(2, byteorder="little", signed=True))
            sound = sa.WaveObject(audio, 1, 2, sample_rate)
            sound.play()
            return sound
        except Exception:
            pass
    _play_os_tone(frequency, duration_ms, volume)


def play_paddle_sound():
    if not SETTINGS["sound"]:
        return
    play_tone(1600, 32, 0.95)
    time.sleep(0.005)
    play_tone(1200, 23, 0.82)
    time.sleep(0.004)
    play_tone(980, 18, 0.68)


def play_score_sound():
    if not SETTINGS["sound"]:
        return
    play_tone(240, 170, 0.9)
    time.sleep(0.03)
    play_tone(420, 170, 0.97)
    time.sleep(0.03)
    play_tone(620, 200, 1.02)
    time.sleep(0.04)
    play_tone(820, 230, 1.08)
    time.sleep(0.03)
    play_tone(1100, 180, 0.96)


def play_single_player_result_sound(player_won):
    if not SETTINGS["sound"]:
        return
    if player_won:
        for freq in (560, 720, 930, 1180, 1440):
            play_tone(freq, 200, 0.96)
            time.sleep(0.04)
    else:
        for freq in (260, 205, 165, 125, 92):
            play_tone(freq, 230, 0.9)
            time.sleep(0.05)


def play_menu_sound():
    if not SETTINGS["sound"]:
        return
    play_tone(560, 75, 0.85)
    time.sleep(0.024)
    play_tone(840, 85, 0.96)


def play_serve_sound():
    if not SETTINGS["sound"]:
        return
    play_tone(760, 90, 0.92)
    time.sleep(0.028)
    play_tone(1040, 130, 1.0)


def update_score():
    pen.clear()
    pen.hideturtle()
    pen.write(f"{score_a}   {score_b}", align="center", font=("Verdana", 24, "bold"))


def reset_paddles_to_start():
    left_paddle.goto(-350, 0)
    right_paddle.goto(350, 0)


def apply_paddle_palette():
    left_color, right_color = PADDLE_PALETTES.get(current_bg, ("white", "white"))
    left_paddle.color(left_color)
    right_paddle.color(right_color)


def apply_visual_theme():
    global current_bg
    if not current_bg:
        current_bg = BACKGROUND_OPTIONS[0][0]
    left_color, right_color = PADDLE_PALETTES.get(current_bg, ("white", "white"))
    field_text_color, ball_color = FIELD_CONTRAST.get(current_bg, ("white", "white"))
    outline_color = "#111111" if current_bg in {"green", "darkorange"} else "#ffffff"
    if ball_color == left_color or ball_color == right_color:
        ball_color = "#FFFFFF" if current_bg in {"green", "navy", "purple", "darkorange"} else "#FFD93D"
    screen.bgcolor(current_bg)
    left_paddle.fillcolor(left_color)
    left_paddle.pencolor(outline_color)
    right_paddle.fillcolor(right_color)
    right_paddle.pencolor(outline_color)
    pen.color(field_text_color)
    ball.fillcolor(ball_color)
    ball.pencolor(outline_color)
    court.color(current_court_color)
    court.pensize(current_line_width)


def flash_paddles_after_score():
    if not SETTINGS["effects"]:
        return
    original_left = left_paddle.fillcolor()
    original_right = right_paddle.fillcolor()
    original_outline = left_paddle.pencolor()
    for _ in range(4):
        left_paddle.fillcolor("white")
        right_paddle.fillcolor("white")
        left_paddle.pencolor("white")
        right_paddle.pencolor("white")
        screen.update()
        time.sleep(0.04)
        left_paddle.fillcolor(original_left)
        right_paddle.fillcolor(original_right)
        left_paddle.pencolor(original_outline)
        right_paddle.pencolor(original_outline)
        screen.update()
        time.sleep(0.04)


def reset_ball_for_serve(scoring_player):
    global serve_player, ball_active
    serve_player = scoring_player
    clear_ghost_trail_history()
    reset_paddles_to_start()
    ball.goto(-200 if serve_player == "left" else 200, 0)
    ball.dx = 0
    ball.dy = 0
    ball_active = False


def launch_ball():
    global ball_active
    if game_over or ball_active:
        return
    ball_active = True
    play_serve_sound()
    direction = 1 if serve_player == "left" else -1
    ball.dx = direction * BALL_SPEED
    ball.dy = random.choice([-2, -1, 0, 1, 2])


def check_for_match_win():
    global game_over
    if game_over:
        return
    if current_mode == "training":
        if training_misses >= MAX_TRAINING_MISSES:
            game_over = True
            pen.clear()
            show_match_end_screen("Training failed!")
        return
    if (score_a >= POINTS_TO_WIN or score_b >= POINTS_TO_WIN) and abs(score_a - score_b) >= WIN_BY:
        game_over = True
        pen.clear()
        winner = "Left" if score_a > score_b else "Right"
        winner_text = f"Player {winner} wins!"
        if current_mode == "single":
            play_single_player_result_sound(score_a > score_b)
        show_match_end_screen(winner_text)


def draw_court():
    court.clear()
    court.speed(0)
    court.hideturtle()
    court.penup()
    court.color(current_court_color)
    court.pensize(current_line_width)

    court.goto(-380, -280)
    court.pendown()
    for _ in range(2):
        court.forward(760)
        court.left(90)
        court.forward(560)
        court.left(90)

    court.penup()
    court.goto(0, -280)
    court.pendown()
    court.setheading(90)
    court.forward(560)

    court.penup()
    court.goto(-380, 0)
    court.pendown()
    court.setheading(0)
    for _ in range(2):
        court.forward(760)
        court.left(90)
        court.forward(0)
        court.left(90)

    court.penup()


def set_random_background():
    global current_bg, current_court_color, current_line_width
    current_bg, current_court_color, current_line_width = random.choice(BACKGROUND_OPTIONS)
    apply_visual_theme()
    draw_court()


def menu_text():
    menu = turtle.Turtle()
    menu.hideturtle()
    menu.penup()
    menu.color("white")
    menu.goto(0, 180)
    menu.write("SCTT", align="center", font=("Verdana", 32, "bold"))
    menu.goto(0, 120)
    menu.write("SELECT MODE", align="center", font=("Verdana", 28, "bold"))
    menu.goto(0, 40)
    menu.write("1 - Single Player", align="center", font=("Verdana", 18, "bold"))
    menu.goto(0, 0)
    menu.write("2 - Multiplayer", align="center", font=("Verdana", 18, "bold"))
    menu.goto(0, -40)
    menu.write("3 - Training", align="center", font=("Verdana", 18, "bold"))
    menu.goto(0, -80)
    menu.write("4 - Options", align="center", font=("Verdana", 18, "bold"))
    menu.goto(0, -120)
    menu.write("M - Manual", align="center", font=("Verdana", 14, "bold"))
    return menu


def show_options_menu():
    global game_screen_state
    game_screen_state = "options"
    play_menu_sound()
    menu.clear()
    menu.goto(0, 180)
    menu.write("OPTIONS", align="center", font=("Verdana", 30, "bold"))
    menu.goto(0, 140)
    menu.write(f"1 - Sound: {'ON' if SETTINGS['sound'] else 'OFF'}", align="center", font=("Verdana", 18, "bold"))
    menu.goto(0, 100)
    menu.write(f"2 - Effects: {'ON' if SETTINGS['effects'] else 'OFF'}", align="center", font=("Verdana", 18, "bold"))
    menu.goto(0, 60)
    menu.write(f"3 - Ghosting: {'ON' if SETTINGS['ghosting'] else 'OFF'}", align="center", font=("Verdana", 18, "bold"))
    menu.goto(0, 20)
    menu.write(f"4 - Ghost Smoothness: {GHOST_BLOCKINESS} (lower = smoother)", align="center", font=("Verdana", 16, "bold"))
    menu.goto(0, -20)
    menu.write(f"5 - Trail Glow: {'ON' if SETTINGS['trail_translucent'] else 'OFF'}", align="center", font=("Verdana", 16, "bold"))
    menu.goto(0, -60)
    menu.write("6 - Back to Menu", align="center", font=("Verdana", 18, "bold"))


def show_main_menu():
    global game_screen_state
    game_screen_state = "menu"
    play_menu_sound()
    clear_ghost_trail_history()
    if current_bg:
        apply_visual_theme()
    court.clear()
    left_paddle.hideturtle()
    right_paddle.hideturtle()
    ball.hideturtle()
    pen.hideturtle()
    menu.clear()
    menu.goto(0, 180)
    menu.write("SCTT", align="center", font=("Verdana", 32, "bold"))
    menu.goto(0, 120)
    menu.write("SELECT MODE", align="center", font=("Verdana", 28, "bold"))
    menu.goto(0, 40)
    menu.write("1 - Single Player", align="center", font=("Verdana", 18, "bold"))
    menu.goto(0, 0)
    menu.write("2 - Multiplayer", align="center", font=("Verdana", 18, "bold"))
    menu.goto(0, -40)
    menu.write("3 - Training", align="center", font=("Verdana", 18, "bold"))
    menu.goto(0, -80)
    menu.write("4 - Options", align="center", font=("Verdana", 18, "bold"))
    menu.goto(0, -120)
    menu.write("M - Manual", align="center", font=("Verdana", 14, "bold"))


menu = menu_text()


def show_manual():
    global manual_visible, manual_show_time
    manual_visible = not manual_visible
    if manual_visible:
        play_menu_sound()
        manual_show_time = time.monotonic()
        menu.clear()
        menu.goto(0, 180)
        menu.write("CONTROLS", align="center", font=("Verdana", 24, "bold"))
        menu.goto(0, 120)
        menu.write("Left: W/S + A/D", align="center", font=("Verdana", 16, "bold"))
        menu.goto(0, 80)
        menu.write("Right: Up/Down + Left/Right", align="center", font=("Verdana", 16, "bold"))
        menu.goto(0, 40)
        menu.write("Space = Start Serve", align="center", font=("Verdana", 16, "bold"))
        menu.goto(0, 0)
        menu.write("R = Reset", align="center", font=("Verdana", 16, "bold"))
        menu.goto(0, -40)
        menu.write("1-2-3 = Mode Select", align="center", font=("Verdana", 16, "bold"))
        menu.goto(0, -80)
        menu.write("M = Back to Menu", align="center", font=("Verdana", 16, "bold"))
    else:
        menu.clear()


def hide_manual_if_needed():
    global manual_visible
    if manual_visible and time.monotonic() - manual_show_time > 2.5:
        manual_visible = False
        menu.clear()


def choose_mode(mode_name):
    global current_mode, manual_visible, game_screen_state
    current_mode = mode_name
    manual_visible = False
    game_screen_state = "game"
    play_menu_sound()
    apply_visual_theme()
    menu.clear()
    menu.hideturtle()
    left_paddle.showturtle()
    right_paddle.showturtle()
    ball.showturtle()
    pen.hideturtle()
    global right_move_up, right_move_down, right_move_front, right_move_back
    right_move_up = False
    right_move_down = False
    right_move_front = False
    right_move_back = False
    reset_game()


def show_match_end_screen(winner_text):
    global game_screen_state
    game_screen_state = "match_end"
    clear_ghost_trail_history()
    menu.clear()
    menu.goto(0, 120)
    menu.write(winner_text, align="center", font=("Verdana", 28, "bold"))
    menu.goto(0, 40)
    menu.write("1 - Play Again", align="center", font=("Verdana", 18, "bold"))
    menu.goto(0, -10)
    menu.write("2 - Main Menu", align="center", font=("Verdana", 18, "bold"))
    left_paddle.hideturtle()
    right_paddle.hideturtle()
    ball.hideturtle()
    pen.hideturtle()


def handle_match_end_choice(option):
    if option == 1:
        play_menu_sound()
        choose_mode(current_mode)
    elif option == 2:
        play_menu_sound()
        show_main_menu()


def handle_options_choice(option):
    global GHOST_BLOCKINESS
    if option == 1:
        SETTINGS["sound"] = not SETTINGS["sound"]
    elif option == 2:
        SETTINGS["effects"] = not SETTINGS["effects"]
    elif option == 3:
        SETTINGS["ghosting"] = not SETTINGS["ghosting"]
        if not SETTINGS["ghosting"]:
            clear_ghost_trail_history()
    elif option == 4:
        current_index = GHOST_BLOCKINESS_OPTIONS.index(GHOST_BLOCKINESS)
        next_index = (current_index + 1) % len(GHOST_BLOCKINESS_OPTIONS)
        GHOST_BLOCKINESS = GHOST_BLOCKINESS_OPTIONS[next_index]
    elif option == 5:
        SETTINGS["trail_translucent"] = not SETTINGS["trail_translucent"]
        if not SETTINGS["trail_translucent"]:
            clear_ghost_trail_history()
    elif option == 6:
        play_menu_sound()
        show_main_menu()
        return
    play_menu_sound()
    show_options_menu()


def toggle_computer_mode():
    choose_mode("single" if current_mode != "single" else "multi")


def reset_game():
    global score_a, score_b, ball_active, game_over, serve_player, training_misses
    score_a = 0
    score_b = 0
    ball_active = False
    game_over = False
    serve_player = "left"
    training_misses = 0
    clear_ghost_trail_history()
    set_random_background()
    reset_paddles_to_start()
    update_score()
    reset_ball_for_serve("left")
    pen.clear()
    pen.hideturtle()
    pen.write(f"{score_a}   {score_b}", align="center", font=("Verdana", 24, "bold"))


def maybe_auto_serve():
    if game_over or ball_active:
        return
    if current_mode == "single" and MODE_SETTINGS[current_mode]["ai_right"] and serve_player == "right":
        launch_ball()


# Keyboard bindings
screen.listen()
screen.onkeypress(lambda: handle_options_choice(1) if game_screen_state == "options" else handle_match_end_choice(1) if game_screen_state == "match_end" else choose_mode("single"), "1")
screen.onkeypress(lambda: handle_options_choice(2) if game_screen_state == "options" else handle_match_end_choice(2) if game_screen_state == "match_end" else choose_mode("multi"), "2")
screen.onkeypress(lambda: handle_options_choice(3) if game_screen_state == "options" else handle_match_end_choice(2) if game_screen_state == "match_end" else choose_mode("training"), "3")
screen.onkeypress(lambda: handle_options_choice(4) if game_screen_state == "options" else show_options_menu() if game_screen_state == "menu" else None, "4")
screen.onkeypress(lambda: handle_options_choice(5) if game_screen_state == "options" else None, "5")
screen.onkeypress(lambda: handle_options_choice(6) if game_screen_state == "options" else None, "6")
for key in ("m", "M"):
    screen.onkeypress(show_manual, key)
for key in ("o", "O"):
    screen.onkeypress(show_options_menu, key)
for key in ("w", "W"):
    screen.onkeypress(move_left_paddle_up, key)
    screen.onkeyrelease(stop_left_paddle_up, key)
for key in ("s", "S"):
    screen.onkeypress(move_left_paddle_down, key)
    screen.onkeyrelease(stop_left_paddle_down, key)
for key in ("d", "D"):
    screen.onkeypress(move_left_paddle_front, key)
    screen.onkeyrelease(stop_left_paddle_front, key)
for key in ("a", "A"):
    screen.onkeypress(move_left_paddle_back, key)
    screen.onkeyrelease(stop_left_paddle_back, key)
screen.onkeypress(move_right_paddle_up, "Up")
screen.onkeyrelease(stop_right_paddle_up, "Up")
screen.onkeypress(move_right_paddle_down, "Down")
screen.onkeyrelease(stop_right_paddle_down, "Down")
screen.onkeypress(move_right_paddle_front, "Right")
screen.onkeyrelease(stop_right_paddle_front, "Right")
screen.onkeypress(move_right_paddle_back, "Left")
screen.onkeyrelease(stop_right_paddle_back, "Left")
for key in ("r", "R"):
    screen.onkeypress(reset_game, key)
screen.onkeypress(launch_ball, "space")

trail_history = {"left": [], "right": [], "ball": []}


def clear_ghost_trail_history():
    for history in trail_history.values():
        history.clear()
    for layer in ghost_layers.values():
        try:
            layer.clearstamps()
        except Exception:
            pass
        try:
            layer.clear()
        except Exception:
            pass
        try:
            layer.hideturtle()
            layer.penup()
            layer.setposition(0, 0)
        except Exception:
            pass


# Initial serve
clear_ghost_trail_history()
show_main_menu()


_ghost_style_cache = {}

def get_object_ghost_style(obj):
    obj_id = id(obj)
    fill_color = obj.fillcolor()
    
    if obj_id in _ghost_style_cache and _ghost_style_cache[obj_id]["raw_color"] == fill_color:
        cached = _ghost_style_cache[obj_id]
        return {
            "x": obj.xcor(),
            "y": obj.ycor(),
            "color": cached["color"],
            "shape": cached["shape"],
            "size_x": cached["size_x"],
            "size_y": cached["size_y"],
        }

    raw_color = fill_color
    if isinstance(fill_color, tuple):
        r, g, b = fill_color[:3]
        fill_color = "#{:02x}{:02x}{:02x}".format(
            int(max(0, min(255, round(r * 255)))),
            int(max(0, min(255, round(g * 255)))),
            int(max(0, min(255, round(b * 255)))),
        )
    shape_size = obj.shapesize()
    shape_name = obj.shape()
    
    _ghost_style_cache[obj_id] = {
        "raw_color": raw_color,
        "color": str(fill_color),
        "shape": shape_name,
        "size_x": float(shape_size[0]),
        "size_y": float(shape_size[1]),
    }
    cached = _ghost_style_cache[obj_id]
    
    return {
        "x": obj.xcor(),
        "y": obj.ycor(),
        "color": cached["color"],
        "shape": cached["shape"],
        "size_x": cached["size_x"],
        "size_y": cached["size_y"],
    }


def clear_ghost_layers():
    for layer in ghost_layers.values():
        try:
            layer.clearstamps()
        except Exception:
            pass


@lru_cache(maxsize=256)
def mix_with_white(color_hex, weight):
    weight = round(weight, 2)
    color_hex = str(color_hex).lstrip('#')
    if len(color_hex) != 6:
        return color_hex
    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)
    r = int(r + (255 - r) * weight)
    g = int(g + (255 - g) * weight)
    b = int(b + (255 - b) * weight)
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def update_ghost_trails():
    try:
        if not screen._root.winfo_exists():
            raise SystemExit

        if not SETTINGS["ghosting"]:
            clear_ghost_trail_history()
            return

        total_trails = 22
        spacing = max(2, GHOST_BLOCKINESS)
        for key, obj in (("left", left_paddle), ("right", right_paddle), ("ball", ball)):
            trail = trail_history[key]
            current = get_object_ghost_style(obj)
            layer = ghost_layers[key]

            if not trail:
                trail.append(current)
            else:
                last = trail[-1]
                dx = current["x"] - last["x"]
                dy = current["y"] - last["y"]
                distance = math.hypot(dx, dy)
                if distance < GHOST_MIN_MOVEMENT:
                    if key != "ball":
                        trail.clear()
                        try:
                            layer.clearstamps()
                        except Exception:
                            pass
                        continue
                else:
                    steps = max(1, int(distance / spacing))
                    for i in range(1, steps + 1):
                        t = i / steps
                        trail.append({
                            "x": last["x"] + dx * t,
                            "y": last["y"] + dy * t,
                            "color": current["color"],
                            "shape": current["shape"],
                            "size_x": current["size_x"],
                            "size_y": current["size_y"],
                        })

            if len(trail) > total_trails:
                del trail[:len(trail) - total_trails]

            try:
                layer.clearstamps()
            except Exception:
                continue

            trail_points = list(reversed(trail))
            for index, point in enumerate(trail_points):
                fade_t = index / max(1, len(trail_points) - 1)
                fade_t = max(0.08, fade_t)
                size_scale = 0.35 + (1.0 - fade_t) * 0.7
                trail_color = point["color"]
                if SETTINGS["trail_translucent"]:
                    trail_color = mix_with_white(trail_color, 0.42 * (1.0 - fade_t))
                layer.penup()
                layer.setposition(point["x"], point["y"])
                layer.shape(point["shape"])
                layer.shapesize(point["size_x"] * size_scale, point["size_y"] * size_scale)
                layer.color(trail_color)
                layer.pencolor(trail_color)
                try:
                    layer.stamp()
                except Exception:
                    continue
    except SystemExit:
        raise
    except Exception as exc:
        if any(token in str(exc) for token in ("application has been destroyed", "invalid command name", "!canvas")):
            raise SystemExit
        raise


screen_update = screen.update
sleep = time.sleep

# Main game loop
while True:
    try:
        screen_update()
        sleep(0.01)
        hide_manual_if_needed()
        state = game_screen_state
        if state == "game":
            update_ghost_trails()
        else:
            clear_ghost_trail_history()
            screen.update()

        if state != "game":
            continue
    except Exception as exc:
        if "invalid command name" in str(exc) or "!canvas" in str(exc):
            break
        raise

    if left_move_up:
        y = left_paddle.ycor() + 5
        if y < 250:
            left_paddle.sety(y)
    if left_move_down:
        y = left_paddle.ycor() - 5
        if y > -250:
            left_paddle.sety(y)
    if current_mode != "single":
        if right_move_up:
            y = right_paddle.ycor() + 5
            if y < 250:
                right_paddle.sety(y)
        if right_move_down:
            y = right_paddle.ycor() - 5
            if y > -250:
                right_paddle.sety(y)
        if right_move_front:
            x = right_paddle.xcor() + 4
            if x < 380:
                right_paddle.setx(x)
        if right_move_back:
            x = right_paddle.xcor() - 4
            if x > 20:
                right_paddle.setx(x)
    if left_move_front:
        x = left_paddle.xcor() + 4
        if x < -20:
            left_paddle.setx(x)
    if left_move_back:
        x = left_paddle.xcor() - 4
        if x > -380:
            left_paddle.setx(x)

    if MODE_SETTINGS[current_mode]["ai_right"] and not game_over:
        if serve_player == "right" and not ball_active:
            maybe_auto_serve()
        target_y = ball.ycor() if ball_active else 0
        ai_speed = 4.2 if ball_active else 2.2
        if right_paddle.ycor() < target_y:
            right_paddle.sety(min(right_paddle.ycor() + ai_speed, 250))
        elif right_paddle.ycor() > target_y:
            right_paddle.sety(max(right_paddle.ycor() - ai_speed, -250))

    if not game_over and ball_active:
        ball.setx(ball.xcor() + ball.dx)
        ball.sety(ball.ycor() + ball.dy)

        # Border checks
        if ball.ycor() > 290 or ball.ycor() < -290:
            ball.dy *= -1

        # Goals are checked before any wall bounce so the score can register reliably.
        if ball.xcor() >= GOAL_RIGHT:
            ball.setx(GOAL_RIGHT)
        elif ball.xcor() <= GOAL_LEFT:
            ball.setx(GOAL_LEFT)

        # Paddle collisions
        bx = ball.xcor()
        by = ball.ycor()
        lx = left_paddle.xcor()
        ly = left_paddle.ycor()
        rx = right_paddle.xcor()
        ry = right_paddle.ycor()

        left_hit = (lx - 20 < bx < lx + 20) and (ly - 50 < by < ly + 50)
        right_hit = (rx - 20 < bx < rx + 20) and (ry - 50 < by < ry + 50)

        if left_hit:
            impact = (by - ly) / 50.0
            paddle_speed = 1.5 if left_move_up else -1.5 if left_move_down else 0
            if left_move_front or left_move_back:
                side_bias = 0.9 if left_move_front else -0.9 if left_move_back else 0
            else:
                side_bias = 0
            ball.dy = impact * 8 + paddle_speed + side_bias
            ball.dx = abs(ball.dx) + 0.8
            ball.setx(lx + 20)
            play_paddle_sound()
        elif right_hit:
            impact = (by - ry) / 50.0
            paddle_speed = 1.5 if right_move_up else -1.5 if right_move_down else 0
            if right_move_front or right_move_back:
                side_bias = 0.9 if right_move_front else -0.9 if right_move_back else 0
            else:
                side_bias = 0
            ball.dy = impact * 8 + paddle_speed + side_bias
            ball.dx = -(abs(ball.dx) + 0.8)
            ball.setx(rx - 20)
            play_paddle_sound()

        # Wall training mode: one life only. If the ball passes the wall, it counts as a miss.
        if current_mode == "training":
            if ball.xcor() >= GOAL_RIGHT:
                training_misses += 1
                play_score_sound()
                flash_paddles_after_score()
                check_for_match_win()
                if not game_over:
                    reset_ball_for_serve("left")
                    pen.clear()
                    pen.write(f"Misses: {training_misses}/1", align="center", font=("Verdana", 20, "bold"))
            elif ball.xcor() <= GOAL_LEFT:
                training_misses += 1
                play_score_sound()
                flash_paddles_after_score()
                check_for_match_win()
                if not game_over:
                    reset_ball_for_serve("right")
                    pen.clear()
                    pen.write(f"Misses: {training_misses}/1", align="center", font=("Verdana", 20, "bold"))
        else:
            # Score conditions
            if ball.xcor() >= GOAL_RIGHT:
                score_a += 1
                play_score_sound()
                flash_paddles_after_score()
                update_score()
                check_for_match_win()
                if not game_over:
                    reset_ball_for_serve("left")
            elif ball.xcor() <= GOAL_LEFT:
                score_b += 1
                play_score_sound()
                flash_paddles_after_score()
                update_score()
                check_for_match_win()
                if not game_over:
                    reset_ball_for_serve("right")

        # Keep the ball in a controlled range so it feels lively without drifting out of control.
        target_speed = MODE_SETTINGS[current_mode]["ball_speed"]
        max_horizontal = target_speed + 2.5
        max_vertical = target_speed + 2.5
        if abs(ball.dx) > max_horizontal:
            ball.dx = max_horizontal if ball.dx > 0 else -max_horizontal
        if abs(ball.dy) > max_vertical:
            ball.dy = max_vertical if ball.dy > 0 else -max_vertical
        if abs(ball.dx) < target_speed:
            ball.dx = target_speed if ball.dx > 0 else -target_speed
        if abs(ball.dy) < target_speed * 0.45:
            ball.dy = (target_speed * 0.45) if ball.dy >= 0 else -(target_speed * 0.45)

screen.mainloop()
