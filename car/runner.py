from car.utl.constants import PLLP_R1_GRID, PLLP_R2_GRID

from car.models.res1lazy import ResOneLazy
from car.models.res1paper import ResOnePaper
from car.models.res2lazy import ResTwoLazy
from car.models.res2paper import ResTwoPaper

print("Choose a model from\n"
      "[R1L] Resolution 1, Lazy\n"
      "[R1P] Resolution 1, Flow\n"
      "[R2L] Resolution 2, Lazy (WARNING: slow on some hardware)\n"
      "[R2P] Resolution 2, Flow (WARNING: slow)"
      )

MODELS = {
    "R1L": ResOneLazy,
    "R1P": ResOnePaper,
    "R2L": ResTwoLazy,
    "R2P": ResTwoPaper
}

choice = None
while True:
    choice = input("Make a choice: ")
    if choice not in MODELS:
        print("Not a valid choice:")
    else:
        break

if "R1" in choice:
    grid = PLLP_R1_GRID
    entrance = 6
    
if "R2" in choice:
    grid = PLLP_R2_GRID
    entrance = 12

import copy

original_grid = copy.deepcopy(grid)

model = MODELS[choice](model_name="test", grid=grid, entrance=entrance)

model.solve()

from pprint import pprint

print("ORIGINAL GRID:")

pprint(original_grid)
print()
try:

    optimized_sol = model.get_optimized_solution()

    print("OPTIMIZED GRID ('#' blocked, 'P' parking, 'D' driving)")
    print()
    pprint(optimized_sol)
    
except:
    pass