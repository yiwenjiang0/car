from gurobipy import *

m = Model()
m.setParam("LazyConstraints", 1)


def in_bounds(position):
    i, j = position
    return 0 <= i and i < M and 0 <= j and j < N


def neighbors(i, j):
    return list(filter(in_bounds, ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1))))


# grid form PLLP_R1
grid = [
    [1, 1, 1, 1, 0, 0, 0],
    [1, 1, 1, 1, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
]

grid_with_border = (
    [(len(grid[0]) + 2) * [1]]
    + [[1] + row + [1] for row in grid]
    + [(len(grid[0]) + 2) * [1]]
)


M = len(grid_with_border)
N = len(grid_with_border[0])

# col of entrance square
e = 7
# entrance square is a street field
grid_with_border[0][e] = 0

X = {(i, j): m.addVar(vtype=GRB.BINARY) for i in range(M) for j in range(N)}
Y = {(i, j): m.addVar(vtype=GRB.BINARY) for i in range(M) for j in range(N)}


m.setObjective(2 * quicksum(X[i, j] for i in range(M) for j in range(N)), GRB.MAXIMIZE)

# 3) street squares for entrance and exit
m.addConstr(Y[0, e] + Y[1, e] == 2)

# 5) connection of parking fields with driving lane
connectParkingFields = {
    (i, j): m.addConstr(X[i, j] <= quicksum(Y[ii, jj] for ii, jj in neighbors(i, j)))
    for i in range(1, M - 1)
    for j in range(1, N - 1)
}

# 6) one type of field per square
oneFieldPerSquare = {
    (i, j): m.addConstr(X[i, j] + Y[i, j] + grid_with_border[i][j] <= 1)
    for i in range(M)
    for j in range(N)
}

# Each street field must be neighbors with one other street field
# (might be redundant after lazy constraints)
streetConnected = {
    (i, j): m.addConstr(Y[i, j] <= quicksum(Y[ii, jj] for ii, jj in neighbors(i, j)))
    for i in range(1, M - 1)
    for j in range(1, N - 1)
}


def find_contiguous(i, j, grid):
    tset = {(i, j)}
    grid[i][j] = -1
    for (ii, jj) in neighbors(i, j):
        if grid[ii][jj] == 1:
            tset |= find_contiguous(ii, jj, grid)

    return tset


def callback(model, where):
    if where != GRB.Callback.MIPSOL:
        return

    YV = model.cbGetSolution(Y)
    # 1 for street, -1 for visited, 0 otherwise
    grid = [[int(YV[i, j] >= 0.9) for j in range(N)] for i in range(M)]

    regions = []
    for i in range(M):
        for j in range(N):
            if grid[i][j] == 1:
                regions.append(find_contiguous(i, j, grid))

    if len(regions) == 1:
        # no disconnected regions
        return

    for region in regions:
        region_neighbors = set()
        for i, j in region:
            region_neighbors |= set(neighbors(i, j))

        print(region_neighbors)
        region_neighbors -= region

        for i, j in region:
            model.cbLazy(Y[i, j] <= quicksum(Y[ii, jj] for ii, jj in region_neighbors))


m.optimize(callback)

for i in range(M):
    for j in range(N):
        square = " "
        if X[i, j].x > 0.9:
            # parking
            square = "@"
        elif Y[i, j].x > 0.9:
            # street
            square = "."

        print(square, end="")
    print()
