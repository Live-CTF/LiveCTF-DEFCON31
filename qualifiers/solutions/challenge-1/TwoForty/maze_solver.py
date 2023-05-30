#!/usr/bin/env python3
# 
# Thanks https://codereview.stackexchange.com/a/198211
# 
import collections
import string
import time

class MazeRunner:

    def __init__(self, file_path, maze_lines = None):
        if maze_lines:
            self.maze = self.load_maze(maze_lines)
        else:
            with open(file_path,'r') as f:
                maze = [list(line.rstrip()) for line in f.readlines()]
                self.maze = self.load_maze(maze)
        self.Point = collections.namedtuple('Point', 'row col parent')
        self.paths = collections.deque()

    def load_maze(self, maze_lines):
        maze_formatted = [["#.@*".find(l) for l in row] for row in maze_lines]
        maze_formatted[-1] = [i*3 for i in maze_formatted[-1]]
        return maze_formatted

    def show_maze(self):
        for row in self.maze:
            s = ""
            for col in row:
                if str(col) in string.ascii_lowercase:
                    s += col
                else:
                    s += "#.@*"[col&0b001]
            print(s)

    def neighbors(self, p):
        if p.row > 0 and self.maze[p.row-1][p.col] & 0b001:
            yield self.Point(p.row-1, p.col, p)
        if p.row < len(self.maze)-1 and self.maze[p.row+1][p.col] & 0b001:
            yield self.Point(p.row+1, p.col, p)
        if p.col > 0 and self.maze[p.row][p.col-1] & 0b001:
            yield self.Point(p.row, p.col-1, p)
        if p.col < len(self.maze[0])-1 and self.maze[p.row][p.col+1] & 0b001:
            yield self.Point(p.row, p.col+1, p)


    def solve(self):
        solution_found = False
        while self.paths:
            current = self.paths.popleft()
            #if self.maze[current.row][current.col] & 0b010:
            if current.row == (len(self.maze) - 1) or current.col == (len(self.maze[0]) - 1):
                solution_found = True
                print('Solution found!')
                break

            for point in self.neighbors(current):
                if not self.maze[point.row][point.col] & 0b100:
                    self.paths.append(point)
                    self.maze[point.row][point.col] |= 0b100

        if not solution_found:
            raise ValueError("Failed to find solution")

        reverse_path = list()
        while current.parent:
            if current.parent.row == current.row - 1:
                reverse_path.append("s")
            elif current.parent.row == current.row + 1:
                reverse_path.append("n")
            elif current.parent.col == current.col + 1:
                reverse_path.append("w")
            elif current.parent.col == current.col - 1:
                reverse_path.append("e")
            else:
                raise ValueError("Can't follow path!")
            
            current = current.parent
            
        path = "".join(reverse_path[::-1])
        
        print(f"Path: {path}")
        
        return path


        # final_path = []
        # while current:
        #     final_path.append(current)
        #     current = current.parent

        # final_path = final_path[::-1]
        # for i, node in enumerate(final_path):
        #     self.maze[node.row][node.col] = string.ascii_lowercase[i%26]

    def find_path(self):
        start_col = self.maze[1].index(0b0010)
        start_row = 1
        self.paths.append(self.Point(start_row, start_col, None))
        #t0 = time.clock()
        return self.solve()
        #t1 = time.clock()
        #print("Solution found in %.2fms" % ((t1-t0)*1000,))

def main():  

    path = "maze.txt"
    solver = MazeRunner(path)

    solver.find_path()
    solver.show_maze() 

if __name__ == "__main__":
    main()