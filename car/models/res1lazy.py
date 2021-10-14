from gurobipy import *
import grblogtools as glt
import matplotlib.pyplot as plt
from pprint import pprint
import copy


def ResOneLazy(grid, e, log_file=None):
    """
    Run the 5x5m resolution model with lazy constraints to enforce connectivity
    of street fields.

    Parameters:
        grid (List[List[int]]): the grid with blocked squares indicated by a 1
        e (int): the column of the entrance to the parking lot
        log_file (Optional[str]): path for the log file of this solve

    Returns:
        (List[List[int]]): the resulting solution, with blocked squares indicated by a 1,
             driving fields indicated by a 3, and unique parking,
             spaces indicated with a unique negative number, otherwise 0
        (int): the objective value, i.e. number of parking spaces in the result
        (int) the runtime: how long the model took to solve
    """
    grid = copy.deepcopy(grid)

    def in_bounds(position):
        i, j = position
        return 0 <= i < M and 0 <= j < N

    def neighbors(i, j):
        return list(filter(in_bounds, ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1))))

    m = Model()

    # GUROBI PARAMS
    m.setParam("LazyConstraints", 1)
    if log_file:
        m.setParam("LogFile", log_file)

    M = len(grid)  # number of rows in the grid
    N = len(grid[0])  # number of columns in the grid

    # Entrance square must not be blocked
    grid[0][e] = 0

    # VARIABLES
    X = {(i, j): m.addVar(vtype=GRB.BINARY)
         for i in range(M) for j in range(N)}
    Y = {(i, j): m.addVar(vtype=GRB.BINARY)
         for i in range(M) for j in range(N)}

    # CONSTRAINTS
    # The entrance is connected to a driving field
    m.addConstr(Y[0, e] + Y[1, e] == 2)

    # Parking fields are accessible from driving fields
    connectParkingFields = {
        (i, j): m.addConstr(X[i, j] <= quicksum(Y[ii, jj] for ii, jj in neighbors(i, j)))
        for i in range(1, M - 1)
        for j in range(1, N - 1)
    }

    # Each grid cell serves at most one purpose
    oneFieldPerSquare = {
        (i, j): m.addConstr(X[i, j] + Y[i, j] + grid[i][j] <= 1)
        for i in range(M)
        for j in range(N)
    }

    # Driving fields are connected to at least one other driving field
    # NOTE: this restraint is redundant given the lazy constrain however
    # including it reduces the solution space while retaining the optimal solution
    streetConnected = {
        (i, j): m.addConstr(Y[i, j] <= quicksum(Y[ii, jj] for ii, jj in neighbors(i, j)))
        for i in range(1, M - 1)
        for j in range(1, N - 1)
    }

    # OBJECTIVE
    m.setObjective(2 * quicksum(X[i, j] for i in range(M)
                   for j in range(N)), GRB.MAXIMIZE)

    def callback(model, where):
        # callback to add the lazy constraint which enforces connectivity
        # of street fields, to be passed to Gurobi
        if where != GRB.Callback.MIPSOL:
            return

        def find_contiguous(i, j, grid):
            tset = {(i, j)}
            grid[i][j] = -1
            for (ii, jj) in neighbors(i, j):
                if grid[ii][jj] == 1:
                    tset |= find_contiguous(ii, jj, grid)

            return tset

        YV = model.cbGetSolution(Y)
        # 1 for street, -1 for visited, 0 otherwise
        grid = [[int(YV[i, j] >= 0.9) for j in range(N)] for i in range(M)]

        regions = []
        for i in range(M):
            for j in range(N):
                if grid[i][j] == 1:
                    regions.append(find_contiguous(i, j, grid))

        if len(regions) == 1:
            # no disconnected regions in the solution
            return

        for region in regions:
            region_neighbors = set()
            for i, j in region:
                region_neighbors |= set(neighbors(i, j))

            region_neighbors -= region

            for i, j in region:
                # Given the current disconneted region, we give the choice
                # to eliminate the region entirely or add at least one driving
                # field to the fields surrounding the region
                model.cbLazy(Y[i, j] <= quicksum(Y[ii, jj]
                             for ii, jj in region_neighbors))

    m.optimize(callback)
    count = 1
    for i in range(M):
        for j in range(N):
            if Y[i, j].x > 0.9:
                grid[i][j] = 2
            elif X[i, j].x > 0.9:
                grid[i][j] = -count
                count += 1

    return grid, m.objVal, m.Runtime
