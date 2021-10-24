__all__ = []

import gurobipy as gp
from car.models.base import BaseModel
from enum import Enum, auto

from car.utl.helpers import add_border

OFFSET = 3
BIGINT = 10e4


def in_bounds(position, grid):
    M, N = len(grid[0]), len(grid)
    i, j = position
    return 0 <= i < M and 0 <= j < N


class Directions(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class ResTwoPaper(BaseModel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        M, N = len(self.grid[0]), len(self.grid)

        # set of squares including border
        self.PLF = [(i, j) for i in range(-OFFSET, M + OFFSET)
                    for j in range(-OFFSET, N + OFFSET)]
        # set of squares including border
        self.PLI = [pos for pos in self.PLF if in_bounds(pos, self.grid)]
        # set of squares on even diagonals
        self.PLFE = [(i, j) for (i, j) in self.PLF if ((i + j) % 2 == 0)]
        # set of squares on even diagonals, not in the border
        self.PLIE = [pos for pos in self.PLFE if in_bounds(pos, self.grid)]
        # set of squares on odd diagonals, not in the border
        self.PLIO = [(i, j) for (i, j) in self.PLI if ((i + j) % 2 == 1)]

        self.grid_with_border = add_border(self.grid, 3, self.entrance, 2)

        self.BOUND = sum(1 - self.grid_with_border[i + OFFSET][j + OFFSET] for i, j in self.PLFE)

        # VARIABLES
        self.X = None
        self.Y = None
        self.fU = None
        self.fD = None

        # CONSTRAINTS

    def set_variables(self):
        self.X = {(direction, *pos): self.m.addVar(vtype=gp.GRB.BINARY)
                  for pos in self.PLFE
                  for direction in Directions}
        self.Y = {pos: self.m.addVar(vtype=gp.GRB.BINARY) for pos in self.PLF}

        # flow to or from upper right neighbor
        self.fU = {pos: self.m.addVar(lb=-self.BOUND, ub=self.BOUND) for pos in self.PLFE}
        # flow to or from the lower right neighbour
        self.fD = {pos: self.m.addVar(lb=-self.BOUND, ub=self.BOUND) for pos in self.PLFE}

    def set_objective(self):
        self.m.setObjective(gp.quicksum(self.X[(d, *pos)]
                                        for pos in self.PLIE for d in Directions), gp.GRB.MAXIMIZE)

    def set_constraints(self):
        M, N = len(self.grid[0]), len(self.grid)

        # (21) frame contains four street fields
        # edited to also count the last col and row
        self.m.addConstr(2 == gp.quicksum(self.Y[pos] for pos in self.PLF)
                         - gp.quicksum(self.Y[i, j] for i, j in self.PLI if i != M - 1 and j != N - 1))

        # no down parking in the last row and no right parking in the last col
        for (i, j) in self.PLIE:
            if i == M - 1:
                self.m.addConstr(self.X[Directions.DOWN, i, j] == 0)
            if j == N - 1:
                self.m.addConstr(self.X[Directions.RIGHT, i, j] == 0)

        # (22) no parking fields in the frame
        self.m.addConstr(0 == gp.quicksum(self.X[(d, *pos)] for pos in self.PLFE for d in Directions)
                         - gp.quicksum(self.X[(d, *pos)] for pos in self.PLIE for d in Directions))

        # (24) define entrance squares in border
        self.m.addConstr(gp.quicksum(self.Y[i, self.entrance] for i in range(-2, 1)) == 3)

        # (28 - 31) connect parking fields with driving lane
        for i, j in self.PLIE:
            self.m.addConstr(self.X[Directions.LEFT, i, j]
                             <= self.Y[i - 1, j - 3] + self.Y[i, j - 3] + self.Y[i - 1, j + 1] + self.Y[i, j + 1])
            self.m.addConstr(self.X[Directions.RIGHT, i, j]
                             <= self.Y[i - 1, j - 2] + self.Y[i, j - 2] + self.Y[i - 1, j + 2] + self.Y[i, j + 2])
            self.m.addConstr(self.X[Directions.UP, i, j]
                             <= self.Y[i - 3, j - 1] + self.Y[i - 3, j] + self.Y[i + 1, j - 1] + self.Y[i + 1, j])
            self.m.addConstr(self.X[Directions.DOWN, i, j]
                             <= self.Y[i - 2, j - 1] + self.Y[i - 2, j] + self.Y[i + 2, j - 1] + self.Y[i + 2, j])

        # (32) single purpose for each square
        for i, j in self.PLIE:
            self.m.addConstr(gp.quicksum(self.X[d, i, j] for d in Directions)
                             + gp.quicksum(0.25 * self.Y[ii, jj] for ii in (i - 1, i)
                                           for jj in (j - 1, j))
                             + self.grid_with_border[i + OFFSET][j + OFFSET] <= 1)
        # (33)
        for i, j in self.PLIO:
            self.m.addConstr(self.X[Directions.RIGHT, i, j - 1]
                             + self.X[Directions.LEFT, i, j + 1]
                             + self.X[Directions.DOWN, i - 1, j]
                             + self.X[Directions.UP, i + 1, j]
                             + gp.quicksum(0.25 * self.Y[ii, jj] for ii in (i - 1, i)
                                           for jj in (j - 1, j))
                             + self.grid_with_border[i + OFFSET][j + OFFSET] <= 1)

        # (34, 35)
        for i, j in self.PLFE:
            self.m.addConstr(self.fD[i, j] <= BIGINT * self.Y[i, j])
            self.m.addConstr(-self.fD[i, j] <= BIGINT * self.Y[i, j])

            if i >= -2:
                self.m.addConstr(self.fU[i, j] <= BIGINT * self.Y[i - 1, j])
                self.m.addConstr(-self.fU[i, j] <= BIGINT * self.Y[i - 1, j])

        # (36 - 39) connectivity of street fields by network flow
        for i, j in self.PLIE:
            self.m.addConstr(self.fU[i, j] <= BIGINT * (self.Y[i - 2, j] + self.Y[i - 1, j + 1]))
            self.m.addConstr(self.fD[i, j] <= BIGINT * (self.Y[i + 1, j] + self.Y[i, j + 1]))
            self.m.addConstr(-self.fU[i, j] <= BIGINT * (self.Y[i - 1, j - 1] + self.Y[i, j]))
            self.m.addConstr(-self.fD[i, j] <= BIGINT * (self.Y[i - 1, j] + self.Y[i, j - 1]))

        # (40 - 43) directing flow to entrance and exit
        for i, j in self.PLIE:
            self.m.addConstr(
                self.Y[i, j] <= self.fU[i, j] + self.fD[i, j] - self.fU[i + 1, j - 1] - self.fD[i - 1, j - 1])
            self.m.addConstr(
                self.Y[i, j] <= self.fU[i + 1, j + 1] + self.fD[i + 1, j + 1] - self.fU[i + 2, j] - self.fD[i, j])

        for i, j in self.PLIO:
            self.m.addConstr(
                self.Y[i, j] <= self.fU[i, j + 1] + self.fD[i, j + 1] - self.fU[i + 1, j] - self.fD[i - 1, j])
            self.m.addConstr(
                self.Y[i, j] <= self.fU[i + 1, j] + self.fD[i + 1, j] - self.fU[i + 2, j - 1] - self.fD[i, j - 1])
