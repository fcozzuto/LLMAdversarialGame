def choose_move(observation):
    W = observation.get("grid_width", 0)
    H = observation.get("grid_height", 0)
    if W <= 0 or H <= 0:
        return [0, 0]
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (x, y))
    obstacles = observation.get("obstacles", [])
    obs = set()
    for c in obstacles:
        try:
            obs.add((c[0], c[1]))
        except Exception:
            pass

    cands = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs:
                cands.append((nx, ny, dx, dy))
    if not cands:
        return [0, 0]

    resources = observation.get("resources", [])
    if resources:
        targets = [(r[0], r[1]) for r in resources if len(r) >= 2]
    else:
        targets = [(c[0], c[1]) for c in observation.get("unclaimed_cells", []) if len(c) >= 2]

    best = None
    best_s = None
    for nx, ny, dx, dy in cands:
        dist_op = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if targets:
            dmin = None
            for tx, ty in targets:
                d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
                if dmin is None or d < dmin:
                    dmin = d
            s = dist_op - dmin
        else:
            s = dist_op
        if best_s is None or s > best_s:
            best_s = s
            best = (dx, dy)
    return [int(best[0]), int(best[1])]