def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0] or 0), int(sp[1] or 0)
    ox, oy = int(op[0] or 0)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
    if not res:
        res = [(ox, oy)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    best = (10**18, 10**18)
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Prefer moving toward nearest resource; tie-break by moving away from opponent.
        nr = min(dist2(nx, ny, rx, ry) for rx, ry in res)
        no = dist2(nx, ny, ox, oy)
        cand = (nr, -no)
        if cand < best:
            best = cand
            best_move = (dx, dy)

    dx, dy = best_move
    if dx == 0 and dy == 0:
        # If all blocked, stay put (still valid).
        return [0, 0]
    return [int(dx), int(dy)]