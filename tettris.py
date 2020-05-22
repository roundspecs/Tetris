import curses
import time
import random
import copy


def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLUE)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_CYAN)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_WHITE)
    stdscr.nodelay(1)
    stdscr.timeout(150)

    class Part:
        part_character = u'\u2593'

        def __init__(self, y, x):
            self.x = x
            self.y = y

        def draw(self):
            if self.y >= 0:
                stdscr.addstr(self.y+1, self.x+1, self.part_character)

        def __str__(self):
            return f'|{self.x} {self.y}|'

    class Block:

        def __init__(self, list_of_parts, board, index_of_center=-1):
            self.list_of_parts = list_of_parts
            self.index_of_center = index_of_center
            self.board = board
            self.color = curses.color_pair(random.randint(1, 5))

        def isRotable(self):
            return self.index_of_center >= 0

        def move(self, direction):
            temp = self.list_of_parts[:]
            for part in temp:
                part.x += direction
                if part.x < 0 or part.x >= board.width:
                    break
            else:
                self.list_of_parts = temp

        def rotate_part_clockwise(self, part_to_be_moved_):
            part_to_be_moved = copy.deepcopy(part_to_be_moved_)
            center = self.list_of_parts[self.index_of_center]
            diff_y = part_to_be_moved.y - center.y
            diff_x = part_to_be_moved.x - center.x
            part_to_be_moved.x = center.x - diff_y
            part_to_be_moved.y = center.y + diff_x
            if (part_to_be_moved.y >= board.height or
                part_to_be_moved.x < 0 or
                    part_to_be_moved.x >= board.width):
                return -1
            return part_to_be_moved

        def rotate(self):
            if self.isRotable():
                rotated_list_of_parts = []
                for part in self.list_of_parts:
                    rotated_part = self.rotate_part_clockwise(part)
                    if rotated_part == -1:
                        break
                    rotated_list_of_parts.append(rotated_part)
                else:
                    self.list_of_parts = rotated_list_of_parts

        def draw(self):
            stdscr.attron(self.color)
            for part in self.list_of_parts:
                part.draw()
            stdscr.attroff(self.color)

        def move_down(self):
            for part in self.list_of_parts:
                part.y += 1

        def move_horizontally(self, direction, board):
            for part in self.list_of_parts:
                if ((direction == -1 and part.x == 0) or
                        (direction == 1 and part.x == board.width-1)):
                    return None
                for locked_part in self.board.locked_up:
                    if (part.x == locked_part.x and part.y == locked_part.y):
                        return None
            for part in self.list_of_parts:
                part.x += direction

    class Board:

        color_pair = curses.color_pair(6)
        locked_up = set()
        hash_map = {}

        def __init__(self, height, width):
            self.width = width
            self.height = height

        def locked_up_update(self, list_of_parts):
            self.locked_up.update(list_of_parts)
            self.hash_map = {}
            for part in self.locked_up:
                self.hash_map[part.y] = self.hash_map.get(part.y, 0) + 1

        def locked_up_remove(self, row):
            def is_row(part):
                return part.y != row

            def move_part_down(part):
                if part.y < row:
                    return Part(part.y+1, part.x)
                return part
            self.locked_up = set(filter(is_row, self.locked_up))
            self.locked_up = set(map(move_part_down, self.locked_up))
            self.locked_up_update(self.locked_up)

        def draw(self):
            stdscr.addstr(0, 0, '_')
            stdscr.addstr(0, 0, u'\u250c')
            stdscr.addstr(0, 1, u'\u2500'*self.width)
            stdscr.addstr(0, self.width+1, u'\u2510')
            for j in range(self.height):
                stdscr.addstr(j+1, 0, u'\u2502')
                stdscr.addstr(j+1, self.width+1, u'\u2502')
            stdscr.addstr(self.height+1, 0, u'\u2514')
            stdscr.addstr(self.height+1, 1, u'\u2500'*self.width)
            stdscr.addstr(self.height+1, self.width+1, u'\u2518')

            stdscr.attron(self.color_pair)
            for part in self.locked_up:
                part.draw()
            stdscr.attroff(self.color_pair)

    x, y = stdscr.getmaxyx()
    if x < y:
        board = Board(x-5, int(x*1.2)-5)
    else:
        board = Board(y//1.2-5, y-5)
    # board = Board(x-10, y-10)
    score = 0
    shape_l = Block([Part(-2, 0), Part(-2, 1),
                     Part(-2, 2), Part(-1, 2)], board, 1)
    shape_sqr = Block(
        [Part(-3, 0), Part(-3, 1), Part(-2, 0), Part(-2, 1)], board)
    shape_s = Block([Part(-3, 1), Part(-2, 1),
                     Part(-2, 0), Part(-1, 0)], board, 1)
    shape_s = Block([Part(-3, 1), Part(-2, 1),
                     Part(-2, 2), Part(-1, 2)], board, 1)
    shape_ln = Block([Part(-3, 1), Part(-2, 1), Part(-1, 1)], board, 1)
    shapes = [shape_l, shape_ln, shape_s, shape_sqr]

    def generate_shape(board):
        shape = copy.deepcopy(random.choice(shapes))
        shape.color = curses.color_pair(random.randint(1, 5))
        rand_x = random.randint(0, board.width - 3)
        for part in shape.list_of_parts:
            part.x += rand_x
        return shape

    shape = generate_shape(board)

    while True:

        # stdscr.nodelay(0)
        key = stdscr.getch()
        stdscr.clear()

        for locked_part in board.locked_up:
            if locked_part.y == 1:
                stdscr.addstr(0, 0, '▓     ▓     ▓▓      ▓      ▓             ▓▓▓▓   ▓      ▓     ▓▓▓  ▓   ▓▓  ▓')
                stdscr.addstr(1, 0, ' ▓   ▓    ▓▓  ▓▓    ▓      ▓          ▓▓▓       ▓      ▓   ▓▓     ▓  ▓    ▓')
                stdscr.addstr(2, 0, '  ▓ ▓    ▓      ▓   ▓      ▓         ▓          ▓      ▓  ▓       ▓ ▓     ▓')
                stdscr.addstr(3, 0, '   ▓    ▓        ▓  ▓      ▓         ▓▓▓▓▓▓▓▓   ▓      ▓  ▓       ▓▓      ▓')
                stdscr.addstr(4, 0, '   ▓     ▓      ▓   ▓      ▓                ▓   ▓      ▓  ▓       ▓ ▓     ▓')
                stdscr.addstr(5, 0, '   ▓      ▓▓  ▓▓     ▓▓  ▓▓              ▓▓▓     ▓▓  ▓▓    ▓▓     ▓  ▓     ')
                stdscr.addstr(6, 0, '   ▓        ▓▓         ▓▓            ▓▓▓▓          ▓▓        ▓▓▓  ▓   ▓▓  ▓')
                stdscr.refresh()
                time.sleep(100)

        done = False
        for part in shape.list_of_parts:
            if part.y == board.height-1:
                board.locked_up_update(shape.list_of_parts)
                shape = generate_shape(board)
                break
            for locked_part in board.locked_up:
                if part.y == locked_part.y-1 and part.x == locked_part.x:
                    board.locked_up_update(shape.list_of_parts)
                    shape = generate_shape(board)
                    done = True
                    break
            if done:
                break
        if key == curses.KEY_RIGHT:
            shape.move_horizontally(1, board)
        elif key == curses.KEY_LEFT:
            shape.move_horizontally(-1, board)
        elif key == curses.KEY_UP:
            shape.rotate()
        board.draw()
        shape.draw()
        shape.move_down()
        stdscr.addstr(board.height+2, 0, f'Score: {score}')
        stdscr.refresh()
        for row in board.hash_map.keys():
            if board.hash_map[row] == board.width:
                board.locked_up_remove(row)
                score += 1
                break
        time.sleep(0.01)

    curses.curs_set(1)


curses.wrapper(main)
