def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))

    candidates = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    def adj_count(cell_set, nx, ny):
        c = 0
        for dx, dy in dirs:
            tx, ty = nx + dx, ny + dy
            if (tx, ty) in cell_set:
                c += 1
        return c

    best = None
    bestv = None
    for dx, dy in candidates:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_terr:
            v = 1000 + adj_count(self_terr, nx, ny) - adj_count(opp_terr, nx, ny)
        elif (nx, ny) in unclaimed:
            v = 100 + 2 * adj_count(self_terr, nx, ny) - 2 * adj_count(opp_terr, nx, ny)
        elif (nx, ny) in self_terr:
            v = 50 + adj_count(self_terr, nx, ny) - adj_count(opp_terr, nx, ny)
        else:
            v = 0

        # Prefer going toward opponent territory when no strong claim exists
        ox, oy = observation.get("opponent_position", (x, y))
        v -= abs(nx - ox) + abs(ny - oy)
        if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]