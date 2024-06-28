import unittest
from maze import *

class Tests(unittest.TestCase):
    def test_maze_create_cells(self):
        num_cols = 20
        num_rows = 15
        m1 = Maze(0, 0, num_rows, num_cols, 40, 40, 
                  rem_col="#d9d9d9")
        self.assertEqual(
            len(m1._cells),
            num_rows,
        )
        self.assertEqual(
            len(m1._cells[0]),
            num_cols,
        )

if __name__ == "__main__":
    unittest.main()