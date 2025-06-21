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
            stdscr.clear()  # Clear menu before starting
            return 8  # Default to level 8
        elif key == ord('l'):
            stdscr.clear()
            stdscr.addstr(sh // 2 - 1, sw // 2 - 10, "Enter Level (1-9): ")
            stdscr.refresh()
            try:
                level = int(stdscr.getch() - ord('0'))  # Get single digit
                if 1 <= level <= 9:
                    stdscr.clear()  # Clear menu after level selection
                    return level
            except:
                continue

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
    curses.curs_set(0)  # Hide cursor
    sh, sw = stdscr.getmaxyx()  # Get screen dimensions
    if sh < 10 or sw < 20:
        stdscr.addstr(0, 0, "Terminal too small!")
        stdscr.refresh()
        time.sleep(2)
        return False, high_score

    w = stdscr.subwin(sh, sw, 0, 0)  # Create game window
    w.box()  # Draw border

    # Initialize snake (using * for body, @ for head)
    snake_x = sw // 4
    snake_y = sh // 2
    snake = [
        [snake_y, snake_x],
        [snake_y, snake_x - 1],
        [snake_y, snake_x - 2]
    ]
    for y, x in snake[1:]:  # Draw body segments as *
        w.addch(y, x, '*')
    w.addch(snake[0][0], snake[0][1], '@')  # Draw head as @

    # Initialize food (using @, but will be regenerated if it overlaps)
    food = [sh // 2, sw // 2]
    while food in snake:
        food = [random.randint(1, sh - 2), random.randint(1, sw - 2)]
    w.addch(food[0], food[1], '@')

    # Initialize direction (right)
    direction = curses.KEY_RIGHT

    # Initialize speed and score
    base_timeout = max(40, 200 - (level * 10))  # 200ms at level 1, 40ms at level 16
    score = 0
    food_count = 0
    w.timeout(base_timeout)
    paused = False

    while True:
        # Display live score and high score at top-right
        w.addstr(1, sw - 20, f"Score: {score}  High: {high_score}")
        # Redraw food to prevent disappearance
        w.addch(food[0], food[1], '@')
        w.refresh()

        try:
            key = w.getch()  # Get user input
        except:
            key = -1

        # Toggle pause/resume with spacebar
        if key == ord(' '):
            paused = not paused
            if paused:
                w.addstr(sh // 2, sw // 2 - 5, "Paused")
                # Redraw food and snake to maintain visibility
                w.addch(food[0], food[1], '@')
                for y, x in snake[1:]:
                    w.addch(y, x, '*')
                w.addch(snake[0][0], snake[0][1], '@')
                w.refresh()
                while paused:
                    key = w.getch()
                    if key == ord(' '):
                        paused = False
                        w.addstr(sh // 2, sw // 2 - 5, "      ")  # Clear "Paused" text
                        w.refresh()
                    elif key == ord('q'):
                        return score, high_score  # Quit game if 'q' pressed while paused
            continue

        if not paused:
            # Map keys to directions (arrow keys and hjkl)
            key_map = {
                curses.KEY_UP: curses.KEY_UP,
                curses.KEY_DOWN: curses.KEY_DOWN,
                curses.KEY_LEFT: curses.KEY_LEFT,
                curses.KEY_RIGHT: curses.KEY_RIGHT,
                ord('k'): curses.KEY_UP,    # Vim: k for up
                ord('j'): curses.KEY_DOWN,  # Vim: j for down
                ord('h'): curses.KEY_LEFT,  # Vim: h for left
                ord('l'): curses.KEY_RIGHT  # Vim: l for right
            }

            # Update direction if valid key pressed
            if key in key_map:
                new_direction = key_map[key]
                # Prevent reversing direction
                if (
                    (new_direction == curses.KEY_RIGHT and direction != curses.KEY_LEFT) or
                    (new_direction == curses.KEY_LEFT and direction != curses.KEY_RIGHT) or
                    (new_direction == curses.KEY_UP and direction != curses.KEY_DOWN) or
                    (new_direction == curses.KEY_DOWN and direction != curses.KEY_UP)
                ):
                    direction = new_direction

            # Calculate new head position
            new_head = [snake[0][0], snake[0][1]]
            if direction == curses.KEY_RIGHT:
                new_head[1] += 1
            elif direction == curses.KEY_LEFT:
                new_head[1] -= 1
            elif direction == curses.KEY_UP:
                new_head[0] -= 1
            elif direction == curses.KEY_DOWN:
                new_head[0] += 1

            # Check for collision with walls
            if new_head[0] <= 0 or new_head[0] >= sh - 1 or new_head[1] <= 0 or new_head[1] >= sw - 1:
                break

            # Check for collision with self
            if new_head in snake[1:]:  # Check body only, not head
                break

            # Insert new head
            snake.insert(0, new_head)
            w.addch(new_head[0], new_head[1], '@')  # Draw new head as @

            # Check if food is eaten
            if new_head == food:
                food_count += 1
                score += level  # Points per bite based on level
                # Generate new food
                food = None
                while food is None or food in snake:
                    nf = [random.randint(1, sh - 2), random.randint(1, sw - 2)]
                    food = nf
                w.addch(food[0], food[1], '@')
                # Update high score live
                if score > high_score:
                    high_score = score
                    high_score_file = get_high_score_file()
                    try:
                        with open(high_score_file, 'w') as f:
                            f.write(str(high_score))
                    except IOError as e:
                        w.addstr(2, 1, f"Error saving high score: {e}")
                        w.refresh()
                        time.sleep(2)
            else:
                tail = snake.pop()
                w.addch(tail[0], tail[1], ' ')

    return score, high_score

def main(stdscr):
    # Load initial high score or initialize to 0
    high_score_file = get_high_score_file()
    high_score = 0
    if os.path.exists(high_score_file):
        try:
            with open(high_score_file, 'r') as f:
                content = f.read().strip()
                if content.isdigit():
                    high_score = int(content)
        except (IOError, ValueError) as e:
            stdscr.addstr(0, 0, f"Error reading high score: {e}")
            stdscr.refresh()
            time.sleep(2)

    while True:
        level = draw_start_menu(stdscr, *stdscr.getmaxyx())
        score, high_score = game_loop(stdscr, level, high_score)
        if score is False:  # Terminal too small
            break
        sh, sw = stdscr.getmaxyx()
        if not draw_menu(stdscr, sh, sw, score, high_score):
            break

if __name__ == '__main__':
    # Check for Python version before starting
    if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
        print("Error: This game requires Python 3.6 or higher.")
        print("Please install Python 3 from https://www.python.org/downloads/")
        sys.exit(1)
    
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nGame exited by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure your terminal supports curses and is large enough (minimum 20x10).")