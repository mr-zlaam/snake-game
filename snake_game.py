import curses
import time
import random
import os
import sys

def get_high_score_file():
    """Returns the correct path for the high score file"""
    config_dir = os.path.expanduser("~/.config/snake-game")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "high_score.txt")

def draw_start_menu(stdscr, sh, sw):
    stdscr.clear()
    title = "Snake Game"
    options = ["Press 's' to Start Game", "Press 'l' to Set Level (1-9)"]
    stdscr.addstr(sh // 2 - 2, sw // 2 - len(title) // 2, title)
    for i, option in enumerate(options):
        stdscr.addstr(sh // 2 + i, sw // 2 - len(option) // 2, option)
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord('s'):
            stdscr.clear()
            return 8  # Default to level 8
        elif key == ord('l'):
            stdscr.clear()
            stdscr.addstr(sh // 2 - 1, sw // 2 - 10, "Enter Level (1-9): ")
            stdscr.refresh()
            try:
                level = int(stdscr.getch() - ord('0'))
                if 1 <= level <= 9:
                    stdscr.clear()
                    return level
            except:
                continue
        elif key == ord('q'):
            raise SystemExit

def draw_menu(stdscr, sh, sw, score, high_score):
    stdscr.clear()
    title = "Snake Game"
    game_over = f"Game Over! Score: {score}"
    high_score_msg = f"High Score: {high_score}"
    options = ["Press 'r' to Restart", "Press 'q' to Quit"]
    stdscr.addstr(sh // 2 - 3, sw // 2 - len(title) // 2, title)
    stdscr.addstr(sh // 2 - 1, sw // 2 - len(game_over) // 2, game_over)
    stdscr.addstr(sh // 2, sw // 2 - len(high_score_msg) // 2, high_score_msg)
    stdscr.addstr(sh // 2 + 2, sw // 2 - len(options[0]) // 2, options[0])
    stdscr.addstr(sh // 2 + 3, sw // 2 - len(options[1]) // 2, options[1])
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord('r'):
            return True
        elif key == ord('q'):
            return False

def game_loop(stdscr, level, high_score):
    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()
    
    # Calculate dimensions for invisible outer box and visible inner box
    outer_padding = 2
    inner_padding = 1
    
    # Outer box dimensions (invisible)
    outer_height = sh - (outer_padding * 2)
    outer_width = sw - (outer_padding * 2)
    
    # Inner box dimensions (visible)
    inner_height = outer_height - (inner_padding * 2)
    inner_width = outer_width - (inner_padding * 2)
    
    if inner_height < 10 or inner_width < 20:
        stdscr.addstr(0, 0, "Terminal too small!")
        stdscr.refresh()
        time.sleep(2)
        return False, high_score

    # Create invisible outer box (no border drawn)
    outer_win = curses.newwin(outer_height, outer_width, outer_padding, outer_padding)
    
    # Draw stats in outer box header (centered)
    stats_text = f" Level: {level} | Score: 0 | High: {high_score} "
    outer_win.addstr(0, (outer_width - len(stats_text)) // 2, stats_text)
    
    # Create visible inner box
    inner_win = curses.newwin(inner_height, inner_width, 
                             outer_padding + inner_padding, 
                             outer_padding + inner_padding)
    inner_win.box()
    
    # Initialize snake (@ for head, o for body)
    snake_x = inner_width // 4
    snake_y = inner_height // 2
    snake = [
        [snake_y, snake_x],
        [snake_y, snake_x - 1],
        [snake_y, snake_x - 2]
    ]
    for y, x in snake[1:]:
        inner_win.addch(y, x, 'o')
    inner_win.addch(snake[0][0], snake[0][1], '@')

    # Initialize food
    food = [random.randint(1, inner_height - 2), random.randint(1, inner_width - 2)]
    while food in snake:
        food = [random.randint(1, inner_height - 2), random.randint(1, inner_width - 2)]
    inner_win.addch(food[0], food[1], '$')

    direction = curses.KEY_RIGHT
    base_timeout = max(40, 200 - (level * 10))
    score = 0
    inner_win.timeout(base_timeout)
    paused = False

    while True:
        # Update stats
        stats_text = f" Level: {level} | Score: {score} | High: {high_score} "
        outer_win.addstr(0, (outer_width - len(stats_text)) // 2, stats_text)
        outer_win.refresh()
        
        key = inner_win.getch()
        if key == ord(' '):
            paused = not paused
            if paused:
                inner_win.addstr(inner_height // 2, inner_width // 2 - 5, "Paused")
                inner_win.refresh()
                while paused:
                    key = inner_win.getch()
                    if key == ord(' '):
                        paused = False
                        inner_win.addstr(inner_height // 2, inner_width // 2 - 5, "      ")
                        inner_win.refresh()
                    elif key == ord('q'):
                        raise SystemExit
            continue
        elif key == ord('q'):
            raise SystemExit

        if not paused:
            # Only hjkl controls
            key_map = {
                ord('k'): curses.KEY_UP,
                ord('j'): curses.KEY_DOWN,
                ord('h'): curses.KEY_LEFT,
                ord('l'): curses.KEY_RIGHT
            }

            if key in key_map:
                new_dir = key_map[key]
                # Prevent reverse movement
                if not ((direction == curses.KEY_UP and new_dir == curses.KEY_DOWN) or
                        (direction == curses.KEY_DOWN and new_dir == curses.KEY_UP) or
                        (direction == curses.KEY_LEFT and new_dir == curses.KEY_RIGHT) or
                        (direction == curses.KEY_RIGHT and new_dir == curses.KEY_LEFT)):
                    direction = new_dir

            # Move head
            head = snake[0]
            new_head = [head[0], head[1]]
            
            if direction == curses.KEY_UP:
                new_head[0] -= 1
            elif direction == curses.KEY_DOWN:
                new_head[0] += 1
            elif direction == curses.KEY_LEFT:
                new_head[1] -= 1
            elif direction == curses.KEY_RIGHT:
                new_head[1] += 1

            # Check collisions with inner box walls or self
            if (new_head[0] <= 0 or new_head[0] >= inner_height - 1 or 
                new_head[1] <= 0 or new_head[1] >= inner_width - 1 or 
                new_head in snake):
                break

            # Move snake
            snake.insert(0, new_head)
            inner_win.addch(new_head[0], new_head[1], '@')
            inner_win.addch(snake[1][0], snake[1][1], 'o')

            # Check food
            if new_head == food:
                score += level
                if score > high_score:
                    high_score = score
                    try:
                        with open(get_high_score_file(), 'w') as f:
                            f.write(str(high_score))
                    except IOError:
                        pass
                
                # Generate new food
                food = [random.randint(1, inner_height - 2), random.randint(1, inner_width - 2)]
                while food in snake:
                    food = [random.randint(1, inner_height - 2), random.randint(1, inner_width - 2)]
                inner_win.addch(food[0], food[1], '$')
            else:
                tail = snake.pop()
                inner_win.addch(tail[0], tail[1], ' ')

        inner_win.refresh()

    return score, high_score

def main(stdscr):
    high_score = 0
    try:
        with open(get_high_score_file(), 'r') as f:
            high_score = int(f.read().strip())
    except:
        pass

    try:
        while True:
            level = draw_start_menu(stdscr, *stdscr.getmaxyx())
            score, high_score = game_loop(stdscr, level, high_score)
            if not draw_menu(stdscr, *stdscr.getmaxyx(), score, high_score):
                break
    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
        print("Error: Requires Python 3.6+")
        sys.exit(1)
    
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Error: {e}")