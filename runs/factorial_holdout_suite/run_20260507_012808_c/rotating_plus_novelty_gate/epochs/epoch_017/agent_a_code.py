def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        cand = [(0, 0), (-dx, 0), (0, -dy), (-dx, -dy), (dx, 0), (0, dy), (dx, dy)]
        for mx, my in cand:
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [mx, my]
        return [0, 0]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue

        # Prefer immediate collection, then resources we can "race" to first.
        val = -0.5 * (abs(nx - ox) + abs(ny - oy))  # keep pressure off opponent path
        for rx, ry in resources:
            if (nx, ny) == (rx, ry):
                val += 100000  # guaranteed collection advantage
                continue
            ds = abs(nx - rx) + abs(ny - ry)
            do = abs(ox - rx) + abs(oy - ry)
            # If we can arrive first, strongly prefer; else mildly prefer being closer.
            if ds < do:
                val += 2000 - 20 * ds
            else:
                val += 30 - 2 * ds + 0.5 * (do - ds)

        # Small tie-break: move reduces our nearest-resource distance
        nearest = min((abs(sx - rx) + abs(sy - ry) for rx, ry in resources), default=0)
        nearest_n = min((abs(nx - rx) + abs(ny - ry) for rx, ry in resources), default=0)
        val += (nearest - nearest_n)

        if val > best_val:
            best_val = val
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]