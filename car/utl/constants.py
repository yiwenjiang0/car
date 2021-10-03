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
# grid_with_border[OFFSET - 1][e + OFFSET] = 0
# grid_with_border[OFFSET - 2][e + OFFSET] = 0
# grid_with_border[OFFSET - 1][e + OFFSET + 1] = 0
# grid_with_border[OFFSET - 2][e + OFFSET + 1] = 0


PLLP_R1_GRID = [
    [1, 1, 1, 1, 0, 0, 0],
    [1, 1, 1, 1, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
]

PLLP_R1_GRID_WITH_BORDER = add_border(PLLP_R1_GRID, 1, 6, 1)

PLLP_R2_GRID = [
    [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

PLLP_R2_GRID_WITH_BORDER = add_border(PLLP_R2_GRID, 3, 12, 2)
