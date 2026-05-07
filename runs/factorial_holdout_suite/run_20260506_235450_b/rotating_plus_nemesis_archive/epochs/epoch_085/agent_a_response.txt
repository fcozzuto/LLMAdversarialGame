def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a "safe" target: maximize opponent delay relative to us.
    # Deterministic tie-breaking: higher margin, then smaller our distance, then lexicographic.
    best_t = None
    best_val = None
    for (rx, ry) in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        val = (do - ds)
        if best_val is None or val > best_val or (val == best_val and (ds < cheb(sx, sy, best_t[0], best_t[1]) or
           (ds == cheb(sx, sy, best_t[0], best_t[1]) and (rx, ry) < best_t))):
            best_val = val
            best_t = (rx, ry)

    tx, ty = best_t

    # Evaluate 1-step moves toward the chosen target, while still preferring states
    # that keep the target safe vs the opponent.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    best_m = (0, 0, sx, sy)
    best_score = None
    for dx, dy, nx, ny in candidates:
        dsn = cheb(nx, ny, tx, ty)
        don = cheb(ox, oy, tx, ty)
        # Safety margin after our move; also slight preference for getting closer.
        score = (don - dsn, -dsn, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_m = (dx, dy, nx, ny)

    return [int(best_m[0]), int(best_m[1])]