def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    oppT = toset(observation.get("opponent_territory"))
    selfT = toset(observation.get("self_territory"))

    if not unclaimed and resources:
        unclaimed = set(resources)

    targets = list(unclaimed) if unclaimed else list(resources) if resources else [(sx, sy)]
    tx, ty = targets[0]
    bestd = None
    for x, y in targets:
        d = abs(x - sx) + abs(y - sy)
        if bestd is None or d < bestd:
            bestd, tx, ty = d, x, y

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        md_t = abs(nx - tx) + abs(ny - ty)
        md_o = abs(nx - ox) + abs(ny - oy)
        sc = 0
        if (nx, ny) in resources:
            sc += 8
        if (nx, ny) in unclaimed:
            sc += 5
        if (nx, ny) in oppT:
            sc -= 6
        if (nx, ny) in selfT:
            sc += 2
        sc += md_o * 0.5
        sc += (bestd - md_t) * 1.5
        if best_score is None or sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]