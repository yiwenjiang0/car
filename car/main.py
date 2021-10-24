from pathlib import Path

import pandas as pd

from car.models.res1lazy import ResOneLazy
from car.models.res1paper import ResOnePaper
from car.models.res2lazy import ResTwoLazy
from car.models.res2paper import ResTwoPaper

import pickle

from car.utl.datagen import generate_grid
from car.utl.helpers import r1_grid_to_r2

Path("./grids").mkdir(parents=True, exist_ok=True)


grids = dict()

for w, h in zip(range(5, 16, 5), range(5, 16, 5)):
    for n_obstacles in range(0, 16, 5):
        current = None
        try:
            current = pickle.load(open(f"./grids/{w}x{h}x{n_obstacles}.p", "rb"))
        except (OSError, IOError) as e:
            current = generate_grid(w, h, n_obstacles)
            pickle.dump(current, open(f"./grids/{w}x{h}x{n_obstacles}.p", "wb"))
        finally:
            assert current is not None
            grids[w, h, n_obstacles] = current

Path("./solutions").mkdir(parents=True, exist_ok=True)

MODELS = {
    "R1L": ResOneLazy,
    "R1P": ResOnePaper,
    "R2L": ResTwoLazy,
    "R2P": ResTwoPaper
}

df = pd.DataFrame(columns=["model", "width", "height", "n_obstacles", "obj", "runtime", "n_lazy"])
for w, h, n_obstacles in grids:
    for model in MODELS:
        grid, entrance = grids[w, h, n_obstacles]
        if "R2" in model:
            grid = r1_grid_to_r2(grid)
            entrance *= 2

        s = MODELS[model](model_name=f"{w}x{h}x{n_obstacles}_{model}", grid=grid, entrance=entrance)
        s.set_time_limit(60)
        print(model)
        s.solve()
        # solution = s.get_optimized_solution()
        # pickle.dump(solution, open(f"./solutions/{w}x{h}x{n_obstacles}_{model}.p", "wb"))

        objVal = None
        runtime = None
        n_lazy = None

        if not s.is_infeasible():
            objVal = s.get_objective_value()
            runtime = s.get_runtime()
            if "L" in model:
                n_lazy = s.get_num_lazy()

        df = df.append({
            "model": model,
            "width": w,
            "height": h,
            "n_obstacles": n_obstacles,
            "obj": objVal,
            "runtime": runtime,
            "n_lazy": n_lazy
        }, ignore_index=True)

df.to_csv("results.csv")
