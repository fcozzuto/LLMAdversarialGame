def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("evad" not in self_role and "purs" in opp_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def mob(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                c += 1
        return c
    def dist(x, y):
        return abs(x - ox) + abs(y - oy)

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if self_is_pursuer and nx == ox and ny == oy:
            return [dx, dy]
        # Tie-breaker: avoid obstacle traps (prefer higher mobility)
        if self_is_pursuer:
            # Primary: minimize distance to opponent (and slight preference to center-ish to avoid cornering)
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_bias = -0.05 * (abs(nx - cx) + abs(ny - cy))
            val = -dist(nx, ny) + 0.15 * mob(nx, ny) + center_bias
        else:
            # Evader: maximize distance from pursuer, keep mobility
            val = dist(nx, ny) + 0.10 * mob(nx, ny)
        # Deterministic tie-break: prefer smaller dx, then smaller dy
        if val > best_val or (val == best_val and (best is None or (dx, dy) < best)):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]