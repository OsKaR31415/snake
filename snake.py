from time import sleep, time
from random import randint
import curses


class Death(BaseException):
    """Error representing the death of the snake."""

    def __init__(self, length: int, level):
        self.length = int(length)
        self.level = level

    def __str__(self):
        return f"Died at level {self.level.level} with length {self.length}."


class Level:
    POINTS_PER_LEVEL = 10


    def __init__(self):
        self.level = 1
        self.points = 0

    def add_point(self):
        self.points += 1
        # after _ points, go to next level
        if self.points > self.POINTS_PER_LEVEL:
            self.points = 0
            self.next()

    def next(self):
        self.level += 1

    def delay(self):
        return 0.1+1/(20+self.level)

    def show(self, stdscr):
        """Show the level info in the stdscr."""
        info = f"level : {self.level} ┃ points: ["
        info += "Ǒ"*self.points + " "*(self.POINTS_PER_LEVEL-self.points) + "]"
        stdscr.addstr(0, 0, info)



class Snake:
    def __init__(self, width, height):
        self.DIRECTION_CHAR = {
                self.move_right: ">",
                self.move_left:  "<",
                self.move_up:    "^",
                self.move_down:  "v"
                }
        self.x = 1
        self.y = 1
        self.width = width//2 - 1
        self.height = height//3 - 1
        self.body = [(self.y, self.x)]
        # set the random coordinates of the apple
        self.apple_coords = tuple()
        self.new_apple_coords()
        # level of the snake
        self.level = Level()
        # method containing the current direction to follow
        self.continue_moving = self.move_right

    def new_apple_coords(self):
        self.apple_coords = (randint(1, self.width - 1),
                             randint(1, self.height - 1))
        while self.apple_coords in self.body:
            self.apple_coords = (randint(1, self.width - 1),
                                 randint(1, self.height))

    def has_lost(self):
        """Test if the snake has stepped over its own body.
        The test must be done before updating the body
        """
        return (self.y, self.x) in self.body

    def update_body(self):
        """Update the body of the snake : append the new position
        and remove the tail if not apple was eaten.
        """
        if self.has_lost():
            raise Death(len(self.body), self.level)
        self.body.append((self.y, self.x))
        # pop the tail of the body only if there is NO apple
        if (self.y, self.x) != self.apple_coords:
            self.body.pop(0)
        else:
            self.level.add_point()
            # change the apple new coords since it has been eaten
            self.new_apple_coords()

    def move_down(self):
        self.y += 1
        self.y %= self.width
        self.continue_moving = self.move_down
        # if self.y == 0:
        #     self.y = self.width

    def move_up(self):
        self.y -= 1
        self.y %= self.width
        self.continue_moving = self.move_up
        # if self.y == 0:
        #     self.y = self.width

    def move_left(self):
        self.x -= 1
        self.x %= self.height
        self.continue_moving = self.move_left
        # if self.x == 0:
        #     self.x = self.height

    def move_right(self):
        self.x += 1
        self.x %= self.height
        self.continue_moving = self.move_right
        # if self.x == 0:
        #     self.x = self.height

    def wait(self, start_time: int):
        """Wait until the step has taken the right time.
        The timing depends on the level."""
        delay = self.level.delay()
        while time() < start_time + delay:
            pass

    def show(self, stdscr):
        """Show the snake in a curses stdscr. """
        # show level info
        self.level.show(stdscr)
        # show snake body
        for y, x in self.body:
            Y, X = 2*y, 3*x
            stdscr.addstr(Y+1, X+1, "┏━┓")
            stdscr.addstr(Y+2, X+1, "┗━┛")
        # show the apple
        apple_y, apple_x = self.apple_coords
        apple_y, apple_x = 2*apple_y, 3*apple_x
        stdscr.addstr(apple_y+1, apple_x+1,   "╭√╮")
        stdscr.addstr(apple_y+2, apple_x+1,   "╰─╯")
        # refresh the screen
        stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)  # hide the cursor
    curses.cbreak(1)
    stdscr.nodelay(1)  # do not wait for the user to move the snake
    scr_width, scr_height = stdscr.getmaxyx()
    snake = Snake(scr_width, scr_height)
    # this function is the one that is used to move the snake
    # to change the snake direction, the value of the variable is changed
    move = snake.move_right
    while True:
        before_step = time()  # time before the snake steps
        stdscr.clear()
        snake.show(stdscr)
        pressed_key = stdscr.getch()
        if pressed_key in (ord("j"), ord("s"), 258):  # 258 is down arrow
            snake.move_down()
        elif pressed_key in (ord("k"), ord("z"), 259):  # 259 is up arrow
            snake.move_up()
        elif pressed_key in (ord("h"), ord("q"), 260):  # 260 is left arrow
            snake.move_left()
        elif pressed_key in (ord("l"), ord("d"), 261):
            snake.move_right()
        else:
            # if no key is pressed, the snake continues in the same direction
            snake.continue_moving()
        try:
            snake.update_body()
        except Death as death:
            return death
            # stdscr.clear()
            # stdscr.addstr(0, 0, f"died with length {death.length}")
            # stdscr.refresh()
            # sleep(1)
            # snake = Snake(scr_width, scr_height)
        snake.wait(start_time = before_step)



if __name__ == "__main__":
    endgame = curses.wrapper(main)
    print(endgame)

