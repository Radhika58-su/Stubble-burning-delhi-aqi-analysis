with open("anand_vihar.csv", "r", encoding="utf-8", errors="replace") as f:
    for i, line in enumerate(f):
        print(repr(line))
        if i > 8:
            break