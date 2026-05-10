def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources", []) or []
    cur_res = {(int(r[0]), int(r[1])) for r in resources if r and len(r) >= 2}
    if (sx, sy) in cur_res:
        return [0, 0]

    best = None
    best_key = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx = int(r[0]); ry = int(r[1])
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        self_d = cheb(sx, sy, rx, ry)
        if self_d == 0:
            return [0, 0]
        opp_d = cheb(ox, oy, rx, ry)
        # Favor: we are closer than opponent; and (slight) preference for far/central pressure.
        col_pref = -abs(rx - (w - 1) / 2.0) * 0.01
        row_pref = -abs(ry - (h - 1) / 2.0) * 0.005
        opp_adv = opp_d - self_d
        key = (opp_adv, -self_d, col_pref + row_pref, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Greedy step toward target, with obstacle-aware fallback.
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Score move: prefer moving like desired, then minimizing distance.
        move_like = -((dx - desired_dx) * (dx - desired_dx) + (dy - desired_dy) * (dy - desired_dy))
        dist = cheb(nx, ny, tx, ty)
        candidates.append((move_like, -dist, -abs((nx - ox)) * 0.001, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][3]), int(candidates[0][4])]