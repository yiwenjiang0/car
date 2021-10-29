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

sizes = [3,4,5,6,7,9]

for w, h in zip(sizes, sizes):
    for n_obstacles in range(0, 6, 5):
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

df = pd.DataFrame(columns=["model", "width", "height", "n_obstacles", "obj", "runtime", "n_lazy", "gap", "is_infeasible"])
for w, h, n_obstacles in grids:
    for model in MODELS:
        grid, entrance = grids[w, h, n_obstacles]
        if "R2" in model:
            grid = r1_grid_to_r2(grid)
            entrance *= 2

        s = MODELS[model](model_name=f"{w}x{h}x{n_obstacles}_{model}", grid=grid, entrance=entrance)
        s.set_time_limit(1800)
        print(model)
        s.solve()
        # solution = s.get_optimized_solution()
        # pickle.dump(solution, open(f"./solutions/{w}x{h}x{n_obstacles}_{model}.p", "wb"))

        objVal = None
        runtime = None
        n_lazy = None
        gap = None
        is_infeasible = False

        if not s.is_infeasible():
            objVal = s.get_objective_value()
            runtime = s.get_runtime()
            gap = s.get_gap()
            if "L" in model:
                n_lazy = s.get_num_lazy()
        else:
            is_infeasible ^= is_infeasible

        df = df.append({
            "model": model,
            "width": w,
            "height": h,
            "n_obstacles": n_obstacles,
            "obj": objVal,
            "runtime": runtime,
            "n_lazy": n_lazy,
            "is_infeasible": is_infeasible,
            "gap": gap
        }, ignore_index=True)

df.to_csv("results.csv")
