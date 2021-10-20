__all__ = []

from gurobipy import *
from enum import Enum, auto
from car.utl.constants import PLLP_R2_GRID, add_border, PLLP_R2_GRID_WITH_BORDER


# index 0 of the grid starts at index OFFSET on grid_with_border
# (different from the paper by -1 since the paper uses 1-based indexing)
OFFSET = 3

M = len(PLLP_R2_GRID[0])
N = len(PLLP_R2_GRID)

# position of left entrance square on the grid
e = 12

BIGINT = 10e4


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
BOUND = sum(1-PLLP_R2_GRID_WITH_BORDER[i+OFFSET][j+OFFSET] for i, j in PLFE)


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
# edited to also count the last col and row
m.addConstr(2 == quicksum(Y[pos]for pos in PLF)
            - quicksum(Y[i, j] for i, j in PLI if i != M-1 and j != N-1))


# no down parking in the last row and no right parking in the last col
for (i, j) in PLIE:
    if i == M-1:
        m.addConstr(X[Directions.DOWN, i, j] == 0)
    if j == N-1:
        m.addConstr(X[Directions.RIGHT, i, j] == 0)

# (22) no parking fields in the frame
m.addConstr(0 == quicksum(X[(d, *pos)] for pos in PLFE for d in Directions)
            - quicksum(X[(d, *pos)] for pos in PLIE for d in Directions))

# (24) define entrance squares in border
m.addConstr(quicksum(Y[i, e] for i in range(-2, 1)) == 3)

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
                + PLLP_R2_GRID_WITH_BORDER[i + OFFSET][j + OFFSET] <= 1)
# (33)
for i, j in PLIO:
    m.addConstr(X[Directions.RIGHT, i, j-1]
                + X[Directions.LEFT, i, j+1]
                + X[Directions.DOWN, i-1, j]
                + X[Directions.UP, i+1, j]
                + quicksum(0.25 * Y[ii, jj] for ii in (i-1, i)
                           for jj in (j-1, j))
                + PLLP_R2_GRID_WITH_BORDER[i + OFFSET][j + OFFSET] <= 1)

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


# result of r1 solution
m.setParam("Cutoff", 38)
# m.setParam("MIPFocus", 1)
m.optimize()
for i in range(M):
    for j in range(N):
        square = "."
        if Y[i, j].x + Y[i, j-1].x + Y[i-1, j].x + Y[i-1, j-1].x > 0.9:
            # street
            square = "D"
        elif (i, j) in PLIO and 0.9 < (X[Directions.RIGHT, i, j-1].x
                                       + X[Directions.LEFT, i, j+1].x
                                       + X[Directions.DOWN, i-1, j].x
                                       + X[Directions.UP, i+1, j].x):
            square = "P"
        elif (i, j) in PLIE and sum(X[d, i, j].x for d in Directions) > 0.9:
            square = "P"
        print(square, end="")
    print()
