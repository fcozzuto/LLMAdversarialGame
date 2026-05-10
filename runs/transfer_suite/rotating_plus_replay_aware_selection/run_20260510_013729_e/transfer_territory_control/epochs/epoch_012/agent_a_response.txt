def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    resources = set(map(tuple, observation.get("resources", [])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_count(nx, ny, cellset):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in cellset:
                    c += 1
        return c

    best = None
    best_sc = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        adj_self = adj_count(nx, ny, self_ter)
        adj_opp = adj_count(nx, ny, opp_ter)
        dopp = abs(nx - ox) + abs(ny - oy)

        sc = 0
        if (nx, ny) in resources:
            sc += 250
        if (nx, ny) in self_ter:
            sc += 60 + 7 * adj_self - 2 * adj_opp
        elif (nx, ny) in opp_ter:
            sc += 170 + 6 * adj_self - 10 * adj_opp
        elif (nx, ny) in unclaimed:
            sc += 130 + 9 * adj_self - 7 * adj_opp
        else:
            sc += 15 + 3 * adj_self - 4 * adj_opp

        sc += 25 - dopp  # deterministic push to attack closer to opponent

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return best if best is not None else [0, 0]