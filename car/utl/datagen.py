import numpy as np


def generate_grid(width: int, height: int, n_obstacles: int):
    grid = [[0 for _ in range(height)] for _ in range(width)]

    obstacles = np.random.choice(width * height, n_obstacles, replace=False)
    for obstacle in obstacles:
        row, col = obstacle // width, obstacle % width

        grid[row][col] = 1

    return grid