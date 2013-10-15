###################################################################
#
#   CSSE1001 - Assignment 1 Solution
#
#
###################################################################

#####################################
# Support given below - DO NOT CHANGE
#####################################


HELP = """? - Help.
n - move North one square.
s - move South one square.
e - move East one square.
w - move West one square.
r - Reset to the beginning.
b - Back up a move.
p - List all possible legal directions from the current position.
q - Quit.
"""

WALL = '#'
FINISH = 'X'
FLOOR = ' '
PLAYER = 'O'

DIRECTIONS = {'n': (-1, 0), 's': (1, 0), 'e': (0, 1), 'w': (0, -1)}

def load_maze(filename):
    """Load the maze from filename.

    load_maze(str) -> list(list(str))

    Precondition: filename is readable and is of the correct format.
    """
    f = open(filename, 'rU')
    maze = []
    for line in f:
        maze.append(list(line.strip()))
    return maze

def print_maze(maze, position):
    """Print the maze with the player shown at the given position.

    Precondition: the given position is a valid place in the maze to be.
    """
    x, y = position
    tmp = maze[x][y]
    maze[x][y] = PLAYER
    for row in maze:
        print ''.join(row)
    maze[x][y] = tmp

def get_position_in_direction(position, direction):
    """Return the position of the square adjacent to position in the given 
    direction.

    get_position_in_direction((int, int), str) -> (int, int)
    """
    row, col = position
    dr, dc = DIRECTIONS[direction]
    return (row+dr, col+dc)

def move(maze, position, direction):
    """Return information about a move from position in maze in direction.

    The return value is of the form (new_position, maze_state)
    where maze_state is the label on the square the user tried to move to
    ('X', 'F' or 'O')
    new_position is the position after the move (and is unchanged if the
    move is not valid)

    move(list(list(str)), (int, int), str) -> ((int, int), str)
    """
    x, y = new_position = get_position_in_direction(position, direction)
    value = maze[x][y]
    if value == WALL:
        new_position = position
    return new_position, value

def get_possible_directions(maze, position):
    """Return a list of all legal directions in maze at position.

    get_possible_directions(list(list(str)), (int, int)) -> list(str)
    """
    dirs = []
    for d in 'nsew':
        x, y = get_position_in_direction(position, d)
        if maze[x][y] != WALL:
            dirs.append(d)
    return dirs

def interact():
    """Cary out the user interaction for exploring a maze.

    interact() -> None
    """
    maze_file = raw_input('Maze File: ')
    maze = load_maze(maze_file)
    # invariant: positions[-1] is the current position
    positions = [(1,1)]
    while True:
        print_maze(maze, positions[-1])
        command = raw_input('Command: ').strip()
        if command == 'r':
            del positions[1:]
        elif command == 'b':
            if positions[1:]:
                positions.pop()
        elif command == '?':
            print HELP
        elif command == 'p':
            print 'Possible directions:',','.join(get_possible_directions(maze, positions[-1]))
        elif command == 'q':
            reply = raw_input('Are you sure you want to quit? [y] or n: ')
            if reply.upper() != 'N':
                break
        elif command in list('nsew'):
            newpos, result = move(maze, positions[-1], command)
            if result == FINISH:
                print "Congratulations - you made it!"
                break
            elif result == FLOOR:
                positions.append(newpos)
            else: # result == WALL
                print "You can't go in that direction"
        else:
            print "Invalid Command: {0}".format(command)



##################################################
# !!!!!! Do not change (or add to) the code below !!!!!
# 
# This code will run the interact function if
# you use Run -> Run Module  (F5)
# Because of this we have supplied a "stub" definition
# for interact above so that you won't get an undefined
# error when you are writing and testing your other functions.
# When you are ready please change the definition of interact above.
###################################################

if __name__ == '__main__': interact()
