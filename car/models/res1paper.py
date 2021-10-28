__all__ = ["ResOnePaper"]

import gurobipy as gp

from .base import BaseModel

from car.utl.helpers import add_border

BIGINT = 10e6


class ResOnePaper(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.grid_with_border = add_border(self.grid, 1, 6)
        self.entrance += 1
        self.grid_with_border[0][self.entrance] = 0

        # VARIABLES
        self.X = None
        self.Y = None
        self.fH = None
        self.fV = None
        self.absfH = None
        self.absfV = None

        # CONSTRAINTS
        self.entranceAccessible = None
        self.edgeIsDriving = None
        self.parkingAccessible = None
        self.mostOnePurpose = None
        self.verticalFlowConserved1 = None
        self.verticalFlowConserved2 = None
        self.horizontalFlowConserved1 = None
        self.horizontalFlowConserved2 = None
        self.netFlow = None
        self.entranceSinks = None

    def set_variables(self):
        M, N = len(self.grid_with_border), len(self.grid_with_border[0])

        self.X = {(i, j): self.m.addVar(vtype=gp.GRB.BINARY) for i in range(M) for j in range(N)}
        self.Y = {(i, j): self.m.addVar(vtype=gp.GRB.BINARY) for i in range(M) for j in range(N)}
        self.fH = {(i, j): self.m.addVar(lb=-BIGINT) for i in range(M) for j in range(N)}
        self.fV = {(i, j): self.m.addVar(lb=-BIGINT) for i in range(M) for j in range(N)}
        self.absfH = {(i, j): self.m.addVar() for i in range(M) for j in range(N)}
        self.absfV = {(i, j): self.m.addVar() for i in range(M) for j in range(N)}

    def set_constraints(self):
        M, N = len(self.grid_with_border), len(self.grid_with_border[0])

        for i in range(M):
            for j in range(N):
                self.m.addConstr(self.absfH[i, j] == gp.abs_(self.fH[i, j]))
                self.m.addConstr(self.absfV[i, j] == gp.abs_(self.fV[i, j]))

        self.entranceAccessible = self.m.addConstr(2 == self.Y[0, self.entrance] + self.Y[1, self.entrance])

        self.edgeIsDriving = self.m.addConstr(
            1 == gp.quicksum(self.X[i, j] + self.Y[i, j] for i in range(M) for j in range(N))
            - gp.quicksum(self.X[i, j] + self.Y[i, j] for i in range(1, M - 1) for j in range(1, N - 1))
        )

        self.parkingAccessible = {(i, j): self.m.addConstr(
            self.X[i, j] <= self.Y[i - 1, j] + self.Y[i + 1, j] + self.Y[i, j - 1] + self.Y[i, j + 1])
            for i in range(1, M - 1)
            for j in range(1, N - 1)
        }

        self.mostOnePurpose = {(i, j): self.m.addConstr(1 >= self.grid_with_border[i][j] + self.X[i, j] + self.Y[i, j])
                               for i in range(M)
                               for j in range(N)
                               }

        self.verticalFlowConserved1 = {(i, j): self.m.addConstr(self.absfV[i, j] <= BIGINT * self.Y[i, j]) for i in
                                       range(M - 1)
                                       for j in range(N - 1)}

        self.verticalFlowConserved2 = {(i, j): self.m.addConstr(self.absfV[i, j] <= BIGINT * self.Y[i + 1, j]) for i in
                                       range(M - 1)
                                       for j in range(N - 1)}

        self.horizontalFlowConserved1 = {(i, j): self.m.addConstr(self.absfH[i, j] <= BIGINT * self.Y[i, j]) for i in
                                         range(M - 1)
                                         for j in range(N - 1)}

        self.horizontalFlowConserved2 = {(i, j): self.m.addConstr(self.absfH[i, j] <= BIGINT * self.Y[i, j + 1]) for i
                                         in range(M - 1)
                                         for j in range(N - 1)}

        self.netFlow = {(i, j): self.m.addConstr(
            self.Y[i, j] <= self.fH[i, j] + self.fV[i, j] - self.fH[i, j - 1] - self.fV[i - 1, j])
                                    for i in range(1, M - 1) for j in range(1, N - 1)}

        self.entranceSinks = self.m.addConstr(-self.fV[0, self.entrance] <= gp.quicksum(
            self.Y[i, j] for i in range(1, M - 1) for j in range(1, N - 1)))

    def set_objective(self):
        M, N = len(self.grid_with_border), len(self.grid_with_border[0])

        self.m.setObjective(2 * gp.quicksum(self.X[i, j] for i in range(1, M - 1) for j in range(1, N - 1)),
                            gp.GRB.MAXIMIZE)

    def get_optimized_solution(self):
        M, N = len(self.grid_with_border), len(self.grid_with_border[0])
        result = [[0 for _ in range(1, M - 1)] for _ in range(1, N - 1)]

        for i in range(1, M - 1):
            for j in range(1, N - 1):
                result[i - 1][j - 1] = self.grid_with_border[i][j]

                if self.Y[i, j].x > 0.9:
                    result[i - 1][j - 1] = '3'

                if self.X[i, j].x > 0.9:
                    result[i - 1][j - 1] = '2'

        return result
