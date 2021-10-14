def add_border(grid, border_size, e, lane_width):
    grid = (
        [(len(grid[0]) + border_size * 2) * [1] for _ in range(border_size)]
        + [[1] * border_size + row + [1] * border_size for row in grid]
        + [(len(grid[0]) + border_size * 2) * [1] for _ in range(border_size)]
    )

    for i in range(lane_width):
        for j in range(lane_width):
            grid[border_size - i - 1][e + border_size + j] = 0

    return grid
