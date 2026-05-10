def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    offset = int(observation.get("turn_index", 0) or 0) % len(dirs)
    dirs = dirs[offset:] + dirs[:offset]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_key = None

    has_unclaimed = bool(unclaimed)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if has_unclaimed:
            min_u = None
            for ux, uy in unclaimed:
                d = (nx - ux) * (nx - ux) + (ny - uy) * (ny - uy)
                if min_u is None or d < min_u:
                    min_u = d
            key = (0, min_u, -d_opp, dx, dy)
        else:
            key = (1, -d_opp, 0, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]