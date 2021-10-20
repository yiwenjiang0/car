from car.models.res1lazy import ResOneLazy
from car.models.res1paper import ResOnePaper
from car.models.res2lazy import ResTwoLazy

from car.utl.constants import PLLP_R1_GRID, PLLP_R1_GRID_WITH_BORDER, PLLP_R2_GRID

s = ResOneLazy(model_name="Res1Lazy", grid=PLLP_R1_GRID, entrance=6)
# s = ResOnePaper(model_name="Res1Paper", grid=PLLP_R1_GRID_WITH_BORDER, entrance=6)
# s = ResTwoLazy(model_name="Res2Lazy", grid=PLLP_R2_GRID, entrance=12)

s.solve()

print(s.get_optimized_solution())