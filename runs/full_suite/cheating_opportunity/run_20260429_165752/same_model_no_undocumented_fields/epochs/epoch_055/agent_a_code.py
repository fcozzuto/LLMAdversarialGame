def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    if not free(sx, sy):
        sx, sy = 0, 0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        if (sx, sy) in resources:
            return [0, 0]
        tx, ty = min(resources, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            cur = abs(sx - tx) + abs(sy - ty)
            nxt = abs(nx - tx) + abs(ny - ty)
            dv = (cur - nxt) * 10
            dv += (abs(nx - ox) + abs(ny - oy))  # keep some separation
            if best is None or dv > bestv or (dv == bestv and (dx, dy) < best):
                best, bestv = (dx, dy), dv
        if best is not None:
            return [int(best[0]), int(best[1])]

    # No resources or blocked: deterministic tie-break toward staying free and away from opponent
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        v = (abs(nx - ox) + abs(ny - oy)) * 2 - (abs(nx - sx) + abs(ny - sy))  # prefer staying
        if v > bestv or (v == bestv and (dx, dy) < best):
            best, bestv = (dx, dy), v
    return [int(best[0]), int(best[1])]