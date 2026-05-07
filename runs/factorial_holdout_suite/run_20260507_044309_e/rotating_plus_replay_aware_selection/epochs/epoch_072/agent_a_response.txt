def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Pick a target we can reach sooner (opponent distance - self distance).
    best_key = None
    best_t = None
    if resources:
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer winning races; then closer; then slightly favor "ahead" (higher y, lower x on average).
            race = do - ds
            key = (race, -ds, -(ry - sy), -abs(rx - (w - 1 - sx)), -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best_t = (rx, ry)

    tx, ty = best_t if best_t is not None else (w // 2, h // 2)

    # Choose move that improves distance to target, while avoiding stepping into obstacles/out of bounds.
    best_m = None
    best_md = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Also prefer moves that keep us from being worse than opponent's reach when races are tight.
        # (Deterministic tie-breakers included.)
        opp_d = cheb(ox, oy, tx, ty)
        key = (d, d - opp_d, -ny, nx, dx, dy)
        if best_md is None or key < best_md:
            best_md = key
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [best_m[0], best_m[1]]