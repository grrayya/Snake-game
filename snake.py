import curses
import random

def main(stdscr):
    # Setup the terminal screen
    curses.curs_set(0)        # Hide the blinking cursor
    stdscr.nodelay(1)         # Don't pause the program waiting for user input
    stdscr.timeout(100)       # Snake speed (lower is faster)
    
    # Get terminal dimensions
    sh, sw = stdscr.getmaxyx()
    
    # Initialize the snake's starting position (middle of the screen)
    snake_x = sw // 4
    snake_y = sh // 2
    snake = [
        [snake_y, snake_x],
        [snake_y, snake_x - 1],
        [snake_y, snake_x - 2]
    ]
    
    # Place the first piece of food
    food = [sh // 2, sw // 2]
    stdscr.addch(food[0], food[1], curses.ACS_PI)
    
    # Initial movement direction
    key = curses.KEY_RIGHT
    
    # Game Loop
    while True:
        next_key = stdscr.getch()
        key = key if next_key == -1 else next_key
        
        # Calculate the new head position based on current direction
        new_head = [snake[0][0], snake[0][1]]
        
        if key == curses.KEY_DOWN:
            new_head[0] += 1
        if key == curses.KEY_UP:
            new_head[0] -= 1
        if key == curses.KEY_LEFT:
            new_head[1] -= 1
        if key == curses.KEY_RIGHT:
            new_head[1] += 1
            
        # Insert the new head to move the snake forward
        snake.insert(0, new_head)
        
        # Game Over condition: Hit the walls or hit itself
        if (snake[0][0] in [0, sh - 1] or 
            snake[0][1] in [0, sw - 1] or 
            snake[0] in snake[1:]):
            break
            
        # Check if the snake ate the food
        if snake[0] == food:
            food = None
            # Generate new food that doesn't overlap with the snake
            while food is None:
                new_food = [
                    random.randint(1, sh - 2),
                    random.randint(1, sw - 2)
                ]
                food = new_food if new_food not in snake else None
            stdscr.addch(food[0], food[1], curses.ACS_PI)
        else:
            # If food wasn't eaten, pop the tail to maintain length
            tail = snake.pop()
            stdscr.addch(tail[0], tail[1], ' ')
            
        # Draw the new snake head
        try:
            stdscr.addch(snake[0][0], snake[0][1], '#')
        except curses.error:
            # Ignore drawing errors at the extreme edges of the terminal
            pass

# Initialize the curses wrapper to handle safe startup/teardown of the terminal UI
if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nGame safely exited.")
