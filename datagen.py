import scipy.stats as sp
import matplotlib.pyplot as plt
import pandas as pd

from math import ceil, floor
from enum import Enum, auto

def graph():
    pass

def get_df():
    pass

class Shapes(Enum):
    RECT = auto()
    ELBOW = auto()
    RAND = auto()

class Scenario:
    def __init__(self, num_obstacles=3, max_width_height=1000, shape=Shapes.RECT):
        if shape == Shapes.RECT:
            self.width = ceil(sp.uniform.rvs(scale=max_width_height))
            self.height = ceil(sp.uniform.rvs(scale=max_width_height))
            self.entrance_col = ceil(sp.uniform.rvs(scale=self.width))
            
            if num_obstacles:
                self.obstacle_rows = [floor(x) for x in sp.uniform.rvs(size=num_obstacles, scale=self.height)]
                self.obstacle_cols = [floor(x) for x in sp.uniform.rvs(size=num_obstacles, scale=self.width)]
        else:
            pass
        
    def grid(self):
        pass
    
    def grid_with_border(self):
        grid = self.grid()
        grid_with_border = (
            [(len(grid[0]) + 2) * [1]]
            + [[1] + row + [1] for row in grid]
            + [(len(grid[0]) + 2) * [1]]
        )
        return grid_with_border
    
    def solve(self):
        pass
