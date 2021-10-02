from typing import List

import gurobipy as gp
import grblogtools as glt

class Scenario:
    def __init__(self, name: str, grid: List[List[int]] = None):
        self.grid = grid
        self.m = gp.Model(name)
        self.log_path = f'./{name}.txt'
        self.M = len(self.grid)
        self.N = len(self.grid[0])

    def solve_model(self):
        self.set_params()
        self.set_variables()
        self.set_objective()
        self.set_constraints()
        self.optimize()
        self.print_result()
        self.produce_plots()

    def set_params(self):
        self.m.setParam("LogFile", self.log_path)

    def set_variables(self):
        pass

    def set_objective(self):
        pass

    def set_constraints(self):
        pass

    def optimize(self):
        self.m.optimize()

    def set_log_path(self, log_path: str):
        self.log_path = log_path

    def print_result(self):
        pass

    def produce_plots(self):
        summary, timelines, rootlp = glt.get_dataframe([self.log_path], timelines=True)
        timelines = timelines.fillna(0)
