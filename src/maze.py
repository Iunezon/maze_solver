from tkinter import Tk, BOTH, Canvas
import random

class Window():
    def __init__(self, width, height):
        self.__root = Tk()
        self.__root.title = "Maze solver"
        self.__root.geometry(f"{width}x{height}")
        self.canvas = Canvas(self.__root, width=width, height=height)
        self.canvas.pack()
        self.__running = False
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()
    
    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()

    def close(self):
        self.__running = False
    
    def draw_line(self, line, fill_color="black"):
        if not isinstance(line, Line):
            raise ValueError("You did not provide a Line item to draw")
        line.draw(self.canvas, fill_color)
        

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line():
    def __init__(self, X, Y):
        if not isinstance(X, Point):
            raise ValueError("First value is not a Point class")
        
        if not isinstance(Y, Point):
            raise ValueError("Second value is not a Point class")
        
        self.X = X
        self.Y = Y

    def draw(self, canvas, fill_color="black"):
        canvas.create_line(
            self.X.x, 
            self.X.y,
            self.Y.x, 
            self.Y.y, 
            fill=fill_color, 
            width=2
            )

class Cell():
    def __init__(self, x1, x2, y1, y2, win,
                 has_left_wall=True, 
                 has_right_wall=True,
                 has_top_wall=True,
                 has_bottom_wall=True,
                 rem_col = "white",
                 visited = False):
        self._x1 = min(x1, x2) # left
        self._x2 = max(x1, x2) # right
        self._y1 = min(y1, y2) # top
        self._y2 = max(y1, y2) # bottom
        self._win = win
        self.has_left_wall = has_left_wall
        self.has_top_wall = has_top_wall
        self.has_bottom_wall = has_bottom_wall
        self.has_right_wall = has_right_wall
        self.rem_col = rem_col
        self.visited = visited
    
    def draw(self, fill_color="black"):
        p1 = Point(self._x1, self._y1) # top-left
        p2 = Point(self._x1, self._y2) # bot-left
        p3 = Point(self._x2, self._y1) # top-right
        p4 = Point(self._x2, self._y2) # bot-right

        if self.has_bottom_wall:
            Line(p2, p4).draw(self._win.canvas, fill_color)
        else:
            Line(p2, p4).draw(self._win.canvas, fill_color=self.rem_col)

        if self.has_top_wall:
            Line(p1, p3).draw(self._win.canvas, fill_color)
        else:
            Line(p1, p3).draw(self._win.canvas, fill_color=self.rem_col)

        if self.has_left_wall:
            Line(p1, p2).draw(self._win.canvas, fill_color)
        else:
            Line(p1, p2).draw(self._win.canvas, fill_color=self.rem_col)

        if self.has_right_wall:
            Line(p3, p4).draw(self._win.canvas, fill_color)
        else:
            Line(p3, p4).draw(self._win.canvas, fill_color=self.rem_col)

    def draw_move(self, to_cell, undo=False):
        if not isinstance(to_cell, Cell):
            raise ValueError("You did not provide a Cell item to draw")

        if undo:
            fill_color = "gray"
        else:
            fill_color = "red"
        
        p1 = Point(
            (self._x1 + self._x2) / 2,
            (self._y1 + self._y2) / 2
        )

        p2 = Point(
            (to_cell._x1 + to_cell._x2) / 2,
            (to_cell._y1 + to_cell._y2) / 2
        )

        Line(p1, p2).draw(self._win.canvas, fill_color)

