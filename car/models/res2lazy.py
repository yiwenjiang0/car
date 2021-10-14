from gurobipy import *
import copy


def ResTwoLazy(grid, E, log_file=None):
    grid = copy.deepcopy(grid)

    M = len(grid)
    N = len(grid[0])

    def in_bounds(position):
        i, j = position
        return 0 <= i < M and 0 <= j < N

    def neighbors(i, j):
        return list(filter(in_bounds, ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1))))

    def dneighbors(i, j):
        res = set()
        for d in D:
            for n in neighbors(i, j):
                if n in d and (i, j) not in d:
                    res.add(d)

        return list(res)

    def dneighborsd(din):
        res = set()
        (a1, a2), (b1, b2), (c1, c2), (d1, d2) = din
        res.add(((a1, a2 + 2), (b1, b2 + 2), (c1, c2 + 2), (d1, d2 + 2)))
        res.add(((a1, a2 - 2), (b1, b2 - 2), (c1, c2 - 2), (d1, d2 - 2)))
        res.add(((a1 + 2, a2), (b1 + 2, b2), (c1 + 2, c2), (d1 + 2, d2)))
        res.add(((a1 - 2, a2), (b1 - 2, b2), (c1 - 2, c2), (d1 - 2, d2)))

        res2 = res.copy()
        for d in res:
            for i, j in d:
                if not in_bounds((i, j)) and d in res2:
                    res2.remove(d)

        return list(res2)

    def dneighborsp(pfield):
        res = set()
        for dcur in D:
            for i, j in pfield:
                for n in neighbors(i, j):
                    if n in dcur:
                        res.add(dcur)
        return list(res)

    # COLUMN GENERATION
    def GenerateParkingFields():
        P = []
        for i in range(M - 1):
            for j in range(N - 1):
                P.append(((i, j), (i + 1, j)))
                P.append(((i, j), (i, j + 1)))
        return P

    def GenerateDrivingFields():
        D = []
        for i in range(M - 1):
            for j in range(N - 1):
                current = (i, j), (i, j + 1), (i + 1, j), (i + 1, j + 1)
                D.append(current)

                if j == E and i == 0:
                    e = current
        return D, e

    P = GenerateParkingFields()
    D, e = GenerateDrivingFields()

    _p = {(i, j, p):
              1 if (i, j) in p else 0
          for i in range(M) for j in range(N) for p in P}

    _d = {(i, j, d):
              1 if (i, j) in d else 0
          for i in range(M) for j in range(N) for d in D}

    # END COLUMN GENERATION

    m = Model()
    m.setParam("LazyConstraints", 1)
    m.setParam("LogFile", "res2lazy.txt")

    X = {p:
             m.addVar(vtype=GRB.BINARY)
         for p in P}

    Y = {d:
             m.addVar(vtype=GRB.BINARY)
         for d in D}

    m.addConstr(Y[e] == 1)

    for i in range(M):
        for j in range(N):
            m.addConstr(quicksum(_p[i, j, p] * X[p] for p in P) <= 1)

    for p in P:
        m.addConstr(X[p]
                    <= quicksum(Y[d] for d in dneighborsp(p)))

    for i in range(M):
        for j in range(N):
            m.addConstr(
                quicksum(_p[i, j, p] * X[p] for p in P) +
                quicksum(_d[i, j, d] * Y[d] for d in D) +
                grid[i][j] <= 1
            )

    for d in D:
        m.addConstr(Y[d]
                    <= quicksum(Y[dd] for dd in dneighborsd(d)))

    m.setObjective(quicksum(X[p] for p in P), GRB.MAXIMIZE)

    from pprint import pprint

    def find_contiguous(d, driving_fields):
        tset = {d}
        driving_fields.remove(d)
        for dd in dneighborsd(d):
            if dd in driving_fields:
                tset |= find_contiguous(dd, driving_fields)

        return tset

    def callback(model, where):
        if where != GRB.Callback.MIPSOL:
            return

        YV = model.cbGetSolution(Y)

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
                region_neighbors |= set(dneighborsd(d))

            region_neighbors -= region

            for d in region:
                model.cbLazy(Y[d] <= quicksum(Y[dd] for dd in region_neighbors))

    m.optimize(callback)

    count = 1
    for p in P:
        if X[p].x > 0.9:
            for i, j in p:
                grid[i][j] = -count
                count += 1
    for d in D:
        if Y[d].x > 0.9:
            for i, j in d:
                grid[i][j] = 2

    return grid, m.objVal, m.Runtime
