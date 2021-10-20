from gurobipy import *
import copy

from car.utl.constants import PLLP_R2_GRID

E = 12

M = len(PLLP_R2_GRID)
N = len(PLLP_R2_GRID[0])

def in_bounds(position):
    i, j = position
    return 0 <= i < M and 0 <= j < N

def dneighborsd(din):
    res = set()
    (a1, a2), (b1, b2), (c1, c2), (d1, d2) = din

    res.add(((a1, a2 + 1), (b1, b2 + 1), (c1, c2 + 1), (d1, d2 + 1)))
    res.add(((a1, a2 - 1), (b1, b2 - 1), (c1, c2 - 1), (d1, d2 - 1)))
    res.add(((a1 + 1, a2), (b1 + 1, b2), (c1 + 1, c2), (d1 + 1, d2)))
    res.add(((a1 - 1, a2), (b1 - 1, b2), (c1 - 1, c2), (d1 - 1, d2)))

    res2 = res.copy()
    for d in res:
        for i, j in d:
            if not in_bounds((i, j)) and d in res2:
                res2.remove(d)

    return list(res2)

def dneighborsp(pfield):
    res = set()
    for dcur in D:
        vertical = pfield[0][0] != pfield[1][0]
        if (vertical):
            neighbors = ((pfield[0][0] - 1, pfield[0][1]),
                         (pfield[1][0] + 1, pfield[1][1]))
        else:
            neighbors = ((pfield[0][0], pfield[0][1] - 1),
                         (pfield[1][0], pfield[1][1] + 1))

        for n in list(filter(in_bounds, neighbors)):
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
            quicksum(0.25 * _d[i, j, d] * Y[d] for d in D) +
            PLLP_R2_GRID[i][j] <= 1
        )

for d in D:
    m.addConstr(Y[d]
                <= quicksum(Y[dd] for dd in dneighborsd(d)))

m.setObjective(quicksum(X[p] for p in P), GRB.MAXIMIZE)

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
            model.cbLazy(Y[d] <= quicksum(Y[dd]
                         for dd in region_neighbors))

m.optimize(callback)

count = 1
for p in P:
    if X[p].x > 0.9:
        for i, j in p:
            PLLP_R2_GRID[i][j] = -count
            count += 1
for d in D:
    if Y[d].x > 0.9:
        for i, j in d:
            PLLP_R2_GRID[i][j] = 2

for row in PLLP_R2_GRID:
    for c in row:
        if c < 0:
            c = "#"
        print(c, end="")
    print("")
