def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) - ox, (h - 1) - oy
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            k = cheb(nx, ny, tx, ty)
            if best is None or k < best[0]:
                best = (k, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Prefer resources where we can arrive no later than opponent, and minimize our arrival time.
    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # key: maximize margin (opponent later), then smaller ds, then stable deterministic ordering
        key = (-(do - ds), ds, rx + 7 * ry, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    # Move one step toward target with local obstacle avoidance; if tie, also avoid giving opponent advantage.
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(ox, oy, rx, ry)
        # Prefer reaching sooner; if equal, keep opponent as late as possible (deterministic).
        key = (ds2, -(do2 - ds2), abs(nx - rx) + abs(ny - ry), dx, dy)
        if best_m is None or key < best_m[0]:
            best_m = (key, dx, dy)
    return [best_m[1], best_m[2]] if best_m else [0, 0]