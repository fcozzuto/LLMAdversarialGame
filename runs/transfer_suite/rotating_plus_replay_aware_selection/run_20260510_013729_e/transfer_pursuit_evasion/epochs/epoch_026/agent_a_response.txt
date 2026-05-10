def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or ("pursuit" in role) or ("chaser" in role) or (role == "pursuer")

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in ob:
                m += 1
        return m

    best = None
    best_score = None

    # Deterministic tie-break: fixed iteration order in deltas and then prefer staying if equal.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in ob:
            continue
        d = manh(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        cen = abs(nx - center_x) + abs(ny - center_y)

        if is_pursuer:
            # primary: reduce distance; bonus for exact capture
            score = (-d * 100.0) + (mob * 1.0) + (-cen * 0.05)
            if nx == ox and ny == oy:
                score += 1e6
        else:
            # evader: increase distance; avoid trapping by staying mobile and slightly away from center if already far
            score = (d * 100.0) + (mob * 1.0) + (cen * 0.02)

        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]