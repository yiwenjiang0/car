from car.models.res1lazy import ResOneLazy
from car.utl.constants import PLLP_R1_GRID_WITH_BORDER

s = ResOneLazy("Resolution 1 (Lazy)", grid=PLLP_R1_GRID_WITH_BORDER)
s.solve_model()

# while True:
#     print(
#         "Available Models:\n"
#         "Resolution 1 (Paper) [R1P]\n"
#         "Resolution 1 (Lazy Constraints) [R1L]\n"
#     )
#
#     model = input("Choose a model: ")
#
#     if model.lower() == "r1p":
#         break
#     elif model.lower() == "r1l":
#         break
#     else:
#         print("Invalid choice. Try again.\n")
