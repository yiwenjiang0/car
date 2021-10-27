__all__ = ["BaseModel"]

from abc import ABC, abstractmethod
from typing import List

import gurobipy as gp


class BaseModel(ABC):
    def __init__(self, model_name: str, grid: List[List[int]], entrance: int, is_logged: bool = False):
        self.grid = grid
        self.grid[0][entrance] = 0
        self.m = gp.Model(model_name)
        self.entrance = entrance

        if is_logged:
            self.m.setParam("LogFile", f"./{model_name}.log")

    def solve(self) -> None:
        """
        Set the variables, constraints, objective, and optimize the model.
        """
        self.set_variables()
        self.set_constraints()
        self.set_objective()
        self.optimize()

    def is_infeasible(self):
        return self.m.Status == gp.GRB.INFEASIBLE

    def get_objective_value(self):
        return self.m.objVal

    def get_runtime(self):
        return self.m.Runtime
    
    def get_gap(self):
        return self.m.MIPGap

    def optimize(self):
        self.m.optimize()

    @abstractmethod
    def set_variables(self):
        """
        Set the variables for the model.

        To be overridden in subclasses.
        :return:
        """
        ...

    @abstractmethod
    def set_constraints(self):
        """
        Set the constraints of the model.

        To be overridden in subclasses.
        :return:
        """
        ...

    @abstractmethod
    def set_objective(self):
        """
        Set the objective for this model.
        :return:
        """
        ...

    def set_time_limit(self, limit: int):
        """
        Set a time limit for the solve() method.

        Params:
            limit: the time limit given in seconds
        """
        self.m.setParam("TimeLimit", limit)

    def set_mip_gap(self, gap: int):
        """
        Set a MIP gap to halt optimization:

        Params:
            gap: the gap to halt at
        """
        self.m.setParam("MIPGap", gap)
