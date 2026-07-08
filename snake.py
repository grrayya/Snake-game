import curses
import random
import os

SCORE_FILE = "highscore.txt"

class SnakeGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.sh, self.sw = stdscr.getmaxyx()
        
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Snake
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Food
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Text/Border
        
        self.high_score = self.load_high_score()
        self.reset_game()

    def load_high_score(self):
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, "r") as f:
                try:
                    return int(f.read().strip())
                except ValueError:
                    return 0
        return 0

    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open(SCORE_FILE, "w") as f:
                f.write(str(self.high_score))

    def reset_game(self):
        self.stdscr.clear()
        self.score = 0
        self.speed = 120
        self.paused = False
        self.game_over = False
        
        # Starting position and state
        snake_x = self.sw // 4
        snake_y = self.sh // 2
        self.snake = [
            [snake_y, snake_x],
            [snake_y, snake_x - 1],
            [snake_y, snake_x - 2]
        ]
        self.direction = curses.KEY_RIGHT
        self.food = self.spawn_food()

    def spawn_food(self):
        while True:
            food = [random.randint(1, self.sh - 2), random.randint(1, self.sw - 2)]
            if food not in self.snake:
                return food

    def process_input(self):
        next_key = self.stdscr.getch()
        
        if next_key == ord('p') or next_key == ord('P'):
            self.paused = not self.paused
            return
            
        if next_key == ord('q') or next_key == ord('Q'):
            self.game_over = True
            return

        if next_key != -1 and not self.paused:
            # Prevent instant self-reversal
            if (self.direction == curses.KEY_RIGHT and next_key != curses.KEY_LEFT) or \
               (self.direction == curses.KEY_LEFT and next_key != curses.KEY_RIGHT) or \
               (self.direction == curses.KEY_DOWN and next_key != curses.KEY_UP) or \
               (self.direction == curses.KEY_UP and next_key != curses.KEY_DOWN):
                self.direction = next_key

    def update_logic(self):
        if self.paused:
            return

        head = self.snake[0]
        new_head = [head[0], head[1]]

        if self.direction == curses.KEY_DOWN:
            new_head[0] += 1
        elif self.direction == curses.KEY_UP:
            new_head[0] -= 1
        elif self.direction == curses.KEY_LEFT:
            new_head[1] -= 1
        elif self.direction == curses.KEY_RIGHT:
            new_head[1] += 1

        self.snake.insert(0, new_head)

        # Collision detection (walls or self)
        if (new_head[0] in [0, self.sh - 1] or 
            new_head[1] in [0, self.sw - 1] or 
            new_head in self.snake[1:]):
            self.save_high_score()
            self.show_game_over_screen()
            return

        # Food eating logic
        if new_head == self.food:
            self.score += 10
            self.speed = max(30, self.speed - 3)  # Increase speed (lower timeout)
            self.food = self.spawn_food()
        else:
            self.snake.pop()  # Remove tail if no food eaten

    def draw(self):
        self.stdscr.clear()
        
        # Draw border
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.border(0)
        
        # Draw Scoreboard
        score_text = f" Score: {self.score} | High Score: {self.high_score} "
        self.stdscr.addstr(0, 2, score_text)
        
        if self.paused:
            self.stdscr.addstr(self.sh // 2, self.sw // 2 - 4, " PAUSED ")
            
        self.stdscr.attroff(curses.color_pair(3))

        # Draw Food
        self.stdscr.attron(curses.color_pair(2))
        self.stdscr.addch(self.food[0], self.food[1], curses.ACS_PI)
        self.stdscr.attroff(curses.color_pair(2))

        # Draw Snake
        self.stdscr.attron(curses.color_pair(1))
        for y, x in self.snake:
            self.stdscr.addch(y, x, '█')
        self.stdscr.attroff(curses.color_pair(1))
        
        self.stdscr.refresh()

    def show_game_over_screen(self):
        self.stdscr.clear()
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.border(0)
        
        msg1 = " GAME OVER "
        msg2 = f" Final Score: {self.score} "
        msg3 = " Press 'R' to Restart or 'Q' to Quit "
        
        self.stdscr.addstr(self.sh // 2 - 1, (self.sw - len(msg1)) // 2, msg1)
        self.stdscr.addstr(self.sh // 2, (self.sw - len(msg2)) // 2, msg2)
        self.stdscr.addstr(self.sh // 2 + 1, (self.sw - len(msg3)) // 2, msg3)
        self.stdscr.attroff(curses.color_pair(3))
        self.stdscr.refresh()
        
        # Wait for valid restart/quit input
        while True:
            key = self.stdscr.getch()
            if key in [ord('r'), ord('R')]:
                self.reset_game()
                break
            elif key in [ord('q'), ord('Q')]:
                self.game_over = True
                break

    def run(self):
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        
        while not self.game_over:
            self.stdscr.timeout(self.speed)
            self.process_input()
            if not self.game_over: # Might have quit from input
                self.update_logic()
            if not self.game_over: # Might have died in update
                self.draw()

def main(stdscr):
    game = SnakeGame(stdscr)
    game.run()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("\nThanks for playing!")
