import re

with open('SCTT_Demo.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add AI for left paddle
old_left_logic = """    if left_move_up:
        y = left_paddle.ycor() + 5
        if y < 250:
            left_paddle.sety(y)
    if left_move_down:
        y = left_paddle.ycor() - 5
        if y > -250:
            left_paddle.sety(y)"""

new_left_logic = """    if True: # AI for left paddle
        target_y_left = ball.ycor() if ball_active else 0
        ai_speed_left = 4.0 if ball_active else 2.0
        if left_paddle.ycor() < target_y_left:
            left_paddle.sety(min(left_paddle.ycor() + ai_speed_left, 250))
        elif left_paddle.ycor() > target_y_left:
            left_paddle.sety(max(left_paddle.ycor() - ai_speed_left, -250))"""

content = content.replace(old_left_logic, new_left_logic)

# 2. Auto launch ball
auto_launch_code = """    if not game_over and ball_active:
        ball.setx(ball.xcor() + ball.dx)"""

new_auto_launch_code = """    if not game_over and not ball_active and state == "game":
        if not hasattr(ball, "auto_launch_timer"):
            ball.auto_launch_timer = time.time()
        elif time.time() - ball.auto_launch_timer > 1.0:
            launch_ball()
            del ball.auto_launch_timer

    if not game_over and ball_active:
        ball.setx(ball.xcor() + ball.dx)"""

content = content.replace(auto_launch_code, new_auto_launch_code)

# 3. Bypass menu
old_startup = """if __name__ == "__main__":
    show_main_menu()
    while True:"""

new_startup = """if __name__ == "__main__":
    choose_mode("single")
    while True:"""

content = content.replace(old_startup, new_startup)

with open('SCTT_Demo.py', 'w', encoding='utf-8') as f:
    f.write(content)
