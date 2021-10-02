from gurobipy import *
from enum import Enum, auto
from car.utl.constants import PLLP_R2_GRID, add_border


# index 0 of the grid starts at index OFFSET on grid_with_border
# (different from the paper by -1 since the paper uses 1-based indexing)
OFFSET = 3
grid_with_border = add_border(PLLP_R2_GRID, OFFSET)


M = len(PLLP_R2_GRID[0])
N = len(PLLP_R2_GRID)

# position of left entrance square on the grid
e = 12

BIGINT = 10e4

# set entrance squares
grid_with_border[OFFSET - 1][e + OFFSET] = 0
grid_with_border[OFFSET - 2][e + OFFSET] = 0
grid_with_border[OFFSET - 1][e + OFFSET + 1] = 0
grid_with_border[OFFSET - 2][e + OFFSET + 1] = 0


def in_bounds(position):
    i, j = position
    return 0 <= i and i < M and 0 <= j and j < N


# positions are relative to the grid (without border) using 0-based indexing

# set of squares including border
PLF = [(i, j) for i in range(-OFFSET, M+OFFSET)
       for j in range(-OFFSET, N+OFFSET)]
# set of squares including border
PLI = [pos for pos in PLF if in_bounds(pos)]
# set of squares on even diagonals
PLFE = [(i, j) for (i, j) in PLF if ((i + j) % 2 == 0)]
# set of squares on even diagonals, not in the border
PLIE = [pos for pos in PLFE if in_bounds(pos)]
# set of squares on odd diagonals, not in the border
PLIO = [(i, j) for (i, j) in PLI if ((i+j) % 2 == 1)]

# flow variables are bounded by the number of unblocked diagonal squares
# TODO: not sure but seems correct?
BOUND = sum(1-grid_with_border[i+OFFSET][j+OFFSET] for i, j in PLFE)


class Directions(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


m = Model("res2 flow model")

X = {(direction, *pos): m.addVar(vtype=GRB.BINARY)
     for pos in PLFE
     for direction in Directions}
Y = {pos: m.addVar(vtype=GRB.BINARY) for pos in PLF}

# flow to or from upper right neighbor
fU = {pos: m.addVar(lb=-BOUND, ub=BOUND) for pos in PLFE}
# flow to or from the lower right neighbour
fD = {pos: m.addVar(lb=-BOUND, ub=BOUND) for pos in PLFE}


m.setObjective(quicksum(X[(d, *pos)]
               for pos in PLIE for d in Directions), GRB.MAXIMIZE)

# (21) frame contains four street fields
m.addConstr(4 == quicksum(Y[pos]for pos in PLF)
            - quicksum(Y[pos] for pos in PLI))

# (22) no parking fields in the frame
m.addConstr(0 == quicksum(X[(d, *pos)] for pos in PLFE for d in Directions)
            - quicksum(X[(d, *pos)] for pos in PLIE for d in Directions))

# (24) define entrance squares in border
m.addConstr(quicksum(Y[i, j] for i in range(-2, 2) for j in (e, e+1)) == 8)

# (28 - 31) connect parking fields with driving lane
for i, j in PLIE:
    m.addConstr(X[Directions.LEFT, i, j]
                <= Y[i-1, j-3] + Y[i, j-3] + Y[i-1, j+1] + Y[i, j+1])
    m.addConstr(X[Directions.RIGHT, i, j]
                <= Y[i-1, j-2] + Y[i, j-2] + Y[i-1, j+2] + Y[i, j+2])
    m.addConstr(X[Directions.UP, i, j]
                <= Y[i-3, j-1] + Y[i-3, j] + Y[i+1, j-1] + Y[i+1, j])
    m.addConstr(X[Directions.DOWN, i, j]
                <= Y[i-2, j-1] + Y[i-2, j] + Y[i+2, j-1] + Y[i+2, j])

# (32) single purpose for each square
for i, j in PLIE:
    m.addConstr(quicksum(X[d, i, j] for d in Directions)
                + quicksum(0.25 * Y[ii, jj] for ii in (i-1, i)
                           for jj in (j-1, j))
                + grid_with_border[i + OFFSET][j + OFFSET] <= 1)
# (33)
for i, j in PLIO:
    m.addConstr(X[Directions.RIGHT, i, j-1]
                + X[Directions.LEFT, i-1, j]
                + X[Directions.DOWN, i-1, j]
                + X[Directions.UP, i+1, j]
                + quicksum(0.25 * Y[ii, jj] for ii in (i-1, i)
                           for jj in (j-1, j))
                + grid_with_border[i + OFFSET][j + OFFSET] <= 1)

# (34, 35)
for i, j in PLFE:
    m.addConstr(fD[i, j] <= BIGINT * Y[i, j])
    m.addConstr(-fD[i, j] <= BIGINT * Y[i, j])

    if i >= -2:
        m.addConstr(fU[i, j] <= BIGINT * Y[i-1, j])
        m.addConstr(-fU[i, j] <= BIGINT * Y[i-1, j])

# (36 - 39) connectivity of street fields by network flow
for i, j in PLIE:
    m.addConstr(fU[i, j] <= BIGINT * (Y[i-2, j] + Y[i-1, j+1]))
    m.addConstr(fD[i, j] <= BIGINT * (Y[i+1, j] + Y[i, j+1]))
    m.addConstr(-fU[i, j] <= BIGINT * (Y[i-1, j-1] + Y[i, j]))
    m.addConstr(-fD[i, j] <= BIGINT * (Y[i-1, j] + Y[i, j-1]))

# (40 - 43) directing flow to entrance and exit
for i, j in PLIE:
    m.addConstr(Y[i, j] <= fU[i, j] + fD[i, j] - fU[i+1, j-1] - fD[i-1, j-1])
    m.addConstr(Y[i, j] <= fU[i+1, j+1] + fD[i+1, j+1] - fU[i+2, j] - fD[i, j])

for i, j in PLIO:
    m.addConstr(Y[i, j] <= fU[i, j+1] + fD[i, j+1] - fU[i+1, j] - fD[i-1, j])
    m.addConstr(Y[i, j] <= fU[i+1, j] + fD[i+1, j] - fU[i+2, j-1] - fD[i, j-1])


# outgoing flow is bounded by number of flow squares
# TODO: (seems correct but not sure)
m.addConstr(-fU[-2, e] <= quicksum(Y[i, j] for i, j in PLFE if (i+j) % 2 == 0))

# result of r1 solution
m.setParam("Cutoff", 38)
# m.setParam("MIPFocus", 1)
m.optimize()

for i in range(M+1):
    for j in range(N+1):
        square = "P"
        if grid_with_border[i + OFFSET][j + OFFSET] > 0.9:
            # border / blocked
            square = "."
        elif Y[i, j].x > 0.9:
            # street
            square = "D"

        print(square, end="")
    print()