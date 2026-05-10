def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick target that we can reach earlier (or at least not later), then closest
    best = None
    best_key = None
    for rx, ry in res:
        myd = man(sx, sy, rx, ry)
        oppd = man(ox, oy, rx, ry)
        lead = oppd - myd
        center = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        # Higher is better: lead first, then prefer smaller distance and more central
        key = (lead, -myd, -center, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # Deterministic move: choose valid step that minimizes distance to target
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    bestd = None
    bestmove = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
            continue
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = man(nx, ny, tx, ty)
        if bestd is None or d < bestd or (d == bestd and (dx, dy) < bestmove):
            bestd = d
            bestmove = (dx, dy)
    return [int(bestmove[0]), int(bestmove[1])]