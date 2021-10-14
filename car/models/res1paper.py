from gurobipy import *

from car.utl.helpers import add_border
import grblogtools as glt
import matplotlib.pyplot as plt
from pprint import pprint

def ResOnePaper(grid, e):
    BIGINT = 10e6
    grid_with_border = add_border(grid, 1, e, 1)
    grid_with_border[0][e] = 0
    
    m = Model("Resolution 1")
    m.setParam("LogFile", "res1paper.txt")
    
    M = len(grid) + 1
    N = len(grid[0]) + 1
    
    
    X = {(i, j): m.addVar(vtype=GRB.BINARY) for i in range(M + 1) for j in range(N + 1)}
    Y = {(i, j): m.addVar(vtype=GRB.BINARY) for i in range(M + 1) for j in range(N + 1)}
    fH = {(i, j): m.addVar(lb=-BIGINT) for i in range(M + 1) for j in range(N + 1)}
    fV = {(i, j): m.addVar(lb=-BIGINT) for i in range(M + 1) for j in range(N + 1)}
    absfH = {(i, j): m.addVar() for i in range(M + 1) for j in range(N + 1)}
    absfV = {(i, j): m.addVar() for i in range(M + 1) for j in range(N + 1)}
    
    for i in range(M + 1):
        for j in range(N + 1):
            m.addConstr(absfH[i, j] == abs_(fH[i, j]))
            m.addConstr(absfV[i, j] == abs_(fV[i, j]))
    
    m.setObjective(2 * quicksum(X[i, j] for i in range(1, M) for j in range(1, N)), GRB.MAXIMIZE)
    
    # Definition of the frame
    m.addConstr(2 == Y[0, e] + Y[1, e])  # Entrance is accessible
    
    m.addConstr(
        1 == quicksum(X[i, j] + Y[i, j] for i in range(M + 1) for j in range(N + 1))
        - quicksum(X[i, j] + Y[i, j] for i in range(1, M) for j in range(1, N))
    )
    
    # Connection of parking fields with driving lanes
    for i in range(1, M):
        for j in range(1, N):
            m.addConstr(X[i, j] <= Y[i - 1, j] + Y[i + 1, j] + Y[i, j - 1] + Y[i, j + 1])
    
    # Single purpose for each field
    for i in range(M + 1):
        for j in range(N + 1):
            m.addConstr(1 >= grid_with_border[i][j] + X[i, j] + Y[i, j])
    
    # Connectivity of street fields
    for i in range(M):
        for j in range(N):
            # Vertical flow is conserved
            m.addConstr(absfV[i, j] <= BIGINT * Y[i, j])
            m.addConstr(absfV[i, j] <= BIGINT * Y[i + 1, j])
    
            # Horizontal flow is conserved
            m.addConstr(absfH[i, j] <= BIGINT * Y[i, j])
            m.addConstr(absfH[i, j] <= BIGINT * Y[i, j + 1])
    
    for i in range(1, M):
        for j in range(1, N):
            m.addConstr(Y[i, j] <= fH[i, j] + fV[i, j] - fH[i, j - 1] - fV[i - 1, j])
    
    m.addConstr(-fV[0, e] <= quicksum(Y[i, j] for i in range(1, M) for j in range(1, N)))
    
    m.optimize()
    
    for i in range(M + 1):
        for j in range(N + 1):
            square = "."
            if X[i, j].x > 0.9:
                # parking
                square = "P"
            elif Y[i, j].x > 0.9:
                # street
                square = "D"
    
            print(square, end="")
        print()

    print(M, N)