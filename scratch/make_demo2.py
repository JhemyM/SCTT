import re

with open('SCTT_Demo.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Auto restart on game over
old_win_logic = """    if (score_a >= POINTS_TO_WIN or score_b >= POINTS_TO_WIN) and abs(score_a - score_b) >= WIN_BY:
        game_over = True
        pen.clear()
        winner = "Left" if score_a > score_b else "Right"
        show_match_end_screen(f"{winner} Wins!")
        if current_mode == "single" and score_a > score_b:
            play_single_player_result_sound(True)
        elif current_mode == "single":
            play_single_player_result_sound(False)
        else:
            play_single_player_result_sound(True)"""

new_win_logic = """    if (score_a >= POINTS_TO_WIN or score_b >= POINTS_TO_WIN) and abs(score_a - score_b) >= WIN_BY:
        game_over = True
        reset_game()"""

content = content.replace(old_win_logic, new_win_logic)

with open('SCTT_Demo.py', 'w', encoding='utf-8') as f:
    f.write(content)
