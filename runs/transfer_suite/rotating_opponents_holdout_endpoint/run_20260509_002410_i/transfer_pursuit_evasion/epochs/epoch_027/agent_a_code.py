def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    sr = (observation.get("self_role") or "").lower()
    orole = (observation.get("opponent_role") or "").lower()
    self_is_pursuer = ("purs" in sr) or ("evad" not in sr and "purs" in orole)
    self_is_evader = ("evad" in sr) or ("purs" not in sr and "evad" in orole)
    if not (self_is_pursuer or self_is_evader):
        self_is_pursuer = True  # safe default

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        if self_is_pursuer:
            dist = man(nx, ny, ox, oy)
            # Prefer moves that reduce distance; slight preference for higher mobility.
            mob = 0
            for ddx, ddy in deltas:
                tx, ty = nx + ddx, ny + ddy
                if inside(tx, ty):
                    mob += 1
            val = (-dist, mob)  # maximize; dist minimized via negative
        else:
            dist = man(nx, ny, ox, oy)
            # Prefer farther from pursuer, avoid trapping (low mobility).
            mob = 0
            for ddx, ddy in deltas:
                tx, ty = nx + ddx, ny + ddy
                if inside(tx, ty):
                    mob += 1
            # maximize dist, then mobility; if tie, prefer staying away from walls by mob
            val = (dist, mob)

        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]