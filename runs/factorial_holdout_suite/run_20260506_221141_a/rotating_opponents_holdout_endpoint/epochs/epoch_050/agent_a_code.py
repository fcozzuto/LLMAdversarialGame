def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Strategic change: prioritize resources where we beat the opponent by distance (deterministic).
    best = None
    best_score = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = (do - ds) * 100 - ds  # large weight to capture races
        # tie-break deterministically by coordinates
        key = (-(score), ds, rx, ry)
        if best is None or key < best_score:
            best = (rx, ry)
            best_score = key

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try direct step, else try alternative moves that get us closest to target without hitting obstacles.
    candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0), (-dx, -dy), (-dx, 0), (0, -dy)]
    best_m = (0, 0)
    best_d = None
    seen = set()
    for mx, my in candidates:
        if (mx, my) in seen:
            continue
        seen.add((mx, my))
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if best_d is None or d < best_d or (d == best_d and (mx, my) < best_m):
            best_d = d
            best_m = (mx, my)

    return [int(best_m[0]), int(best_m[1])]