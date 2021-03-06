import numpy as np


def generate_grid(width: int, height: int, n_obstacles: int):
    grid = [[0 for _ in range(width)] for _ in range(height)]

    obstacles = np.random.choice(width * height, n_obstacles, replace=False)
    for obstacle in obstacles:
        row, col = obstacle // width, obstacle % width
        grid[row][col] = 1

    entrance_choices = set(range(width))
    entrance_choices -= set(obstacles)
    entrance = np.random.choice(list(entrance_choices))

    return grid, entrance
