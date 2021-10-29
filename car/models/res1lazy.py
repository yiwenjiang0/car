__all__ = ["ResOneLazy"]

import gurobipy as gp

from car.utl.helpers import in_bounds

import copy

from .base import BaseModel


def neighbors(i, j, grid):
    return list(filter(lambda p: in_bounds(p, grid), ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1))))


class ResOneLazy(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.m.setParam("LazyConstraints", 1)

        self.num_lazy = 0

        # VARIABLES
        self.X = None
        self.Y = None

        # CONSTRAINTS
        self.entranceAccessible = None
        self.connectParkingFields = None
        self.oneFieldPerSquare = None
        self.streetConnected = None

    def optimize(self):
        rows, cols = range(len(self.grid)), range(len(self.grid[0]))

        def callback(model, where):
            # callback to add the lazy constraint which enforces connectivity
            # of street fields, to be passed to Gurobi
            if where != gp.GRB.Callback.MIPSOL:
                return

            def find_contiguous(i, j, grid):
                tset = {(i, j)}
                grid[i][j] = -1
                for (ii, jj) in neighbors(i, j, grid):
                    if grid[ii][jj] == 1:
                        tset |= find_contiguous(ii, jj, grid)

                return tset

            YV = model.cbGetSolution(self.Y)
            # 1 for street, -1 for visited, 0 otherwise
            grid = [[int(YV[i, j] >= 0.9) for j in cols] for i in rows]

            regions = []
            for i in rows:
                for j in cols:
                    if grid[i][j] == 1:
                        regions.append(find_contiguous(i, j, grid))

            if len(regions) == 1:
                # no disconnected regions in the solution
                return

            for region in regions:
                region_neighbors = set()
                for i, j in region:
                    region_neighbors |= set(neighbors(i, j, grid))

                region_neighbors -= region

                for i, j in region:
                    # Given the current disconnected region, we give the choice
                    # to eliminate the region entirely or add at least one driving
                    # field to the fields surrounding the region
                    model.cbLazy(self.Y[i, j] <= gp.quicksum(self.Y[r, c]
                                                             for r, c in region_neighbors))
                    self.num_lazy += 1

        self.m.optimize(callback)

    def set_variables(self):
        rows, cols = range(len(self.grid)), range(len(self.grid[0]))

        self.X = {(i, j): self.m.addVar(vtype=gp.GRB.BINARY)
                  for i in rows for j in cols}

        self.Y = {(i, j): self.m.addVar(vtype=gp.GRB.BINARY)
                  for i in rows for j in cols}

    def set_constraints(self):
        rows, cols = range(len(self.grid)), range(len(self.grid[0]))

        self.entranceAccessible = self.m.addConstr(self.Y[0,
                                                          self.entrance] == 1)

        self.connectParkingFields = {
            (i, j):
                self.m.addConstr(self.X[i, j] <= gp.quicksum(self.Y[r, c] for r, c in neighbors(i, j, self.grid)))
            for i in rows
            for j in cols
        }

        self.oneFieldPerSquare = {
            (i, j): self.m.addConstr(self.X[i, j] + self.Y[i, j] + self.grid[i][j] <= 1)
            for i in rows
            for j in cols
        }

        self.streetConnected = {
            (i, j): self.m.addConstr(self.Y[i, j] <= gp.quicksum(self.Y[r, c] for r, c in neighbors(i, j, self.grid)))
            for i in rows
            for j in cols
        }

    def set_objective(self):
        rows, cols = range(len(self.grid)), range(len(self.grid[0]))

        self.m.setObjective(2 * gp.quicksum(self.X[i, j] for i in rows
                                            for j in cols), gp.GRB.MAXIMIZE)

    def get_num_lazy(self):
        return self.num_lazy

    def get_optimized_solution(self):
        rows, cols = range(len(self.grid)), range(len(self.grid[0]))

        result = copy.deepcopy(self.grid)

        for i in rows:
            for j in cols:
                if result[i][j] == 1:
                    result[i][j] = '#'

                elif self.Y[i, j].x > 0.9:
                    result[i][j] = 'D'

                elif self.X[i, j].x > 0.9:
                    result[i][j] = 'P'
                    
                else:
                    result[i][j] = '.'

        return result
