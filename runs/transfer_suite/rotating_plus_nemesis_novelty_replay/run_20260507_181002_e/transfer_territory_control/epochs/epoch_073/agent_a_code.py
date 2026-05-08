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

    blocked = toset(observation.get("obstacles"))
    targets = toset(observation.get("resources"))
    if observation.get("remaining_resource_count", None) in (0, "0", "0.0"):
        targets = set()
    if not targets:
        targets = toset(observation.get("unclaimed_cells"))
    if not targets:
        return [0, 0]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_score = None
    tp = sorted(targets)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in blocked:
            continue
        mind = 10**9
        for x, y in tp:
            d = man(nx, ny, x, y)
            if d < mind:
                mind = d
                if mind == 0:
                    break
        opp_adj = 1 if man(nx, ny, ox, oy) <= 1 else 0
        # Prefer closer to targets; avoid opponent proximity; tie-break deterministically by direction
        score = (mind * 10 + opp_adj * 3, dx == 0 and dy == 0)
        if best is None or score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    dx, dy = best
    return [int(dx), int(dy)]