class Maze():
    def __init__(self,
                 x1,
                 y1,
                 num_rows,
                 num_cols,
                 cell_size_x,
                 cell_size_y,
                 rem_col="white",
                 win=Window(800, 600),
                 seed=None):
        self.x1 = x1
        self.y1 = y1
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self.rem_col = rem_col
        self.win = win
        self.seed = seed

        if self.seed is not None:
            self.seed = random.seed(seed)

        self._create_cells()
        self._reset_cells_visited()
        self._break_entrance_and_exit()
        self._break_walls_r(0, 0)
        self._reset_cells_visited()

        self._solve()

        self.win.wait_for_close()

    def _create_cells(self):
        self._cells = []

        for row in range(self.num_rows):
            column = [None] * self.num_cols
            self._cells.append(column)
            
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                self._draw_cell(row, col)
    
    def _draw_cell(self, i, j):
        cell_x1 = self.x1 + j * self.cell_size_x
        cell_x2 = self.x1 + (j + 1) * self.cell_size_x
        cell_y1 = self.y1 + i * self.cell_size_y
        cell_y2 = self.y1 + (i + 1) * self.cell_size_y
        self._cells[i][j] = Cell(cell_x1, 
                                cell_x2, 
                                cell_y1, 
                                cell_y2, 
                                self.win,
                                rem_col=self.rem_col)
        self._cells[i][j].draw()
        self._animate()

    def _animate(self):
        self.win.redraw()
        import time
        time.sleep(0.001)

    def _break_entrance_and_exit(self):
        self._cells[0][0].has_top_wall = False
        self._cells[0][0].draw()
        self._cells[self.num_rows - 1][self.num_cols - 1].has_bottom_wall = False
        self._cells[self.num_rows - 1][self.num_cols - 1].draw()
        self._animate()

    def _break_walls_r(self, i, j):
        self._cells[i][j].visited = True

        while True:
            cell_track = []

            if i < self.num_rows - 1 and not self._cells[i + 1][j].visited:  # Check Below
                cell_track.append((1, 0))  # Move down
            if i > 0 and not self._cells[i - 1][j].visited:  # Check Above
                cell_track.append((-1, 0))  # Move up

            if j < self.num_cols - 1 and not self._cells[i][j + 1].visited:  # Check Right
                cell_track.append((0, 1))  # Move right
            if j > 0 and not self._cells[i][j - 1].visited:  # Check Left
                cell_track.append((0, -1))  # Move left

            if not cell_track:
                self._cells[i][j].draw()
                self._animate()
                return
            else:
                n_i, n_j = random.choice(cell_track)
                if n_i == 1:
                    self._cells[i][j].has_bottom_wall = False
                    self._cells[i + 1][j].has_top_wall = False
                    self._break_walls_r(i + 1, j)
                elif n_i == -1:
                    self._cells[i][j].has_top_wall = False
                    self._cells[i - 1][j].has_bottom_wall = False
                    self._break_walls_r(i - 1, j)
                elif n_j == 1:
                    self._cells[i][j].has_right_wall = False
                    self._cells[i][j + 1].has_left_wall = False
                    self._break_walls_r(i, j + 1)
                elif n_j == -1:
                    self._cells[i][j].has_left_wall = False
                    self._cells[i][j - 1].has_right_wall = False
                    self._break_walls_r(i, j - 1)

    def _reset_cells_visited(self):
        for row in self._cells:
            for cell in row:
                cell.visited = False

    def _solve(self):
        return self._solve_r(0, 0)

    def _solve_r(self, i, j):
        self._animate()
        self._cells[i][j].visited = True
        
        if i == self.num_rows - 1 and j == self.num_cols - 1:
            return True
        
        if (i < self.num_rows - 1 
            and not self._cells[i][j].has_bottom_wall 
            and not self._cells[i + 1][j].visited):
            self._cells[i][j].draw_move(self._cells[i + 1][j])
            res = self._solve_r(i + 1, j)
            if res:
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i + 1][j], undo=True)

        if (i > 0 
            and not self._cells[i][j].has_top_wall
            and not self._cells[i - 1][j].visited):  # Check Above
            self._cells[i][j].draw_move(self._cells[i - 1][j])
            res = self._solve_r(i - 1, j)
            if res:
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i - 1][j], undo=True)


        if (j < self.num_cols - 1 
            and not self._cells[i][j].has_right_wall
            and not self._cells[i][j + 1].visited):  # Check Right
            self._cells[i][j].draw_move(self._cells[i][j + 1])
            res = self._solve_r(i, j + 1)
            if res:
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i][j + 1], undo=True)

            
        if (j > 0 
            and not self._cells[i][j].has_left_wall
            and not self._cells[i][j - 1].visited):
            self._cells[i][j].draw_move(self._cells[i][j - 1])
            res = self._solve_r(i, j - 1)
            if res:
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i][j - 1], undo=True)

        return False
       