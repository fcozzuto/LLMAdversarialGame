def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res or (sx, sy) in obst:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Prefer resources where we have advantage (opponent farther than us), then closer, then deterministic id.
    best = None
    best_t = None
    for tx, ty in res:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        key = (od - sd, -sd, (tx + 31 * ty) % 997)
        if best is None or key > best:
            best = key
            best_t = (tx, ty)

    tx, ty = best_t
    # Move 1 step toward target (diagonal allowed). Prefer step that reduces chebyshev distance; avoid obstacles.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                dist = cheb(nx, ny, tx, ty)
                # Small deterministic tie-breaker: lower dx priority then dy.
                candidates.append((dist, dx, dy))
    candidates.sort(key=lambda z: (z[0], z[1] == 0, z[2] == 0, z[1], z[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]