def add_border(grid, border_size, e):
    grid = (
            [(len(grid[0]) + border_size * 2) * [1] for _ in range(border_size)]
            + [[1] * border_size + row + [1] * border_size for row in grid]
            + [(len(grid[0]) + border_size * 2) * [1] for _ in range(border_size)]
    )

    return grid


def in_bounds(position, grid):
    i, j = position

    M, N = len(grid), len(grid[0])
    return 0 <= i < M and 0 <= j < N


def r1_grid_to_r2(grid):
    M, N = len(grid[0]), len(grid)
    res = [[0 for _ in range(N*2)] for _ in range(M*2)]
    for r in range(M):
        for c in range(N):
            if grid[r][c] == 1:
                res[r * 2][c * 2] = 1
                res[r * 2 + 1][c * 2] = 1
                res[r * 2][c * 2 + 1] = 1
                res[r * 2 + 1][c * 2 + 1] = 1

    return res
