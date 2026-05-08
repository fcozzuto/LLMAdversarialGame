def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    targets = unclaimed or resources
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def score_target(tx, ty):
        d = abs(tx - sx) + abs(ty - sy)
        return d

    tx, ty = sx, sy
    if targets:
        best = None
        for x, y in targets:
            if (x, y) in obstacles:
                continue
            v = score_target(x, y)
            if best is None or v < best[0] or (v == best[0] and (x, y) < best[1]):
                best = (v, (x, y))
        if best is not None:
            tx, ty = best[1]
    else:
        tx, ty = w // 2, h // 2

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dt = abs(nx - tx) + abs(ny - ty)
        do = abs(nx - ox) + abs(ny - oy)
        val = dt * 10 - do
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]