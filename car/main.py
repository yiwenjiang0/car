from car.models.res1lazy import ResOneLazy
from car.models.res1paper import ResOnePaper
from car.models.res2lazy import ResTwoLazy
from car.models.res2paper import ResTwoPaper

from car.utl.datagen import generate_grid

from car.utl.constants import PLLP_R1_GRID, PLLP_R2_GRID

s = ResOneLazy(model_name="Res1Lazy", grid=PLLP_R1_GRID, entrance=6)
s.solve()

s = ResOnePaper(model_name="Res1Paper", grid=PLLP_R1_GRID, entrance=6)
s.solve()

s = ResTwoLazy(model_name="Res2Lazy", grid=PLLP_R2_GRID, entrance=12)
s.solve()
# s = ResTwoPaper(model_name="Res2Paper", grid=PLLP_R2_GRID, entrance=12)
