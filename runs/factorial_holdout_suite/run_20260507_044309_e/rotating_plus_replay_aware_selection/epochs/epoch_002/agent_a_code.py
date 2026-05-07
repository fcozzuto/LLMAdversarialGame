def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v
    def cheb(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy
    def best_target():
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (ds - do, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        return best[1] if best else None
    target = best_target()
    if target is None:
        tx, ty = clamp(w // 2, 0, w - 1), clamp(h // 2, 0, h - 1)
    else:
        tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    # Prefer diagonal, then axes, then stay.
    for mx, my in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((mx, my))
    if not candidates:
        return [0, 0]

    def score_move(mx, my):
        nx, ny = sx + mx, sy + my
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (ds - do, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, None)
        # If no resources, just move toward center.
        if best is None:
            return (cheb(nx, ny, w // 2, h // 2),)
        return (best[0][0], best[0][1], best[0][2], best[0][3])
    best_m = min(candidates, key=lambda m: score_move(m[0], m[1]))
    return [int(best_m[0]), int(best_m[1])]