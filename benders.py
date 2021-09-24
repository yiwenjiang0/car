from datagen import Scenario
from gurobipy import *


class Benders(Scenario):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.grid = self.grid()
        self.e = 2
        self.M = len(self.grid[0])
        self.N = len(self.grid)

        self.m = Model("Bender's")
        self.m.setParam("LazyConstraints", 1)

        self.X = {(i, j): self.m.addVar(vtype=GRB.BINARY) for i in range(self.M) for j in range(self.N)}
        self.Y = {(i, j): self.m.addVar(vtype=GRB.BINARY) for i in range(self.M) for j in range(self.N)}

    def solve(self):
        self.m.setObjective(2 * quicksum(self.X[i, j] for i in range(self.M) for j in range(self.N)), GRB.MAXIMIZE)

        # 3) street squares for entrance and exit
        self.m.addConstr(self.Y[0, self.e] + self.Y[1, self.e] == 2)

        # 5) connection of parking fields with driving lane
        connectParkingFields = {
            (i, j): self.m.addConstr(self.X[i, j] <= quicksum(self.Y[ii, jj] for ii, jj in self.neighbors(i, j)))
            for i in range(1, self.M - 1)
            for j in range(1, self.N - 1)
        }

        # 6) one type of field per square
        oneFieldPerSquare = {
            (i, j): self.m.addConstr(self.X[i, j] + self.Y[i, j] + self.grid[i][j] <= 1)
            for i in range(self.M)
            for j in range(self.N)
        }

        # Each street field must be neighbors with one other street field
        # (might be redundant after lazy constraints)
        streetConnected = {
            (i, j): self.m.addConstr(self.Y[i, j] <= quicksum(self.Y[ii, jj] for ii, jj in self.neighbors(i, j)))
            for i in range(1, self.M - 1)
            for j in range(1, self.N - 1)
        }

        self.m.optimize(self.callback)

        for i in range(self.M):
            for j in range(self.N):
                square = " "
                if self.X[i, j].x > 0.9:
                    # parking
                    square = "@"
                elif self.Y[i, j].x > 0.9:
                    # street
                    square = "."

                print(square, end="")
            print()

    def callback(self, model, where):
        if where != GRB.Callback.MIPSOL:
            return

        YV = model.cbGetSolution(self.Y)
        # 1 for street, -1 for visited, 0 otherwise
        grid = [[int(YV[i, j] >= 0.9) for j in range(self.width)] for i in range(self.height)]

        regions = []
        for i in range(self.height):
            for j in range(self.width):
                if grid[i][j] == 1:
                    regions.append(self.find_contiguous(i, j, grid))

        if len(regions) == 1:
            # no disconnected regions
            return

        for region in regions:
            region_neighbors = set()
            for i, j in region:
                region_neighbors |= set(self.neighbors(i, j))

            print(region_neighbors)
            region_neighbors -= region

            for i, j in region:
                model.cbLazy(self.Y[i, j] <= quicksum(self.Y[ii, jj] for ii, jj in region_neighbors))

    def in_bounds(self, position):
        i, j = position
        return 0 <= i < self.height and 0 <= j < self.width

    def neighbors(self, i, j):
        return list(filter(self.in_bounds, ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1))))

    def find_contiguous(self, i, j, grid):
        tset = {(i, j)}
        grid[i][j] = -1
        for (ii, jj) in self.neighbors(i, j):
            if grid[ii][jj] == 1:
                tset |= self.find_contiguous(ii, jj, grid)

        return tset


def main():
    s = Benders()
    s.solve()


if __name__ == '__main__':
    main()
