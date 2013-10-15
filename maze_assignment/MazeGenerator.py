
# Maze generator based on
# http://www.mazeworks.com/mazegen/mazetut/index.htm

import sys,random

# Some useful constants 
WALL = '#'
FINISH = 'X'
FLOOR = ' '

DIRECTIONS = [(-1,0),(1,0), (0,1), (0,-1)]

SQUARES = [WALL,FINISH,FLOOR]

class MazeGenerator(object):
    """For creating mazes."""

    def __init__(self):
        self.maze = None

    def _get_build_adj(self, cell, size):
        """Support for building mazes - get adjacent walls."""

        if self.maze is None:
            return None
        result = []
        for rd, cd in [(-2,0),(2,0), (0,2), (0,-2)]:
            r,c = cell
            nr = r + rd
            nc = c + cd
            if nr == r and nc == c:
                continue
            if nr < 0 or nr > size-1:
                continue
            if nc < 0 or nc > size-1:
                continue
            if self.maze[nr][nc] == WALL:
                result.append((nr,nc))
        return result

    def _set_square(self, i, j, tile):
        """Support for building mazes - set the tile at position (i,j)"""

        if self.maze is not None:
            self.maze[i][j] = tile

    def make_maze(self, n):
        """Return a string representation of a randomly generated maze 
        of size 2*n+1

        make_maze(int) -> string
        """

        m = 2*n+1
        self.maze = [m*[WALL] for i in range(m)]
        num_cells = n*n
        visited = 1
        locations = [(1,1)]
        cell = (1,1)
        self._set_square(1, 1, FLOOR)
        while visited < num_cells:
            adj = self._get_build_adj(cell, m)
            if adj:
                r,c = cell
                cell = random.choice(adj)
                locations.append(cell)
                nr,nc = cell
                self._set_square(nr, nc, FLOOR)
                self._set_square((r+nr)/2, (c+nc)/2, FLOOR)
                visited += 1
            else:
                cell = locations.pop()
        path = [(1,1)]
        longest_list = self._get_longest_path_end(path)
        longest_list.sort()
        _, (r,c) = random.choice(longest_list)
        self._set_square(r, c, FINISH)
        # punch some holes through walls to construct loops
        hashes = [(i,j) for i in range(1,n-1) \
                      for j in range(1,n-1) if self.maze[i][j] == WALL]
        random.shuffle(hashes)
        picks = hashes[:(1+n/8)]
        [self._set_square(i, j, FLOOR) for i,j in picks]
        return '\n'.join([''.join(x) for x in self.maze])

    def _get_adj(self, pos, seen):
        """Support - get the the non-wall squares adjacent to pos"""

        return [(pos[0]+r, pos[1]+c) for r,c in DIRECTIONS if \
                    self.maze[pos[0]+r][ pos[1]+c] != WALL and \
                    (pos[0]+r, pos[1]+c) not in seen]

    def _get_longest_path_end(self, path_sofar):
        """Support - find all the longest paths with path_sofar as the initial
        part of the paths
        """

        longest_list = []
        for pos in (self._get_adj(path_sofar[-1], path_sofar)):
            path_sofar.append(pos)
            longest_list.extend(self._get_longest_path_end(path_sofar))
            path_sofar.pop()
        if longest_list == []:
            longest_list = [(len(path_sofar), path_sofar[-1])]
        return longest_list
      
    def __str__(self):
        if self.maze is None:
            return ''
        return '\n'.join([''.join(x) for x in self.maze])

if __name__ == '__main__':
    m = MazeGenerator()
    m.make_maze(8)
    print m
