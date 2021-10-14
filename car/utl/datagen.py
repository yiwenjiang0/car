import scipy.stats as sp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from math import ceil, floor, sqrt
from enum import Enum, auto

from pprint import pprint

def Factors(n):
    factors = set()
    for i in range(2, ceil(sqrt(n)) + 1):
        if n / i == n // i:
            factors.add(i)
            
    return factors

def GenerateGrids(area, cell_width):
    area = area // cell_width**2
    factors = Factors(area)
    
    grids = []
    for h in factors:
        w = int(area / h)
        grid = [[0 for _ in range(h)] for _ in range(w)]
        grids.append(grid)
        
    return grids
    