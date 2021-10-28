__all__ = ["ResTwoLazy"]

import gurobipy as gp

from car.utl.helpers import in_bounds

from .base import BaseModel


# COLUMN GENERATION
def GenerateParkingFields(grid):
    M, N = len(grid), len(grid[0])

    P = []
    for i in range(M - 1):
        for j in range(N - 1):
            P.append(((i, j), (i + 1, j)))
            P.append(((i, j), (i, j + 1)))
    return P


def GenerateDrivingFields(grid, E):
    M, N = len(grid), len(grid[0])

    D = []
    for i in range(M - 1):
        for j in range(N - 1):
            current = (i, j), (i, j + 1), (i + 1, j), (i + 1, j + 1)
            D.append(current)

            if j == E and i == 0:
                e = current
                
    print(E)
    return D, e


# END COLUMN GENERATION


class ResTwoLazy(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        M, N = len(self.grid), len(self.grid[0])

        self.m.setParam("LazyConstraints", 1)

        # COLUMNS GENERATED
        self.P = GenerateParkingFields(self.grid)
        self.D, self.entrance = GenerateDrivingFields(self.grid, self.entrance)

        self._p = {(i, j, p):
                       1 if (i, j) in p else 0
                   for i in range(M) for j in range(N) for p in self.P}

        self._d = {(i, j, d):
                       1 if (i, j) in d else 0
                   for i in range(M) for j in range(N) for d in self.D}

        self.num_lazy = 0

        # VARIABLES
        self.X = None
        self.Y = None

        # CONSTRAINTS
        self.entranceAccessible = None
        self.parkingFieldsNonOverlapping = None
        self.parkingFieldsAccessible = None
        self.singlePurpose = None
        self.drivingFieldsAdjacent = None

    def optimize(self):
        def callback(model, where):
            if where != gp.GRB.Callback.MIPSOL:
                return

            def find_contiguous(d, driving_fields):
                tset = {d}
                driving_fields.remove(d)
                for dd in self._dneighborsd(d):
                    if dd in driving_fields:
                        tset |= find_contiguous(dd, driving_fields)

                return tset

            YV = model.cbGetSolution(self.Y)

            driving_fields = set()
            for d in YV:
                if YV[d] >= 0.9:
                    driving_fields.add(d)

            regions = []
            for d in driving_fields.copy():
                if d in driving_fields:
                    regions.append(find_contiguous(d, driving_fields))

            if len(regions) == 1:
                return

            for region in regions:
                region_neighbors = set()
                for d in region:
                    region_neighbors |= set(self._dneighborsd(d))

                region_neighbors -= region

                for d in region:
                    model.cbLazy(self.Y[d] <= gp.quicksum(self.Y[dd]
                                                          for dd in region_neighbors))
                    self.num_lazy += 1

        self.m.optimize(callback)

    def set_variables(self):
        self.X = {p: self.m.addVar(vtype=gp.GRB.BINARY)
                  for p in self.P}

        self.Y = {d: self.m.addVar(vtype=gp.GRB.BINARY)
                  for d in self.D}

    def set_constraints(self):
        rows, cols = range(len(self.grid)), range(len(self.grid[0]))

        self.entranceAccessible = self.m.addConstr(self.Y[self.entrance] == 1)
        #
        # self.parkingFieldsNonOverlapping = {(i, j):
        #     self.m.addConstr(
        #         gp.quicksum(self._p[i, j, p] * self.X[p] for p in self.P) <= 1)
        #     for i in rows for j in cols}

        self.parkingFieldsAccessible = {p:
            self.m.addConstr(
                self.X[p] <= gp.quicksum(self.Y[d] for d in self._dneighborsp(p)))
            for p in self.P}

        self.singlePurpose = {(i, j):
            self.m.addConstr(
                gp.quicksum(self._p[i, j, p] * self.X[p] for p in self.P) +
                gp.quicksum(0.25 * self._d[i, j, d] * self.Y[d] for d in self.D) +
                self.grid[i][j] <= 1
            )
            for i in rows for j in cols
        }

        self.drivingFieldsAdjacent = {d: self.m.addConstr(
            self.Y[d] <= gp.quicksum(self.Y[dd] for dd in self._dneighborsd(d)))
            for d in self.D}

    def set_objective(self):
        self.m.setObjective(gp.quicksum(self.X[p] for p in self.P), gp.GRB.MAXIMIZE)

    def _dneighborsp(self, pfield):
        res = set()
        for dcur in self.D:
            vertical = pfield[0][0] != pfield[1][0]
            if vertical:
                neighbors = ((pfield[0][0] - 1, pfield[0][1]),
                             (pfield[1][0] + 1, pfield[1][1]))
            else:
                neighbors = ((pfield[0][0], pfield[0][1] - 1),
                             (pfield[1][0], pfield[1][1] + 1))

            for n in list(filter(lambda p: in_bounds(p, self.grid), neighbors)):
                if n in dcur:
                    res.add(dcur)
        return list(res)

    def _dneighborsd(self, din):
        res = set()
        (a1, a2), (b1, b2), (c1, c2), (d1, d2) = din

        res.add(((a1, a2 + 1), (b1, b2 + 1), (c1, c2 + 1), (d1, d2 + 1)))
        res.add(((a1, a2 - 1), (b1, b2 - 1), (c1, c2 - 1), (d1, d2 - 1)))
        res.add(((a1 + 1, a2), (b1 + 1, b2), (c1 + 1, c2), (d1 + 1, d2)))
        res.add(((a1 - 1, a2), (b1 - 1, b2), (c1 - 1, c2), (d1 - 1, d2)))

        res2 = res.copy()
        for d in res:
            for i, j in d:
                if not in_bounds((i, j), self.grid) and d in res2:
                    res2.remove(d)

        return list(res2)

    def get_num_lazy(self):
        return self.num_lazy
