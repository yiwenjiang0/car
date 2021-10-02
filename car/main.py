from car.models import res1lazy, res1paper

while True:
    print(
        "Available Models:\n"
        "Resolution 1 (Paper) [R1P]\n"
        "Resolution 1 (Lazy Constraints) [R1L]\n"
    )

    model = input("Choose a model: ")

    if model.lower() == "r1p":
        break
    elif model.lower() == "r1l":
        break
    else:
        print("Invalid choice. Try again.\n")
