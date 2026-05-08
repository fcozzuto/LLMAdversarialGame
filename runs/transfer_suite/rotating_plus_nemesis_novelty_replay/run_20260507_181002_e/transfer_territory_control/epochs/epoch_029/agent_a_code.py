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
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))

    if not unclaimed and resources:
        unclaimed = set(resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_path = observation.get("opponent_path") or []
    recent_opp = set()
    for p in opp_path[-3:]:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            recent_opp.add((int(p[0]), int(p[1])))

    targets = list(unclaimed) if unclaimed else (list(resources) if resources else [])
    if targets:
        tx, ty = min(targets, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), abs(t[0] - ox) + abs(t[1] - oy)))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-(10**9), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        odist = abs(nx - ox) + abs(ny - oy)
        penalty = 20 if (nx, ny) in recent_opp else 0
        cell_bonus = 1 if (nx, ny) in unclaimed else (1 if (nx, ny) in resources else 0)
        score = -dist + 0.2 * odist + cell_bonus - penalty
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]