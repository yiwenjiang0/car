from gurobipy import *
from car.utl.constants import PLLP_R1_GRID_WITH_BORDER
import grblogtools as glt
import matplotlib.pyplot as plt

from .scenario import Scenario


class ResOneLazy(Scenario):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.e = 7
        self.grid[0][self.e] = 0

    def set_params(self):
        super().set_params()
        self.m.setParam("LazyConstraints", 1)

    def set_variables(self):
        self.X = {(i, j): self.m.addVar(vtype=GRB.BINARY) for i in range(self.M) for j in range(self.N)}
        self.Y = {(i, j): self.m.addVar(vtype=GRB.BINARY) for i in range(self.M) for j in range(self.N)}

    def set_objective(self):
        self.m.setObjective(2 * quicksum(self.X[i, j] for i in range(self.M) for j in range(self.N)), GRB.MAXIMIZE)

    def set_constraints(self):
        # 3) street squares for entrance and exit
        self.m.addConstr(self.Y[0, self.e] + self.Y[1, self.e] == 2)

        # 5) connection of parking fields with driving lane
        connectParkingFields = {
            (i, j): self.m.addConstr(self.X[i, j] <= quicksum(self.Y[ii, jj] for ii, jj in self._neighbors(i, j)))
            for i in range(1, self.M - 1)
            for j in range(1, self.N - 1)
        }

        # 6) one type of field per square
        oneFieldPerSquare = {
            (i, j): self.m.addConstr(self.X[i, j] + self.Y[i, j] + PLLP_R1_GRID_WITH_BORDER[i][j] <= 1)
            for i in range(self.M)
            for j in range(self.N)
        }

        # Each street field must be neighbors with one other street field
        # (might be redundant after lazy constraints)
        streetConnected = {
            (i, j): self.m.addConstr(self.Y[i, j] <= quicksum(self.Y[ii, jj] for ii, jj in self._neighbors(i, j)))
            for i in range(1, self.M - 1)
            for j in range(1, self.N - 1)
        }

    def optimize(self):
        def callback(model, where):
            if where != GRB.Callback.MIPSOL:
                return

            YV = model.cbGetSolution(self.Y)
            # 1 for street, -1 for visited, 0 otherwise
            grid = [[int(YV[i, j] >= 0.9) for j in range(self.N)] for i in range(self.M)]

            regions = []
            for i in range(self.M):
                for j in range(self.N):
                    if grid[i][j] == 1:
                        regions.append(self._find_contiguous(i, j, grid))

            if len(regions) == 1:
                # no disconnected regions
                return

            for region in regions:
                region_neighbors = set()
                for i, j in region:
                    region_neighbors |= set(self._neighbors(i, j))

                region_neighbors -= region

                for i, j in region:
                    model.cbLazy(self.Y[i, j] <= quicksum(self.Y[ii, jj] for ii, jj in region_neighbors))

        self.m.optimize(callback)

    def print_result(self):
        for i in range(self.M):
            for j in range(self.N):
                square = "."
                if self.X[i, j].x > 0.9:
                    # parking
                    square = "P"
                elif self.Y[i, j].x > 0.9:
                    # street
                    square = "D"

                print(square, end="")
            print()

    def _in_bounds(self, position):
        i, j = position
        return 0 <= i < self.M and 0 <= j < self.N

    def _neighbors(self, i, j):
        return list(filter(self._in_bounds, ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1))))

    def _find_contiguous(self, i, j, grid):
        tset = {(i, j)}
        grid[i][j] = -1
        for (ii, jj) in self._neighbors(i, j):
            if grid[ii][jj] == 1:
                tset |= self._find_contiguous(ii, jj, grid)

        return tset
