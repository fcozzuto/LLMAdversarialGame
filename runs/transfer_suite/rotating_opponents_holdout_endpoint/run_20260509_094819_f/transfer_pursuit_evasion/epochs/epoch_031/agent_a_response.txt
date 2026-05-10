def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    role = (observation.get("self_role", "") or "").lower()
    env = (observation.get("environment_name", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or ("escape" in role) or ("evasion" in env) or ("escape" in env)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            if inb(x + dx, y + dy):
                c += 1
        return c

    # Main heuristic: for pursuer minimize distance while keeping mobility; for evader maximize distance
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        mob = mobility(nx, ny)

        # Obstacle proximity penalty (discourage stepping into tight corridors)
        obs_pen = 0
        for bx, by in blocked:
            d = cheb(nx, ny, bx, by)
            if d <= 1:
                obs_pen += 3
            elif d == 2:
                obs_pen += 1

        # Prefer central-ish moves when tied to avoid boundary trapping.
        center_pen = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)

        if is_evader:
            score = (-dist * 10.0) + (-mob * 1.5) + (-center_pen * 0.05) + (obs_pen * 2.0)
        else:
            score = (dist * 10.0) + (-mob * 1.5) + (center_pen * 0.05) + (obs_pen * 2.0)

        if best is None or score < best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        # Deterministic fallback: stay if all moves blocked
        return [0, 0]
    return [int(best[0]), int(best[1])]