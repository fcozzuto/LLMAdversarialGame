def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(dx, dy):
        nx, ny = sx + dx, sy + dy
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    candidates = [(dx, dy) for dx, dy in moves if legal(dx, dy)]
    if not candidates:
        return [0, 0]

    targets = resources if resources else [(ox, oy)]
    best = None
    best_key = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        dself = 10**18
        for tx, ty in targets:
            dd = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            if dd < dself:
                dself = dd
        dopp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        key = (dself, -dopp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]