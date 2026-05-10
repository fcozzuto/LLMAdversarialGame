def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for it in observation.get("obstacles", []) or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None: 
            continue
        x, y = int(x), int(y)
        if inside(x, y):
            obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("chaser" in self_role)
    is_evader = ("evader" in self_role) or ("runner" in self_role)
    if not (is_pursuer or is_evader):
        # Heuristic fallback: in pursuit_evasion, agent usually pursuer if role mentions it; else behave as pursuer.
        is_pursuer = True

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    # Deterministic tie-break: prefer smaller dx, then smaller dy in list order already deterministic.
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        d2 = dist(nx, ny, ox, oy)

        # Obstacle pressure: penalize being adjacent to obstacles (more important for evader to avoid traps).
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0: 
                    continue
                xx, yy = nx + ax, ny + ay
                if inside(xx, yy) and (xx, yy) in obstacles:
                    adj_pen += 1

        # Pursuer: minimize distance; Evader: maximize distance. Add mild center-seeking to break symmetry.
        centerx, centery = (w - 1) / 2.0, (h - 1) / 2.0
        cen = -dist(nx, ny, int(centerx + 0.0), int(centery + 0.0))

        if is_pursuer:
            score = (-d2) + 0.08 * cen - 0.20 * adj_pen
        else:
            score = (d2) + 0.05 * cen - 0.60 * adj_pen

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]