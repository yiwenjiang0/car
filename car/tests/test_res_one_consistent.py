from car.utl.datagen import generate_grid

from car.models.res1lazy import ResOneLazy
from car.models.res1paper import ResOnePaper
"""
The models from the paper and our model should always agree on the objective value. 
"""


def test_res_one_consistent():
    for _ in range(10):
        grid = generate_grid(10, 10, 1)

        res_one_lazy = ResOneLazy(model_name="r1l", grid=grid, entrance=2)
        res_one_paper = ResOnePaper(model_name="r1p", grid=grid, entrance=2)

        res_one_lazy.solve()
        res_one_paper.solve()

        assert res_one_lazy.get_objective_value() == res_one_paper.get_objective_value()


def test_res_one_consistent_no_obstacles():
    for _ in range(10):
        grid = generate_grid(5, 5, 0)
        res_one_lazy = ResOneLazy(model_name="r1l", grid=grid, entrance=2)
        res_one_paper = ResOnePaper(model_name="r1p", grid=grid, entrance=2)

        res_one_lazy.solve()
        res_one_paper.solve()

        assert res_one_lazy.get_objective_value() == res_one_paper.get_objective_value()
